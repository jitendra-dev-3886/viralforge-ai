import { Link } from "react-router-dom";

export default function HistoryPage() {
  return (
    <div className="p-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">History</h1>
          <p className="text-slate-500 mt-2">Review your generated content and publishing history.</p>
        </div>
        <Link
          to="/generate"
          className="inline-flex items-center justify-center rounded-2xl bg-blue-600 px-5 py-3 text-white hover:bg-blue-700"
        >
          Generate New Content
        </Link>
      </div>

      <div className="rounded-3xl border border-dashed border-slate-300 bg-white p-12 text-center">
        <h2 className="text-2xl font-semibold">No history available</h2>
        <p className="text-slate-500 mt-3">Your generated content history will appear here once you create something.</p>
      </div>
    </div>
  );
}
