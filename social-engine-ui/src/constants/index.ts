/**
 * constants/index.ts - Application-wide constants and configuration.
 */
import type { PageView } from "../types";

/** Backend API base URL */
export const API_BASE = "http://127.0.0.1:8000";

/** Sidebar navigation items definition */
export const NAV_ITEMS: { key: PageView; label: string; icon: string }[] = [
  { key: "dashboard", label: "Dashboard", icon: "🏠" },
  { key: "blog", label: "Blog Generator", icon: "📝" },
  { key: "create", label: "Create Post", icon: "✨" },
];
