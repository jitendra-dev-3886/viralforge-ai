# ViralForge AI User Manual

## Setup

Apply database updates with `cd backend` followed by `venv\Scripts\alembic.exe upgrade head`. Start the backend and frontend, open the Vite URL, and sign in.

## Configure the workspace

1. In **Settings**, add, edit, hide, or delete niches. Only visible niches appear elsewhere.
2. In **Brands**, create a brand with a niche, colors, font, and an uploaded or URL-based logo.
3. Create a **Project** and associate it with the brand.

## Generate content

### Creation Workspace (separate module)

### Personal AI provider setup

Every signed-in user must first open **Settings → My AI providers**, select
Gemini, Groq, Cerebras, OpenRouter, Mistral, Cloudflare Workers AI, or Hugging Face,
and save their own API key and exact model
ID. Saving stores the configuration; the first generation request checks access
with the provider. A blank key when editing keeps the previously saved key.
Disable or remove a provider to stop using it in subsequent requests.

Cloudflare additionally requires a 32-character Account ID and a token with
Workers AI access. Use a supported Workers AI chat model ID (typically `@cf/...`).
Hugging Face requires a token with Inference Providers permission and a supported
chat model, rather than an arbitrary Hub repository. Mistral uses its console API
key and model ID. Select models that support JSON output. Free allowances and
model availability are controlled by each provider; saving a provider does not
guarantee free use or enforce a free-only spending limit.

AI Studio and Creation Workspace list only the account's enabled providers.
**Auto** tries only those providers. Content generation does not use shared
server keys or server-local Ollama/LocalAI models. Provider charges apply to the
user's provider account. Topic discovery retains its source-based suggestions
without calling the shared AI ranking key.

Keys are encrypted in the existing `api_settings` table and never returned by
the settings API. Back up `backend/.secrets/` privately alongside the database;
it is outside public storage and ignored by Git. Production deployments can set
`API_CREDENTIAL_ENCRYPTION_KEY` (a Fernet key) and `JWT_SECRET_KEY` instead; keep
them stable across workers and deployments. Do not replace the encryption key
without migrating stored credentials. The change from the old fixed login
signing key requires existing users to sign in again.

### Guided creation

Open **Creation Workspace** in the sidebar, or visit `/creation-workspace`.
It provides six steps: **Brief → Script → Media → Audio → Design & export → Schedule**.

In **Voice**, generate narration, choose a voice and speed, and enable or disable
narration for export. Background music discovery, upload, and mixing are removed
from the workspace. Workspace exports ignore any previously selected music.
Image exports remain silent.

Brief settings and unsaved script edits are saved locally for the signed-in user
in this browser. **Save draft** or changing steps saves script edits to the project.
Use **Save layout** in the design step to save overlay changes. Regenerate narration
when the spoken text changes. Scheduling uses the existing manual publishing queue
and requires explicit approval. Keep the workspace open during generation/export.

The existing AI Studio, editor, Voice, Media, Export, and Scheduler pages remain
available. The workspace uses the same saved project content and APIs; editing an
existing item here edits that item, while generating creates a new item.

### AI Studio

1. Open **AI Studio**.
2. Select the project, platforms, formats, niche, and topic.
3. Choose a package and provider, select a **Visual style**, preview the formats, then select **Generate**.
4. For quotes, choose **हिंदी सुविचार** or **English Quote**.

Reels use video scenes. Carousels and quotes use images. Carousels contain at least three image scenes.

## Edit and approve

1. Open **History** and select **Edit** beside an item.
2. Edit its title, hook, script, caption, hashtags, keywords, and CTA.
3. Edit each scene's text, duration, and transition.
4. Reorder scenes with the arrow buttons, replace media, or delete a scene.
5. Choose **Save draft**, **Send to review**, or **Approve**.

Only approved content can be scheduled.

## Add narration

1. Open **Voice** and select a project, content item, and scene.
2. Choose Hindi or English and a natural voice.
3. Generate and preview the narration.

Scene text loads automatically. Devanagari text automatically selects a Hindi-compatible voice. Regenerate narration after changing scene text.

## Render the final content

1. Find **Finish & merge** in AI Studio or the Content Editor.
2. Drag the text, logo, and username into position.
3. Optionally upload background music.
4. Save the layout and select **Merge all scenes**.
5. Preview and download the final MP4.

The renderer applies platform dimensions and embeds overlays, narration, and optional music.

## Export

Open **Export** to download final videos, scene images/videos, and narration. Select several items to download a ZIP. For a carousel, select all slide images to export the complete slide set.

## Schedule and publish

1. Approve content in the editor.
2. Open **Scheduler**, select the approved item and date/time, then schedule it.
3. After uploading it to the social platform, select **Mark published**.

Automatic social posting remains disabled until approved Meta/YouTube developer credentials and publishing permissions are configured. The current scheduler manages a safe manual publishing queue.

## Super admin

`super_admin@gmail.com` and `ystechlab@gmail.com` have unlimited brands and exports with no plan expiry while their accounts are active. **Plans & usage** shows **Owner access** for these two accounts. Other users, including other super admins, retain their normal plan limits. Export history, ownership checks, and the one-export-at-a-time rule still apply; AI provider charges are separate.

Set `SUPER_ADMIN_EMAIL` in `backend/.env` to an existing account email. Restart the backend, log out, and log in again. **Super Admin** then provides user activation, verification, role controls, totals, and cross-workspace visibility.

Under **Super Admin > Users > Actions**, use **Delete** and confirm to permanently remove a user and their linked database records. The list and totals refresh afterward. Your own account and configured owner accounts cannot be deleted; other admins must first be demoted to users. Accounts that have issued plan grants must be disabled instead to preserve grant history. An export in progress blocks deletion until it finishes. Deleted or disabled accounts cannot continue using existing authentication tokens. Stored media files and posts already published externally are not removed by this action.

## Troubleshooting

- Restart both servers after configuration changes.
- Missing logo: save the overlay layout again and rerender.
- Missing narration: generate voice for the exact scene and rerender.
- Incorrect Hindi voice: select a Hindi voice and regenerate.
- Missing scene media: use **Replace media** and verify stock-media API keys.
- Scheduling error: approve the content first.
- Provider error: verify its API key or select Auto.
## Visual styles

In Generate content, choose a Visual style: Minimal, Bold, Cinematic, Professional,
Playful, or Scrapbook / Notes. Switch the preview between Reel / Story, Carousel,
Post / Quote, and Long video before selecting Generate. The sample uses placeholder
artwork; the chosen preset applies to every selected output. Writing tone remains
a separate package option.

After generation, use Finish & export to preview each scene and adjust the shared
text, logo, and username positions. Export styled images produces PNGs (a ZIP for
multiple slides); Merge all scenes produces the styled MP4. Source downloads are
the original stock assets. Previously saved content without a visual preset keeps
its original appearance. Preview text is approximate; exports fit text to the canvas.

The six designs keep the full photo or video visible. They use compact translucent
backgrounds behind captions, small usernames, and logos without added badges.
Typography and overlay positions differ between styles. Uploaded logo transparency
is preserved; an existing background inside a logo image is not automatically removed.
Use the separate **Overlay opacity** sliders for logo, username, and text.
In **Finish & export**, use **Design layout** to restyle existing content without
regenerating its scenes. **Use preset positions** resets all three overlays to that
design's layout; you can then drag to adjust and export again. Old shared default
positions are upgraded automatically, while manually moved positions are retained.

## Plans and usage (payments deferred)

Open **Plans & usage** from the sidebar to see your allowance, expiry date,
export usage, and complimentary access history. Prices are proposed monthly
prices; there is no checkout, payment collection, or automatic renewal yet.
Your configured AI provider's charges are separate.

| Plan | Proposed price | Brands | Video allowance | Image allowance |
| --- | --- | --- | --- | --- |
| Trial (7 days) | Free | 1 | 3 exports | 10 images |
| Creator | INR 499/month | 1 | 30 minutes | 100 images |
| Pro | INR 999/month | 5 | 90 minutes | 300 images |
| Agency | INR 2,499/month | 15 | 250 minutes | 1,000 images |

The one-time trial starts when an account first opens its usage page or uses a
plan-gated action. Limits are enforced by the backend. Each carousel slide counts
as one image; video allowance uses scene durations including longer narration,
rounded up to whole seconds per scene. Running exports reserve allowance, and
failed renders release it. Downloading a completed file again does not use more
allowance; deliberately rendering another export does. A download/network failure
after a successful render does not refund that render. Use the saved Media file
to download it again. Only one export can run per account at a time.

Administrators can use **Admin > Pilot plan access** to grant a complimentary
30-day Creator, Pro, or Agency period, with an audit reason. Active paid-tier pilot
periods cannot be reset. A new grant after expiry starts a fresh allowance period.
Expired accounts retain saved content, but cannot generate AI content, create new
brands, or render new exports. Existing brands are not deleted if over the cap.

After a server interruption, an administrator can release a pending reservation
after confirming its render worker has stopped. This restores the reserved
allowance. Ordinary render failures release reservations automatically.

Restart the backend after updating: startup creates `billing_plans`,
`export_usage`, and `plan_grants`, then seeds missing catalog entries. Access
periods use the existing `subscriptions` table. No payment credentials are needed.
