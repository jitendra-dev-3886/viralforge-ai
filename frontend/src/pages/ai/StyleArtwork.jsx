import PlatformUsername from "./PlatformUsername";
import { useLayoutEffect, useRef, useState } from "react";
import { FONT_FAMILIES, mediaPlacement } from "./visualStyles";

export function StyleFrame({ preset }) {
    if (!preset) return null;
    return <div className="pointer-events-none absolute inset-0" aria-hidden="true">
        {preset.gradient && <div className="absolute inset-0" style={{ background: "linear-gradient(to bottom, transparent 25%, rgba(5,9,16,.88) 90%)" }} />}
        {preset.shapes.map(([x, y, w, h, color], index) => <span key={index} className="absolute" style={{ left: `${x * 100}%`, top: `${y * 100}%`, width: `${w * 100}%`, height: `${h * 100}%`, background: color }} />)}
        {preset.circles.map(([x, y, size, color], index) => <span key={`circle-${index}`} className="absolute rounded-full" style={{ left: `${x * 100}%`, top: `${y * 100}%`, width: `${size * 100}%`, aspectRatio: "1", background: color, transform: "translate(-50%, -50%)" }} />)}
    </div>;
}

export function StyledCaption({ preset, role = "text", text, opacity }) {
    const ref = useRef(null);
    const spec = preset[role];
    const [strips, setStrips] = useState([]);
    // Fit to the same height budget used by the export renderer, including long handles.
    useLayoutEffect(() => {
        const element = ref.current;
        const stage = element?.closest("[data-style-stage]");
        if (!stage) return;
        const fit = () => {
            const maxHeight = stage.clientHeight * (role === "text" ? .34 : .12);
            element.style.setProperty("--caption-pad", `${Math.max(3, Math.min(stage.clientWidth * .022, stage.clientHeight * (role === "username" ? .018 : .04)))}px`);
            let size = stage.clientWidth * spec.size;
            if (spec.mode === "strips") {
                const context = document.createElement("canvas").getContext("2d");
                if (!context) return;
                const pad = stage.clientWidth * .022;
                const available = element.clientWidth - pad * 2;
                let lines;
                do {
                    context.font = `${size}px ${FONT_FAMILIES[spec.font]}`;
                    lines = [];
                    for (const paragraph of (spec.uppercase ? String(text || "").toUpperCase() : String(text || "")).split("\n")) {
                        let line = "";
                        for (const word of paragraph.split(/\s+/).filter(Boolean)) {
                            const next = line ? `${line} ${word}` : word;
                            if (line && context.measureText(next).width > available) { lines.push(line); line = word; } else { line = next; }
                        }
                        lines.push(line);
                    }
                    if (lines.length * (size * 1.2 + pad) <= maxHeight && lines.every((line) => context.measureText(line).width <= available)) break;
                    size -= 1;
                } while (size > 8);
                element.style.fontSize = `${size}px`;
                setStrips(lines);
                return;
            }
            element.style.fontSize = `${size}px`;
            while (element.offsetHeight > maxHeight && size > 8) {
                size -= 1;
                element.style.fontSize = `${size}px`;
            }
        };
        const observer = new ResizeObserver(fit);
        observer.observe(stage);
        fit();
        return () => observer.disconnect();
    }, [text, role, spec]);
    const mode = spec.mode;
    const isPaper = mode === "paper";
    const isBubble = mode === "bubble";
    const isRule = mode === "cinema" || mode === "byline";
    const content = spec.uppercase ? String(text).toUpperCase() : text;
    const style = {
        position: "relative", whiteSpace: "pre-wrap", overflowWrap: "anywhere", wordBreak: "normal",
        fontFamily: FONT_FAMILIES[spec.font], fontWeight: ["sans", "rounded"].includes(spec.font) ? 700 : 400,
        fontSize: `${spec.size * 100}cqw`, lineHeight: spec.lineHeight ?? (mode === "paper" ? 1.4 : 1.28),
        textAlign: spec.align, background: mode === "strips" ? "transparent" : spec.background, color: spec.color,
        opacity: opacity ?? spec.opacity ?? 1,
        ...(mode === "caption" ? { display: "inline-block", maxWidth: "100%", textShadow: "0 1px 2px rgba(0,0,0,.75)" } : {}),
        padding: mode === "strips" ? "0" : `${isPaper || isRule ? "calc(var(--caption-pad, 2.2cqw) * 2)" : "var(--caption-pad, 2.2cqw)"} var(--caption-pad, 2.2cqw) var(--caption-pad, 2.2cqw)`,
        borderRadius: `${spec.radius * 100}cqw`, transform: `rotate(${spec.rotation}deg)`,
        ...(isBubble ? { border: `.5cqw solid ${spec.color}`, boxShadow: `1cqw 1cqw 0 ${preset.accent}` } : {}),
        ...(isPaper ? { backgroundImage: "repeating-linear-gradient(transparent 0, transparent calc(1.4em - 1px), #b7cad3 calc(1.4em - 1px), #b7cad3 1.4em)", borderBottom: ".8cqw dashed #e5d9bc" } : {}),
        ...(mode === "sidebar" ? { borderLeft: `.5cqw solid ${preset.accent}` } : {}),
        ...(mode === "tag" ? { border: `.3cqw solid ${preset.accent}` } : {}),
        ...(["underline", "label"].includes(mode) ? { borderBottom: `.2cqw solid ${preset.accent}` } : {}),
    };
    return <div ref={ref} style={style}>
        {spec.decoration && spec.decoration !== "highlight" && <svg aria-hidden="true" viewBox="0 0 100 100" preserveAspectRatio="none" style={{ position: "absolute", inset: 0, width: "100%", height: "100%", pointerEvents: "none", overflow: "visible" }}>
            <g fill="none" stroke={preset.accent} strokeWidth="1.5" vectorEffect="non-scaling-stroke">
                {spec.decoration === "titleCorners" && <path d="M1 20 V3 H12 M88 97 H99 V80" />}
                {spec.decoration === "bulletin" && <path d="M1 99 V1 H22" strokeWidth="2.5" />}
                {spec.decoration === "diamond" && <><path d="M28 95 H46 M54 95 H72" /><path d="M49 95 L50 92 L51 95 L50 98 Z" fill={preset.accent} /></>}
                {spec.decoration === "signature" && <path d="M4 96 H24" />}
                {spec.decoration === "cinema" && <path d="M32 3 H68 M32 97 H68" />}
                {spec.decoration === "rail" && <path d="M1 10 V90" strokeWidth="2" />}
                {spec.decoration === "doodle" && <path d="M18 94 L80 91 M18 98 L80 95 M94 9 H99 M96.5 4 V14" />}
                {spec.decoration === "notes" && <><path d="M4 97 H96" strokeDasharray="3 3" /><path d="M1 15 V3 H5" /></>}
            </g>
        </svg>}
        {isRule && <span aria-hidden="true" className="absolute" style={{ left: mode === "cinema" ? "35%" : "2.2cqw", top: "1.1cqw", width: "30%", height: ".2cqw", background: preset.accent }} />}
        {isPaper && <><span aria-hidden="true" className="absolute" style={{ width: "36%", height: "3.3cqw", top: "-1.1cqw", left: "32%", background: preset.accent }} /><span aria-hidden="true" className="absolute bottom-0 top-0" style={{ left: "1.5cqw", width: "1px", background: "#d69c94" }} /></>}
        {isBubble && <span aria-hidden="true" className="absolute" style={{ bottom: "-2.2cqw", left: "4.4cqw", borderTop: `2.4cqw solid ${spec.background}`, borderRight: "2.2cqw solid transparent" }} />}
        {mode === "strips" ? (strips.length ? strips : [content]).map((line, index) => <div key={index} style={{ marginBottom: ".7cqw" }}><span style={{ display: "inline-block", background: spec.background, borderBottom: `.3cqw solid ${preset.accent}`, color: spec.color, padding: "1.1cqw 2.2cqw", lineHeight: 1 }}>{line}</span></div>) : content}
    </div>;
}

export function StyledLogo({ preset, src, label = "Brand logo", initial = "V", opacity }) {
    const spec = preset.logo;
    if (spec.visible === false) return null;
    const circle = ["circle", "seal", "sticker"].includes(spec.shape);
    if (spec.shape === "transparent") return <span className="relative block w-full" style={{ aspectRatio: "1", opacity: opacity ?? spec.opacity ?? 1, padding: spec.decoration ? "15%" : 0 }}>
        {src ? <img src={src} alt={label} className="h-full w-full object-contain" /> : <span aria-label={label} className="flex h-full items-center justify-center text-white" style={{ fontSize: `${spec.size * 45}cqw` }}>{initial}</span>}
        {spec.decoration && <svg aria-hidden="true" viewBox="0 0 100 100" className="pointer-events-none absolute inset-0 h-full w-full" fill="none" stroke={preset.accent} strokeWidth="1.8">
            {spec.decoration === "signature" && <path d="M30 96 H70" />}
            {["corners", "bracket"].includes(spec.decoration) && <path d="M4 26 V4 H26 M74 96 H96 V74" />}
            {spec.decoration === "orbit" && <><path d="M92 69 A46 46 0 0 1 8 69" /><path d="M8 31 A46 46 0 0 1 92 31" /></>}
            {spec.decoration === "spark" && <path d="M73 17 H93 M83 7 V27" />}
        </svg>}
    </span>;
    return <span className="relative flex w-full items-center justify-center" style={{
        aspectRatio: spec.shape === "polaroid" ? "1 / 1.2" : "1", background: spec.background,
        border: `min(${spec.borderWidth * 100}cqw, ${spec.borderWidth * 100}cqh) solid ${spec.border}`,
        borderRadius: circle ? "50%" : spec.shape === "tile" ? "14%" : 0,
        transform: `rotate(${spec.rotation}deg)`, padding: circle ? "18%" : "11%",
        paddingBottom: spec.shape === "polaroid" ? "30%" : undefined,
        color: preset.ink, fontSize: `min(${spec.size * 35}cqw, ${spec.size * 35}cqh)`, fontWeight: 800,
    }}>
        {spec.shape === "seal" && <span aria-hidden="true" className="pointer-events-none absolute rounded-full" style={{ inset: "9%", border: `.15cqw solid ${spec.border}` }} />}
        {src ? <img src={src} alt={label} className="h-full w-full object-contain" /> : <span aria-label={label}>{initial}</span>}
    </span>;
}

export function SampleComposition({ preset, topic, brandName, logo, platform, compact = false }) {
    const positions = preset.layout;
    const overlay = (role, children) => <div className="absolute" style={{ left: `${positions[role].x}%`, top: `${positions[role].y}%`, width: role === "logo" ? `min(${preset.logo.size * 100}cqw, ${preset.logo.size * 100}cqh)` : `${preset[role].width * 100}%`, textAlign: "center", transform: "translate(-50%, -50%)" }}>{children}</div>;
    return <>
        <svg viewBox="0 0 400 500" preserveAspectRatio="xMidYMid slice" style={mediaPlacement(preset)} aria-hidden="true">
            <defs><linearGradient id={`sky-${preset.id}-${compact}`} x2="0" y2="1"><stop stopColor="#a1b5b4" /><stop offset="1" stopColor="#314e4d" /></linearGradient></defs>
            <rect width="400" height="500" fill={`url(#sky-${preset.id}-${compact})`} />
            <circle cx="280" cy="130" r="48" fill="#f0d6a7" />
            <path d="M-80 500 120 130 350 500Z" fill="#527473" /><path d="M80 500 350 220 480 500Z" fill="#2e5050" />
        </svg>
        <StyleFrame preset={preset} />
        {overlay("logo", <StyledLogo preset={preset} src={logo} initial={brandName?.[0]?.toUpperCase() || "V"} />)}
        {overlay("username", <PlatformUsername preset={preset} text={brandName || (preset.username.source === "brand_name" ? "Your Brand" : "@yourbrand")} platform={platform} />)}
        {overlay("text", <StyledCaption preset={preset} text={compact ? "Make every moment count." : (topic?.trim() || "Make every moment count.").slice(0, 100)} />)}
    </>;
}
