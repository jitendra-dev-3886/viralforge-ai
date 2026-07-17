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
    <div className="bg-white rounded-3xl shadow-lg p-6 mt-6">

      <h2 className="text-xl font-bold">
        Content Types
      </h2>

      <p className="text-slate-500 mt-1 mb-6">
        Select content types for each platform.
      </p>

      {selectedPlatforms.map((platform) => (

        <div key={platform} className="mb-8">

          <h3 className="font-bold capitalize text-lg mb-4">
            {platform}
          </h3>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">

            {contentMap[platform].map((item) => {

              const key = `${platform}:${item.id}`;

              const active = selectedContent.includes(key);

              return (

                <button
                  key={item.id}
                  type="button"
                  onClick={() => toggleContent(platform, item.id)}
                  className={`
                    p-4
                    rounded-2xl
                    border-2
                    transition

                    ${
                      active
                        ? "border-indigo-600 bg-indigo-50"
                        : "border-slate-200 hover:border-indigo-400"
                    }
                  `}
                >
                  <div className="font-semibold">
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

    </div>
  );
}