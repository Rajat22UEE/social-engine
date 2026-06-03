/**
 * views/CreatePostView.tsx - Content generation wizard.
 *
 * Flow: Topic + Aspect → Generating → Result
 * User selects aspect ratio (Feed 4:5 or Story 9:16), enters topic, and generates.
 */
"use client";
import type { GenerateResult, CreateStep } from "../types";
import { API_BASE } from "../constants";

interface CreatePostViewProps {
  step: CreateStep;
  setStep: (s: CreateStep) => void;
  topic: string;
  setTopic: (s: string) => void;
  brandName: string;
  setBrandName: (s: string) => void;
  ctaText: string;
  setCtaText: (s: string) => void;
  selectedAspect: "4:5" | "9:16";
  setSelectedAspect: (a: "4:5" | "9:16") => void;
  error: string | null;
  handleGenerate: () => void;
  result: GenerateResult | null;
  copyFullPost: () => void;
  resetCreateFlow: () => void;
}

export default function CreatePostView({
  step, setStep, topic, setTopic, brandName, setBrandName,
  ctaText, setCtaText, selectedAspect, setSelectedAspect,
  error, handleGenerate, result, copyFullPost, resetCreateFlow,
}: CreatePostViewProps) {
  return (
    <div className="space-y-6">
      {/* Error banner */}
      {error && (
        <div className="p-4 bg-red-50 text-red-800 rounded-xl border border-red-200 text-sm">
          ❌ {error}
        </div>
      )}

      {/* ── Step 1: Topic + Aspect Ratio ──────────────────────────────────── */}
      {step === "topic" && (
        <div className="max-w-xl mx-auto space-y-6">
          <div className="text-center space-y-2">
            <h2 className="text-3xl font-bold text-slate-900">What do you want to post about?</h2>
            <p className="text-slate-600">Enter a topic and we'll generate professional Instagram content for you.</p>
          </div>

          {/* Aspect ratio selector */}
          <div>
            <label className="text-sm text-slate-700 mb-3 block font-semibold">Format</label>
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => setSelectedAspect("4:5")}
                className={`p-4 rounded-2xl border-2 text-center transition-all ${
                  selectedAspect === "4:5"
                    ? "border-blue-500 bg-blue-50"
                    : "border-slate-200 bg-white hover:border-blue-300"
                }`}
              >
                <div className="w-16 h-20 mx-auto mb-2 rounded-lg bg-gradient-to-br from-blue-100 to-blue-200 border border-blue-300" />
                <p className="font-bold text-slate-900">Instagram Feed</p>
                <p className="text-xs text-slate-500">4:5 &bull; 1080x1350</p>
              </button>
              <button
                onClick={() => setSelectedAspect("9:16")}
                className={`p-4 rounded-2xl border-2 text-center transition-all ${
                  selectedAspect === "9:16"
                    ? "border-blue-500 bg-blue-50"
                    : "border-slate-200 bg-white hover:border-blue-300"
                }`}
              >
                <div className="w-16 h-28 mx-auto mb-2 rounded-lg bg-gradient-to-br from-purple-100 to-purple-200 border border-purple-300" />
                <p className="font-bold text-slate-900">Instagram Story</p>
                <p className="text-xs text-slate-500">9:16 &bull; 1080x1920</p>
              </button>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-sm text-slate-700 mb-2 block">Topic *</label>
              <input
                value={topic} onChange={(e) => setTopic(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
                placeholder="e.g., AI automation for small businesses"
                className="w-full bg-white p-4 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 outline-none text-lg text-slate-900"
                autoFocus
              />
            </div>
            <div>
              <label className="text-sm text-slate-700 mb-2 block">Brand Name (optional)</label>
              <input
                value={brandName} onChange={(e) => setBrandName(e.target.value)}
                placeholder="e.g., Your Company"
                className="w-full bg-white p-4 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 outline-none text-slate-900"
              />
            </div>
            <div>
              <label className="text-sm text-slate-700 mb-2 block">CTA Text (optional)</label>
              <input
                value={ctaText} onChange={(e) => setCtaText(e.target.value)}
                placeholder="e.g., Sign up for our newsletter"
                className="w-full bg-white p-4 rounded-xl border border-slate-300 focus:ring-2 focus:ring-green-500 outline-none text-slate-900"
              />
            </div>
          </div>
          <button
            onClick={handleGenerate} disabled={!topic.trim()}
            className="w-full bg-green-600 hover:bg-green-500 text-white py-4 rounded-xl font-bold transition disabled:opacity-50 disabled:cursor-not-allowed text-lg"
          >
            🚀 Generate Content
          </button>
        </div>
      )}

      {/* ── Step 2: Generating ────────────────────────────────────────────── */}
      {step === "generating" && (
        <div className="max-w-xl mx-auto text-center space-y-6">
          <div className="text-6xl animate-pulse">✨</div>
          <h2 className="text-2xl font-bold text-slate-900">Generating your content...</h2>
          <p className="text-slate-600">Our AI is crafting professional Instagram content for you.</p>
          <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
            <div className="h-full bg-gradient-to-r from-blue-500 to-green-500 animate-pulse" style={{ width: "60%" }} />
          </div>
        </div>
      )}

      {/* ── Step 3: Result Display ────────────────────────────────────────── */}
      {step === "result" && result && (
        <div className="max-w-5xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-slate-900">✨ Your Content is Ready!</h2>
              <p className="text-sm text-slate-600">
                {result.aspect_ratio === "4:5" ? "Instagram Feed" : "Instagram Story"} &bull; {result.aspect_ratio}
              </p>
            </div>
            <button onClick={resetCreateFlow} className="px-4 py-2 rounded-xl font-bold border border-slate-300 text-slate-900 hover:bg-slate-50 transition text-sm">Create New</button>
          </div>

          {/* Image + content grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Image preview */}
            <div className="lg:col-span-2">
              <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
                <img src={`${API_BASE}/${result.image_path}`} alt="Generated post" className="w-full max-h-[500px] object-contain rounded-xl" />
                <div className="mt-4 grid grid-cols-2 gap-3">
                  <a href={`${API_BASE}/api/posts/${result.post_id}/export?format=png`} download target="_blank"
                     className="block w-full text-center bg-green-600 hover:bg-green-500 text-white py-3 rounded-xl font-bold transition">Download PNG</a>
                  <a href={`${API_BASE}/api/posts/${result.post_id}/export?format=jpg`} download target="_blank"
                     className="block w-full text-center bg-blue-600 hover:bg-blue-500 text-white py-3 rounded-xl font-bold transition">Download JPG</a>
                </div>
              </div>
            </div>

            {/* Text content sidebar */}
            <div className="space-y-3">
              <ContentBlock label="Headline" color="yellow">{result.headline}</ContentBlock>
              <ContentBlock label="Hook">{result.hook}</ContentBlock>
              <ContentBlock label="Caption" textColor="slate-700">{result.caption}</ContentBlock>
              <ContentBlock label="CTA" color="blue" bold>{result.cta}</ContentBlock>
              <HashtagsBlock hashtags={result.hashtags} />
            </div>
          </div>

          {/* Action buttons */}
          <div className="grid grid-cols-2 gap-3">
            <button onClick={copyFullPost} className="bg-blue-600 hover:bg-blue-500 text-white py-3 rounded-xl font-bold transition">Copy Full Post</button>
            <button onClick={() => { navigator.clipboard.writeText(result.hashtags.join(" ")); alert("Hashtags copied!"); }}
                    className="border border-cyan-200 text-cyan-700 bg-cyan-50 hover:bg-cyan-100 py-3 rounded-xl font-bold transition">Copy Hashtags</button>
            <a href={`${API_BASE}/${result.image_path}`} download target="_blank"
               className="text-center border border-slate-300 text-slate-900 hover:bg-slate-50 py-3 rounded-xl font-bold transition">Direct Download</a>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Sub-components ──────────────────────────────────────────────────────────────

function ContentBlock({ label, children, color, textColor, bold }: {
  label: string; children: string; color?: string; textColor?: string; bold?: boolean;
}) {
  const borderMap: Record<string, string> = { yellow: "border-yellow-200", blue: "border-blue-200" };
  const bgMap: Record<string, string> = { yellow: "bg-yellow-50", blue: "bg-blue-50" };
  const labelColorMap: Record<string, string> = { yellow: "text-yellow-600", blue: "text-blue-600" };
  const border = borderMap[color || ""] || "border-slate-200";
  const bg = bgMap[color || ""] || "bg-white";
  const labelColor = labelColorMap[color || ""] || "text-slate-500";
  return (
    <div className={`p-4 ${bg} rounded-xl border ${border}`}>
      <p className={`text-xs ${labelColor} mb-1`}>{label}</p>
      <p className={`${bold ? "text-lg font-semibold" : ""} ${textColor || "text-slate-900"}`}>{children}</p>
    </div>
  );
}

function HashtagsBlock({ hashtags }: { hashtags: string[] }) {
  return (
    <div className="p-4 bg-cyan-50 rounded-xl border border-cyan-200">
      <p className="text-xs text-cyan-600 mb-2 font-semibold">Hashtags</p>
      <div className="flex flex-wrap gap-2">
        {hashtags.map((tag, i) => (
          <span key={i} className="bg-cyan-100 text-cyan-700 px-3 py-1 rounded-full text-sm border border-cyan-200">{tag}</span>
        ))}
      </div>
    </div>
  );
}