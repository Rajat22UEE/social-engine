"use client";

import { useState } from "react";

interface ExportButtonsProps {
  postId: number;
  imagePath: string;
  headline: string;
  hook: string;
  caption: string;
  cta: string;
  hashtags: string[];
}

export default function ExportButtons({
  postId,
  imagePath,
  headline,
  hook,
  caption,
  cta,
  hashtags,
}: ExportButtonsProps) {
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const API_BASE = "http://127.0.0.1:8000";

  const showToast = (message: string, type: "success" | "error" = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 2500);
  };

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      showToast(`${label} copied!`);
    } catch {
      showToast("Failed to copy", "error");
    }
  };

  const downloadImage = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/export/download?post_id=${postId}`, {
        credentials: "include",
      });
      if (!res.ok) throw new Error("Download failed");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `post_${postId}.png`;
      a.click();
      URL.revokeObjectURL(url);
      showToast("Image downloaded!");
    } catch {
      // Fallback: direct link
      const link = document.createElement("a");
      link.href = `${API_BASE}/${imagePath}`;
      link.download = `post_${postId}.png`;
      link.target = "_blank";
      link.click();
    }
  };

  const copyPostDescription = async () => {
    const postText = [
      `📌 ${headline}`,
      `💡 ${hook}`,
      ``,
      caption,
      cta,
      hashtags.join(" "),
    ]
      .filter(Boolean)
      .join("\n\n");
    await copyToClipboard(postText, "Full post description");
  };

  const copyCaption = () => copyToClipboard(caption, "Caption");
  const copyCta = () => copyToClipboard(cta, "CTA");
  const copyHashtags = () => copyToClipboard(hashtags.join(" "), "Hashtags");
  const copyHook = () => copyToClipboard(hook, "Hook");
  const copyHeadline = () => copyToClipboard(headline, "Headline");

  return (
    <>
      {/* Toast notification */}
      {toast && (
        <div
          className={`fixed top-6 right-6 z-50 px-5 py-3 rounded-xl shadow-lg transition-all duration-300 animate-in slide-in-from-top-2 ${
            toast.type === "success"
              ? "bg-green-600 text-white"
              : "bg-red-600 text-white"
          }`}
        >
          {toast.type === "success" ? "✅ " : "❌ "}
          {toast.message}
        </div>
      )}

      {/* Download Image Button */}
      <button
        onClick={downloadImage}
        className="block w-full text-center bg-green-600 hover:bg-green-500 py-3 rounded-xl font-bold transition"
      >
        📥 Download Image
      </button>

      {/* Copy all helper buttons */}
      <div className="flex gap-2">
        <button
          onClick={copyHeadline}
          className="flex-1 bg-yellow-600/20 hover:bg-yellow-600/30 text-yellow-300 py-2 rounded-xl text-sm transition border border-yellow-500/30"
          title="Copy headline"
        >
          📋 Headline
        </button>
        <button
          onClick={copyHook}
          className="flex-1 bg-white/5 hover:bg-white/10 text-gray-300 py-2 rounded-xl text-sm transition border border-white/20"
          title="Copy hook"
        >
          📋 Hook
        </button>
        <button
          onClick={copyCaption}
          className="flex-1 bg-white/5 hover:bg-white/10 text-gray-300 py-2 rounded-xl text-sm transition border border-white/20"
          title="Copy caption"
        >
          📋 Caption
        </button>
      </div>

      <div className="flex gap-2">
        <button
          onClick={copyCta}
          className="flex-1 bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 py-2 rounded-xl text-sm transition border border-blue-500/30"
          title="Copy CTA"
        >
          📋 CTA
        </button>
        <button
          onClick={copyHashtags}
          className="flex-1 bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 py-2 rounded-xl text-sm transition border border-cyan-500/30"
          title="Copy hashtags"
        >
          📋 Hashtags
        </button>
        <button
          onClick={copyPostDescription}
          className="flex-1 bg-gradient-to-r from-blue-600/30 to-purple-600/30 hover:from-blue-600/40 hover:to-purple-600/40 text-blue-300 py-2 rounded-xl text-sm transition border border-blue-500/30"
          title="Copy entire post"
        >
          📋 All
        </button>
      </div>
    </>
  );
}