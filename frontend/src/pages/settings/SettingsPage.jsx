export default function SettingsPage() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-slate-500 mt-2">Configure account details, API keys, and workspace preferences.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-3xl bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold">Account</h2>
          <p className="mt-3 text-slate-500">Manage your profile, email, and password settings.</p>
        </div>

        <div className="rounded-3xl bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold">API & Integrations</h2>
          <p className="mt-3 text-slate-500">Connect third-party services and update API credentials.</p>
        </div>
      </div>
    </div>
  );
}
