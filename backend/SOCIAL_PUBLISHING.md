# Connected accounts and automatic posting

## Use the feature

1. Open **Settings → Connected social accounts** and authorize Instagram, Facebook Pages, or YouTube. This connection is separate from social sign-in.
2. Generate content, review it, export the finished images/video, and approve the content.
3. Open **Scheduler**, select approved content and **Automatic**, then select the connected account and exact media. Select images in posting order. The same automatic form is also available in **Creation Workspace → Schedule**.
4. Review the caption, choose a future time, and click **Schedule automatic post**. For YouTube, explicitly choose visibility and the made-for-kids audience setting.
5. **Scheduler → Posting records → Posting history** shows the saved outcome, events, and platform post ID/link where available. YouTube private/unlisted uploads are recorded as `uploaded`, not publicly `published`.

The server must remain running. Closing the browser after scheduling is fine. The queue checks every 10 seconds; platform processing may delay completion. Manual reminders remain available and never publish automatically. Uploading an image to a scene does not itself authorize a social post; scheduling an automatic post does.

## Administrator setup

Configure the following in `backend/.env` (use the placeholders in `.env.example`; never commit credentials):

| Setting | Purpose |
| --- | --- |
| `FRONTEND_URL` | Browser app origin, e.g. `https://app.example.com` |
| `BACKEND_URL` | Public API origin, e.g. `https://api.example.com` |
| `PUBLIC_MEDIA_BASE_URL` | Public HTTPS origin serving `/storage/...` for Instagram |
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | Google web OAuth client with YouTube Data API v3 enabled |
| `FACEBOOK_CLIENT_ID`, `FACEBOOK_CLIENT_SECRET` | Meta app configured for Facebook Login and Page publishing |
| `INSTAGRAM_CLIENT_ID`, `INSTAGRAM_CLIENT_SECRET` | Instagram API with Instagram Login app credentials |
| `META_GRAPH_VERSION` | Supported Graph version enabled for your app; current application default is `v23.0` |
| `AUTO_PUBLISH_ENABLED` | `true` enables the API's background queue worker; `false` prevents new automatic schedules and stops the worker on restart |
| `PUBLISHING_ENCRYPTION_KEY` | Optional stable Fernet key, shared across deployments using the same DB |

When the encryption key is unset, the app creates `backend/.secrets/publishing.key`. Keep it private, persist it across restarts and back it up with the DB. Losing it requires reconnecting accounts. All API replicas need access to the same media storage and encryption key. Use the same site for frontend/API hosting so the browser can set the OAuth binding cookie.

Register these publishing redirect URLs in the provider consoles, replacing the API origin with your deployment:

```text
https://api.example.com/api/social-connections/instagram/callback
https://api.example.com/api/social-connections/facebook/callback
https://api.example.com/api/social-connections/youtube/callback
```

These are different from `/api/auth/oauth/.../callback`, which is only for sign-in. The Google console can use `http://localhost:8000/api/social-connections/youtube/callback` for local testing. Instagram needs externally reachable HTTPS media; localhost files cannot be fetched by Instagram.

The API startup creates the four new tables when missing: `publishing_accounts`, `publishing_oauth_states`, `publish_jobs`, and `publish_events`. An Alembic migration (`f5d902c6b132`) is also included for managed deployments. Restart the backend after configuring credentials; restart/rebuild the frontend as appropriate.

### Platform setup and supported posts

- **Instagram:** authorize a professional Business/Creator account using `instagram_business_basic` and `instagram_business_content_publish`. Supports single feed images, image carousels (2–10 images), and Reels. Feed images are converted to JPEG; the app accepts 4:5–1.91:1 aspect ratios. Media URLs must be publicly fetchable throughout processing. The implementation follows [Meta's Instagram collection](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api?entity=request-23987686-3fe78620-2258-44b6-893f-42d76c7200d7).
- **Facebook:** connect managed Pages, with `pages_show_list`, `pages_read_engagement`, and `pages_manage_posts`. Supports Page photo posts and Page Reels; it does not publish to personal profiles. The Reel flow follows [Meta's Facebook collection](https://www.postman.com/meta/facebook/documentation/r56bjfd/facebook-api?entity=request-23987686-4437f4e3-569e-4982-95ba-69a9c2452500).
- **YouTube:** enable YouTube Data API v3 and configure OAuth consent/test users. Requests `youtube.upload` and `youtube.readonly` with offline access. Videos/Shorts use [YouTube's resumable upload protocol](https://developers.google.com/youtube/v3/guides/using_resumable_upload_protocol). Community posts are not supported. Uploads from unverified API projects may be restricted to private until the project passes Google's audit; see [videos.insert](https://developers.google.com/youtube/v3/docs/videos/insert).

Meta production access may require app review and the corresponding permissions; Google may require OAuth verification/API audit. During development, use the provider's app-role/test accounts. Configure and test these apps with your own accounts before relying on unattended production publishing. Live OAuth and posting cannot be verified by unit tests.

## Records and failure behavior

Each automatic schedule stores the approved title/caption, account, ordered media selection and file hashes, requested visibility, UTC due time and display timezone, event history, and platform result. Editing content later does not change its queued caption. If a selected file is replaced or deleted, the worker stops that post. Cancel a queued post and schedule again to change its contents. Disconnecting an account erases the locally stored tokens and cancels queued jobs; in-progress jobs must finish before disconnecting.

OAuth state is browser-bound, expires after ten minutes and can be consumed once. Access/refresh tokens are encrypted, never returned to the browser, and separated from login identities. YouTube tokens refresh before use; Instagram long-lived tokens refresh when near expiry during publishing. Expired/revoked grants require reconnection. No maintenance refresh happens while an account is idle.

Queue claims and client request keys prevent duplicate processing/scheduling. Provider container IDs are persisted between processing polls. Ambiguous network failures or interrupted workers become `needs_review`; there is deliberately no automatic resubmission that might duplicate a public post. Check the platform using the saved post ID before deciding to schedule again. Repeated provider processing is bounded and eventually also requires review.

Automatic posting records cannot be deleted through the Scheduler. Existing project/content/user deletion policies still apply to linked records, and administrator account deletion removes publishing credentials and history. Pending jobs are checked against active user status and content approval before each platform step. Already-submitted platform work may complete independently of later account/content changes.
