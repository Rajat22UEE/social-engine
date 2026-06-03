/**
 * page.tsx - Main application entry point (Home page).
 *
 * Orchestrates the full application:
 * - Manages global state (active view, generation flow)
 * - Routes between views based on activeView
 * - Handles generation and copy actions
 */
"use client";

import { useState } from "react";
import { useSession } from "../hooks/useSession";

import Sidebar from "../layouts/Sidebar";
import DashboardView from "../views/DashboardView";
import CreatePostView from "../views/CreatePostView";

import {
  generatePost,
} from "../lib/api";

import type {
  GenerateResult, CreateStep, PageView,
} from "../types";

export default function Home() {
  const { session, loading: sessionLoading } = useSession();

  // ── UI state ─────────────────────────────────────────────────────────────
  const [activeView, setActiveView] = useState<PageView>("dashboard");
  const [step, setStep] = useState<CreateStep>("topic");

  // ── Generation form state ─────────────────────────────────────────────────
  const [selectedAspect, setSelectedAspect] = useState<"4:5" | "9:16">("4:5");
  const [topic, setTopic] = useState("");
  const [brandName, setBrandName] = useState("");
  const [ctaText, setCtaText] = useState("");
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<GenerateResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // ── Handle content generation ──────────────────────────────────────────────
  const handleGenerate = async () => {
    if (!topic.trim()) {
      setError("Please enter a topic");
      return;
    }
    setError(null);
    setGenerating(true);
    setResult(null);
    setStep("generating");

    try {
      const template_id = selectedAspect === "4:5" ? 1 : 2;
      const data = await generatePost({
        topic,
        template_id,
        category: undefined,
        brand_name: brandName || undefined,
        cta_text: ctaText || undefined,
      });
      setResult(data);
      setStep("result");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Generation failed");
      setStep("topic");
    } finally {
      setGenerating(false);
    }
  };

  // ── Copy full post to clipboard ────────────────────────────────────────────
  const copyFullPost = () => {
    if (!result) return;
    const text = [result.caption, result.cta, result.hashtags.join(" ")]
      .filter(Boolean)
      .join("\n\n");
    navigator.clipboard.writeText(text);
    alert("Full post copied!");
  };

  // ── Reset create flow back to step 1 ──────────────────────────────────────
  const resetCreateFlow = () => {
    setStep("topic");
    setTopic("");
    setBrandName("");
    setCtaText("");
    setSelectedAspect("4:5");
    setResult(null);
    setError(null);
  };

  // ── Navigate to create view ───────────────────────────────────────────────
  const startCreate = () => {
    setActiveView("create");
    setStep("topic");
  };

  // ── Loading state ─────────────────────────────────────────────────────────
  if (sessionLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-slate-500">Loading...</div>
      </div>
    );
  }

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex">
      {/* Sidebar navigation */}
      <Sidebar
        activeView={activeView}
        setActiveView={setActiveView}
        session={session}
        resetCreateFlow={resetCreateFlow}
      />

      {/* Main content area */}
      <main className="flex-1 overflow-y-auto px-8 py-8">
        {activeView === "dashboard" && (
          <DashboardView
            startCreate={startCreate}
          />
        )}

        {activeView === "create" && (
          <CreatePostView
            step={step}
            setStep={setStep}
            topic={topic}
            setTopic={setTopic}
            brandName={brandName}
            setBrandName={setBrandName}
            ctaText={ctaText}
            setCtaText={setCtaText}
            selectedAspect={selectedAspect}
            setSelectedAspect={setSelectedAspect}
            error={error}
            handleGenerate={handleGenerate}
            result={result}
            copyFullPost={copyFullPost}
            resetCreateFlow={resetCreateFlow}
          />
        )}
      </main>
    </div>
  );
}