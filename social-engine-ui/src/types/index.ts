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
export type PageView = "dashboard" | "create";