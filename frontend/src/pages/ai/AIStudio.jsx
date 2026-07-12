import { useState } from "react";

import { generateContent } from "../../api/ai";
import NicheSelector from "./NicheSelector";
import TrendingTopics from "./TrendingTopics";
import PackageSelector from "./PackageSelector";
import GenerateButton from "./GenerateButton";
import PreviewPanel from "./PreviewPanel";

export default function AIStudio() {

    const [selectedNiche, setSelectedNiche] = useState("");

    const [selectedTopic, setSelectedTopic] = useState("");

    const [selectedPackage, setSelectedPackage] = useState("complete");

    const [loading, setLoading] = useState(false);

    const [generatedContent, setGeneratedContent] = useState(null);

    const handleGenerate = async () => {

        if (!selectedNiche) {
            alert("Please select a niche.");
            return;
        }

        if (!selectedTopic) {
            alert("Please select a topic.");
            return;
        }

        setLoading(true);

        try {

            const response = await generateContent({

                niche: selectedNiche,

                topic: selectedTopic,

                package: selectedPackage,

            });

            setGeneratedContent(response);

        } catch (error) {

            console.error(error);

            alert("Failed to generate content.");

        } finally {

            setLoading(false);

        }

    };

    return (

        <div className="p-8">

            <h1 className="text-3xl font-bold mb-8">
                AI Studio
            </h1>

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