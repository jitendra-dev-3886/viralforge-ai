export default function App() {
  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8">

        <h1 className="text-4xl font-bold text-blue-600 text-center">
          ViralForge AI
        </h1>

        <p className="text-center text-gray-500 mt-2">
          Tailwind CSS Test
        </p>

        <div className="mt-8 space-y-4">

          <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg">
            Primary Button
          </button>

          <button className="w-full bg-green-600 hover:bg-green-700 text-white py-3 rounded-lg">
            Success Button
          </button>

          <button className="w-full bg-red-600 hover:bg-red-700 text-white py-3 rounded-lg">
            Danger Button
          </button>

        </div>

        <div className="grid grid-cols-3 gap-3 mt-8">

          <div className="bg-blue-100 rounded-xl p-4 text-center">
            <p className="text-2xl font-bold">15</p>
            <p className="text-sm">Brands</p>
          </div>

          <div className="bg-green-100 rounded-xl p-4 text-center">
            <p className="text-2xl font-bold">250</p>
            <p className="text-sm">Posts</p>
          </div>

          <div className="bg-purple-100 rounded-xl p-4 text-center">
            <p className="text-2xl font-bold">18K</p>
            <p className="text-sm">Views</p>
          </div>

        </div>

      </div>
    </div>
  );
}