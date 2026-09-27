export default function StockSourceCredit({ provider }) {
    if (provider === "Openverse") return <a href="https://openverse.org" target="_blank" rel="noreferrer" className="text-xs text-slate-600">Photo via Openverse · CC0</a>;
    if (provider !== "Coverr") return null;
    return <a href="https://coverr.co" target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 text-xs text-slate-600">
        Videos by <img src="https://storage.googleapis.com/coverr-public/logos/logo-dark.svg" alt="Coverr" className="h-5 w-auto" />
    </a>;
}
