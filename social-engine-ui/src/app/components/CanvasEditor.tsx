"use client";

import { useState, useEffect, useRef, useCallback } from "react";

interface CanvasEditorProps {
  postId: number;
  imagePath: string;
  templateId: number;
  onPreview?: (newImagePath: string) => void;
  onClose?: () => void;
}

interface CanvasEdits {
  headline_x: number | null;
  headline_y: number | null;
  headline_size: number | null;
  headline_color: string | null;
  hook_x: number | null;
  hook_y: number | null;
  hook_size: number | null;
  hook_color: string | null;
  caption_x: number | null;
  caption_y: number | null;
  caption_size: number | null;
}

const API_BASE = "http://127.0.0.1:8000";

export default function CanvasEditor({ postId, imagePath, templateId, onPreview, onClose }: CanvasEditorProps) {
  const [edits, setEdits] = useState<CanvasEdits>({
    headline_x: null, headline_y: null, headline_size: null, headline_color: null,
    hook_x: null, hook_y: null, hook_size: null, hook_color: null,
    caption_x: null, caption_y: null, caption_size: null,
  });
  const [previewImage, setPreviewImage] = useState(imagePath);
  const [saving, setSaving] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [message, setMessage] = useState<{ text: string; type: "success" | "error" } | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [hasEdits, setHasEdits] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  // Load existing edits on mount
  useEffect(() => {
    fetch(`${API_BASE}/api/v1/canvas-edit/${postId}`, { credentials: "include" })
      .then((r) => r.json())
      .then((data) => {
        if (data.edits && Object.keys(data.edits).length > 1) {
          setEdits((prev) => ({ ...prev, ...data.edits }));
          setHasEdits(true);
        }
      })
      .catch(() => {});
  }, [postId]);

  const showMessage = (text: string, type: "success" | "error") => {
    setMessage({ text, type });
    setTimeout(() => setMessage(null), 3000);
  };

  const updateEdit = (key: keyof CanvasEdits, value: number | string | null) => {
    setEdits((prev) => ({ ...prev, [key]: value }));
  };

  const handlePreview = async () => {
    setPreviewLoading(true);
    try {
      const body: Record<string, number | string> = {};
      for (const [key, value] of Object.entries(edits)) {
        if (value !== null) body[key] = value;
      }
      
      const res = await fetch(`${API_BASE}/api/v1/canvas-edit/${postId}/preview`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (data.image_path) {
        setPreviewImage(data.image_path);
        onPreview?.(data.image_path);
        showMessage("Preview updated!", "success");
      } else {
        showMessage("Preview failed", "error");
      }
    } catch {
      showMessage("Preview failed", "error");
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const body: Record<string, number | string> = {};
      for (const [key, value] of Object.entries(edits)) {
        if (value !== null) body[key] = value;
      }
      
      const res = await fetch(`${API_BASE}/api/v1/canvas-edit/${postId}/save`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (data.status === "success") {
        setHasEdits(true);
        showMessage("Canvas edits saved!", "success");
      } else {
        showMessage("Save failed", "error");
      }
    } catch {
      showMessage("Save failed", "error");
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    if (!confirm("Reset to default template positioning?")) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/canvas-edit/${postId}/reset`, {
        method: "DELETE",
        credentials: "include",
      });
      const data = await res.json();
      if (data.status === "success") {
        setEdits({
          headline_x: null, headline_y: null, headline_size: null, headline_color: null,
          hook_x: null, hook_y: null, hook_size: null, hook_color: null,
          caption_x: null, caption_y: null, caption_size: null,
        });
        setPreviewImage(imagePath);
        setHasEdits(false);
        showMessage("Reset to defaults", "success");
      }
    } catch {
      showMessage("Reset failed", "error");
    }
  };

  const hasAnyEdits = Object.values(edits).some((v) => v !== null);

  return (
    <div className="bg-white/5 border border-white/10 rounded-3xl p-6 space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">🎨 Canvas Editor</h2>
        <div className="flex gap-2">
          {hasEdits && <span className="bg-green-600/20 text-green-400 px-2 py-0.5 rounded-full text-xs">Edited</span>}
          {onClose && (
            <button onClick={onClose} className="text-gray-400 hover:text-white text-sm">✕</button>
          )}
        </div>
      </div>

      {message && (
        <div className={`px-4 py-2 rounded-xl text-sm ${
          message.type === "success" ? "bg-green-600/20 text-green-400 border border-green-500/30" : "bg-red-600/20 text-red-400 border border-red-500/30"
        }`}>
          {message.type === "success" ? "✅ " : "❌ "}{message.text}
        </div>
      )}

      {/* Preview Image */}
      <div className="bg-[#1e293b] rounded-xl overflow-hidden border border-white/10">
        <img
          ref={imgRef}
          src={`${API_BASE}/${previewImage}`}
          alt="Canvas preview"
          className="w-full max-h-80 object-contain"
        />
      </div>

      {/* Headline Controls */}
      <div className="space-y-3 p-4 bg-[#1e293b] rounded-xl border border-yellow-500/20">
        <p className="text-sm font-semibold text-yellow-400">📰 Headline</p>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className="text-xs text-gray-500">X Position</label>
            <input
              type="range"
              min="0"
              max="100"
              value={edits.headline_x ?? 64}
              onChange={(e) => updateEdit("headline_x", Number(e.target.value))}
              className="w-full accent-yellow-500"
            />
            <span className="text-xs text-gray-400">{edits.headline_x ?? 64}px</span>
          </div>
          <div>
            <label className="text-xs text-gray-500">Y Position</label>
            <input
              type="range"
              min="0"
              max="600"
              value={edits.headline_y ?? 350}
              onChange={(e) => updateEdit("headline_y", Number(e.target.value))}
              className="w-full accent-yellow-500"
            />
            <span className="text-xs text-gray-400">{edits.headline_y ?? 350}px</span>
          </div>
          <div>
            <label className="text-xs text-gray-500">Font Size</label>
            <input
              type="range"
              min="40"
              max="120"
              value={edits.headline_size ?? 90}
              onChange={(e) => updateEdit("headline_size", Number(e.target.value))}
              className="w-full accent-yellow-500"
            />
            <span className="text-xs text-gray-400">{edits.headline_size ?? 90}px</span>
          </div>
        </div>
      </div>

      {/* Hook Controls */}
      <div className="space-y-3 p-4 bg-[#1e293b] rounded-xl border border-green-500/20">
        <p className="text-sm font-semibold text-green-400">💡 Hook</p>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className="text-xs text-gray-500">X Position</label>
            <input
              type="range"
              min="0"
              max="100"
              value={edits.hook_x ?? 64}
              onChange={(e) => updateEdit("hook_x", Number(e.target.value))}
              className="w-full accent-green-500"
            />
            <span className="text-xs text-gray-400">{edits.hook_x ?? 64}px</span>
          </div>
          <div>
            <label className="text-xs text-gray-500">Y Position</label>
            <input
              type="range"
              min="0"
              max="800"
              value={edits.hook_y ?? 500}
              onChange={(e) => updateEdit("hook_y", Number(e.target.value))}
              className="w-full accent-green-500"
            />
            <span className="text-xs text-gray-400">{edits.hook_y ?? 500}px</span>
          </div>
          <div>
            <label className="text-xs text-gray-500">Font Size</label>
            <input
              type="range"
              min="20"
              max="80"
              value={edits.hook_size ?? 48}
              onChange={(e) => updateEdit("hook_size", Number(e.target.value))}
              className="w-full accent-green-500"
            />
            <span className="text-xs text-gray-400">{edits.hook_size ?? 48}px</span>
          </div>
        </div>
      </div>

      {/* Advanced: Colors */}
      <button
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="text-sm text-gray-400 hover:text-white transition"
      >
        {showAdvanced ? "▼" : "▶"} Advanced: Colors
      </button>
      
      {showAdvanced && (
        <div className="space-y-3 p-4 bg-[#1e293b] rounded-xl border border-white/10">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-gray-500">Headline Color</label>
              <div className="flex items-center gap-2 mt-1">
                <input
                  type="color"
                  value={edits.headline_color || "#FFD700"}
                  onChange={(e) => updateEdit("headline_color", e.target.value)}
                  className="w-10 h-10 rounded-lg cursor-pointer border border-white/10"
                />
                <input
                  value={edits.headline_color || ""}
                  onChange={(e) => updateEdit("headline_color", e.target.value || null)}
                  placeholder="#FFD700"
                  className="flex-1 bg-[#0f172a] p-2 rounded-lg border border-white/10 text-xs outline-none"
                />
              </div>
            </div>
            <div>
              <label className="text-xs text-gray-500">Hook Color</label>
              <div className="flex items-center gap-2 mt-1">
                <input
                  type="color"
                  value={edits.hook_color || "#29BE71"}
                  onChange={(e) => updateEdit("hook_color", e.target.value)}
                  className="w-10 h-10 rounded-lg cursor-pointer border border-white/10"
                />
                <input
                  value={edits.hook_color || ""}
                  onChange={(e) => updateEdit("hook_color", e.target.value || null)}
                  placeholder="#29BE71"
                  className="flex-1 bg-[#0f172a] p-2 rounded-lg border border-white/10 text-xs outline-none"
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={handlePreview}
          disabled={previewLoading || !hasAnyEdits}
          className="flex-1 bg-blue-600 hover:bg-blue-500 py-2.5 rounded-xl font-bold transition disabled:opacity-50"
        >
          {previewLoading ? "Rendering..." : "👁️ Preview"}
        </button>
        <button
          onClick={handleSave}
          disabled={saving || !hasAnyEdits}
          className="flex-1 bg-green-600 hover:bg-green-500 py-2.5 rounded-xl font-bold transition disabled:opacity-50"
        >
          {saving ? "Saving..." : "💾 Save"}
        </button>
        <button
          onClick={handleReset}
          disabled={!hasEdits}
          className="flex-1 bg-red-600/20 hover:bg-red-600/30 text-red-400 py-2.5 rounded-xl font-bold transition disabled:opacity-30 border border-red-500/30"
        >
          ↩ Reset
        </button>
      </div>
    </div>
  );
}