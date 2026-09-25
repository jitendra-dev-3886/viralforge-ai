import { updateContent } from "../../api/content";
import { loadWorkspaceContent } from "./workspaceApi";
import { assertSuccess } from "./workflow";

export default function NarrationSettings({ content, busy, run, refresh }) {
    const enabled = content.generation_config?.audio?.voice_enabled !== false;
    const save = async (voiceEnabled) => {
        const current = await loadWorkspaceContent(content.id);
        assertSuccess(await updateContent(content.id, { generation_config: {
            ...current.generation_config,
            audio: { ...current.generation_config?.audio, voice_enabled: voiceEnabled },
        } }));
        await refresh();
    };
    return <div className="space-y-2 rounded-xl border border-slate-200 p-4">
        <label className="flex items-center gap-2 text-sm"><input type="checkbox" disabled={busy} checked={enabled} onChange={(event) => { const value = event.target.checked; run("Saving narration preference...", () => save(value)); }} />Include generated narration in exports</label>
        <p className="text-xs text-slate-500">Workspace exports use generated narration only. Turn it off for a silent video. Images remain silent.</p>
    </div>;
}
