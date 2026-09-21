import { useState } from "react";
import { generateVoice } from "../../api/voice";
import { assetUrl } from "../../api/axios";
import { assertSuccess, latestVoices } from "./workflow";
import NarrationSettings from "./NarrationSettings";
import { audioSuggestion } from "./audioSuggestions";

const VOICES = {
  English: [
    ["en-US-AriaNeural", "Aria"],
    ["en-US-GuyNeural", "Guy"],
    ["en-GB-SoniaNeural", "Sonia"],
  ],
  Hindi: [
    ["hi-IN-SwaraNeural", "Swara"],
    ["hi-IN-MadhurNeural", "Madhur"],
  ],
};
export default function VoiceStep({
  content,
  voices,
  busy,
  run,
  refreshVoices,
  refresh,
}) {
  const suggestion = audioSuggestion(content);
  const [speed, setSpeed] = useState(suggestion.speed);
  const [language, setLanguage] = useState(
    content.language === "Hindi" ? "Hindi" : "English",
  );
  const [voice, setVoice] = useState(VOICES[language][0][0]);
  const records = latestVoices(voices, content.id);
  const generate = async (scene) => {
    const text = scene.voice_text ?? scene.text;
    if (!text?.trim())
      throw new Error("Add narration text in the Script step first.");
    const actualLanguage = /[\u0900-\u097f]/.test(text) ? "Hindi" : language;
    const actualVoice =
      actualLanguage === language ? voice : VOICES[actualLanguage][0][0];
    assertSuccess(
      await generateVoice({
        project_id: content.project_id,
        content_id: content.id,
        scene_id: scene.id,
        provider: "edge-tts",
        voice: actualVoice,
        language: actualLanguage,
        speed,
        pitch: "+0Hz",
        text,
      }),
    );
    await refreshVoices();
  };
  return (
    <div className="space-y-5">
      <NarrationSettings
        content={content}
        busy={busy}
        run={run}
        refresh={refresh}
      />
      <div>
        <h2 className="text-xl font-bold">Add narration</h2>
        <p className="mt-1 text-sm text-slate-500">
          Optional for silent videos and image exports. Hindi text automatically
          uses a Hindi voice.
        </p>
      </div>
      <fieldset disabled={busy} className="flex flex-wrap gap-3">
        <label className="text-sm">
          Narration pace
          <select
            value={speed}
            onChange={(e) => setSpeed(e.target.value)}
            className="ml-2 rounded-lg border bg-white p-2"
          >
            {["-10%", "-5%", "+0%", "+5%", "+10%"].map((item) => (
              <option key={item} value={item}>
                {item}
                {item === suggestion.speed ? " (suggested)" : ""}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          Language
          <select
            value={language}
            onChange={(e) => {
              setLanguage(e.target.value);
              setVoice(VOICES[e.target.value][0][0]);
            }}
            className="ml-2 rounded-lg border bg-white p-2"
          >
            {Object.keys(VOICES).map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          Voice
          <select
            value={voice}
            onChange={(e) => setVoice(e.target.value)}
            className="ml-2 rounded-lg border bg-white p-2"
          >
            {VOICES[language].map(([id, label]) => (
              <option key={id} value={id}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <button
          type="button"
          onClick={() =>
            run("Generating narration for all scenes...", async () => {
              for (const scene of content.scenes) await generate(scene);
            })
          }
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white"
        >
          Generate all voices
        </button>
      </fieldset>
      {content.scenes.map((scene, index) => {
        const record = records[scene.id];
        const stale =
          record &&
          record.text?.trim() !== (scene.voice_text ?? scene.text ?? "").trim();
        return (
          <article
            key={scene.id}
            className="rounded-xl border border-slate-200 p-4"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h3 className="text-sm font-semibold">Scene {index + 1}</h3>
              <button
                type="button"
                disabled={busy}
                onClick={() =>
                  run(`Generating voice for scene ${index + 1}...`, () =>
                    generate(scene),
                  )
                }
                className="rounded-lg bg-indigo-50 px-3 py-2 text-sm text-indigo-700"
              >
                {record ? "Regenerate voice" : "Generate voice"}
              </button>
            </div>
            <p className="mt-2 text-sm text-slate-600">
              {scene.voice_text ?? scene.text}
            </p>
            {stale && (
              <p className="mt-2 text-sm text-amber-700">
                Narration changed. Regenerate this voice before exporting video.
              </p>
            )}
            {record?.audio_url && (
              <audio
                controls
                preload="none"
                src={assetUrl(record.audio_url)}
                className="mt-3 w-full"
              />
            )}
          </article>
        );
      })}
    </div>
  );
}
