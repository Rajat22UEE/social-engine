"use client";

import { useState, useEffect } from "react";
import { useSession } from "../hooks/useSession";

const API_BASE = "http://127.0.0.1:8000";

interface Template {
  id: number;
  name: string;
  aspect_ratio: string;
  width: number;
  height: number;
  is_default: boolean;
}

interface Category {
  id: number;
  name: string;
  key: string;
  description: string;
  icon: string;
}

interface GenerateResult {
  post_id: number;
  headline: string;
  hook: string;
  caption: string;
  cta: string;
  hashtags: string[];
  image_path: string;
  aspect_ratio: string;
}

interface AnalyticsData {
  total_posts: number;
  total_drafts: number;
  total_downloads: number;
  generation_count: number;
  template_usage: {
    template_id: number;
    template_name: string;
    count: number;
  }[];
  ratio_usage: { aspect_ratio: string; count: number }[];
}

interface PostItem {
  id: number;
  topic: string;
  headline: string;
  hook: string;
  caption: string;
  cta: string;
  hashtags: string;
  image_path: string;
  template_id: number;
  category: string;
  brand_name: string;
  created_at: string;
  download_count: number;
}

type Step = "topic" | "template" | "category" | "generating" | "result";
type PageView =
  | "dashboard"
  | "create"
  | "templates"
  | "drafts"
  | "history"
  | "analytics";

const NAV_ITEMS: { key: PageView; label: string; icon: string }[] = [
  { key: "dashboard", label: "Dashboard", icon: "🏠" },
  { key: "create", label: "Create Post", icon: "✨" },
  { key: "templates", label: "Templates", icon: "📐" },
  { key: "drafts", label: "Drafts", icon: "📝" },
  { key: "history", label: "History", icon: "📋" },
  { key: "analytics", label: "Analytics", icon: "📊" },
];

export default function Home() {
  const { session, loading: sessionLoading } = useSession();
  const [activeView, setActiveView] = useState<PageView>("dashboard");
  const [step, setStep] = useState<Step>("topic");
  const [templates, setTemplates] = useState<Template[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<number>(1);
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [topic, setTopic] = useState("");
  const [brandName, setBrandName] = useState("");
  const [ctaText, setCtaText] = useState("");
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<GenerateResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [recentPosts, setRecentPosts] = useState<PostItem[]>([]);
  const [recentDrafts, setRecentDrafts] = useState<PostItem[]>([]);

  // ── Load data on mount ────────────────────────────────────────────────────────
  useEffect(() => {
    async function fetchAll() {
      try {
        const [tRes, cRes, aRes, pRes, dRes] = await Promise.all([
          fetch(`${API_BASE}/api/templates`, { credentials: "include" }),
          fetch(`${API_BASE}/api/categories`, { credentials: "include" }),
          fetch(`${API_BASE}/api/analytics`, { credentials: "include" }),
          fetch(`${API_BASE}/api/posts?limit=6`, { credentials: "include" }),
          fetch(`${API_BASE}/api/drafts?limit=6`, { credentials: "include" }),
        ]);
        const tData = await tRes.json();
        const cData = await cRes.json();
        const aData = await aRes.json();
        const pData = await pRes.json();
        const dData = await dRes.json();
        if (tData.status === "success") setTemplates(tData.templates);
        if (cData.status === "success") setCategories(cData.categories);
        if (aData.status === "success") setAnalytics(aData.analytics);
        if (pData.status === "success") setRecentPosts(pData.posts || []);
        if (dData.status === "success") setRecentDrafts(dData.posts || []);
      } catch (e) {
        console.error("Failed to fetch data:", e);
      }
    }
    fetchAll();
  }, []);

  const handleGenerate = async () => {
    if (!topic.trim()) {
      setError("Please enter a topic");
      return;
    }
    setError(null);
    setGenerating(true);
    setResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/generate`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic,
          template_id: selectedTemplate,
          category: selectedCategory || undefined,
          brand_name: brandName || undefined,
          cta_text: ctaText || undefined,
        }),
      });
      if (!res.ok) {
        const errText = await res.text();
        let msg = `Server error (${res.status})`;
        try {
          const j = JSON.parse(errText);
          msg = j.error || j.detail || msg;
        } catch {}
        throw new Error(msg);
      }
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setResult(data);
      setStep("result");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Generation failed");
    } finally {
      setGenerating(false);
    }
  };

  const copyFullPost = () => {
    if (!result) return;
    const text = [result.caption, result.cta, result.hashtags.join(" ")]
      .filter(Boolean)
      .join("\n\n");
    navigator.clipboard.writeText(text);
    alert("Full post copied!");
  };

  const handleSaveDraft = async () => {
    if (!result) return;
    try {
      const res = await fetch(`${API_BASE}/api/drafts`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          template_id: selectedTemplate,
          aspect_ratio: result.aspect_ratio,
          topic,
          headline: result.headline,
          hook: result.hook,
          caption: result.caption,
          cta: result.cta,
          hashtags: JSON.stringify(result.hashtags),
          image_path: result.image_path,
          category: selectedCategory,
          brand_name: brandName,
        }),
      });
      const data = await res.json();
      if (data.status === "success") alert("Draft saved!");
      else throw new Error(data.error || "Failed to save draft");
    } catch (e) {
      console.error(e);
      alert("Failed to save draft");
    }
  };

  const resetCreateFlow = () => {
    setStep("topic");
    setTopic("");
    setBrandName("");
    setCtaText("");
    setSelectedCategory("");
    setResult(null);
    setError(null);
  };

  const startCreate = () => {
    setActiveView("create");
    setStep("topic");
  };

  if (sessionLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-slate-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex">
      <Sidebar
        activeView={activeView}
        setActiveView={setActiveView}
        session={session}
        resetCreateFlow={resetCreateFlow}
      />
      <main className="flex-1 overflow-y-auto px-8 py-8">
        {activeView === "dashboard" ? (
          <DashboardView
            analytics={analytics}
            recentPosts={recentPosts}
            recentDrafts={recentDrafts}
            startCreate={startCreate}
            setActiveView={setActiveView}
            API_BASE={API_BASE}
          />
        ) : activeView === "create" ? (
          <CreatePostView
            step={step}
            setStep={setStep}
            topic={topic}
            setTopic={setTopic}
            brandName={brandName}
            setBrandName={setBrandName}
            ctaText={ctaText}
            setCtaText={setCtaText}
            templates={templates}
            selectedTemplate={selectedTemplate}
            setSelectedTemplate={setSelectedTemplate}
            categories={categories}
            selectedCategory={selectedCategory}
            setSelectedCategory={setSelectedCategory}
            error={error}
            handleGenerate={handleGenerate}
            result={result}
            copyFullPost={copyFullPost}
            handleSaveDraft={handleSaveDraft}
            resetCreateFlow={resetCreateFlow}
            API_BASE={API_BASE}
          />
        ) : activeView === "templates" ? (
          <TemplatesView templates={templates} />
        ) : activeView === "drafts" ? (
          <DraftsView drafts={recentDrafts} />
        ) : activeView === "history" ? (
          <HistoryView posts={recentPosts} API_BASE={API_BASE} />
        ) : activeView === "analytics" ? (
          <AnalyticsView analytics={analytics} />
        ) : null}
      </main>
    </div>
  );
}

// ── Sidebar Component ───────────────────────────────────────────────────────────
function Sidebar({
  activeView,
  setActiveView,
  session,
  resetCreateFlow,
}: {
  activeView: PageView;
  setActiveView: (v: PageView) => void;
  session: { session_id: string } | null;
  resetCreateFlow: () => void;
}) {
  return (
    <aside className="w-56 bg-white border-r border-slate-200 shadow-sm flex flex-col flex-shrink-0">
      <div className="p-4 border-b border-slate-200 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center font-bold text-sm">
          K
        </div>
        <span className="font-bold text-slate-900">Kyma AI</span>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.key}
            onClick={() => {
              setActiveView(item.key);
              if (item.key !== "create") resetCreateFlow();
            }}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
              activeView === item.key
                ? "bg-blue-50 text-blue-700 border border-blue-200"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            <span>{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>
      {session && (
        <div className="p-4 border-t border-slate-200 flex items-center gap-2 text-xs text-slate-500">
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
          {session.session_id.slice(0, 8)}...
        </div>
      )}
    </aside>
  );
}

// ── Dashboard View ──────────────────────────────────────────────────────────────
function DashboardView({
  analytics,
  recentPosts,
  recentDrafts,
  startCreate,
  setActiveView,
  API_BASE,
}: {
  analytics: AnalyticsData | null;
  recentPosts: PostItem[];
  recentDrafts: PostItem[];
  startCreate: () => void;
  setActiveView: (v: PageView) => void;
  API_BASE: string;
}) {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm">
          <p className="text-xs text-blue-600 mb-1">Total Posts</p>
          <p className="text-3xl font-bold text-slate-900">
            {analytics?.total_posts ?? 0}
          </p>
        </div>
        <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm">
          <p className="text-xs text-purple-600 mb-1">Drafts</p>
          <p className="text-3xl font-bold text-slate-900">
            {analytics?.total_drafts ?? 0}
          </p>
        </div>
        <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm">
          <p className="text-xs text-green-600 mb-1">Downloads</p>
          <p className="text-3xl font-bold text-slate-900">
            {analytics?.total_downloads ?? 0}
          </p>
        </div>
        <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm">
          <p className="text-xs text-yellow-600 mb-1">Generations</p>
          <p className="text-3xl font-bold text-slate-900">
            {analytics?.generation_count ?? 0}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          onClick={startCreate}
          className="p-6 bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl text-left text-white hover:from-blue-500 hover:to-blue-600 transition shadow-sm"
        >
          <span className="text-3xl">✨</span>
          <h3 className="font-bold mt-2">Create New Post</h3>
          <p className="text-sm text-blue-100 mt-1">
            Generate AI-powered content in seconds
          </p>
        </button>
        <button
          onClick={() => setActiveView("templates")}
          className="p-6 bg-gradient-to-br from-purple-600 to-purple-700 rounded-2xl text-left text-white hover:from-purple-500 hover:to-purple-600 transition shadow-sm"
        >
          <span className="text-3xl">📐</span>
          <h3 className="font-bold mt-2">Browse Templates</h3>
          <p className="text-sm text-purple-100 mt-1">
            Choose from multiple formats
          </p>
        </button>
        <button
          onClick={() => setActiveView("analytics")}
          className="p-6 bg-gradient-to-br from-green-600 to-green-700 rounded-2xl text-left text-white hover:from-green-500 hover:to-green-600 transition shadow-sm"
        >
          <span className="text-3xl">📊</span>
          <h3 className="font-bold mt-2">View Analytics</h3>
          <p className="text-sm text-green-100 mt-1">
            Track your content performance
          </p>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-4">
          <div className="flex justify-between items-center mb-3">
            <h3 className="font-bold text-slate-900">Recent Posts</h3>
            <button
              onClick={() => setActiveView("history")}
              className="text-xs text-blue-600 hover:text-blue-700"
            >
              View All →
            </button>
          </div>
          {recentPosts.length === 0 ? (
            <p className="text-sm text-slate-500 py-4">
              No posts yet. Create your first one!
            </p>
          ) : (
            <div className="space-y-2">
              {recentPosts.slice(0, 4).map((p) => (
                <div
                  key={p.id}
                  className="flex items-center gap-3 p-2 rounded-lg bg-slate-50 hover:bg-slate-100 transition"
                >
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-slate-600 to-slate-800 flex-shrink-0 overflow-hidden">
                    {p.image_path && (
                      <img
                        src={`${API_BASE}/${p.image_path}`}
                        alt=""
                        className="w-full h-full object-cover"
                      />
                    )}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium truncate">
                      {p.topic || "Untitled"}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(p.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-4">
          <div className="flex justify-between items-center mb-3">
            <h3 className="font-bold text-slate-900">Drafts</h3>
            <button
              onClick={() => setActiveView("drafts")}
              className="text-xs text-purple-600 hover:text-purple-700"
            >
              View All →
            </button>
          </div>
          {recentDrafts.length === 0 ? (
            <p className="text-sm text-slate-500 py-4">No drafts saved.</p>
          ) : (
            <div className="space-y-2">
              {recentDrafts.slice(0, 4).map((p) => (
                <div
                  key={p.id}
                  className="flex items-center gap-3 p-2 rounded-lg bg-slate-50 hover:bg-slate-100 transition"
                >
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-600 to-slate-800 flex-shrink-0 overflow-hidden">
                    {p.image_path && (
                      <img
                        src={`${API_BASE}/${p.image_path}`}
                        alt=""
                        className="w-full h-full object-cover"
                      />
                    )}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium truncate">
                      {p.topic || "Untitled Draft"}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(p.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Templates View ─────────────────────────────────────────────────────────────
function TemplatesView({ templates }: { templates: Template[] }) {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-slate-900">Templates</h1>
        <p className="text-sm text-slate-500">{templates.length} available</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {templates.map((t) => (
          <div
            key={t.id}
            className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm"
          >
            <div
              className="mx-auto mb-4 rounded-lg border-2 border-slate-300 overflow-hidden"
              style={{
                width: (t.width / t.height) * 180,
                height: 180,
                maxWidth: 180,
              }}
            >
              <div
                className="w-full h-full bg-gradient-to-br from-slate-100 to-slate-200"
                style={{ aspectRatio: `${t.width}/${t.height}` }}
              />
            </div>
            <h3 className="font-bold text-slate-900">{t.name}</h3>
            <p className="text-sm text-slate-500 mt-1">
              {t.aspect_ratio} &bull; {t.width}&times;{t.height}px
            </p>
            {t.is_default && (
              <span className="text-xs text-blue-600 mt-2 inline-block">
                Default
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Drafts View ────────────────────────────────────────────────────────────────
function DraftsView({ drafts }: { drafts: PostItem[] }) {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-slate-900">Drafts</h1>
      {drafts.length === 0 ? (
        <div className="text-center py-12 text-slate-500">
          <p className="text-4xl mb-3">📝</p>
          <p>No drafts yet. Generate a post and save it as a draft!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {drafts.map((p) => (
            <div
              key={p.id}
              className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm"
            >
              <p className="font-bold text-slate-900">
                {p.topic || "Untitled Draft"}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                {new Date(p.created_at).toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── History View ──────────────────────────────────────────────────────────────
function HistoryView({
  posts,
  API_BASE,
}: {
  posts: PostItem[];
  API_BASE: string;
}) {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-slate-900">Post History</h1>
      {posts.length === 0 ? (
        <div className="text-center py-12 text-slate-500">
          <p className="text-4xl mb-3">📖</p>
          <p>No posts generated yet. Create your first one!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {posts.map((p) => (
            <div
              key={p.id}
              className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm"
            >
              <div className="w-full h-32 rounded-lg bg-gradient-to-br from-slate-200 to-slate-300 mb-3 overflow-hidden">
                {p.image_path && (
                  <img
                    src={`${API_BASE}/${p.image_path}`}
                    alt=""
                    className="w-full h-full object-cover"
                  />
                )}
              </div>
              <p className="font-bold text-sm text-slate-900">
                {p.topic || "Untitled"}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                {new Date(p.created_at).toLocaleDateString()}
              </p>
              <div className="flex gap-2 mt-2">
                <a
                  href={`${API_BASE}/api/posts/${p.id}/export?format=png`}
                  download
                  target="_blank"
                  className="text-xs px-2 py-1 bg-green-50 text-green-700 rounded-lg border border-green-200"
                >
                  Download
                </a>
                <button
                  onClick={async () => {
                    await fetch(`${API_BASE}/api/posts/${p.id}/duplicate`, {
                      method: "POST",
                      credentials: "include",
                    });
                    alert("Post duplicated!");
                  }}
                  className="text-xs px-2 py-1 bg-blue-50 text-blue-700 rounded-lg border border-blue-200"
                >
                  Duplicate
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Analytics View ─────────────────────────────────────────────────────────────
function AnalyticsView({ analytics }: { analytics: AnalyticsData | null }) {
  const maxTemplate = analytics?.template_usage?.length
    ? Math.max(...analytics.template_usage.map((t) => t.count))
    : 1;
  const maxRatio = analytics?.ratio_usage?.length
    ? Math.max(...analytics.ratio_usage.map((r) => r.count))
    : 1;
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Analytics</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm">
          <p className="text-xs text-blue-600 mb-1">Total Posts</p>
          <p className="text-3xl font-bold text-slate-900">
            {analytics?.total_posts ?? 0}
          </p>
        </div>
        <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm">
          <p className="text-xs text-purple-600 mb-1">Drafts</p>
          <p className="text-3xl font-bold text-slate-900">
            {analytics?.total_drafts ?? 0}
          </p>
        </div>
        <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm">
          <p className="text-xs text-green-600 mb-1">Downloads</p>
          <p className="text-3xl font-bold text-slate-900">
            {analytics?.total_downloads ?? 0}
          </p>
        </div>
        <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm">
          <p className="text-xs text-yellow-600 mb-1">Generations</p>
          <p className="text-3xl font-bold text-slate-900">
            {analytics?.generation_count ?? 0}
          </p>
        </div>
      </div>

      {analytics?.template_usage && analytics.template_usage.length > 0 && (
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
          <h3 className="font-bold mb-3 text-slate-900">Most Used Templates</h3>
          <div className="space-y-2">
            {analytics.template_usage.map((t) => (
              <div key={t.template_id} className="flex items-center gap-3">
                <span className="text-sm w-32 truncate text-slate-700">
                  {t.template_name}
                </span>
                <div className="flex-1 h-4 bg-slate-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 rounded-full"
                    style={{ width: `${(t.count / maxTemplate) * 100}%` }}
                  />
                </div>
                <span className="text-xs text-slate-500">{t.count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {analytics?.ratio_usage && analytics.ratio_usage.length > 0 && (
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
          <h3 className="font-bold mb-3 text-slate-900">Aspect Ratio Usage</h3>
          <div className="space-y-2">
            {analytics.ratio_usage.map((r) => (
              <div key={r.aspect_ratio} className="flex items-center gap-3">
                <span className="text-sm w-24 text-slate-700">
                  {r.aspect_ratio}
                </span>
                <div className="flex-1 h-4 bg-slate-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-500 rounded-full"
                    style={{ width: `${(r.count / maxRatio) * 100}%` }}
                  />
                </div>
                <span className="text-xs text-slate-500">{r.count}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Create Post View ────────────────────────────────────────────────────────────
function CreatePostView({
  step,
  setStep,
  topic,
  setTopic,
  brandName,
  setBrandName,
  ctaText,
  setCtaText,
  templates,
  selectedTemplate,
  setSelectedTemplate,
  categories,
  selectedCategory,
  setSelectedCategory,
  error,
  handleGenerate,
  result,
  copyFullPost,
  handleSaveDraft,
  resetCreateFlow,
  API_BASE,
}: {
  step: Step;
  setStep: (s: Step) => void;
  topic: string;
  setTopic: (s: string) => void;
  brandName: string;
  setBrandName: (s: string) => void;
  ctaText: string;
  setCtaText: (s: string) => void;
  templates: Template[];
  selectedTemplate: number;
  setSelectedTemplate: (n: number) => void;
  categories: Category[];
  selectedCategory: string;
  setSelectedCategory: (s: string) => void;
  error: string | null;
  handleGenerate: () => void;
  result: GenerateResult | null;
  copyFullPost: () => void;
  handleSaveDraft: () => void;
  resetCreateFlow: () => void;
  API_BASE: string;
}) {
  return (
    <div className="space-y-6">
      {error && (
        <div className="p-4 bg-red-50 text-red-800 rounded-xl border border-red-200 text-sm">
          ❌ {error}
        </div>
      )}

      {step === "topic" && (
        <div className="max-w-xl mx-auto space-y-6">
          <div className="text-center space-y-2">
            <h2 className="text-3xl font-bold text-slate-900">
              What do you want to post about?
            </h2>
            <p className="text-slate-600">
              Enter a topic and we'll generate professional Instagram content
              for you.
            </p>
          </div>
          <div className="space-y-4">
            <div>
              <label className="text-sm text-slate-700 mb-2 block">
                Topic *
              </label>
              <input
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && setStep("template")}
                placeholder="e.g., AI automation for small businesses"
                className="w-full bg-white p-4 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 outline-none text-lg text-slate-900"
                autoFocus
              />
            </div>
            <div>
              <label className="text-sm text-slate-700 mb-2 block">
                Brand Name (optional)
              </label>
              <input
                value={brandName}
                onChange={(e) => setBrandName(e.target.value)}
                placeholder="e.g., Your Company"
                className="w-full bg-white p-4 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 outline-none text-slate-900"
              />
            </div>
          </div>
          <button
            onClick={() => setStep("template")}
            disabled={!topic.trim()}
            className="w-full bg-blue-600 hover:bg-blue-500 text-white py-4 rounded-xl font-bold transition disabled:opacity-50 disabled:cursor-not-allowed text-lg"
          >
            Continue →
          </button>
        </div>
      )}

      {step === "template" && (
        <div className="max-w-3xl mx-auto space-y-6">
          <div className="text-center space-y-2">
            <h2 className="text-3xl font-bold text-slate-900">
              Choose Your Format
            </h2>
            <p className="text-slate-600">
              Select the Instagram format for your post.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {templates.map((t) => (
              <button
                key={t.id}
                onClick={() => setSelectedTemplate(t.id)}
                className={`p-6 rounded-2xl border text-left transition-all ${
                  selectedTemplate === t.id
                    ? "border-blue-500 bg-blue-50"
                    : "border-slate-200 bg-white hover:border-blue-300 hover:shadow-md"
                }`}
              >
                <div
                  className="mx-auto mb-4 rounded-lg border-2 border-slate-300 overflow-hidden"
                  style={{
                    width: (t.width / t.height) * 200,
                    height: 200,
                    maxWidth: 200,
                  }}
                >
                  <div
                    className="w-full h-full bg-gradient-to-br from-slate-100 to-slate-200"
                    style={{ aspectRatio: `${t.width}/${t.height}` }}
                  />
                </div>
                <h3 className="text-lg font-bold text-slate-900">{t.name}</h3>
                <p className="text-sm text-slate-600 mt-1">
                  {t.aspect_ratio} &bull; {t.width}&times;{t.height}px
                </p>
              </button>
            ))}
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setStep("topic")}
              className="px-6 py-4 rounded-xl font-bold border border-slate-300 text-slate-900 hover:bg-slate-50 transition"
            >
              &larr; Back
            </button>
            <button
              onClick={() => setStep("category")}
              className="flex-1 bg-blue-600 hover:bg-blue-500 text-white py-4 rounded-xl font-bold transition text-lg"
            >
              Continue &rarr;
            </button>
          </div>
        </div>
      )}

      {step === "category" && (
        <div className="max-w-3xl mx-auto space-y-6">
          <div className="text-center space-y-2">
            <h2 className="text-3xl font-bold text-slate-900">Content Style</h2>
            <p className="text-slate-600">
              Choose a content category and customize your CTA.
            </p>
          </div>
          <div className="space-y-4">
            <div>
              <label className="text-sm text-slate-700 mb-3 block">
                Content Category
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {categories.map((c) => (
                  <button
                    key={c.id}
                    onClick={() => setSelectedCategory(c.key)}
                    className={`p-3 rounded-xl border text-center transition-all ${
                      selectedCategory === c.key
                        ? "border-green-500 bg-green-50"
                        : "border-slate-200 bg-white hover:border-green-300 hover:shadow-md"
                    }`}
                  >
                    <span className="text-2xl">{c.icon}</span>
                    <p className="text-sm font-semibold mt-1 text-slate-900">
                      {c.name}
                    </p>
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="text-sm text-slate-700 mb-2 block">
                Custom CTA (optional)
              </label>
              <input
                value={ctaText}
                onChange={(e) => setCtaText(e.target.value)}
                placeholder="e.g., Sign up for our newsletter"
                className="w-full bg-white p-4 rounded-xl border border-slate-300 focus:ring-2 focus:ring-green-500 outline-none text-slate-900"
              />
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setStep("template")}
              className="px-6 py-4 rounded-xl font-bold border border-slate-300 text-slate-900 hover:bg-slate-50 transition"
            >
              &larr; Back
            </button>
            <button
              onClick={handleGenerate}
              className="flex-1 bg-green-600 hover:bg-green-500 text-white py-4 rounded-xl font-bold transition text-lg"
            >
              🚀 Generate Content
            </button>
          </div>
        </div>
      )}

      {step === "generating" && (
        <div className="max-w-xl mx-auto text-center space-y-6">
          <div className="text-6xl animate-pulse">✨</div>
          <h2 className="text-2xl font-bold text-slate-900">
            Generating your content...
          </h2>
          <p className="text-slate-600">
            Our AI is crafting professional Instagram content for you.
          </p>
          <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-green-500 animate-pulse"
              style={{ width: "60%" }}
            />
          </div>
        </div>
      )}

      {step === "result" && result && (
        <div className="max-w-5xl mx-auto space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-slate-900">
                ✨ Your Content is Ready!
              </h2>
              <p className="text-sm text-slate-600">
                {result.aspect_ratio === "4:5"
                  ? "Instagram Feed"
                  : "Instagram Story"}{" "}
                &bull; {result.aspect_ratio}
              </p>
            </div>
            <button
              onClick={resetCreateFlow}
              className="px-4 py-2 rounded-xl font-bold border border-slate-300 text-slate-900 hover:bg-slate-50 transition text-sm"
            >
              Create New
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
                <img
                  src={`${API_BASE}/${result.image_path}`}
                  alt="Generated post"
                  className="w-full max-h-[500px] object-contain rounded-xl"
                />
                <div className="mt-4 grid grid-cols-2 gap-3">
                  <a
                    href={`${API_BASE}/api/posts/${result.post_id}/export?format=png`}
                    download
                    target="_blank"
                    className="block w-full text-center bg-green-600 hover:bg-green-500 py-3 rounded-xl font-bold transition"
                  >
                    Download PNG
                  </a>
                  <a
                    href={`${API_BASE}/api/posts/${result.post_id}/export?format=jpg`}
                    download
                    target="_blank"
                    className="block w-full text-center bg-blue-600 hover:bg-blue-500 py-3 rounded-xl font-bold transition"
                  >
                    Download JPG
                  </a>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <div className="p-4 bg-yellow-50 rounded-xl border border-yellow-200">
                <p className="text-xs text-yellow-600 mb-1">Headline</p>
                <p className="text-xl font-bold text-yellow-800">
                  {result.headline}
                </p>
              </div>
              <div className="p-4 bg-white rounded-xl border border-slate-200">
                <p className="text-xs text-slate-500 mb-1">Hook</p>
                <p className="text-slate-900">{result.hook}</p>
              </div>
              <div className="p-4 bg-white rounded-xl border border-slate-200">
                <p className="text-xs text-slate-500 mb-1">Caption</p>
                <p className="text-slate-700">{result.caption}</p>
              </div>
              <div className="p-4 bg-blue-50 rounded-xl border border-blue-200">
                <p className="text-xs text-blue-600 mb-1 font-semibold">CTA</p>
                <p className="text-lg font-semibold text-blue-800">
                  {result.cta}
                </p>
              </div>
              <div className="p-4 bg-cyan-50 rounded-xl border border-cyan-200">
                <p className="text-xs text-cyan-600 mb-2 font-semibold">
                  Hashtags
                </p>
                <div className="flex flex-wrap gap-2">
                  {result.hashtags.map((tag: string, i: number) => (
                    <span
                      key={i}
                      className="bg-cyan-100 text-cyan-700 px-3 py-1 rounded-full text-sm border border-cyan-200"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={copyFullPost}
              className="bg-blue-600 hover:bg-blue-500 text-white py-3 rounded-xl font-bold transition"
            >
              Copy Full Post
            </button>
            <button
              onClick={() => {
                navigator.clipboard.writeText(result.hashtags.join(" "));
                alert("Hashtags copied!");
              }}
              className="border border-cyan-200 text-cyan-700 bg-cyan-50 hover:bg-cyan-100 py-3 rounded-xl font-bold transition"
            >
              Copy Hashtags
            </button>
            <button
              onClick={handleSaveDraft}
              className="bg-purple-600 hover:bg-purple-500 text-white py-3 rounded-xl font-bold transition"
            >
              Save as Draft
            </button>
            <a
              href={`${API_BASE}/${result.image_path}`}
              download
              target="_blank"
              className="text-center border border-slate-300 text-slate-900 hover:bg-slate-50 py-3 rounded-xl font-bold transition"
            >
              Direct Download
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
