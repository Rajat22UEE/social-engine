/**
 * views/DashboardView.tsx - Main dashboard overview.
 *
 * Displays quick action buttons to create posts.
 */
"use client";

interface DashboardViewProps {
  startCreate: () => void;
}

export default function DashboardView({
  startCreate,
}: DashboardViewProps) {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>

      {/* ── Quick action buttons ───────────────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ActionButton
          icon="✨" title="Create New Post" desc="Generate AI-powered content in seconds"
          color="from-blue-600 to-blue-700" hoverColor="from-blue-500 to-blue-600"
          onClick={startCreate}
        />
      </div>
    </div>
  );
}

function ActionButton({ icon, title, desc, color, hoverColor, onClick }: {
  icon: string; title: string; desc: string; color: string; hoverColor: string; onClick: () => void;
}) {
  return (
    <button onClick={onClick} className={`p-6 bg-gradient-to-br ${color} rounded-2xl text-left text-white hover:${hoverColor} transition shadow-sm`}>
      <span className="text-3xl">{icon}</span>
      <h3 className="font-bold mt-2">{title}</h3>
      <p className="text-sm text-white/70 mt-1">{desc}</p>
    </button>
  );
}