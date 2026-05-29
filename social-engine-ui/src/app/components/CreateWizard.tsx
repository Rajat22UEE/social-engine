"use client";

import { useState, useEffect } from "react";

interface Platform {
  id: number; name: string; key: string; description: string;
  icon: string; max_headline_chars: number; max_hook_chars: number; text_density: string;
}
interface Goal {
  id: number; name: string; key: string; description: string;
  template_style: string; default_cta_style: string;
}
interface Template { id: number; name: string; frame_size: string; }

const API_BASE = "http://127.0.0.1:8000";

export default function CreateWizard() {
  const [step, setStep] = useState(1);
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedPlatform, setSelectedPlatform] = useState<Platform | null>(null);
  const [selectedGoal, setSelectedGoal] = useState<Goal | null>(null);
  const [topic, setTopic] = useState("");
  const [industry, setIndustry] = useState("");
  const [audience, setAudience] = useState("");
  const [tone, setTone] = useState("professional");
  const [ctaText, setCtaText] = useState("");
  const [selectedTemplate, setSelectedTemplate] = useState<number>(1);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  interface GenerateResult {
    status: string; post_id: number; platform: string; goal: string;
    headline: string; subheading?: string; hook: string; caption: string;
    cta: string; hashtags: string[]; content_angle: string;
    image_path: string; branded: boolean; design_rules: Record<string, string>;
  }
  const [result, setResult] = useState<GenerateResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const [pRes, gRes, tRes] = await Promise.all([
          fetch(`${API_BASE}/api/v1/platforms`, { credentials: "include" }),
          fetch(`${API_BASE}/api/v1/goals`, { credentials: "include" }),
          fetch(`${API_BASE}/api/v1/templates`, { credentials: "include" }),
        ]);
        const pD = await pRes.json(); const gD = await gRes.json(); const tD = await tRes.json();
        if (pD.status === "success") setPlatforms(pD.platforms);
        if (gD.status === "success") setGoals(gD.goals);
        if (tD.status === "success") setTemplates(tD.templates);
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    }
    fetchData();
  }, []);

  const handleGenerate = async () => {
    if (!topic.trim()) { setError("Please enter a topic"); return; }
    setError(null); setGenerating(true); setResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/generate-v2`, {
        method: "POST", credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          platform_id: selectedPlatform!.id, goal_id: selectedGoal!.id,
          topic, industry: industry || null, target_audience: audience || null,
          tone, cta_text: ctaText || null, template_id: selectedTemplate,
        }),
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setResult(data);
      setStep(5);
    } catch (e: unknown) { setError(e instanceof Error ? e.message : "Generation failed"); }
    finally { setGenerating(false); }
  };

  if (loading) return <div className="p-8 text-center text-gray-400">Loading...</div>;

  return (
    <div className="bg-white/5 border border-white/10 rounded-3xl p-8">
      {/* Step Indicator */}
      <div className="flex items-center gap-2 mb-8">
        {[1,2,3,4].map((s) => (
          <div key={s} className="flex items-center gap-2 flex-1 last:flex-none">
            <div className={`flex items-center gap-2 ${step >= s ? "text-blue-400" : "text-gray-600"}`}>
              <span className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${step >= s ? "bg-blue-600" : "bg-gray-700"}`}>{s}</span>
              <span className="text-sm hidden md:inline">{["Platform","Goal","Content","Generate"][s-1]}</span>
            </div>
            {s < 4 && <div className="flex-1 h-px bg-gray-700" />}
          </div>
        ))}
      </div>

      {error && <div className="mb-4 p-3 bg-red-600/20 text-red-400 rounded-xl border border-red-500/30 text-sm">{error}</div>}

      {/* Step 1: Platform */}
      {step === 1 && (
        <div className="space-y-6">
          <h2 className="text-2xl font-bold">Choose Platform</h2>
          <p className="text-gray-400 text-sm">Select where you want to post</p>
          <div className="grid grid-cols-2 gap-4">
            {platforms.map((p) => (
              <button key={p.id} onClick={() => { setSelectedPlatform(p); setStep(2); }}
                className="text-left p-5 rounded-2xl border border-white/10 bg-white/5 hover:border-blue-400/50 hover:bg-blue-600/5 transition-all"
              >
                <div className="text-3xl mb-3">{p.icon}</div>
                <h3 className="text-lg font-bold mb-1">{p.name}</h3>
                <p className="text-sm text-gray-400">{p.description}</p>
                <div className="flex gap-2 mt-3 text-xs text-gray-500">
                  <span className="bg-white/10 px-2 py-1 rounded">Max {p.max_headline_chars} chars</span>
                  <span className="bg-white/10 px-2 py-1 rounded capitalize">{p.text_density}</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Step 2: Goal */}
      {step === 2 && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">Choose Goal</h2>
              <p className="text-gray-400 text-sm">For {selectedPlatform?.icon} {selectedPlatform?.name}</p>
            </div>
            <button onClick={() => setStep(1)} className="text-sm text-gray-400 hover:text-white px-3 py-1.5 rounded-lg border border-white/10">← Back</button>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {goals.map((g) => (
              <button key={g.id} onClick={() => { setSelectedGoal(g); setStep(3); }}
                className="text-left p-5 rounded-2xl border border-white/10 bg-white/5 hover:border-green-400/50 transition-all"
              >
                <h3 className="text-lg font-bold mb-1">{g.name}</h3>
                <p className="text-sm text-gray-400 mb-3">{g.description}</p>
                <div className="flex gap-2 text-xs">
                  <span className="bg-purple-600/20 text-purple-300 px-2 py-1 rounded capitalize">{g.template_style?.replace("-"," ")}</span>
                  <span className="bg-blue-600/20 text-blue-300 px-2 py-1 rounded capitalize">CTA: {g.default_cta_style?.replace("-"," ")}</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Step 3: Business Info */}
      {step === 3 && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">Content Details</h2>
              <p className="text-gray-400 text-sm">{selectedPlatform?.icon} {selectedPlatform?.name} · {selectedGoal?.name}</p>
            </div>
            <button onClick={() => setStep(2)} className="text-sm text-gray-400 hover:text-white px-3 py-1.5 rounded-lg border border-white/10">← Back</button>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="text-sm text-gray-400 mb-1 block">Topic *</label>
              <input value={topic} onChange={e => setTopic(e.target.value)}
                placeholder="e.g., AI automation for small businesses"
                className="w-full bg-[#1e293b] p-3 rounded-xl border border-white/10 focus:ring-2 focus:ring-blue-500 outline-none"
              />
              {selectedPlatform && <p className="text-xs text-gray-500 mt-1">Max {selectedPlatform.max_headline_chars} chars for headline</p>}
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-gray-400 mb-1 block">Industry (optional)</label>
                <input value={industry} onChange={e => setIndustry(e.target.value)}
                  placeholder="e.g., Marketing, SaaS, Food"
                  className="w-full bg-[#1e293b] p-3 rounded-xl border border-white/10 focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>
              <div>
                <label className="text-sm text-gray-400 mb-1 block">Target Audience (optional)</label>
                <input value={audience} onChange={e => setAudience(e.target.value)}
                  placeholder="e.g., SMB owners, marketers"
                  className="w-full bg-[#1e293b] p-3 rounded-xl border border-white/10 focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-gray-400 mb-1 block">Tone</label>
                <select value={tone} onChange={e => setTone(e.target.value)}
                  className="w-full bg-[#1e293b] p-3 rounded-xl border border-white/10 focus:ring-2 focus:ring-blue-500 outline-none"
                >
                  <option value="professional">Professional</option>
                  <option value="casual">Casual</option>
                  <option value="humorous">Humorous</option>
                  <option value="inspirational">Inspirational</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
              <div>
                <label className="text-sm text-gray-400 mb-1 block">Custom CTA (optional)</label>
                <input value={ctaText} onChange={e => setCtaText(e.target.value)}
                  placeholder="e.g., Comment below"
                  className="w-full bg-[#1e293b] p-3 rounded-xl border border-white/10 focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>
            </div>
          </div>

          <button onClick={() => setStep(4)}
            className="w-full bg-blue-600 hover:bg-blue-500 py-3 rounded-xl font-bold transition">
            Continue to Template →
          </button>
        </div>
      )}

      {/* Step 4: Template + Generate */}
      {step === 4 && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">Choose Template</h2>
              <p className="text-gray-400 text-sm">{selectedPlatform?.icon} {selectedPlatform?.name} · {selectedGoal?.name} · {topic}</p>
            </div>
            <button onClick={() => setStep(3)} className="text-sm text-gray-400 hover:text-white px-3 py-1.5 rounded-lg border border-white/10">← Back</button>
          </div>

          <div className="grid grid-cols-3 gap-3">
            {templates.map((t) => (
              <button key={t.id} onClick={() => setSelectedTemplate(t.id)}
                className={`p-4 rounded-xl border text-left transition-all ${
                  selectedTemplate === t.id
                    ? "border-blue-500 bg-blue-600/10"
                    : "border-white/10 bg-white/5 hover:border-blue-400/30"
                }`}
              >
                <p className="text-sm font-bold">{t.name}</p>
                <p className="text-xs text-gray-500 mt-1">{t.frame_size}</p>
              </button>
            ))}
          </div>

          <button onClick={handleGenerate} disabled={generating || !topic.trim()}
            className="w-full bg-green-600 hover:bg-green-500 py-3 rounded-xl font-bold transition disabled:opacity-50">
            {generating ? "✨ Generating..." : "🚀 Generate Content & Image"}
          </button>
        </div>
      )}

      {/* Step 5: Result */}
      {step === 5 && result && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">✨ Generated Post</h2>
              <p className="text-sm text-gray-400">{result.platform} · {result.goal} · Angle: {result.content_angle}</p>
            </div>
            <button onClick={() => { setStep(1); setResult(null); setSelectedPlatform(null); setSelectedGoal(null); setTopic(""); }}
              className="text-sm text-gray-400 hover:text-white px-3 py-1.5 rounded-lg border border-white/10">Create New</button>
          </div>

          {/* Image */}
          <div className="bg-[#1e293b] p-4 rounded-xl border border-white/20">
            <img src={`${API_BASE}/${result.image_path}`} alt="Generated" className="w-full max-h-80 object-contain rounded-lg mb-4" />
            <a href={`${API_BASE}/${result.image_path}`} download target="_blank"
              className="block w-full text-center bg-green-600 hover:bg-green-500 py-2.5 rounded-xl font-bold transition">📥 Download</a>
          </div>

          {/* Content */}
          <div className="space-y-3">
            <div className="p-4 bg-[#1e293b] rounded-xl border border-yellow-500/30">
              <p className="text-xs text-yellow-400 mb-1">Headline</p>
              <p className="text-xl font-bold text-yellow-300">{result.headline}</p>
            </div>
            {result.subheading && (
              <div className="p-4 bg-[#1e293b] rounded-xl border border-white/20">
                <p className="text-xs text-gray-400 mb-1">Subheading</p>
                <p className="text-white">{result.subheading}</p>
              </div>
            )}
            <div className="p-4 bg-[#1e293b] rounded-xl border border-white/20">
              <p className="text-xs text-gray-400 mb-1">Hook</p>
              <p className="text-white">{result.hook}</p>
            </div>
            <div className="p-4 bg-[#1e293b] rounded-xl border border-white/20">
              <p className="text-xs text-gray-400 mb-1">Caption</p>
              <p className="text-gray-200">{result.caption}</p>
            </div>
            <div className="p-4 bg-[#1e293b] rounded-xl border border-blue-500/30">
              <p className="text-xs text-blue-400 mb-1">CTA</p>
              <p className="text-lg font-semibold text-blue-300">{result.cta}</p>
            </div>
            <div className="p-4 bg-[#1e293b] rounded-xl border border-cyan-500/30">
              <p className="text-xs text-cyan-400 mb-2">Hashtags</p>
              <div className="flex flex-wrap gap-2">
                {result.hashtags?.map((tag: string, i: number) => (
                  <span key={i} className="bg-cyan-600/20 text-cyan-300 px-3 py-1 rounded-full text-sm border border-cyan-500/50">{tag}</span>
                ))}
              </div>
            </div>
          </div>

          <button onClick={() => { navigator.clipboard.writeText([result.caption, result.cta, result.hashtags?.join(" ")].filter(Boolean).join("\n\n")); }}
            className="w-full bg-blue-600 hover:bg-blue-500 py-2.5 rounded-xl font-bold transition">📋 Copy Post Description</button>
        </div>
      )}
    </div>
  );
}