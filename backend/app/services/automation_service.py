"""Recurring generation, using the existing AI, export and publishing paths."""
import logging
import asyncio
import os
import re
from datetime import datetime, time, timedelta, timezone
from difflib import SequenceMatcher
from uuid import NAMESPACE_URL, uuid5
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models.automation import AutomationRule, AutomationRun
from app.models.content import Content
from app.models.project import Project
from app.models.user import User
from app.schemas.ai import GenerateRequest
from app.schemas.automation import AutomationConfig
from app.services.publishing_accounts import now

logger = logging.getLogger(__name__)


class NoUnusedTrend(ValueError):
    pass


def select_trend(db, user_id, config):
    from app.api.trends import trending
    from app.services.trend_service import TrendService

    result = trending(niche=config.niche, project_id=config.project_id, platform=config.platform,
                      content_type=config.content_type, db=db, user_id=user_id)
    used = set()
    history = db.query(Content.title, Content.generation_config).filter_by(
        user_id=user_id, project_id=config.project_id).yield_per(100)
    for title, saved in history:
        saved = saved or {}
        prior_trend = saved.get("trend") or {}
        used.update(TrendService._title_key(value) for value in
                    (title, saved.get("topic"), prior_trend.get("title"), prior_trend.get("source_title")) if value)
    language = "hi" if config.language.casefold() in {"hi", "hindi", "हिंदी", "हिन्दी"} else "en"
    # The existing ranker orders best first within each language. English
    # sources also support generation in languages other than Hindi/English.
    for topic in result.get("trends", []):
        if topic.get("source") != "live" or topic.get("language") != language or not topic.get("title"):
            continue
        keys = {TrendService._title_key(value) for value in (topic["title"], topic.get("source_title")) if value}
        if keys and not keys.intersection(used):
            return topic
    raise NoUnusedTrend("No unused live trend is available for this niche and project. This run was skipped; the next scheduled run will check again.")


def utc(value):
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def next_occurrence(config, after):
    """One occurrence per local date; skip nonexistent spring-forward times."""
    zone = ZoneInfo(config.timezone)
    date = utc(after).astimezone(zone).date()
    for offset in range(15):
        day = date + timedelta(days=offset)
        if day.weekday() not in config.days:
            continue
        local = datetime.combine(day, time.fromisoformat(config.time), zone)
        candidate = local.astimezone(timezone.utc)
        if candidate.astimezone(zone).replace(tzinfo=None) != local.replace(tzinfo=None):
            continue
        if candidate > utc(after):
            return candidate
    raise ValueError("No upcoming occurrence found.")


def validate_resources(db, user_id, config):
    from app.models.publishing import PublishingAccount

    if not db.query(Project.id).filter_by(id=config.project_id, user_id=user_id).first():
        raise HTTPException(404, "Project not found.")
    if config.content_type in {"Reel", "Shorts", "Video"} and config.music_id:
        selected_music(db, user_id, config)
    if config.mode == "automatic":
        if os.getenv("AUTO_PUBLISH_ENABLED", "true").lower() != "true":
            raise HTTPException(503, "Automatic publishing is disabled on this server. Choose drafts for approval.")
        account = db.query(PublishingAccount).filter_by(
            id=config.publishing_account_id, user_id=user_id, provider=config.platform, status="connected"
        ).first()
        if not account:
            raise HTTPException(400, "Choose a connected account matching this platform.")


def selected_music(db, user_id, config):
    from app.models.media import Media
    from app.services.project_render_service import ProjectRenderService

    music = db.query(Media).filter_by(id=config.music_id, user_id=user_id, project_id=config.project_id,
                                     media_type="music", status="ready").first()
    if not music or not ProjectRenderService._media_path(music.file_path).is_file():
        raise HTTPException(422, "Selected music is unavailable. Upload or select a track in Auto Mode.")
    return music


def prepare_audio(db, content, config):
    from app.schemas.voice import VoiceCreate
    from app.services.voice_service import VoiceService

    if config.music_id:
        selected_music(db, content.user_id, config)
    content.generation_config = {**(content.generation_config or {}), "audio": {
        "voice_enabled": config.voice != "off", "music_id": config.music_id, "music_volume": config.music_volume,
    }}
    db.commit()
    if config.voice == "off":
        return

    async def narrate():
        for scene in sorted(content.scenes, key=lambda item: item.scene_number):
            text = (scene.voice_text or scene.text or "").strip()
            if not text:
                raise ValueError(f"Scene {scene.scene_number} has no narration text. Review the draft before posting.")
            result = await VoiceService.generate(db=db, user_id=content.user_id, request=VoiceCreate(
                project_id=content.project_id, content_id=content.id, scene_id=scene.id,
                voice="" if config.voice == "auto" else config.voice, gender=None,
                language=content.language or config.language, speed=config.voice_speed, text=text,
            ))
            if not result or not result.get("success"):
                raise ValueError(f"Narration failed for scene {scene.scene_number}. Review the draft and regenerate its voice before posting.")

    asyncio.run(narrate())


def claim_run(db, rule_id, at):
    rule = db.get(AutomationRule, rule_id)
    if not rule or not rule.enabled:
        return None
    config = AutomationConfig(**rule.config)
    scheduled = utc(rule.next_run_at)
    if scheduled - timedelta(minutes=config.lead_minutes) > at:
        return None
    following = next_occurrence(config, max(at, scheduled))
    # Advance the cursor and reserve the occurrence in one transaction. The
    # unique active_user also serializes a user's different rules across workers.
    changed = db.query(AutomationRule).filter_by(id=rule.id, enabled=True, next_run_at=rule.next_run_at).update(
        {"next_run_at": following}, synchronize_session=False
    )
    if changed != 1:
        db.rollback()
        return None
    missed = scheduled <= at
    run = AutomationRun(rule_id=rule.id, user_id=rule.user_id, scheduled_at=scheduled, started_at=at,
                        status="skipped" if missed else "generating", active_user=None if missed else rule.user_id,
                        error_message="Missed posting time; skipped to avoid a backlog of late posts." if missed else None)
    db.add(run)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # An edited lead time can select an occurrence already prepared. Move
        # past that occurrence, but leave a busy user's unclaimed slot intact.
        if db.query(AutomationRun.id).filter_by(rule_id=rule_id, scheduled_at=scheduled).first():
            db.query(AutomationRule).filter_by(id=rule_id, next_run_at=scheduled).update({"next_run_at": following})
            db.commit()
        return None
    return None if missed else run.id


def check_repetition(content, previous):
    normalize = lambda value: " ".join(re.findall(r"\w+", str(value or "").casefold()))
    for old in previous:
        for field in ("title", "caption", "script"):
            current, earlier = normalize(getattr(content, field)), normalize(old.get(field))
            if current and earlier and (current == earlier or (min(len(current), len(earlier)) >= 40 and SequenceMatcher(None, current, earlier).ratio() >= 0.9)):
                raise ValueError("Content repeats a recent title, caption or script. Kept for review without posting.")
    previous_urls = {scene.get("media_url") for old in previous for scene in old.get("scenes", []) if scene.get("media_url")}
    urls = [scene.media.file_url for scene in content.scenes if scene.media and scene.media.file_url]
    if previous_urls.intersection(urls) or len(urls) != len(set(urls)):
        raise ValueError("A visual was reused. Kept for review without posting.")


def generate_and_render(db, rule, run, config):
    from app.services.ai_service import AIService
    from app.services.content_service import ContentService
    from app.services.project_render_service import ProjectRenderService
    from app.api.render import render_image_batch
    from app.core.render_errors import run_render

    topic = select_trend(db, rule.user_id, config)
    recent = db.query(Content).filter_by(user_id=rule.user_id).order_by(Content.id.desc()).limit(30).all()
    previous = [ContentService._serialize(content) for content in recent]
    video = config.content_type in {"Reel", "Shorts", "Video"}
    request = GenerateRequest(
        project_id=config.project_id, platforms=[config.platform.title()], content_types=[config.content_type],
        outputs=[f"{config.platform.title()}: {config.content_type}"], niche=config.niche, topic=topic["title"],
        package="reel" if video else config.content_type.lower(), language=config.language, provider="auto",
        scene_count=config.scene_count, total_duration=config.total_duration, style=config.style, visual_style=config.visual_style,
    )
    result = AIService.generate(request, db, rule.user_id, previous_outputs=previous)
    content = db.get(Content, result["content_id"])
    run.content_id = content.id
    content.generation_config = {**(content.generation_config or {}), "topic": topic["title"], "trend": topic,
                                 "automation_rule_id": rule.id, "automation_run_id": run.id}
    db.commit()
    check_repetition(content, previous)
    if not content.scenes or any(not scene.media_id for scene in content.scenes):
        raise ValueError("Some scenes have no matching visual. Review the draft before exporting or posting.")
    kwargs = dict(db=db, user_id=rule.user_id, request_key=f"automation-export-{run.id}")
    if video:
        prepare_audio(db, content, config)
        rendered = run_render(ProjectRenderService.generate, project_id=config.project_id, content_id=content.id, **kwargs)
        media_ids = [rendered["media_id"]]
    else:
        rendered = run_render(render_image_batch, scene_ids=[scene.id for scene in sorted(content.scenes, key=lambda scene: scene.scene_number)], as_image=True, **kwargs)
        media_ids = rendered["media_ids"]
    return content, media_ids


def process_run(db, run_id):
    from app.api.schedule import create_schedule
    from app.schemas.schedule import ScheduleCreate

    run = db.get(AutomationRun, run_id)
    if not run or run.status != "generating":
        return
    rule = db.get(AutomationRule, run.rule_id)
    config = AutomationConfig(**rule.config)
    try:
        if not rule.enabled or not db.query(User.id).filter_by(id=rule.user_id, is_active=True).first():
            raise ValueError("Automation paused or account unavailable.")
        validate_resources(db, rule.user_id, config)
        content, media_ids = generate_and_render(db, rule, run, config)
        # Generation/export commit internally. Re-read and lock before queuing,
        # so a pause during generation prevents unattended publication.
        db.expire_all()
        rule = db.query(AutomationRule).filter_by(id=rule.id).populate_existing().with_for_update().one()
        run = db.get(AutomationRun, run_id)
        if run.status != "generating":
            db.rollback()
            return
        if config.mode == "automatic" and rule.enabled:
            if utc(run.scheduled_at) <= now():
                raise ValueError("Generation finished after the posting time. Review and reschedule the draft.")
            content.status = "approved"
            db.flush()
            result = create_schedule(ScheduleCreate(
                project_id=config.project_id, content_id=content.id, platform=config.platform,
                scheduled_at=utc(run.scheduled_at), timezone=config.timezone, publishing_account_id=config.publishing_account_id,
                media_ids=media_ids, privacy=config.privacy, made_for_kids=bool(config.made_for_kids),
                request_key=uuid5(NAMESPACE_URL, f"viralforge:automation:{run.id}"),
            ), db, rule.user_id)
            run.schedule_id = result["schedule"]["id"]
            run.status = "scheduled"
        else:
            run.status = "draft"
    except Exception as exc:
        db.rollback()
        run = db.get(AutomationRun, run_id)
        if not run:
            return
        run.status = "skipped" if isinstance(exc, NoUnusedTrend) else "needs_review" if run.content_id else "failed"
        run.error_message = (str(exc.detail) if isinstance(exc, HTTPException) else str(exc) if isinstance(exc, ValueError)
                             else "Automation could not finish. Review any saved draft and check server logs.")[:1000]
        if not isinstance(exc, NoUnusedTrend):
            logger.exception("Automation run %s did not finish", run_id)
    run.active_user = None
    db.commit()


def tick():
    with SessionLocal() as db:
        at = now()
        db.query(AutomationRun).filter(AutomationRun.status == "generating", AutomationRun.started_at < at - timedelta(hours=2)).update(
            {"status": "needs_review", "active_user": None, "error_message": "Generation was interrupted. Check saved content and posting records; this occurrence will not be retried."}, synchronize_session=False)
        db.commit()
        rules = db.query(AutomationRule).filter(AutomationRule.enabled.is_(True), AutomationRule.next_run_at <= at + timedelta(days=1)).order_by(AutomationRule.next_run_at).all()
        for rule in rules:
            run_id = claim_run(db, rule.id, now())
            if run_id:
                process_run(db, run_id)


def run_worker(stop):
    while not stop.is_set():
        try:
            tick()
        except Exception:
            logger.exception("Auto Mode worker could not process its queue")
        stop.wait(15)
