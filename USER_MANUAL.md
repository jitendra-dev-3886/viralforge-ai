# ViralForge AI User Manual

## Setup

Apply database updates with `cd backend` followed by `venv\Scripts\alembic.exe upgrade head`. Start the backend and frontend, open the Vite URL, and sign in.

## Configure the workspace

1. In **Settings**, add, edit, hide, or delete niches. Only visible niches appear elsewhere.
2. In **Brands**, create a brand with a niche, colors, font, and an uploaded or URL-based logo.
3. Create a **Project** and associate it with the brand.

## Generate content

1. Open **AI Studio**.
2. Select the project, platforms, formats, niche, and topic.
3. Choose a package and provider, then select **Generate**.
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

Set `SUPER_ADMIN_EMAIL` in `backend/.env` to an existing account email. Restart the backend, log out, and log in again. **Super Admin** then provides user activation, verification, role controls, totals, and cross-workspace visibility.

## Troubleshooting

- Restart both servers after configuration changes.
- Missing logo: save the overlay layout again and rerender.
- Missing narration: generate voice for the exact scene and rerender.
- Incorrect Hindi voice: select a Hindi voice and regenerate.
- Missing scene media: use **Replace media** and verify stock-media API keys.
- Scheduling error: approve the content first.
- Provider error: verify its API key or select Auto.
