export default function Analytics() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Analytics</h1>
        <p className="text-slate-500 mt-2">Monitor performance metrics for your AI content and brand campaigns.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-3xl bg-white p-6 shadow-sm">
          <p className="text-slate-500">Engagement</p>
          <h2 className="mt-3 text-4xl font-bold text-slate-900">1.8K</h2>
          <p className="mt-2 text-sm text-slate-500">Total likes, comments, and shares.</p>
        </div>

        <div className="rounded-3xl bg-white p-6 shadow-sm">
          <p className="text-slate-500">Reach</p>
          <h2 className="mt-3 text-4xl font-bold text-slate-900">72K</h2>
          <p className="mt-2 text-sm text-slate-500">Impressions across all platforms.</p>
        </div>

        <div className="rounded-3xl bg-white p-6 shadow-sm">
          <p className="text-slate-500">Conversions</p>
          <h2 className="mt-3 text-4xl font-bold text-slate-900">245</h2>
          <p className="mt-2 text-sm text-slate-500">Actions taken from your content.</p>
        </div>
      </div>
    </div>
  );
}
