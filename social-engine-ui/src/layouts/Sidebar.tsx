/**
 * layouts/Sidebar.tsx - Sidebar navigation component.
 *
 * Renders the navigation menu with all available views.
 * Highlights the currently active view.
 */
"use client";
import { NAV_ITEMS } from "../constants";
import type { PageView } from "../types";

interface SidebarProps {
  activeView: PageView;
  setActiveView: (v: PageView) => void;
  session: { session_id: string } | null;
  resetCreateFlow: () => void;
}

export default function Sidebar({ activeView, setActiveView, session, resetCreateFlow }: SidebarProps) {
  return (
    <aside className="w-56 bg-white border-r border-slate-200 shadow-sm flex flex-col flex-shrink-0">
      {/* Brand header */}
      <div className="p-4 border-b border-slate-200 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center font-bold text-sm text-white">
          K
        </div>
        <span className="font-bold text-slate-900">Kyma AI</span>
      </div>

      {/* Navigation links */}
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

      {/* Session indicator */}
      {session && (
        <div className="p-4 border-t border-slate-200 flex items-center gap-2 text-xs text-slate-500">
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
          {session.session_id.slice(0, 8)}...
        </div>
      )}
    </aside>
  );
}