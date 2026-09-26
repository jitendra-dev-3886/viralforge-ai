export const formatPlatformLabel = (platform) => {
        const labels = {
            instagram: "Instagram",
            facebook: "Facebook",
            youtube: "YouTube",
        };
        return labels[platform] || platform;
    };

export const formatContentTypeLabel = (value) => {
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

export const formatContentTypePrompt = (value) => {
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


export function studioGenerationPayload({ selectedProjectId, selectedPlatforms, selectedContent, selectedNiche, selectedTopic, selectedPackage, generationOptions, selectedProvider, visualStyle, contentGoal }) {
    return {
                project_id: selectedProjectId,
                platforms: selectedPlatforms.map(formatPlatformLabel),
                content_types: Array.from(
                    new Set(selectedContent.map(formatContentTypePrompt)),
                ),
                outputs: selectedContent.map((item) => {
                    const [platform] = item.split(":");
                    return `${formatPlatformLabel(platform)}: ${formatContentTypePrompt(item)}`;
                }),
                niche: selectedNiche,
                topic: selectedTopic,
                package: selectedPackage,
                language: generationOptions.language || "English",
                scene_count: ["reel","carousel","story"].includes(selectedPackage) ? generationOptions.scene_count : undefined,
                total_duration: selectedPackage === "reel" ? generationOptions.total_duration : undefined,
                style: ["reel","carousel","story"].includes(selectedPackage) ? generationOptions.style : undefined,
                provider: selectedProvider,
                visual_style: visualStyle,
                ...(contentGoal ? { content_goal: contentGoal } : {}),
            };
}
