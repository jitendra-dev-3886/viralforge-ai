import { useState, useEffect } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { useBrand } from "../../context/BrandContext";
import { getBrand, uploadBrandLogo } from "../../api/brand";
import { assetUrl } from "../../api/axios";
import { useNiches } from "../../context/NicheContext";

export default function EditBrand() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { editBrand } = useBrand();
    const { niches } = useNiches();
    
    const [loading, setLoading] = useState(false);
    const [fetching, setFetching] = useState(true);
    const [error, setError] = useState(null);
    const [logoFile, setLogoFile] = useState(null);

    const [formData, setFormData] = useState({
        name: "",
        description: "",
        niche: "",
        website: "",
        logo: "",
        website: "",
        primary_color: "#2563EB",
        secondary_color: "#1E293B",
        font: "Inter",
    });

    // Fetch existing brand data when the component mounts
    useEffect(() => {
        const fetchBrandData = async () => {
            try {
                const data = await getBrand(id);
                if (data.success && data.brand) {
                    setFormData({
                        name: data.brand.name || "",
                        description: data.brand.description || "",
                        niche: data.brand.niche || "",
                        website: data.brand.website || "",
                        logo: data.brand.logo || "",
                        primary_color: data.brand.primary_color || "#2563EB",
                        secondary_color: data.brand.secondary_color || "#1E293B",
                        font: data.brand.font || "Inter",
                    });
                } else {
                    setError(data.message || "Brand not found.");
                }
            } catch (err) {
                setError("Failed to load brand details.");
                console.error(err);
            } finally {
                setFetching(false);
            }
        };

        fetchBrandData();
    }, [id]);

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
            const payload = { ...formData };
            if (logoFile) {
                if (logoFile.size > 5 * 1024 * 1024) {
                    throw new Error("Logo image must be 5 MB or smaller.");
                }
                const upload = await uploadBrandLogo(logoFile);
                payload.logo = upload.logo_url;
            }
            
            // Clean up empty website strings to avoid FastAPI 422 URL validation errors
            if (!payload.website) {
                payload.website = null; // Update schema accepts None/null
            }

            const response = await editBrand(id, payload);

            if (response.success) {
                navigate("/brands");
            } else {
                setError(response.message);
            }
        } catch (err) {
            if (err.response?.status === 422) {
                console.error("422 Validation Details:", err.response.data.detail);
                setError("Validation Error: Please check your input fields (e.g., ensure website is a valid URL).");
            } else {
                setError(err.response?.data?.detail || err.message || "An unexpected error occurred. Please try again.");
            }
        } finally {
            setLoading(false);
        }
    };

    if (fetching) {
        return (
            <div className="mx-auto max-w-2xl p-4 text-center text-gray-500 sm:p-8">
                Loading brand details...
            </div>
        );
    }

    return (
        <div className="mx-auto max-w-2xl p-1 sm:p-4 lg:p-8">
            <div className="flex items-center gap-4 mb-8">
                <Link to="/brands" className="text-gray-500 hover:text-gray-800">
                    &larr; Back
                </Link>
                <h1 className="text-3xl font-bold">Edit Brand</h1>
            </div>

            {error && (
                <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-xl border border-red-200">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="bg-white p-6 rounded-2xl border shadow-sm">
                
                {/* Brand Name */}
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
                        ><option value="">Select a niche</option>{formData.niche && !niches.some((niche) => niche.name === formData.niche) && <option value={formData.niche}>{formData.niche} (currently hidden)</option>}{niches.map((niche) => <option key={niche.id} value={niche.name}>{niche.icon} {niche.name}</option>)}</select>
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
                    {formData.logo && (
                        <img src={assetUrl(formData.logo)} alt="Current brand logo" className="mt-3 h-20 w-20 rounded-xl border bg-white object-contain p-1" />
                    )}
                    <div className="my-3 flex items-center gap-3 text-xs text-gray-400"><span className="h-px flex-1 bg-gray-200" />OR<span className="h-px flex-1 bg-gray-200" /></div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Upload a new logo image</label>
                    <input
                        type="file"
                        accept="image/png,image/jpeg,image/webp"
                        onChange={(event) => setLogoFile(event.target.files?.[0] || null)}
                        className="w-full rounded-xl border p-3 text-sm"
                    />
                    <p className="mt-1 text-xs text-gray-500">PNG, JPG, or WebP, maximum 5 MB. The new image replaces the current logo.</p>
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
                        {loading ? "Saving..." : "Save Changes"}
                    </button>
                </div>
            </form>
        </div>
    );
}
