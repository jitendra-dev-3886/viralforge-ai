import { StyledCaption } from "./StyleArtwork";

export const platformKey = (value) => String(value || "").toLowerCase();
export function platformUsername(text, platform) {
    const value = String(text || "").trim();
    return value && ["instagram", "youtube"].includes(platformKey(platform)) ? `@${value.replace(/^@+/, "")}` : value;
}
export default function PlatformUsername({ preset, text, platform, opacity }) {
    const key = platformKey(platform);
    const brandCredit = preset?.username.source === "brand_name";
    const supported = !brandCredit && ["instagram", "facebook", "youtube"].includes(key);
    const color = { instagram: "#e1306c", facebook: "#1877f2", youtube: "#ff0033" }[key];
    if (!text?.trim() || preset?.username.visible === false) return null;
    return <span className="inline-flex max-w-full items-center justify-center gap-[.8cqw]" style={{ opacity: opacity ?? preset?.username.opacity ?? 1 }}>
        {supported && <span className="flex shrink-0 items-center justify-center rounded-[.7cqw]" style={{ width: "3.6cqw", height: "3.6cqw", background: color, color: "white" }}><svg aria-label={platform} role="img" viewBox="0 0 120 120" className="h-full w-full" fill="none" stroke="white" strokeWidth="7">
            {key === "instagram" && <><rect x="23" y="23" width="74" height="74" rx="21" /><circle cx="60" cy="60" r="18" /><circle cx="82" cy="35" r="4" fill="white" stroke="none" /></>}
            {key === "youtube" && <><rect x="18" y="30" width="84" height="60" rx="16" /><path d="M51 44 L51 76 L78 60 Z" fill="white" stroke="none" /></>}
            {key === "facebook" && <path d="M75 25 H62 L51 36 V102 M32 53 H78" strokeWidth="13" />}
        </svg></span>}
        <span className="min-w-0">{preset ? <StyledCaption preset={preset} role="username" text={brandCredit ? text : platformUsername(text, platform)} opacity={1} /> : <span className="rounded bg-black/40 px-2 py-1 text-xs text-white">{platformUsername(text, platform)}</span>}</span>
    </span>;
}
