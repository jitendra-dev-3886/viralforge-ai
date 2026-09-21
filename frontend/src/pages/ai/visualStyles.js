import presets from "../../../../backend/app/config/visual_styles.json";

export const VISUAL_STYLES = presets;
export const getVisualStyle = (id) => presets.find((preset) => preset.id === id);
export const DEFAULT_LAYOUT = { text: { x: 50, y: 68 }, logo: { x: 10, y: 8 }, username: { x: 82, y: 92 } };
export const getDefaultLayout = (preset) => preset?.layout || DEFAULT_LAYOUT;
export function mediaPlacement(preset) {
    const [x, y, w, h] = preset?.mediaRect || [0, 0, 1, 1];
    return { position: "absolute", left: `${x * 100}%`, top: `${y * 100}%`, width: `${w * 100}%`, height: `${h * 100}%`, objectFit: "cover", objectPosition: `50% ${(preset?.mediaFocusY ?? .5) * 100}%` };
}
export function getSavedLayout(preset, config = {}) {
    let saved = config.overlay_layout || {};
    const oldY = { minimal: 72, bold: 65, cinematic: 72, professional: 72, playful: 65, scrapbook: 70 };
    const legacy = { ...DEFAULT_LAYOUT, text: { x: 50, y: oldY[preset?.id] ?? 68 } };
    if (config.visual_layout_version !== 2 && Object.keys(legacy).every((name) => saved[name]?.x === legacy[name].x && saved[name]?.y === legacy[name].y)) saved = {};
    return Object.fromEntries(Object.entries(getDefaultLayout(preset)).map(([name, position]) => [name, { ...position, ...saved[name] }]));
}
export const FONT_FAMILIES = {
    serif: 'Georgia, "Nirmala UI", "Noto Sans Devanagari", serif',
    mono: 'Consolas, "Nirmala UI", "Noto Sans Devanagari", monospace',
    condensed: 'Impact, "Arial Narrow", "Nirmala UI", sans-serif',
    rounded: 'Arial, "Nirmala UI", "Noto Sans Devanagari", sans-serif',
    sans: 'Arial, "Nirmala UI", "Noto Sans Devanagari", sans-serif',
};
