import { useState } from "react";

import { generateContent } from "../../api/ai";
import NicheSelector from "./NicheSelector";
import TrendingTopics from "./TrendingTopics";
import PackageSelector from "./PackageSelector";
import GenerateButton from "./GenerateButton";
import PreviewPanel from "./PreviewPanel";
import PlatformSelector from "./PlatformSelector";
import ContentTypeSelector from "./ContentTypeSelector";
import SummaryPanel from "./SummaryPanel";

export default function AIStudio() {

    const [selectedNiche, setSelectedNiche] = useState("");

    const [selectedTopic, setSelectedTopic] = useState("");

    const [selectedPackage, setSelectedPackage] = useState("complete");

    const [loading, setLoading] = useState(false);

    const [generatedContent, setGeneratedContent] = useState(null);

    const [selectedPlatforms, setSelectedPlatforms] = useState([]);
    const [selectedContent, setSelectedContent] = useState([]);

   const handleGenerate = async () => {

    if (selectedPlatforms.length === 0) {
        alert("Please select at least one platform.");
        return;
    }

    if (selectedContent.length === 0) {
        alert("Please select at least one content type.");
        return;
    }

    if (!selectedNiche) {
        alert("Please select a niche.");
        return;
    }

    if (!selectedTopic.trim()) {
        alert("Please select or enter a topic.");
        return;
    }

    setLoading(true);

    try {

        const payload = {

            platforms: selectedPlatforms,

            content_types: selectedContent,

            niche: selectedNiche,

            topic: selectedTopic,

            package: selectedPackage,

        };

        console.log(payload);

        const response = await generateContent(payload);

        setGeneratedContent(response);

    } catch (err) {

        console.log(err);

        alert("Generation failed.");

    } finally {

        setLoading(false);

    }

};

    return (

        <div className="p-8">

            <h1 className="text-3xl font-bold mb-8">
                AI Studio
            </h1>

              {/* 1️⃣ Platform */}
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
                onChange={setSelectedPackage}
            />

            <SummaryPanel
                platforms={selectedPlatforms}
                contents={selectedContent}
                niche={selectedNiche}
                topic={selectedTopic}
                packageType={selectedPackage}
            />
            <GenerateButton
                loading={loading}
                onGenerate={handleGenerate}
            />

            <PreviewPanel
                data={generatedContent}
            />

        </div>

    );

}