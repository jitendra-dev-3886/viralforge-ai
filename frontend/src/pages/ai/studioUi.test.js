import test from "node:test";
import assert from "node:assert/strict";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { createServer } from "vite";

test("AI Studio exposes language selection for every package and scheduling for every saved output", async () => {
    const vite = await createServer({ server: { middlewareMode: true, watch: null }, appType: "custom" });
    try {
        const { default: PackageSelector } = await vite.ssrLoadModule("/src/pages/ai/PackageSelector.jsx");
        for (const selected of ["complete", "quote", "reel", "carousel", "story"]) {
            const html = renderToStaticMarkup(React.createElement(PackageSelector, {
                selected, options: { language: "Hinglish", scene_count: 7, total_duration: 30, style: "Educational" },
            }));
            assert.match(html, /Content language/);
            assert.match(html, /value="Hinglish" selected=""/);
        }
        const { default: PreviewPanel } = await vite.ssrLoadModule("/src/pages/ai/PreviewPanel.jsx");
        const content = { title: "Saved post", content_id: 11, project_id: 7, platform: "Instagram", scenes: [] };
        const render = (data) => renderToStaticMarkup(React.createElement(MemoryRouter, {}, React.createElement(PreviewPanel, { data })));
        assert.equal((render({ content_id: 11, data: content }).match(/Schedule this post/g) || []).length, 1);
        const multiple = render({ data: { instagram: { post: content }, youtube: { shorts: { ...content, content_id: 12, platform: "YouTube" } } } });
        assert.equal((multiple.match(/Schedule this post/g) || []).length, 2);
        assert.equal((render(null).match(/Schedule this post/g) || []).length, 0);
    } finally { await vite.close(); }
});
