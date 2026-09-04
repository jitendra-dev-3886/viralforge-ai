import { useEffect } from "react";
import { Link } from "react-router-dom";
import { useBrand } from "../../context/BrandContext";
import { assetUrl } from "../../api/axios";
export default function BrandPage() {
    const { brands, loading, loadBrands, removeBrand } = useBrand();

    useEffect(() => {
        loadBrands();
    }, []);

    const handleDelete = async (id) => {
        if (window.confirm("Are you sure you want to delete this brand?")) {
            await removeBrand(id);
        }
    };

    return (
        <div className="p-1 sm:p-4 lg:p-8">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold">Brand Studio</h1>
                    <p className="text-gray-500 mt-1">Manage your brands for AI content generation.</p>
                </div>
                <Link
                    to="/brands/create"
                    className="px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white transition"
                >
                    + New Brand
                </Link>
            </div>

            {/* Loading State */}
            {loading && (
                <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {[1, 2, 3, 4, 5, 6].map(i => (
                        <div key={i} className="animate-pulse rounded-2xl border p-6 h-48 bg-gray-100" />
                    ))}
                </div>
            )}

            {/* Empty State */}
            {!loading && brands.length === 0 && (
                <div className="rounded-2xl border border-dashed p-20 text-center">
                    <h2 className="text-2xl font-semibold mb-2">No Brands Yet</h2>
                    <p className="text-gray-500">Create your first brand to start generating content.</p>
                </div>
            )}

            {/* Brand Cards Grid */}
            {!loading && brands.length > 0 && (
                <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {brands.map((brand) => (
                        <div key={brand.id} className="rounded-2xl border hover:shadow-xl transition bg-white">
                            <div className="p-6">
                                <div className="flex items-center gap-4">
                                    <img src={assetUrl(brand.logo)} alt="Current brand logo" className="w-14 h-14 rounded-xl" />
                                    <div>
                                        <h2 className="font-semibold text-lg">{brand.name}</h2>
                                        <p className="text-gray-500">{brand.niche || "No niche set"}</p>
                                    </div>
                                </div>
                                <p className="mt-5 text-gray-600 line-clamp-3">
                                    {brand.description || "No description provided."}
                                </p>
                                <div className="mt-6 flex justify-between">
                                    <Link to={`/brands/${brand.id}/edit`} className="text-blue-600">
                                        Edit
                                    </Link>
                                    <button 
                                        onClick={() => handleDelete(brand.id)} 
                                        className="text-red-500"
                                    >
                                        Delete
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
