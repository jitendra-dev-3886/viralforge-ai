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
    <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

      <h2 className="text-lg font-semibold text-slate-900">
        1. Choose channels
      </h2>

      <p className="text-slate-500 mt-1 mb-6">
        Choose one or more platforms.
      </p>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">

        {platforms.map((platform) => {

          const Icon = platform.icon;
          const active = selected.includes(platform.id);

          return (

            <button
              key={platform.id}
              type="button"
              onClick={() => togglePlatform(platform.id)}
              className={`
                rounded-xl
                border
                transition-all
                duration-300
                p-4
                text-left
                hover:-translate-y-0.5

                ${
                  active
                    ? "border-blue-600 bg-blue-50 shadow-sm"
                    : "border-slate-200 hover:border-blue-300 bg-white"
                }
              `}
            >

              <div
                className={`
                  w-10
                  h-10
                  rounded-lg
                  bg-gradient-to-r
                  ${platform.color}
                  flex
                  items-center
                  justify-center
                  text-white
                  text-xl
                `}
              >
                <Icon />
              </div>

              <h3 className="mt-3 text-sm font-semibold text-slate-900">
                {platform.name}
              </h3>

              <p className="text-slate-500 text-xs mt-1">
                Generate optimized content
              </p>

              {active && (
                <div className="mt-3">
                  <span className="bg-blue-600 text-white px-2.5 py-1 rounded-full text-xs">
                    Selected
                  </span>
                </div>
              )}

            </button>

          );
        })}

      </div>

    </section>
  );
}
