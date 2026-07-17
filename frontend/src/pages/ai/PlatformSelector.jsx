import { FaInstagram, FaFacebook, FaYoutube } from "react-icons/fa";

const platforms = [
  {
    id: "instagram",
    name: "Instagram",
    icon: FaInstagram,
    color: "from-pink-500 via-purple-500 to-orange-400",
  },
  {
    id: "facebook",
    name: "Facebook",
    icon: FaFacebook,
    color: "from-blue-600 to-blue-400",
  },
  {
    id: "youtube",
    name: "YouTube",
    icon: FaYoutube,
    color: "from-red-600 to-red-400",
  },
];

export default function PlatformSelector({
  selected,
  onChange,
}) {
  const togglePlatform = (platform) => {
    if (selected.includes(platform)) {
      onChange(selected.filter((p) => p !== platform));
    } else {
      onChange([...selected, platform]);
    }
  };

  return (
    <div className="bg-white rounded-3xl shadow-lg p-6 mt-6">

      <h2 className="text-xl font-bold text-slate-800">
        Select Platform
      </h2>

      <p className="text-slate-500 mt-1 mb-6">
        Choose one or more platforms.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">

        {platforms.map((platform) => {

          const Icon = platform.icon;
          const active = selected.includes(platform.id);

          return (

            <button
              key={platform.id}
              type="button"
              onClick={() => togglePlatform(platform.id)}
              className={`
                rounded-2xl
                border-2
                transition-all
                duration-300
                p-6
                text-left
                hover:scale-105

                ${
                  active
                    ? "border-indigo-600 shadow-xl bg-indigo-50"
                    : "border-slate-200 hover:border-indigo-300 bg-white"
                }
              `}
            >

              <div
                className={`
                  w-14
                  h-14
                  rounded-xl
                  bg-gradient-to-r
                  ${platform.color}
                  flex
                  items-center
                  justify-center
                  text-white
                  text-3xl
                `}
              >
                <Icon />
              </div>

              <h3 className="mt-5 text-lg font-bold">
                {platform.name}
              </h3>

              <p className="text-slate-500 text-sm mt-1">
                Generate optimized content
              </p>

              {active && (
                <div className="mt-5">
                  <span className="bg-indigo-600 text-white px-3 py-1 rounded-full text-xs">
                    Selected
                  </span>
                </div>
              )}

            </button>

          );
        })}

      </div>

    </div>
  );
}