/**
 * types/index.ts - Shared TypeScript interfaces for the entire app.
 */

export interface GenerateResult {
  post_id: number;
  headline: string;
  hook: string;
  caption: string;
  cta: string;
  hashtags: string[];
  image_path: string;
  aspect_ratio: string;
}

export type CreateStep = "topic" | "generating" | "result";
export type PageView = "dashboard" | "create" | "blog";

export interface FAQItem {
  question: string;
  answer: string;
}

export interface InternalLink {
  text: string;
  url: string;
}

export interface BlogResult {
  id: number;
  title: string;
  meta_title: string;
  meta_description: string;
  url_slug: string;
  primary_keyword: string;
  secondary_keywords: string[];
  content: string;
  word_count: number;
  faq_questions: FAQItem[];
  internal_links: InternalLink[];
  seo_checklist: string[];
  created_at?: string;
}

export type BlogStep = "input" | "generating" | "result";
