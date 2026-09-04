import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useBrand } from "../../context/BrandContext";
import { uploadBrandLogo } from "../../api/brand";
import { useNiches } from "../../context/NicheContext";

export default function CreateBrand() {
    const navigate = useNavigate();
    const { addBrand } = useBrand();
    const { niches } = useNiches();
    
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [logoFile, setLogoFile] = useState(null);

    // Initial state matching the FastAPI CreateBrandRequest schema
    const [formData, setFormData] = useState({
        name: "",
        description: "",
        niche: "",
        website: "",
        logo: "",
        primary_color: "#2563EB",
        secondary_color: "#1E293B",
        font: "Inter",
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            // Clean up the payload before sending
            const payload = { ...formData };
            if (logoFile) {
                if (logoFile.size > 5 * 1024 * 1024) {
                    throw new Error("Logo image must be 5 MB or smaller.");
                }
                const upload = await uploadBrandLogo(logoFile);
                payload.logo = upload.logo_url;
            }
            
            // If website is empty, delete it so it sends as undefined/null rather than an invalid empty string
            if (!payload.website) {
                delete payload.website;
            }

            const response = await addBrand(payload);

            if (response.success) {
                // Redirect back to the Brand Studio grid on success
                navigate("/brands");
            } else {
                // Handle logical errors from the backend (e.g., "Brand name already exists.")
                setError(response.message);
            }
        } catch (err) {
            // Handle HTTP errors, specifically the 422 Validation Error
            if (err.response?.status === 422) {
                const validationErrors = err.response.data.detail;
                console.error("422 Validation Details:", validationErrors);
                setError("Validation Error: Please check your input fields (e.g., ensure website is a valid URL).");
            } else {
                setError(err.response?.data?.detail || err.message || "An unexpected error occurred. Please try again.");
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="mx-auto max-w-2xl p-1 sm:p-4 lg:p-8">
            <div className="flex items-center gap-4 mb-8">
                <Link to="/brands" className="text-gray-500 hover:text-gray-800">
                    &larr; Back
                </Link>
                <h1 className="text-3xl font-bold">Create New Brand</h1>
            </div>

            {error && (
                <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-xl border border-red-200">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="bg-white p-6 rounded-2xl border shadow-sm">
                
                {/* Brand Name (Required) */}
                <div className="mb-5">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Brand Name *
                    </label>
                    <input
                        type="text"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        required
                        className="w-full p-3 border rounded-xl"
                        placeholder="e.g. Acme Corp"
                    />
                </div>

                {/* Niche & Website */}
                <div className="mb-5 grid gap-5 sm:grid-cols-2">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Niche / Industry
                        </label>
                        <select
                            name="niche"
                            value={formData.niche}
                            onChange={handleChange}
                            className="w-full p-3 border rounded-xl"
                        ><option value="">Select a niche</option>{niches.map((niche) => <option key={niche.id} value={niche.name}>{niche.icon} {niche.name}</option>)}</select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Website URL
                        </label>
                        <input
                            type="url"
                            name="website"
                            value={formData.website}
                            onChange={handleChange}
                            className="w-full p-3 border rounded-xl"
                            placeholder="https://example.com"
                        />
                    </div>
                </div>

                <div className="mb-5">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Logo URL
                    </label>
                    <input
                        type="url"
                        name="website"
                        value={formData.website}
                        onChange={handleChange}
                        className="w-full p-3 border rounded-xl"
                        placeholder="https://example.com/logo.png"
                    />
                    <p className="mt-1 text-xs text-gray-500">Use a public HTTPS image URL so it can be included in exported reels and carousel images.</p>
                    <div className="my-3 flex items-center gap-3 text-xs text-gray-400"><span className="h-px flex-1 bg-gray-200" />OR<span className="h-px flex-1 bg-gray-200" /></div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Upload logo image</label>
                    <input
                        type="file"
                        accept="image/png,image/jpeg,image/webp"
                        onChange={(event) => setLogoFile(event.target.files?.[0] || null)}
                        className="w-full rounded-xl border p-3 text-sm"
                    />
                    <p className="mt-1 text-xs text-gray-500">PNG, JPG, or WebP, maximum 5 MB. An uploaded image replaces the URL above.</p>
                </div>

                {/* Description */}
                <div className="mb-5">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Brand Description & Voice
                    </label>
                    <textarea
                        name="description"
                        value={formData.description}
                        onChange={handleChange}
                        rows="4"
                        className="w-full p-3 border rounded-xl"
                        placeholder="Describe the brand's tone, audience, and core message..."
                    />
                </div>

                {/* Colors & Typography */}
                <div className="mb-8 grid gap-5 border-t pt-5 sm:grid-cols-2 lg:grid-cols-3">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Primary Color
                        </label>
                        <div className="flex gap-2 items-center">
                            <input
                                type="color"
                                name="primary_color"
                                value={formData.primary_color}
                                onChange={handleChange}
                                className="h-10 w-10 rounded cursor-pointer"
                            />
                            <span className="text-sm text-gray-500 uppercase">{formData.primary_color}</span>
                        </div>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Secondary Color
                        </label>
                        <div className="flex gap-2 items-center">
                            <input
                                type="color"
                                name="secondary_color"
                                value={formData.secondary_color}
                                onChange={handleChange}
                                className="h-10 w-10 rounded cursor-pointer"
                            />
                            <span className="text-sm text-gray-500 uppercase">{formData.secondary_color}</span>
                        </div>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Font Family
                        </label>
                        <input
                            type="text"
                            name="font"
                            value={formData.font}
                            onChange={handleChange}
                            className="w-full p-2.5 border rounded-xl"
                        />
                    </div>
                </div>

                {/* Submit Button */}
                <div className="flex justify-end">
                    <button
                        type="submit"
                        disabled={loading}
                        className={`px-6 py-3 rounded-xl text-white font-medium transition ${
                            loading ? "bg-blue-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"
                        }`}
                    >
                        {loading ? "Creating..." : "Create Brand"}
                    </button>
                </div>
            </form>
        </div>
    );
}
