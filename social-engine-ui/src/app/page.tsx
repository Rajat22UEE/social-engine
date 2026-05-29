"use client";
import { useState, useEffect } from "react";

export default function Home() {
  const [view, setView] = useState("create"); // Default to create
  const [topic, setTopic] = useState("");
  const [templates, setTemplates] = useState<{ id: number; name: string }[]>(
    [],
  );
  const [selectedTemplate, setSelectedTemplate] = useState<number>(1);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{
    headline: string;
    hook: string;
    caption: string;
    cta: string;
    hashtags: string[];
    image_path: string;
  } | null>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/templates")
      .then((res) => res.json())
      .then((data) => setTemplates(data))
      .catch((err) => console.error("Error fetching templates:", err));
  }, []);

  const handleCreate = async () => {
    if (!topic) return alert("Please enter a topic!");
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, template_id: selectedTemplate }),
      });

      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setResult(data);
    } catch (err) {
      alert("Error: " + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    alert(`${label} copied to clipboard!`);
  };

  const copyPostDescription = () => {
    if (!result) return;
    const postText = [result.caption, result.cta, result.hashtags.join(" ")].filter(Boolean).join("\n\n");
    navigator.clipboard.writeText(postText);
    alert("Post description copied to clipboard!");
  };

  return (
    <div className="flex h-screen bg-[#0f172a] text-white">
      {/* Sidebar */}
      <aside className="w-72 bg-white/5 backdrop-blur-xl border-r border-white/10 p-6 flex flex-col">
        <h1 className="text-2xl font-bold tracking-tight mb-10">
          AI Workspace
        </h1>
        <nav className="space-y-3">
          <button
            onClick={() => setView("dashboard")}
            className={`w-full text-left px-4 py-3 rounded-xl transition ${view === "dashboard" ? "bg-blue-600" : "bg-white/5 hover:bg-white/10"}`}
          >
            Dashboard
          </button>
          <button
            onClick={() => setView("create")}
            className={`w-full text-left px-4 py-3 rounded-xl transition ${view === "create" ? "bg-blue-600" : "bg-white/5 hover:bg-white/10"}`}
          >
            Create Post
          </button>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-auto">
        {view === "create" ? (
          <div className="max-w-2xl bg-white/5 border border-white/10 rounded-3xl p-8 space-y-6">
            <h1 className="text-3xl font-bold">Create New Post</h1>

            <div className="space-y-2">
              <label className="text-sm text-gray-400">Select Template</label>
              <select
                className="w-full bg-[#1e293b] p-3 rounded-xl border border-white/10 focus:ring-2 focus:ring-blue-500 outline-none"
                onChange={(e) => setSelectedTemplate(Number(e.target.value))}
              >
                {templates.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name}
                  </option>
                ))}
              </select>
            </div>

            <input
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Enter content topic..."
              className="w-full bg-[#1e293b] p-3 rounded-xl border border-white/10 focus:ring-2 focus:ring-blue-500 outline-none"
            />

            <button
              onClick={handleCreate}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-500 py-3 rounded-xl font-bold transition"
            >
              {loading ? "Generating Assets..." : "Generate Content & Image"}
            </button>

            {result && (
              <div className="border-t border-white/10 pt-6 space-y-6 animate-in fade-in duration-500">
                {/* Image Preview - shown first since it's the main output */}
                <div className="bg-[#1e293b] p-4 rounded-xl border border-white/20">
                  <p className="text-xs text-gray-400 mb-3">Generated Image</p>
                  <p className="text-xs text-green-400 mb-2">
                    ✨ Headline + Hook are rendered on the image
                  </p>
                  <img
                    src={`http://127.0.0.1:8000/${result.image_path}`}
                    alt="Generated post"
                    className="w-full max-h-96 object-cover rounded-lg mb-4"
                  />
                  <a
                    href={`http://127.0.0.1:8000/${result.image_path}`}
                    download
                    target="_blank"
                    className="block w-full text-center bg-green-600 hover:bg-green-500 py-3 rounded-xl font-bold transition"
                  >
                    📥 Download Image
                  </a>
                </div>

                <h3 className="font-semibold text-lg text-gray-200">
                  Generated Content:
                </h3>

                {/* Headline - shown on image */}
                <div className="bg-[#1e293b] p-4 rounded-xl border border-yellow-500/30">
                  <div className="flex justify-between items-center mb-2">
                    <p className="text-xs text-yellow-400">Headline (on image)</p>
                    <button
                      onClick={() => copyToClipboard(result.headline, "Headline")}
                      className="text-xs text-yellow-400 hover:text-yellow-300 px-2 py-1 rounded border border-yellow-500/30 hover:border-yellow-500/50 transition"
                    >
                      📋 Copy
                    </button>
                  </div>
                  <p className="text-xl font-bold text-yellow-300">
                    {result.headline}
                  </p>
                </div>

                {/* Hook - shown on image */}
                <div className="bg-[#1e293b] p-4 rounded-xl border border-white/20">
                  <div className="flex justify-between items-center mb-2">
                    <p className="text-xs text-gray-400">Hook (on image)</p>
                    <button
                      onClick={() => copyToClipboard(result.hook, "Hook")}
                      className="text-xs text-gray-400 hover:text-gray-300 px-2 py-1 rounded border border-white/20 hover:border-white/40 transition"
                    >
                      📋 Copy
                    </button>
                  </div>
                  <p className="text-white">{result.hook}</p>
                </div>

                {/* Caption - for post description */}
                <div className="bg-[#1e293b] p-4 rounded-xl border border-white/20">
                  <div className="flex justify-between items-center mb-2">
                    <p className="text-xs text-gray-400">Caption (for post description)</p>
                    <button
                      onClick={() => copyToClipboard(result.caption, "Caption")}
                      className="text-xs text-gray-400 hover:text-gray-300 px-2 py-1 rounded border border-white/20 hover:border-white/40 transition"
                    >
                      📋 Copy
                    </button>
                  </div>
                  <p className="text-gray-200">{result.caption}</p>
                </div>

                {/* CTA - for post description */}
                <div className="bg-[#1e293b] p-4 rounded-xl border border-blue-500/30">
                  <div className="flex justify-between items-center mb-2">
                    <p className="text-xs text-blue-400">Call-to-Action (for post description)</p>
                    <button
                      onClick={() => copyToClipboard(result.cta, "CTA")}
                      className="text-xs text-blue-400 hover:text-blue-300 px-2 py-1 rounded border border-blue-500/30 hover:border-blue-500/50 transition"
                    >
                      📋 Copy
                    </button>
                  </div>
                  <p className="text-lg font-semibold text-blue-300">
                    {result.cta}
                  </p>
                </div>

                {/* Hashtags - for post description */}
                <div className="bg-[#1e293b] p-4 rounded-xl border border-cyan-500/30">
                  <div className="flex justify-between items-center mb-3">
                    <p className="text-xs text-cyan-400">Hashtags (for post description)</p>
                    <button
                      onClick={() => copyToClipboard(result.hashtags.join(" "), "Hashtags")}
                      className="text-xs text-cyan-400 hover:text-cyan-300 px-2 py-1 rounded border border-cyan-500/30 hover:border-cyan-500/50 transition"
                    >
                      📋 Copy All
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {result.hashtags.map((tag, idx) => (
                      <span
                        key={idx}
                        className="bg-cyan-600/20 text-cyan-300 px-3 py-1 rounded-full text-sm border border-cyan-500/50"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Copy All Post Description */}
                <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 p-4 rounded-xl border border-blue-500/30">
                  <p className="text-xs text-blue-300 mb-3">
                    📝 Copy entire post description (Caption + CTA + Hashtags)
                  </p>
                  <button
                    onClick={copyPostDescription}
                    className="w-full bg-blue-600 hover:bg-blue-500 py-3 rounded-xl font-bold transition flex items-center justify-center gap-2"
                  >
                    📋 Copy Post Description
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center mt-20 text-gray-500">
            Dashboard stats coming soon...
          </div>
        )}
      </main>
    </div>
  );
}