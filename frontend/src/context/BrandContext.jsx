import { createContext, useContext, useEffect, useState } from "react";
import { getBrands, createBrand, updateBrand, deleteBrand } from "../api/brand";

const BrandContext = createContext();

export function BrandProvider({ children }) {
    const [brands, setBrands] = useState([]);
    const [loading, setLoading] = useState(false);
    const [selectedBrand, setSelectedBrand] = useState(null);

    const loadBrands = async () => {
        try {
            setLoading(true);
            const response = await getBrands();
            setBrands(response.brands || []);
        } catch (error) {
            console.error("Load Brands Error:", error);
        } finally {
            setLoading(false);
        }
    };

    const addBrand = async (payload) => {
        const response = await createBrand(payload);
        await loadBrands();
        return response;
    };

    const editBrand = async (brandId, payload) => {
        const response = await updateBrand(brandId, payload);
        await loadBrands();
        return response;
    };

    const removeBrand = async (brandId) => {
        const response = await deleteBrand(brandId);
        await loadBrands();
        return response;
    };

    // Load brands on initial mount
    useEffect(() => {
        loadBrands();
    }, []);

    return (
        <BrandContext.Provider
            value={{
                brands,
                loading,
                selectedBrand,
                setSelectedBrand,
                loadBrands,
                addBrand,
                editBrand,
                removeBrand,
            }}
        >
            {children}
        </BrandContext.Provider>
    );
}

export function useBrand() {
    return useContext(BrandContext);
}