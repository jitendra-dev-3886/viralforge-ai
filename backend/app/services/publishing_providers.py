"""Durable provider stages. A timed-out final publish is never blindly repeated."""
import json
from urllib.parse import urlparse

from app.services.publishing_accounts import PublishingAccounts, ProviderError, api, request
from app.services.publishing_media import file_path, checksum


class Pending(Exception):
    pass


def save_state(db, job, **values):
    job.provider_state = {**(job.provider_state or {}), **values}
    db.commit()


def require_id(result, key="id"):
    value = result.get(key)
    if not value:
        raise ProviderError("Platform returned no post identifier. Check the account before trying again.", uncertain=True)
    return str(value)


def publish(db, job, account):
    for asset in job.payload["assets"]:
        if checksum(file_path(asset["path"])) != asset["sha256"]:
            raise ProviderError("Selected media changed after scheduling. Cancel and schedule the approved export again.")
    token = PublishingAccounts.token(db, account)
    if account.provider == "instagram":
        return instagram(db, job, account, token)
    if account.provider == "facebook":
        return facebook(db, job, account, token)
    return youtube(db, job, account, token)


def instagram(db, job, account, token):
    graph = PublishingAccounts.graph("instagram")
    headers = {"Authorization": f"Bearer {token}"}
    state, payload = job.provider_state or {}, job.payload
    if not state.get("container_id"):
        assets = payload["assets"]
        fields = {"caption": payload["caption"]}
        if len(assets) > 1:
            children = list(state.get("children", []))
            for asset in assets[len(children):]:
                child = api("POST", f"{graph}/{account.remote_id}/media", headers=headers, data={"image_url": asset["url"], "is_carousel_item": "true"})
                children.append(require_id(child))
                save_state(db, job, children=children)
            for child in children:
                status = api("GET", f"{graph}/{child}", headers=headers, params={"fields": "status_code"})["status_code"]
                if status in {"ERROR", "EXPIRED"}:
                    raise ProviderError("Instagram could not process a carousel image. Check its format and public URL.")
                if status != "FINISHED":
                    raise Pending()
            fields.update(media_type="CAROUSEL", children=",".join(children))
        elif payload["kind"] == "video":
            fields.update(media_type="REELS", video_url=assets[0]["url"], share_to_feed="true")
        else:
            fields["image_url"] = assets[0]["url"]
        result = api("POST", f"{graph}/{account.remote_id}/media", headers=headers, data=fields)
        save_state(db, job, container_id=require_id(result))
        raise Pending()
    container = state["container_id"]
    if not state.get("post_id"):
        result = api("GET", f"{graph}/{container}", headers=headers, params={"fields": "status_code"})
        if result.get("status_code") in {"ERROR", "EXPIRED"}:
            raise ProviderError("Instagram could not process this media. Check the export and public media URL.")
        if result.get("status_code") != "FINISHED":
            raise Pending()
        result = api("POST", f"{graph}/{account.remote_id}/media_publish", headers=headers, data={"creation_id": container})
        save_state(db, job, post_id=require_id(result))
    post_id = job.provider_state["post_id"]
    try:
        link = api("GET", f"{graph}/{post_id}", headers=headers, params={"fields": "permalink"}).get("permalink")
    except ProviderError:
        link = None  # Publishing succeeded even if fetching its link failed.
    return post_id, link, "published"


def facebook(db, job, account, token):
    graph = PublishingAccounts.graph("facebook")
    headers = {"Authorization": f"Bearer {token}"}
    state, payload = job.provider_state or {}, job.payload
    if payload["kind"] == "images":
        if not state.get("post_id"):
            photos = list(state.get("photos", []))
            for asset in payload["assets"][len(photos):]:
                with file_path(asset["path"]).open("rb") as source:
                    result = api("POST", f"{graph}/{account.remote_id}/photos", headers=headers,
                                 data={"published": "false"}, files={"source": (file_path(asset["path"]).name, source, asset["mime"] or "image/jpeg")})
                photos.append(require_id(result))
                save_state(db, job, photos=photos)
            fields = {"message": payload["caption"], **{f"attached_media[{i}]": json.dumps({"media_fbid": id}) for i, id in enumerate(photos)}}
            result = api("POST", f"{graph}/{account.remote_id}/feed", headers=headers, data=fields)
            save_state(db, job, post_id=require_id(result))
        post_id = job.provider_state["post_id"]
        return post_id, f"https://www.facebook.com/{post_id}", "published"
    # Facebook video exports are published as Page Reels.
    if not state.get("video_id"):
        result = api("POST", f"{graph}/{account.remote_id}/video_reels", headers=headers, data={"upload_phase": "start"})
        save_state(db, job, video_id=require_id(result, "video_id"))
    video_id = job.provider_state["video_id"]
    if not job.provider_state.get("uploaded"):
        asset = payload["assets"][0]
        with file_path(asset["path"]).open("rb") as source:
            result = api("POST", f"https://rupload.facebook.com/video-upload/{graph.rsplit('/', 1)[-1]}/{video_id}",
                         headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(asset["size"]), "Content-Type": "application/octet-stream"}, data=source)
        if not result.get("success"):
            raise ProviderError("Facebook did not accept the video upload.")
        save_state(db, job, uploaded=True)
    status = api("GET", f"{graph}/{video_id}", headers=headers, params={"fields": "status"}).get("status", {})
    if status.get("video_status") == "error" or any(status.get(phase, {}).get("status") == "error" for phase in ("uploading_phase", "processing_phase", "publishing_phase")):
        raise ProviderError("Facebook rejected this video. Check Reel duration, dimensions and encoding.")
    if not job.provider_state.get("submitted"):
        if status.get("uploading_phase", {}).get("status") != "complete" and status.get("video_status") != "ready":
            raise Pending()
        result = api("POST", f"{graph}/{account.remote_id}/video_reels", headers=headers, data={"upload_phase": "finish", "video_id": video_id, "video_state": "PUBLISHED", "description": payload["caption"], "title": payload["title"]})
        if not result.get("success"):
            raise ProviderError("Facebook did not confirm publication. Check the Page before posting again.", uncertain=True)
        save_state(db, job, submitted=True)
        raise Pending()
    if status.get("publishing_phase", {}).get("status") != "complete":
        raise Pending()
    return video_id, f"https://www.facebook.com/reel/{video_id}", "published"


def youtube(db, job, account, token):
    headers = {"Authorization": f"Bearer {token}"}
    payload, state = job.payload, job.provider_state or {}
    asset = payload["assets"][0]
    if not state.get("upload_url"):
        result = request("POST", "https://www.googleapis.com/upload/youtube/v3/videos", params={"uploadType": "resumable", "part": "snippet,status"},
                         headers={**headers, "X-Upload-Content-Length": str(asset["size"]), "X-Upload-Content-Type": asset["mime"] or "video/mp4"},
                         json={"snippet": {"title": payload["title"], "description": payload["caption"], "tags": payload.get("tags", []), "categoryId": "22"},
                               "status": {"privacyStatus": payload["privacy"], "selfDeclaredMadeForKids": payload["made_for_kids"]}})
        location = result.headers.get("Location", "")
        parsed = urlparse(location)
        if parsed.scheme != "https" or parsed.hostname != "www.googleapis.com" or parsed.username or parsed.password:
            raise ProviderError("YouTube returned an invalid upload session.", uncertain=True)
        save_state(db, job, upload_url=location)
    if not job.provider_state.get("post_id"):
        with file_path(asset["path"]).open("rb") as source:
            result = api("PUT", job.provider_state["upload_url"], headers={**headers, "Content-Length": str(asset["size"]), "Content-Type": asset["mime"] or "video/mp4"}, data=source)
        save_state(db, job, post_id=require_id(result))
    post_id = job.provider_state["post_id"]
    result = api("GET", "https://www.googleapis.com/youtube/v3/videos", headers=headers, params={"part": "status,processingDetails", "id": post_id})
    items = result.get("items", [])
    if not items:
        raise Pending()
    status = items[0].get("status", {})
    if status.get("uploadStatus") in {"rejected", "failed", "deleted"}:
        raise ProviderError("YouTube rejected the upload. Review the video in YouTube Studio.")
    if status.get("uploadStatus") != "processed":
        raise Pending()
    actual = status.get("privacyStatus")
    save_state(db, job, actual_privacy=actual)
    if actual != payload["privacy"]:
        raise ProviderError("YouTube changed the requested visibility. Review this video in YouTube Studio before scheduling another upload.", uncertain=True)
    return post_id, f"https://www.youtube.com/watch?v={post_id}", "published" if actual == "public" else "uploaded"
