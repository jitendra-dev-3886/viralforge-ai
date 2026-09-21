import { StyledCaption } from "./StyleArtwork";

export default function PlatformUsername({ preset, text, opacity }) {
    if (!text?.trim() || preset?.username.visible === false) return null;
    return <span className="inline-flex max-w-full items-center justify-center" style={{ opacity: opacity ?? preset?.username.opacity ?? 1 }}>
        <span className="min-w-0">{preset ? <StyledCaption preset={preset} role="username" text={text} opacity={1} /> : <span className="rounded bg-black/40 px-2 py-1 text-xs text-white">{text}</span>}</span>
    </span>;
}
