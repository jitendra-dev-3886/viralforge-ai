const contentMap = {
  instagram: [
    { id: "reel", name: "Reel" },
    { id: "carousel", name: "Carousel" },
    { id: "story", name: "Story" },
    { id: "post", name: "Post" },
    { id: "quote", name: "Quote" },
  ],

  facebook: [
    { id: "reel", name: "Reel" },
    { id: "carousel", name: "Carousel" },
    { id: "story", name: "Story" },
    { id: "post", name: "Post" },
    { id: "quote", name: "Quote" },
  ],

  youtube: [
    { id: "shorts", name: "Shorts" },
    { id: "video", name: "Long Video" },
    { id: "community", name: "Community Post" },
  ],
};

export default function ContentTypeSelector({
  selectedPlatforms,
  selectedContent,
  onChange,
}) {

  const toggleContent = (platform, type) => {

    const key = `${platform}:${type}`;

    if (selectedContent.includes(key)) {
      onChange(selectedContent.filter((item) => item !== key));
    } else {
      onChange([...selectedContent, key]);
    }
  };

  if (selectedPlatforms.length === 0) return null;

  return (
    <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

      <h2 className="text-lg font-semibold text-slate-900">
        2. Choose formats
      </h2>

      <p className="text-slate-500 mt-1 mb-6">
        Select content types for each platform.
      </p>

      {selectedPlatforms.map((platform) => (

        <div key={platform} className="mb-5 last:mb-0">

          <h3 className="mb-3 text-sm font-semibold capitalize text-slate-700">
            {platform}
          </h3>

          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-5">

            {contentMap[platform].map((item) => {

              const key = `${platform}:${item.id}`;

              const active = selectedContent.includes(key);

              return (

                <button
                  key={item.id}
                  type="button"
                  onClick={() => toggleContent(platform, item.id)}
                  className={`
                    p-3
                    rounded-xl
                    border
                    transition

                    ${
                      active
                        ? "border-blue-600 bg-blue-50 text-blue-900"
                        : "border-slate-200 hover:border-indigo-400"
                    }
                  `}
                >
                  <div className="text-sm font-medium">
                    {item.name}
                  </div>

                  {active && (
                    <div className="text-xs text-indigo-600 mt-2">
                      Selected
                    </div>
                  )}
                </button>

              );
            })}

          </div>

        </div>

      ))}

    </section>
  );
}
