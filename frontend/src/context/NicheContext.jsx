import { createContext, useContext, useEffect, useState } from "react";
import { getNiches } from "../api/niche";

const NicheContext = createContext(null);

export function NicheProvider({ children }) {
    const [niches, setNiches] = useState([]);
    const [loading, setLoading] = useState(false);
    const loadNiches = async (includeInactive = false) => {
        setLoading(true);
        try {
            const response = await getNiches(includeInactive);
            setNiches(response.niches || []);
            return response.niches || [];
        } finally {
            setLoading(false);
        }
    };
    useEffect(() => { loadNiches(); }, []);
    return <NicheContext.Provider value={{ niches, loading, loadNiches }}>{children}</NicheContext.Provider>;
}

export const useNiches = () => useContext(NicheContext);
