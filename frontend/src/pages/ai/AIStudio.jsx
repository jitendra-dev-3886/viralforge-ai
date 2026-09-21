import UserProviderSelector from "../settings/UserProviderSelector";
import { useContext, useEffect, useMemo, useState } from "react";

import { generateContent } from "../../api/ai";
import { useProject } from "../../context/ProjectContext";
import NicheSelector from "./NicheSelector";
import TrendingTopics from "./TrendingTopics";
import PackageSelector from "./PackageSelector";
import GenerateButton from "./GenerateButton";
import PreviewPanel from "./PreviewPanel";
import PlatformSelector from "./PlatformSelector";
import ContentTypeSelector from "./ContentTypeSelector";
import SummaryPanel from "./SummaryPanel";
import VisualStyleSelector from "./VisualStyleSelector";
import { getVisualStyle } from "./visualStyles";
import { assetUrl } from "../../api/axios";
import { AuthContext } from "../../context/AuthContext";
import { useBrand } from "../../context/BrandContext";

export default function AIStudio() {

    const [selectedNiche, setSelectedNiche] = useState("");

    const [selectedTopic, setSelectedTopic] = useState("");

    const [selectedPackage, setSelectedPackage] = useState("complete");
    const [quoteLanguage, setQuoteLanguage] = useState("Hindi");
    const [generationOptions, setGenerationOptions] = useState({ language: "Hindi", scene_count: 7, total_duration: 30, style: "Educational" });
    const [selectedProvider, setSelectedProvider] = useState("auto");
    const [visualStyle, setVisualStyle] = useState("minimal");

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const [generatedContent, setGeneratedContent] = useState(null);
    const [selectedProjectId, setSelectedProjectId] = useState(null);

    const { projects } = useProject();
    const { brands } = useBrand();
    const { user } = useContext(AuthContext);
    const [selectedPlatforms, setSelectedPlatforms] = useState([]);
    const [selectedContent, setSelectedContent] = useState([]);
    const hasQuoteOutput = selectedContent.some((item) => item.endsWith(":quote"));

    const selectedProject = useMemo(
        () => projects.find((project) => Number(project.id) === Number(selectedProjectId)),
        [projects, selectedProjectId],
    );
    const selectedBrand = useMemo(
        () => brands.find((brand) => Number(brand.id) === Number(selectedProject?.brand_id)),
        [brands, selectedProject?.brand_id],
    );
    const branding = generatedContent?.branding || generatedContent?.data?.branding || {};
    const overlayUsername = branding.username || user?.name || selectedBrand?.name || "";
    const overlayLogo = branding.logo || selectedBrand?.logo || "";

    const isReady = Boolean(
        selectedProjectId
        && selectedPlatforms.length
        && selectedContent.length
        && selectedNiche
        && selectedTopic.trim(),
    );

    const formatPlatformLabel = (platform) => {
        const labels = {
            instagram: "Instagram",
            facebook: "Facebook",
            youtube: "YouTube",
        };
        return labels[platform] || platform;
    };

    const formatContentTypeLabel = (value) => {
        const [platform, type] = value.split(":");
        const typeLabels = {
            reel: "Reel",
            carousel: "Carousel",
            story: "Story",
            post: "Post",
            quote: "Quote",
            shorts: "Shorts",
            video: "Long Video",
            community: "Community Post",
        };

        const platformLabel = formatPlatformLabel(platform);
        const typeLabel = typeLabels[type] || type.charAt(0).toUpperCase() + type.slice(1);

        return `${platformLabel} ${typeLabel}`;
    };

    const formatContentTypePrompt = (value) => {
        const [, type] = value.split(":");
        const typeLabels = {
            reel: "Reel",
            carousel: "Carousel",
            story: "Story",
            post: "Post",
            quote: "Quote",
            shorts: "Shorts",
            video: "Long Video",
            community: "Community Post",
        };
        return typeLabels[type] || type.charAt(0).toUpperCase() + type.slice(1);
    };

    const handleGenerate = async () => {

        if (!selectedProjectId) {
            setError("Select a project before generating content.");
            return;
        }

        if (selectedPlatforms.length === 0) {
            setError("Select at least one platform.");
            return;
        }

        if (selectedContent.length === 0) {
            setError("Select at least one content type.");
            return;
        }

        if (!selectedNiche) {
            setError("Select a niche to tailor the generated content.");
            return;
        }

        if (!selectedTopic.trim()) {
            setError("Choose or enter a topic before generating content.");
            return;
        }

        setLoading(true);
        setError("");

        setGeneratedContent(null);

        try {

            const payload = {
                project_id: selectedProjectId,
                platforms: selectedPlatforms.map(formatPlatformLabel),
                content_types: Array.from(
                    new Set(selectedContent.map(formatContentTypePrompt)),
                ),
                outputs: selectedContent.map((item) => {
                    const [platform, type] = item.split(":");
                    return `${formatPlatformLabel(platform)}: ${formatContentTypePrompt(item)}`;
                }),
                niche: selectedNiche,
                topic: selectedTopic,
                package: selectedPackage,
                language: ["quote","reel","carousel","story"].includes(selectedPackage) || hasQuoteOutput ? generationOptions.language : (selectedProject?.language || "English"),
                scene_count: ["reel","carousel","story"].includes(selectedPackage) ? generationOptions.scene_count : undefined,
                total_duration: selectedPackage === "reel" ? generationOptions.total_duration : undefined,
                style: ["reel","carousel","story"].includes(selectedPackage) ? generationOptions.style : undefined,
                provider: selectedProvider,
                visual_style: visualStyle,
            };

            const response = await generateContent(payload);

            setGeneratedContent(response);

        } catch (error) {

            console.error(error);

            let message = "Something went wrong.";

            if (error.response) {

                const data = error.response.data;

                if (Array.isArray(data.detail)) {

                    message = data.detail
                        .map(item => item.msg)
                        .join("\n");

                } else if (typeof data.detail === "string") {

                    message = data.detail;

                } else if (data.detail?.message) {

                    message = data.detail.message;

                } else {

                    message = "Server Error.";
                }

            } else if (error.request) {

                message = "Cannot connect to backend server.";

            } else if (error.message) {

                message = error.message;

            }

            setError(message);

        } finally {

            setLoading(false);

        }

    };

    useEffect(() => {
        if (!selectedProjectId && projects.length > 0) {
            setSelectedProjectId(projects[0].id);
        }
    }, [projects, selectedProjectId]);

    useEffect(() => {
        setSelectedContent((current) => current.filter((item) => (
            selectedPlatforms.includes(item.split(":")[0])
        )));
    }, [selectedPlatforms]);

    return (

        <div className="mx-auto max-w-6xl pb-10">

            <div className="mb-8 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                <div>
                    <p className="text-sm font-semibold text-blue-600">CONTENT CREATION</p>
                    <h1 className="mt-1 text-3xl font-bold text-slate-900">Generate content</h1>
                    <p className="mt-2 text-slate-500">Create platform-ready scripts, captions, and scenes in one workflow.</p>
                </div>
                <div className="rounded-full bg-slate-100 px-4 py-2 text-sm font-medium text-slate-600">
                    {selectedContent.length} output{selectedContent.length === 1 ? "" : "s"} selected
                </div>
            </div>

            <div className="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                    Project
                </label>
                <select
                    className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
                    value={selectedProjectId || ""}
                    onChange={(event) => setSelectedProjectId(Number(event.target.value))}
                >
                    <option value="" disabled>
                        Select a project
                    </option>
                    {projects.map((project) => (
                        <option key={project.id} value={project.id}>
                            {project.title}
                        </option>
                    ))}
                </select>

                {projects.length === 0 && (
                    <p className="mt-3 text-sm text-slate-500">
                        No projects available. Create a project first on the Projects page.
                    </p>
                )}
            </div>

            {error && (
                <div role="alert" className="mb-6 rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
                    {error}
                </div>
            )}

              {/* Platform */}
        <PlatformSelector
            selected={selectedPlatforms}
            onChange={setSelectedPlatforms}
        />

        <ContentTypeSelector
            selectedPlatforms={selectedPlatforms}
            selectedContent={selectedContent}
            onChange={setSelectedContent}
        />

            <NicheSelector
                selected={selectedNiche}
                onChange={setSelectedNiche}
            />

            <TrendingTopics
                niche={selectedNiche}
                onSelect={setSelectedTopic}
            />

            {/* We'll use this later */}
            {/* <AIIdeas onSelect={setSelectedTopic} /> */}

            {/* <MyTopic
                value={selectedTopic}
                onChange={setSelectedTopic}
            /> */}

            <PackageSelector
                selected={selectedPackage}
                onChange={(value) => {
                    setSelectedPackage(value);
                    const defaults = value === "carousel" ? { scene_count: 5, total_duration: 25, style: "Educational" } : value === "story" ? { scene_count: 7, total_duration: 35, style: "Emotional" } : value === "reel" ? { scene_count: 7, total_duration: 30, style: "Energetic" } : {};
                    setGenerationOptions((current) => ({ ...current, ...defaults }));
                }}
                quoteLanguage={quoteLanguage}
                onQuoteLanguageChange={(language) => { setQuoteLanguage(language); setGenerationOptions((current) => ({ ...current, language })); }}
                showQuoteOptions={hasQuoteOutput}
                options={generationOptions}
                onOptionsChange={setGenerationOptions}
            />

            <div className="bg-white rounded-3xl shadow-lg p-6 mt-6">
                <UserProviderSelector value={selectedProvider} onChange={setSelectedProvider} disabled={loading} />
            </div>

            <VisualStyleSelector value={visualStyle} onChange={setVisualStyle} topic={selectedTopic} brandName={selectedBrand?.name || ""} logo={assetUrl(selectedBrand?.logo)} disabled={loading} />

            <SummaryPanel
                visualStyle={getVisualStyle(visualStyle)?.name}
                platforms={selectedPlatforms}
                contents={selectedContent}
                niche={selectedNiche}
                topic={selectedTopic}
                packageType={selectedPackage}
            />
            <GenerateButton
                loading={loading}
                onGenerate={handleGenerate}
                disabled={!isReady}
            />

            <PreviewPanel
                data={generatedContent}
                username={overlayUsername}
                brandName={branding.brand_name || selectedBrand?.name || ""}
                logo={overlayLogo}
                projectId={selectedProjectId}
            />

        </div>

    );

}
