// Render the new module and existing AI Studio through their real providers.
// Uses installed Vite/React only; no network calls or database writes.
import assert from "node:assert/strict";
import { createServer } from "vite";
import React from "react";
import { renderToString } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";

globalThis.localStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };
const server = await createServer({ server: { middlewareMode: true, hmr: false }, optimizeDeps: { noDiscovery: true, include: [] }, appType: "custom" });
try {
    const [auth, project, brand, niche, workspace, studio, finisher] = await Promise.all([
        server.ssrLoadModule("/src/context/AuthContext.jsx"),
        server.ssrLoadModule("/src/context/ProjectContext.jsx"),
        server.ssrLoadModule("/src/context/BrandContext.jsx"),
        server.ssrLoadModule("/src/context/NicheContext.jsx"),
        server.ssrLoadModule("/src/pages/workspace/CreationWorkspace.jsx"),
        server.ssrLoadModule("/src/pages/ai/AIStudio.jsx"),
        server.ssrLoadModule("/src/pages/ai/ContentFinisher.jsx"),
    ]);
    const wrap = (component) => React.createElement(auth.AuthContext.Provider, { value: { user: { id: 123, name: "Test creator" }, isAuthenticated: true } },
        React.createElement(project.ProjectProvider, null,
            React.createElement(brand.BrandProvider, null,
                React.createElement(niche.NicheProvider, null,
                    React.createElement(MemoryRouter, null, component)))));
    const guided = renderToString(wrap(React.createElement(workspace.default)));
    assert.match(guided, /Creation Workspace/);
    assert.ok(guided.includes("What are we creating?"), "The brief form should render with the workspace.");
    assert.match(guided, /Resume saved content/);
    assert.match(guided, /Creation steps/);
    const existing = renderToString(wrap(React.createElement(studio.default)));
    assert.match(existing, /Generate content/);
    assert.match(existing, /Choose a package/);
    assert.doesNotMatch(existing, /Creation steps/);
    const legacyFinisher = renderToString(React.createElement(finisher.default, { content: {
        id: 1, project_id: 1, title: "Existing post", platform: "Instagram", content_type: "Post",
        scenes: [{ id: 1, text: "Hello", media_type: "image", media_url: "/storage/test.png" }],
    } }));
    assert.match(legacyFinisher, /Export styled images/);
    const audio = await server.ssrLoadModule("/src/pages/workspace/VoiceStep.jsx");
    const audioMarkup = renderToString(React.createElement(audio.default, {
        content: { id: 1, project_id: 1, title: "Workout", scenes: [], generation_config: { audio: { voice_enabled: false, music_id: 2, music_volume: .2 } } },
        voices: [], media: [{ id: 2, media_type: "music", status: "ready", title: "Licensed track", file_url: "/storage/music.mp3" }],
    }));
    assert.match(audioMarkup, /Include generated narration/);
    assert.doesNotMatch(audioMarkup, /Pixabay|Licensed track|Music volume|Suggested Pixabay/);
    const billing = await server.ssrLoadModule("/src/pages/settings/BillingPage.jsx");
    const pilot = await server.ssrLoadModule("/src/pages/admin/PilotPlans.jsx");
    assert.match(renderToString(React.createElement(billing.default)), /Plans &amp; usage/);
    assert.match(renderToString(React.createElement(pilot.default, { users: [] })), /Grant complimentary access/);
    console.log("PASS: Workspace, Audio, AI Studio, ContentFinisher, Plans and admin pilot controls render successfully.");
} finally {
    await server.close();
}
