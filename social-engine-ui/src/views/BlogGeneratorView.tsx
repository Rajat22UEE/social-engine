/**
 * views/BlogGeneratorView.tsx - AI SEO Blog Generator wizard.
 *
 * Flow: Input Topic → Generating (8-step progress) → Result (markdown blog)
 */
"use client";
import { useRef } from "react";
import type { BlogResult, BlogStep } from "../types";
import { API_BASE } from "../constants";

interface BlogGeneratorViewProps {
  step: BlogStep;
  setStep: (s: BlogStep) => void;
  topic: string;
  setTopic: (s: string) => void;
  error: string | null;
  handleGenerate: () => void;
  result: BlogResult | null;
  resetBlogFlow: () => void;
  currentStep: number;
}

const STEP_LABELS = [
  "Analyzing Topic",
  "Creating Outline",
  "Writing Content",
  "SEO Optimization",
  "Adding Visuals & Tables",
  "Generating Checklist",
  "Publish & Promote Strategy",
  "Monitor & Update Guidance",
];

const STEP_EMOJIS = ["🔍", "📋", "✍️", "🔧", "🎨", "✅", "📢", "📊"];

export default function BlogGeneratorView({
  step, setStep, topic, setTopic,
  error, handleGenerate, result, resetBlogFlow, currentStep,
}: BlogGeneratorViewProps) {
  const contentRef = useRef<HTMLDivElement>(null);

  const downloadMarkdown = () => {
    if (!result) return;
    window.open(`${API_BASE}/api/blog/${result.id}/download`, "_blank");
  };

  const copyMarkdown = async () => {
    if (!result) return;
    const md = result.content;
    await navigator.clipboard.writeText(md);
    alert("Blog content copied to clipboard!");
  };

  return (
    <div className="space-y-6">
      {/* Error banner */}
      {error && (
        <div className="p-4 bg-red-50 text-red-800 rounded-xl border border-red-200 text-sm">
          ❌ {error}
        </div>
      )}

      {/* ── Step 1: Topic Input ────────────────────────────────────────────── */}
      {step === "input" && (
        <div className="max-w-3xl mx-auto space-y-6">
          <div className="text-center space-y-3">
            <h2 className="text-3xl font-bold text-slate-900">AI SEO Blog Generator</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Enter a blog topic and our AI will generate a complete, SEO-optimized blog post
              following a proven 8-step framework — from keyword research to publish strategy.
            </p>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div>
              <label className="text-sm text-slate-700 mb-2 block font-semibold">
                Blog Topic *
              </label>
              <textarea
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., Top 10 GenAI Tools Every Student Should Learn in 2026"
                className="w-full bg-white p-4 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 outline-none text-lg text-slate-900 min-h-[120px] resize-y"
                autoFocus
              />
              <p className="text-xs text-slate-400 mt-1">
                Be specific with your topic for better results. Include year/numbers for listicles.
              </p>
            </div>

            {/* 8-step preview */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {STEP_LABELS.map((label, i) => (
                <div key={i} className="flex items-center gap-2 p-2 rounded-lg bg-slate-50 border border-slate-100">
                  <span className="text-sm">{STEP_EMOJIS[i]}</span>
                  <span className="text-xs text-slate-600">{label}</span>
                </div>
              ))}
            </div>

            <button
              onClick={handleGenerate}
              disabled={!topic.trim()}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white py-4 rounded-xl font-bold transition disabled:opacity-50 disabled:cursor-not-allowed text-lg"
            >
              🚀 Generate SEO Blog
            </button>
          </div>
        </div>
      )}

      {/* ── Step 2: Generating with 8-step progress ────────────────────────── */}
      {step === "generating" && (
        <div className="max-w-2xl mx-auto text-center space-y-8">
          <div className="text-6xl animate-pulse">{STEP_EMOJIS[currentStep] || "✨"}</div>
          <h2 className="text-2xl font-bold text-slate-900">
            {STEP_LABELS[currentStep] || "Generating your blog..."}
          </h2>
          <p className="text-slate-500">
            Step {currentStep + 1} of 8 — Our AI is crafting an SEO-optimized blog post for you.
          </p>

          {/* Step progress bar */}
          <div className="space-y-3">
            <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-green-500 rounded-full transition-all duration-700"
                style={{ width: `${((currentStep + 1) / 8) * 100}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-slate-400">
              {STEP_LABELS.map((label, i) => (
                <div
                  key={i}
                  className={`text-center transition-colors ${
                    i <= currentStep ? "text-blue-600 font-semibold" : ""
                  }`}
                  style={{ width: "12.5%" }}
                >
                  <span className="block">{STEP_EMOJIS[i]}</span>
                  <span className="hidden sm:block text-[10px] leading-tight mt-1">{label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Step 3: Result Display ─────────────────────────────────────────── */}
      {step === "result" && result && (
        <div className="max-w-5xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h2 className="text-2xl font-bold text-slate-900">📝 Blog Generated!</h2>
              <p className="text-sm text-slate-500">
                ~{result.word_count.toLocaleString()} words &bull; Primary keyword:{" "}
                <span className="font-semibold text-blue-600">{result.primary_keyword}</span>
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={copyMarkdown}
                className="px-4 py-2 rounded-xl font-bold border border-blue-300 text-blue-700 bg-blue-50 hover:bg-blue-100 transition text-sm"
              >
                📋 Copy Markdown
              </button>
              <button
                onClick={downloadMarkdown}
                className="px-4 py-2 rounded-xl font-bold border border-green-300 text-green-700 bg-green-50 hover:bg-green-100 transition text-sm"
              >
                ⬇️ Download .md
              </button>
              <button
                onClick={resetBlogFlow}
                className="px-4 py-2 rounded-xl font-bold border border-slate-300 text-slate-900 hover:bg-slate-50 transition text-sm"
              >
                New Blog
              </button>
            </div>
          </div>

          {/* SEO Metadata Panel */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <h3 className="font-bold text-slate-900 text-sm uppercase tracking-wider">SEO Metadata</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <MetadataField label="Meta Title" value={result.meta_title} note="Max 60 chars" />
              <MetadataField label="Meta Description" value={result.meta_description} note="150-160 chars" />
              <MetadataField label="URL Slug" value={result.url_slug} note="Keyword-rich" />
              <MetadataField label="Primary Keyword" value={result.primary_keyword} note="1-2% density" />
            </div>
            {result.secondary_keywords.length > 0 && (
              <div>
                <p className="text-xs text-slate-500 mb-1 font-semibold">Secondary Keywords</p>
                <div className="flex flex-wrap gap-2">
                  {result.secondary_keywords.map((kw: string, i: number) => (
                    <span key={i} className="bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full text-xs border border-indigo-200">
                      {kw}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Main Blog Content */}
          <div ref={contentRef} className="bg-white p-6 md:p-10 rounded-2xl border border-slate-200 shadow-sm">
            <pre className="whitespace-pre-wrap font-sans text-slate-800 leading-relaxed text-sm">
              {result.content}
            </pre>
          </div>

          {/* SEO Checklist */}
          {result.seo_checklist.length > 0 && (
            <div className="bg-green-50 p-5 rounded-2xl border border-green-200 space-y-2">
              <h3 className="font-bold text-green-800 text-sm uppercase tracking-wider">✅ SEO Checklist</h3>
              <ul className="space-y-1">
                {result.seo_checklist.map((item: string, i: number) => (
                  <li key={i} className="text-green-700 text-sm flex items-start gap-2">
                    <span className="mt-0.5">✅</span>
                    <span>{item.replace(/^✅\s*/, "")}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* FAQ Section */}
          {result.faq_questions.length > 0 && (
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
              <h3 className="font-bold text-slate-900 text-sm uppercase tracking-wider">❓ Frequently Asked Questions</h3>
              {result.faq_questions.map((faq: { question: string; answer: string }, i: number) => (
                <details key={i} className="group border-b border-slate-100 pb-3 last:border-0">
                  <summary className="cursor-pointer text-slate-800 font-semibold text-sm py-2 flex items-center gap-2">
                    <span className="text-blue-500">Q{i + 1}.</span>
                    {faq.question}
                  </summary>
                  <p className="text-slate-600 text-sm pl-8 mt-1">{faq.answer}</p>
                </details>
              ))}
            </div>
          )}

          {/* Internal Links */}
          {result.internal_links.length > 0 && (
            <div className="bg-amber-50 p-5 rounded-2xl border border-amber-200 space-y-2">
              <h3 className="font-bold text-amber-800 text-sm uppercase tracking-wider">🔗 Internal Links to Add</h3>
              <ul className="space-y-1">
                {result.internal_links.map((link: { text: string; url: string }, i: number) => (
                  <li key={i} className="text-amber-700 text-sm">
                    <a href={link.url} target="_blank" rel="noopener noreferrer" className="underline hover:text-amber-900">
                      {link.text}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Bottom Actions */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <button onClick={copyMarkdown} className="bg-blue-600 hover:bg-blue-500 text-white py-3 rounded-xl font-bold transition">
              📋 Copy Markdown
            </button>
            <button onClick={downloadMarkdown} className="bg-green-600 hover:bg-green-500 text-white py-3 rounded-xl font-bold transition">
              ⬇️ Download .md
            </button>
            <button onClick={resetBlogFlow} className="border border-slate-300 text-slate-900 hover:bg-slate-50 py-3 rounded-xl font-bold transition">
              ✏️ New Blog
            </button>
          </div>

          {/* Publish Strategy */}
          <div className="bg-purple-50 p-5 rounded-2xl border border-purple-200 space-y-2">
            <h3 className="font-bold text-purple-800 text-sm uppercase tracking-wider">📢 Publish & Promote</h3>
            <ul className="space-y-1 text-purple-700 text-sm">
              <li>📊 Submit URL to Google Search Console for indexing</li>
              <li>📱 Share on Instagram, LinkedIn, and Twitter</li>
              <li>📧 Send to email subscribers</li>
              <li>🔗 Add links from 2-3 older blog posts to this new post</li>
            </ul>
            <h3 className="font-bold text-purple-800 text-sm uppercase tracking-wider mt-3">📊 Monitor & Update</h3>
            <ul className="space-y-1 text-purple-700 text-sm">
              <li>📈 Track ranking via Google Search Console</li>
              <li>🔄 Refresh pricing/features every 6 months</li>
              <li>📅 Update year in title annually</li>
            </ul>
          </div>

          {/* Company CTA */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-700 p-6 rounded-2xl text-white text-center space-y-3">
            <h3 className="text-xl font-bold">🚀 Join Kyma AI's GenAI Coaching Program</h3>
            <p className="text-blue-100 text-sm max-w-lg mx-auto">
              Master AI tools and future-proof your career with expert coaching from
              Oracle, HCL, and IBM veterans. Based in Agartala, Tripura (Northeast India).
            </p>
            <a
              href="https://kyma-ai.in"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block bg-white text-blue-700 px-6 py-3 rounded-xl font-bold hover:bg-blue-50 transition"
            >
              Learn More →
            </a>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Sub-components ──────────────────────────────────────────────────────────────

function MetadataField({ label, value, note }: { label: string; value: string; note?: string }) {
  return (
    <div>
      <p className="text-xs text-slate-500 mb-1 font-semibold">
        {label} <span className="text-slate-400 font-normal">{note ? `(${note})` : ""}</span>
      </p>
      <p className="text-sm text-slate-800 bg-slate-50 p-2 rounded-lg border border-slate-200 break-all">
        {value || "—"}
      </p>
    </div>
  );
}