import { useCallback, useEffect, useRef, useState } from "react";
import JSZip from "jszip";
import {
    Sparkles,
    Copy,
    Check,
    ZoomIn,
    ZoomOut,
    RotateCcw,
    Maximize,
    Minimize,
    X,
    ChevronLeft,
    ChevronRight,
    Download,
    Package,
} from "lucide-react";

/* --------------------------------------------------------------------------
 | Constants & Utilities
 -------------------------------------------------------------------------- */

const MIN_ZOOM = 0.5;
const MAX_ZOOM = 4;
const ZOOM_STEP = 0.25;

/**
 * Utility to strip excessive whitespace from multi-line Tailwind classes.
 */
function cx(...classes) {
    return classes
        .filter(Boolean)
        .map((c) => String(c).replace(/\s+/g, " ").trim())
        .join(" ");
}

function normalizeArray(value) {
    if (!value) return [];
    if (Array.isArray(value)) {
        return value.map((item) => String(item).trim()).filter(Boolean);
    }
    return String(value)
        .split(/[,\n]+/)
        .map((item) => item.trim())
        .filter(Boolean);
}

function sanitizeFilename(value) {
    return String(value || "media")
        .replace(/[<>:"/\\|?*\x00-\x1F]/g, "")
        .replace(/\s+/g, "-")
        .replace(/-+/g, "-")
        .replace(/^-|-$/g, "")
        .slice(0, 100) || "media";
}

function getMediaExtension(url) {
    try {
        const pathname = new URL(url, window.location.href).pathname;
        const match = pathname.match(/\.([a-zA-Z0-9]+)$/);
        if (match) {
            const extension = match[1].toLowerCase();
            if (["jpg", "jpeg", "png", "webp", "gif", "bmp", "mp4", "webm", "mov"].includes(extension)) {
                return extension;
            }
        }
    } catch {
        // Ignore invalid URL
    }
    return "mp4"; // Default fallback
}

function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);

    setTimeout(() => {
        URL.revokeObjectURL(url);
    }, 150);
}

/* --------------------------------------------------------------------------
 | Canvas Rendering Engine (Bakes Overlays into Media for Download)
 -------------------------------------------------------------------------- */

// Shared function to draw text, gradients, and logos uniformly
function drawCanvasOverlays(ctx, width, height, text, username, logoImg) {
    // 1. Draw bottom gradient
    if (text || username) {
        const gradient = ctx.createLinearGradient(0, height * 0.4, 0, height);
        gradient.addColorStop(0, "transparent");
        gradient.addColorStop(0.6, "rgba(0,0,0,0.6)");
        gradient.addColorStop(1, "rgba(0,0,0,0.95)");
        ctx.fillStyle = gradient;
        ctx.fillRect(0, height * 0.4, width, height * 0.6);
    }

    // 2. Draw Logo
    if (logoImg) {
        const logoSize = Math.max(50, width * 0.08);
        ctx.fillStyle = "rgba(255, 255, 255, 0.9)";
        ctx.beginPath();
        ctx.roundRect(20, 20, logoSize + 10, logoSize + 10, 10);
        ctx.fill();
        ctx.drawImage(logoImg, 25, 25, logoSize, logoSize);
    }

    // 3. Draw Text (with automatic word wrap)
    if (text) {
        const fontSize = Math.max(24, width * 0.045);
        ctx.font = `bold ${fontSize}px sans-serif`;
        ctx.fillStyle = "white";
        ctx.textAlign = "center";
        ctx.shadowColor = "rgba(0,0,0,0.8)";
        ctx.shadowBlur = 8;
        ctx.shadowOffsetY = 2;

        const maxWidth = width * 0.85;
        const words = text.split(" ");
        let line = "";
        const lines = [];

        for (let n = 0; n < words.length; n++) {
            const testLine = line + words[n] + " ";
            const metrics = ctx.measureText(testLine);
            if (metrics.width > maxWidth && n > 0) {
                lines.push(line);
                line = words[n] + " ";
            } else {
                line = testLine;
            }
        }
        lines.push(line);

        const lineHeight = fontSize * 1.3;
        const textBottomY = height - (height * 0.15);
        let startY = textBottomY - (lines.length * lineHeight);

        lines.forEach((l) => {
            ctx.fillText(l.trim(), width / 2, startY);
            startY += lineHeight;
        });
    }

    // 4. Draw Username Pill
    if (username) {
        const fontSize = Math.max(16, width * 0.025);
        ctx.font = `bold ${fontSize}px sans-serif`;
        const textWidth = ctx.measureText(username).width;
        const padding = fontSize * 0.8;
        
        const boxW = textWidth + (padding * 2);
        const boxH = fontSize + (padding * 2);
        const x = width - boxW - 20;
        const y = height - boxH - 20;

        ctx.shadowBlur = 0;
        ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
        ctx.beginPath();
        ctx.roundRect(x, y, boxW, boxH, 8);
        ctx.fill();

        ctx.fillStyle = "white";
        ctx.textAlign = "left";
        ctx.textBaseline = "top";
        ctx.fillText(username, x + padding, y + padding);
    }
}

// Loads a logo image cross-origin
async function loadLogo(logoSrc) {
    if (!logoSrc) return null;
    return new Promise((resolve) => {
        const img = new Image();
        img.crossOrigin = "anonymous";
        img.onload = () => resolve(img);
        img.onerror = () => resolve(null);
        img.src = logoSrc;
    });
}

// Bakes overlays into a static Image
async function generateImageWithOverlay(src, text, username, logoSrc) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.crossOrigin = "anonymous";
        
        img.onload = async () => {
            const canvas = document.createElement("canvas");
            canvas.width = img.width;
            canvas.height = img.height;
            const ctx = canvas.getContext("2d");

            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            const logoImg = await loadLogo(logoSrc);
            
            drawCanvasOverlays(ctx, canvas.width, canvas.height, text, username, logoImg);

            canvas.toBlob((blob) => resolve({ blob, extension: "jpg" }), "image/jpeg", 0.95);
        };
        
        img.onerror = () => reject(new Error("Failed to load image"));
        img.src = src;
    });
}

// Bakes overlays into a Video by recording an HTML Canvas in real-time
async function generateVideoWithOverlay(src, text, username, logoSrc, onProgress) {
    return new Promise(async (resolve, reject) => {
        const video = document.createElement("video");
        video.crossOrigin = "anonymous";
        video.src = src;
        video.muted = true; // Must be muted to auto-play invisibly
        video.playsInline = true;

        video.onloadedmetadata = async () => {
            const canvas = document.createElement("canvas");
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext("2d");

            const logoImg = await loadLogo(logoSrc);
            
            // Capture video stream from canvas
            const canvasStream = canvas.captureStream(30);
            let finalStream = canvasStream;

            // Attempt to preserve original audio track
            try {
                const audioStream = video.captureStream ? video.captureStream() : video.mozCaptureStream ? video.mozCaptureStream() : null;
                if (audioStream && audioStream.getAudioTracks().length > 0) {
                    finalStream = new MediaStream([...canvasStream.getVideoTracks(), ...audioStream.getAudioTracks()]);
                }
            } catch (e) {
                console.warn("Could not capture audio, exporting muted video.", e);
            }

            // Fallback to supported formats
            let mimeType = 'video/webm;codecs=vp9';
            if (MediaRecorder.isTypeSupported('video/mp4')) mimeType = 'video/mp4';
            else if (MediaRecorder.isTypeSupported('video/webm;codecs=vp8')) mimeType = 'video/webm;codecs=vp8';

            const recorder = new MediaRecorder(finalStream, { mimeType });
            const chunks = [];

            recorder.ondataavailable = (e) => { if (e.data.size > 0) chunks.push(e.data); };
            recorder.onstop = () => {
                const blob = new Blob(chunks, { type: mimeType });
                resolve({ blob, extension: mimeType.includes('mp4') ? 'mp4' : 'webm' });
            };

            // Drawing loop
            function drawFrame() {
                if (video.paused || video.ended) return;
                
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                drawCanvasOverlays(ctx, canvas.width, canvas.height, text, username, logoImg);

                if (onProgress) {
                    onProgress(Math.round((video.currentTime / video.duration) * 100));
                }

                requestAnimationFrame(drawFrame);
            }

            video.addEventListener("play", () => drawFrame());
            video.addEventListener("ended", () => recorder.stop());

            recorder.start();
            video.play().catch((err) => reject(new Error("Video playback failed: " + err.message)));
        };

        video.onerror = () => reject(new Error("Failed to load video. Check CORS policy."));
    });
}

// Master Media Fetcher
async function getMediaBlobForDownload(scene, username, logo, onProgress) {
    const isVideo = scene.media_type === "video";
    
    try {
        if (isVideo) {
            return await generateVideoWithOverlay(scene.media_url, scene.text, username, logo, onProgress);
        } else {
            return await generateImageWithOverlay(scene.media_url, scene.text, username, logo);
        }
    } catch (error) {
        console.warn("Canvas generation failed. Downloading raw fallback file.", error);
        // Fallback if canvas is tainted by CORS
        const response = await fetch(scene.media_url);
        const blob = await response.blob();
        return { 
            blob, 
            extension: isVideo ? "mp4" : getMediaExtension(scene.media_url) 
        };
    }
}

/* --------------------------------------------------------------------------
 | UI Components: Branded Image & Reel Video
 -------------------------------------------------------------------------- */

function BrandedImage({ src, alt, text, username, logo, onClick }) {
    return (
        <button
            type="button"
            onClick={onClick}
            className={cx(`
                group relative mt-4 block w-full overflow-hidden
                rounded-xl bg-slate-100 text-left aspect-[4/5] sm:aspect-video
                focus:outline-none focus:ring-2 focus:ring-indigo-500
            `)}
            aria-label="Open full image"
        >
            <img
                src={src}
                alt={alt}
                loading="lazy"
                className={cx(`
                    block h-full w-full bg-slate-100 object-cover
                    transition-transform duration-300 group-hover:scale-[1.03]
                `)}
            />
            {text && <div className="pointer-events-none absolute inset-x-0 bottom-0 h-2/3 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />}
            {text && (
                <div className="pointer-events-none absolute bottom-14 left-5 right-5 text-center text-xl font-bold leading-tight text-white drop-shadow-lg sm:text-2xl">
                    {text}
                </div>
            )}
            {logo && <img src={logo} alt="" className="pointer-events-none absolute left-4 top-4 h-10 w-10 rounded-lg bg-white/90 p-1 object-contain shadow" />}
            {username && (
                <div className="pointer-events-none absolute bottom-4 right-4 rounded-lg bg-black/50 px-2.5 py-1 text-xs font-medium text-white backdrop-blur-sm">
                    {username}
                </div>
            )}
            <div className="absolute right-3 top-3 rounded-lg bg-black/70 px-3 py-2 text-xs font-medium text-white opacity-0 transition-opacity group-hover:opacity-100">
                View full image
            </div>
        </button>
    );
}

function BrandedVideo({ src, text, username, logo, onClick, inline = true }) {
    return (
        <div 
            onClick={onClick}
            className={cx(`
                relative block w-full overflow-hidden rounded-xl bg-slate-950 aspect-[9/16] 
                ${inline ? 'mt-4 sm:aspect-video' : 'h-full w-full max-h-full cursor-pointer'}
            `)}
        >
            <video
                src={src}
                className="block h-full w-full object-cover bg-slate-950"
                controls={!inline}
                autoPlay={!inline}
                loop={!inline}
                muted={inline}
                preload="metadata"
                controlsList="nodownload"
            />
            {text && <div className="pointer-events-none absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-black/80 to-transparent opacity-80" />}
            {text && (
                <div className="pointer-events-none absolute bottom-16 left-5 right-5 text-center text-xl font-bold leading-tight text-white drop-shadow-md sm:text-2xl">
                    {text}
                </div>
            )}
            {logo && <img src={logo} alt="" className="pointer-events-none absolute left-4 top-4 h-10 w-10 rounded-lg bg-white/90 p-1 object-contain shadow" />}
            {username && (
                <div className="pointer-events-none absolute bottom-14 right-4 rounded-lg bg-black/50 px-2.5 py-1 text-xs font-medium text-white backdrop-blur-sm">
                    {username}
                </div>
            )}
            {inline && (
                <div className="pointer-events-none absolute right-3 top-3 rounded-lg bg-black/70 px-3 py-2 text-xs font-medium text-white opacity-0 transition-opacity hover:opacity-100">
                    Click to expand video
                </div>
            )}
        </div>
    );
}

function OverlayImage({ src, alt, text, username, logo, className = "", style = {} }) {
    return (
        <div className={cx(`relative overflow-hidden bg-slate-100 rounded-lg shadow-2xl`, className)} style={style}>
            <img src={src} alt={alt} draggable={false} className="block h-full w-full object-cover" />
            
            {text && <div className="pointer-events-none absolute inset-x-0 bottom-0 h-2/3 bg-gradient-to-t from-black/80 via-black/30 to-transparent" />}
            {text && (
                <div className="pointer-events-none absolute bottom-12 left-6 right-6 text-center text-2xl font-bold leading-tight text-white drop-shadow-[0_2px_6px_rgba(0,0,0,0.8)] sm:text-3xl">
                    {text}
                </div>
            )}
            {logo && <img src={logo} alt="" className="pointer-events-none absolute left-4 top-4 h-10 w-10 rounded-lg bg-white/90 p-1 object-contain shadow-lg" />}
            {username && <div className="pointer-events-none absolute bottom-4 right-4 rounded-lg bg-black/50 px-3 py-1.5 text-xs font-semibold text-white backdrop-blur-sm">{username}</div>}
        </div>
    );
}

/* --------------------------------------------------------------------------
 | Carousel Viewer & Downloading
 -------------------------------------------------------------------------- */

function CarouselViewer({ scenes = [], initialIndex = 0, username = "", logo = "", onClose }) {
    const [currentIndex, setCurrentIndex] = useState(initialIndex);
    const [zoom, setZoom] = useState(1);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [isDownloading, setIsDownloading] = useState(false);
    const [downloadStatus, setDownloadStatus] = useState("");

    const viewerRef = useRef(null);
    const currentScene = scenes[currentIndex];
    const isCurrentSceneVideo = currentScene?.media_type === "video";

    const zoomIn = useCallback(() => setZoom((prev) => clampZoom(Number((prev + ZOOM_STEP).toFixed(2)))), []);
    const zoomOut = useCallback(() => setZoom((prev) => clampZoom(Number((prev - ZOOM_STEP).toFixed(2)))), []);
    const resetZoom = useCallback(() => setZoom(1), []);

    const goToSlide = useCallback((index) => {
        if (!scenes.length) return;
        setCurrentIndex((index + scenes.length) % scenes.length);
        setZoom(1);
    }, [scenes.length]);

    const nextSlide = useCallback(() => goToSlide(currentIndex + 1), [currentIndex, goToSlide]);
    const previousSlide = useCallback(() => goToSlide(currentIndex - 1), [currentIndex, goToSlide]);

    const handleWheel = useCallback((event) => {
        if (isCurrentSceneVideo) return; // Prevent zoom on video
        event.preventDefault();
        setZoom((prev) => clampZoom(event.deltaY < 0 ? prev + 0.15 : prev - 0.15));
    }, [isCurrentSceneVideo]);

    const handleDoubleClick = useCallback(() => {
        if (isCurrentSceneVideo) return;
        setZoom((prev) => (prev === 1 ? 2 : 1));
    }, [isCurrentSceneVideo]);

    const handleFullscreen = useCallback(async () => {
        try {
            if (!viewerRef.current) return;
            const doc = document;
            const el = viewerRef.current;
            const isFull = doc.fullscreenElement || doc.webkitFullscreenElement;

            if (!isFull) {
                if (el.requestFullscreen) await el.requestFullscreen();
                else if (el.webkitRequestFullscreen) await el.webkitRequestFullscreen();
            } else {
                if (doc.exitFullscreen) await doc.exitFullscreen();
                else if (doc.webkitExitFullscreen) await doc.webkitExitFullscreen();
            }
        } catch (error) {
            console.error("Fullscreen error:", error);
        }
    }, []);

    // --------------------------------------------------
    // Downloads with Overlays
    // --------------------------------------------------

    const downloadCurrentSlide = useCallback(async () => {
        if (!currentScene?.media_url) return;
        setIsDownloading(true);
        setDownloadStatus("Preparing download...");

        try {
            const { blob, extension } = await getMediaBlobForDownload(
                currentScene, 
                username, 
                logo, 
                (progress) => setDownloadStatus(isCurrentSceneVideo ? `Rendering video... ${progress}%` : "Baking image...")
            );
            
            const sceneNumber = currentScene.scene || currentIndex + 1;
            const filename = `${sanitizeFilename(currentScene.keyword || currentScene.text || `slide-${sceneNumber}`)}.${extension}`;

            downloadBlob(blob, filename);
            setDownloadStatus("Downloaded!");
            setTimeout(() => setDownloadStatus(""), 2000);
        } catch (error) {
            console.error("Download failed:", error);
            setDownloadStatus("Download failed");
            setTimeout(() => setDownloadStatus(""), 2500);
        } finally {
            setIsDownloading(false);
        }
    }, [currentScene, currentIndex, username, logo, isCurrentSceneVideo]);

    const downloadAllIndividually = useCallback(async () => {
        if (!scenes.length) return;
        setIsDownloading(true);
        setDownloadStatus(`Downloading 0 / ${scenes.length}`);

        try {
            for (let index = 0; index < scenes.length; index += 1) {
                const scene = scenes[index];
                if (!scene?.media_url) continue;

                try {
                    const { blob, extension } = await getMediaBlobForDownload(
                        scene, 
                        username, 
                        logo,
                        (progress) => setDownloadStatus(`Rendering ${index + 1}/${scenes.length}... ${progress}%`)
                    );
                    
                    const sceneNumber = scene.scene || index + 1;
                    const filename = `${String(sceneNumber).padStart(2, "0")}-${sanitizeFilename(scene.keyword || scene.text || `slide-${sceneNumber}`)}.${extension}`;

                    downloadBlob(blob, filename);
                } catch (error) {
                    console.error(`Failed to download slide ${index + 1}:`, error);
                }
                await new Promise((resolve) => setTimeout(resolve, 500)); 
            }
            setDownloadStatus("All media downloaded!");
            setTimeout(() => setDownloadStatus(""), 2500);
        } finally {
            setIsDownloading(false);
        }
    }, [scenes, username, logo]);

    const downloadAllAsZip = useCallback(async () => {
        if (!scenes.length) return;
        setIsDownloading(true);
        setDownloadStatus(`Preparing ZIP 0 / ${scenes.length}`);

        try {
            const zip = new JSZip();
            let downloadedCount = 0;

            for (let index = 0; index < scenes.length; index += 1) {
                const scene = scenes[index];
                if (!scene?.media_url) continue;

                try {
                    const { blob, extension } = await getMediaBlobForDownload(
                        scene, 
                        username, 
                        logo,
                        (progress) => setDownloadStatus(`Processing ${index + 1}/${scenes.length}... ${progress}%`)
                    );
                    
                    const sceneNumber = scene.scene || index + 1;
                    const filename = `${String(sceneNumber).padStart(2, "0")}-${sanitizeFilename(scene.keyword || scene.text || `slide-${sceneNumber}`)}.${extension}`;

                    zip.file(filename, blob);
                    downloadedCount += 1;
                    setDownloadStatus(`Zipping ${downloadedCount} / ${scenes.length}`);
                } catch (error) {
                    console.error(`Failed to add slide ${index + 1} to ZIP:`, error);
                }
            }

            setDownloadStatus("Compressing ZIP...");
            const zipBlob = await zip.generateAsync({
                type: "blob",
                compression: "DEFLATE",
                compressionOptions: { level: 6 },
            });

            downloadBlob(zipBlob, "carousel-media.zip");
            setDownloadStatus("ZIP downloaded");
            setTimeout(() => setDownloadStatus(""), 2500);
        } catch (error) {
            console.error("ZIP download failed:", error);
            setDownloadStatus("ZIP download failed");
            setTimeout(() => setDownloadStatus(""), 2500);
        } finally {
            setIsDownloading(false);
        }
    }, [scenes, username, logo]);

    useEffect(() => {
        const handleKeyDown = (event) => {
            switch (event.key) {
                case "Escape":
                    if (document.fullscreenElement || document.webkitFullscreenElement) {
                        if (document.exitFullscreen) document.exitFullscreen();
                        else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
                    } else {
                        onClose();
                    }
                    break;
                case "ArrowLeft": previousSlide(); break;
                case "ArrowRight": nextSlide(); break;
                case "+": case "=": zoomIn(); break;
                case "-": zoomOut(); break;
                case "0": resetZoom(); break;
                default: break;
            }
        };

        document.addEventListener("keydown", handleKeyDown);
        return () => document.removeEventListener("keydown", handleKeyDown);
    }, [nextSlide, previousSlide, zoomIn, zoomOut, resetZoom, onClose]);

    if (!currentScene) return null;

    return (
        <div ref={viewerRef} className="fixed inset-0 z-[9999] flex flex-col bg-black/95 text-white" role="dialog">
            <div className="flex shrink-0 items-center justify-between gap-3 border-b border-white/10 bg-black/80 px-3 py-3 sm:px-5">
                <div className="min-w-0">
                    <p className="truncate text-sm font-semibold">Media Viewer</p>
                    <p className="text-xs text-slate-400">Slide {currentIndex + 1} of {scenes.length} {(!isCurrentSceneVideo) && `• ${Math.round(zoom * 100)}%`}</p>
                </div>
                <div className="flex items-center gap-1">
                    {!isCurrentSceneVideo && (
                        <>
                            <button type="button" onClick={zoomOut} disabled={zoom <= MIN_ZOOM || isDownloading} className="rounded-lg p-2 text-white hover:bg-white/10 disabled:opacity-30"><ZoomOut size={18} /></button>
                            <button type="button" onClick={zoomIn} disabled={zoom >= MAX_ZOOM || isDownloading} className="rounded-lg p-2 text-white hover:bg-white/10 disabled:opacity-30"><ZoomIn size={18} /></button>
                        </>
                    )}
                    <button type="button" onClick={handleFullscreen} disabled={isDownloading} className="hidden rounded-lg p-2 text-white hover:bg-white/10 sm:block">{isFullscreen ? <Minimize size={18} /> : <Maximize size={18} />}</button>
                    <button type="button" onClick={onClose} className="ml-1 rounded-lg p-2 text-slate-300 hover:bg-red-500 hover:text-white"><X size={20} /></button>
                </div>
            </div>

            <div className="relative flex min-h-0 flex-1 items-center justify-center overflow-hidden">
                <button type="button" onClick={previousSlide} disabled={scenes.length <= 1 || isDownloading} className="absolute left-2 z-20 rounded-full bg-black/60 p-2.5 text-white shadow-lg backdrop-blur-sm transition hover:bg-white/20 disabled:opacity-30 sm:left-5 sm:p-3"><ChevronLeft size={24} /></button>
                
                <div className="flex h-full w-full items-center justify-center overflow-auto p-8 sm:p-12" onWheel={handleWheel} onDoubleClick={handleDoubleClick}>
                    {isCurrentSceneVideo ? (
                        <div style={{ transform: `scale(${zoom})`, transformOrigin: "center center" }} className="w-full h-full max-h-full max-w-[800px] flex justify-center items-center">
                            <BrandedVideo
                                src={currentScene.media_url}
                                text={currentScene.text}
                                username={username}
                                logo={logo}
                                inline={false}
                            />
                        </div>
                    ) : (
                        <OverlayImage
                            src={currentScene.media_url}
                            alt={currentScene.keyword || `Slide ${currentIndex + 1}`}
                            text={currentScene.text}
                            username={username}
                            logo={logo}
                            className="max-h-full max-w-full aspect-[4/5] sm:aspect-video"
                            style={{ transform: `scale(${zoom})`, transformOrigin: "center center" }}
                        />
                    )}
                </div>

                <button type="button" onClick={nextSlide} disabled={scenes.length <= 1 || isDownloading} className="absolute right-2 z-20 rounded-full bg-black/60 p-2.5 text-white shadow-lg backdrop-blur-sm transition hover:bg-white/20 disabled:opacity-30 sm:right-5 sm:p-3"><ChevronRight size={24} /></button>
            </div>

            <div className="flex shrink-0 flex-wrap items-center justify-center gap-2 border-t border-white/10 bg-black/90 px-3 py-3 sm:justify-between sm:px-5">
                <div className="hidden text-xs text-slate-400 sm:block">
                    {downloadStatus || (isCurrentSceneVideo ? "← → to navigate videos" : "Scroll to zoom • ← → navigate")}
                </div>
                <div className="flex flex-wrap items-center gap-2">
                    <button type="button" onClick={downloadCurrentSlide} disabled={isDownloading} className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-3 py-2 text-xs font-medium text-white transition hover:bg-indigo-500 disabled:opacity-50"><Download size={16} /><span className="hidden sm:inline">Current</span></button>
                    <button type="button" onClick={downloadAllIndividually} disabled={isDownloading} className="inline-flex items-center gap-2 rounded-lg border border-white/15 bg-white/5 px-3 py-2 text-xs font-medium text-white transition hover:bg-white/10 disabled:opacity-50"><Download size={16} /><span className="hidden sm:inline">All</span></button>
                    <button type="button" onClick={downloadAllAsZip} disabled={isDownloading} className="inline-flex items-center gap-2 rounded-lg border border-white/15 bg-white/5 px-3 py-2 text-xs font-medium text-white transition hover:bg-white/10 disabled:opacity-50"><Package size={16} /><span className="hidden sm:inline">ZIP</span></button>
                </div>
            </div>

            {/* Thumbnail Strip */}
            <div className="shrink-0 overflow-x-auto border-t border-white/10 bg-black/95 px-3 py-3 sm:px-5">
                <div className="flex min-w-max justify-center gap-2">
                    {scenes.map((scene, index) => (
                        <button
                            key={scene.scene || index}
                            type="button"
                            onClick={() => goToSlide(index)}
                            disabled={isDownloading}
                            className={cx(`
                                relative h-16 w-16 shrink-0 overflow-hidden rounded-lg border-2 transition sm:h-20 sm:w-20
                                ${index === currentIndex ? "border-indigo-500 ring-2 ring-indigo-500/30" : "border-white/10 hover:border-white/40"}
                            `)}
                        >
                            {scene.media_type === "video" ? (
                                <video src={scene.media_url} className="h-full w-full object-cover" muted playsInline preload="metadata" />
                            ) : (
                                <img src={scene.media_url} alt={`Thumbnail ${index + 1}`} className="h-full w-full object-cover" />
                            )}
                            <span className="absolute bottom-1 left-1 rounded bg-black/70 px-1.5 py-0.5 text-[10px] font-medium text-white">{index + 1}</span>
                        </button>
                    ))}
                </div>
            </div>

            {isDownloading && (
                <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-[2px]">
                    <div className="rounded-2xl border border-white/10 bg-slate-900 px-6 py-5 text-center shadow-2xl">
                        <div className="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-2 border-white/20 border-t-white" />
                        <p className="text-sm font-medium text-white">{downloadStatus || "Processing media..."}</p>
                        <p className="mt-1 text-xs text-slate-400">Please wait</p>
                    </div>
                </div>
            )}
        </div>
    );
}

/* --------------------------------------------------------------------------
 | Scene Card
 -------------------------------------------------------------------------- */

function SceneCard({ scene, index, username, logo, scenes }) {
    const mediaType = scene.media_type || "image";
    const sceneNumber = scene.scene || index + 1;
    const [isViewerOpen, setIsViewerOpen] = useState(false);

    return (
        <>
            <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
                <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
                    <span className="text-sm font-semibold text-slate-800">Scene {sceneNumber}</span>
                    <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium capitalize text-slate-600">
                        {mediaType}
                    </span>
                </div>

                <div className="p-4">
                    <div className="space-y-2 text-sm text-slate-700">
                        {scene.text && <p><strong>Text:</strong> {scene.text}</p>}
                        {scene.keyword && <p><strong>Keyword:</strong> {scene.keyword}</p>}
                    </div>

                    {scene.media_url ? (
                        mediaType === "video" ? (
                            <div className="relative w-full cursor-pointer group" onClick={() => setIsViewerOpen(true)}>
                                <BrandedVideo
                                    src={scene.media_url}
                                    text={scene.text}
                                    username={username}
                                    logo={logo}
                                    inline={true} 
                                />
                                <div className="absolute inset-0 flex items-center justify-center bg-black/20 opacity-0 group-hover:opacity-100 transition rounded-xl mt-4">
                                    <Maximize className="text-white drop-shadow-md" size={32} />
                                </div>
                            </div>
                        ) : (
                            <BrandedImage
                                src={scene.media_url}
                                alt={scene.keyword || `Scene ${sceneNumber}`}
                                text={scene.text}
                                username={username}
                                logo={logo}
                                onClick={() => setIsViewerOpen(true)}
                            />
                        )
                    ) : (
                        <p className="mt-4 rounded-xl bg-amber-50 px-3 py-2 text-xs text-amber-800">
                            Media preview is unavailable for this scene.
                        </p>
                    )}
                </div>
            </div>

            {isViewerOpen && (
                <CarouselViewer
                    scenes={scenes}
                    initialIndex={index}
                    username={username}
                    logo={logo}
                    onClose={() => setIsViewerOpen(false)}
                />
            )}
        </>
    );
}

/* --------------------------------------------------------------------------
 | Main UI Handlers & Layout
 -------------------------------------------------------------------------- */

function SceneMedia({ scenes, username, logo, isCarousel }) {
    if (!Array.isArray(scenes) || !scenes.length) return null;
    const [isViewerOpen, setIsViewerOpen] = useState(false);

    if (isCarousel) {
        const firstScene = scenes[0];
        const isFirstVideo = firstScene.media_type === "video";

        return (
            <div className="overflow-hidden rounded-2xl border border-slate-200 bg-slate-950 shadow-sm relative group cursor-pointer" onClick={() => setIsViewerOpen(true)}>
                {isFirstVideo ? (
                    <div className="relative pointer-events-none">
                         <BrandedVideo src={firstScene.media_url} text="Click to view full Carousel" username={username} logo={logo} inline={true} />
                    </div>
                ) : (
                    <BrandedImage src={firstScene.media_url} alt="Carousel Thumbnail" text="Click to view full Carousel" username={username} logo={logo} />
                )}
                
                <div className="absolute inset-0 bg-black/30 flex items-center justify-center opacity-0 group-hover:opacity-100 transition rounded-2xl">
                    <button className="bg-indigo-600 text-white px-5 py-2 rounded-lg font-medium shadow-xl flex items-center gap-2">
                        <Maximize size={18} /> Open Media Carousel
                    </button>
                </div>

                {isViewerOpen && (
                    <CarouselViewer
                        scenes={scenes}
                        initialIndex={0}
                        username={username}
                        logo={logo}
                        onClose={() => setIsViewerOpen(false)}
                    />
                )}
            </div>
        );
    }

    return (
        <div className="space-y-5">
            {scenes.map((scene, index) => (
                <SceneCard key={scene.scene || index} scene={scene} index={index} username={username} logo={logo} scenes={scenes} />
            ))}
        </div>
    );
}

function ContentCard({ content, username, logo }) {
    const [copied, setCopied] = useState(false);
    const isCarousel = Boolean(content.story) && Array.isArray(content.scenes);

    const copyContent = async () => {
        const text = `
Title: ${content.title || ""}
Caption: ${content.caption || ""}
        `.trim();
        try {
            await navigator.clipboard.writeText(text);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (error) {
            console.error("Failed to copy content:", error);
        }
    };

    return (
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-8">
            <div className="mb-6 flex items-center justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-indigo-600 sm:text-3xl">Generated Content</h2>
                    {isCarousel && <p className="mt-1 text-sm text-slate-500">Carousel format</p>}
                </div>
            </div>

            {/* Background Audio Preview */}
            {content.music_url && (
                <div className="mb-6 rounded-2xl bg-slate-900 p-4 shadow-inner">
                    <div className="mb-2 flex items-center gap-2">
                        <span className="text-lg">🎵</span>
                        <h3 className="text-sm font-semibold text-white">Background Track</h3>
                    </div>
                    <audio controls src={content.music_url} className="h-10 w-full" controlsList="nodownload">
                        Your browser does not support the audio element.
                    </audio>
                </div>
            )}

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5 sm:p-6">
                <div className="space-y-6">
                    {content.caption && (
                        <div>
                            <strong className="text-slate-900">Caption</strong>
                            <p className="mt-2 whitespace-pre-line text-slate-700">{content.caption}</p>
                        </div>
                    )}
                </div>
                
                <button onClick={copyContent} className="mt-8 inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-3 text-sm font-medium text-white hover:bg-indigo-700">
                    {copied ? <><Check size={18} /> Copied</> : <><Copy size={18} /> Copy Text</>}
                </button>
            </div>

            {Array.isArray(content.scenes) && content.scenes.length > 0 && (
                <div className="mt-8">
                    <SceneMedia scenes={content.scenes} username={username} logo={logo} isCarousel={isCarousel} />
                </div>
            )}
        </div>
    );
}

export default function PreviewPanel({ data, username = "", logo = "" }) {
    if (!data || !data.data) {
        return (
            <div className="mt-10 rounded-3xl border border-slate-200 bg-white p-10 text-center shadow-sm">
                <Sparkles size={64} className="mx-auto text-blue-500" />
                <h2 className="mt-6 text-2xl font-bold text-slate-800 sm:text-3xl">AI Content Preview</h2>
            </div>
        );
    }

    const isFlatResponse = data.data.title !== undefined || data.data.scenes !== undefined;

    if (isFlatResponse) {
        return (
            <div className="mt-8">
                <ContentCard content={data.data} username={username} logo={logo} />
            </div>
        );
    }

    return (
        <div className="mt-8 space-y-10">
            {Object.entries(data.data).map(([platform, platformData]) => (
                <section key={platform}>
                    <h2 className="mb-5 text-2xl font-bold capitalize text-indigo-600 sm:text-3xl">
                        {platform.replaceAll("_", " ")}
                    </h2>
                    <div className="space-y-8">
                        {Object.entries(platformData).map(([type, content]) => (
                            <div key={type}>
                                <ContentCard content={content} username={username} logo={logo} />
                            </div>
                        ))}
                    </div>
                </section>
            ))}
        </div>
    );
}