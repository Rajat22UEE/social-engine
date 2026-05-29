"use client";

import { useEffect } from "react";
import { useHistory } from "../../hooks/useHistory";

export default function Dashboard() {
  const {
    posts,
    stats,
    loading,
    page,
    totalPages,
    total,
    fetchHistory,
    toggleFavorite,
    deletePost,
  } = useHistory();

  useEffect(() => {
    fetchHistory(1);
  }, [fetchHistory]);

  const handleDelete = async (postId: number, topic: string) => {
    if (!confirm(`Delete post "${topic}"?`)) return;
    await deletePost(postId);
  };

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-5 gap-4">
        <div className="bg-blue-600/20 border border-blue-500/30 rounded-xl p-4">
          <p className="text-xs text-blue-400">Total Posts</p>
          <p className="text-2xl font-bold text-blue-300">{stats?.total_posts || 0}</p>
        </div>
        <div className="bg-green-600/20 border border-green-500/30 rounded-xl p-4">
          <p className="text-xs text-green-400">Today</p>
          <p className="text-2xl font-bold text-green-300">{stats?.posts_today || 0}</p>
        </div>
        <div className="bg-purple-600/20 border border-purple-500/30 rounded-xl p-4">
          <p className="text-xs text-purple-400">This Week</p>
          <p className="text-2xl font-bold text-purple-300">{stats?.posts_week || 0}</p>
        </div>
        <div className="bg-yellow-600/20 border border-yellow-500/30 rounded-xl p-4">
          <p className="text-xs text-yellow-400">Favorites</p>
          <p className="text-2xl font-bold text-yellow-300">{stats?.favorites || 0}</p>
        </div>
        <div className="bg-cyan-600/20 border border-cyan-500/30 rounded-xl p-4">
          <p className="text-xs text-cyan-400">Downloads</p>
          <p className="text-2xl font-bold text-cyan-300">{stats?.total_views || 0}</p>
        </div>
      </div>

      {/* Top Hashtags */}
      {stats?.top_hashtags && stats.top_hashtags.length > 0 && (
        <div className="bg-white/5 border border-white/10 rounded-xl p-4">
          <p className="text-sm text-gray-400 mb-3">Top Hashtags</p>
          <div className="flex flex-wrap gap-2">
            {stats.top_hashtags.map((ht, i) => (
              <span key={i} className="bg-cyan-600/20 text-cyan-300 px-3 py-1 rounded-full text-sm border border-cyan-500/50">
                {ht.tag} <span className="text-xs text-cyan-500">×{ht.count}</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Posts Grid / History */}
      <div className="bg-white/5 border border-white/10 rounded-3xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">
            Post History {total > 0 && <span className="text-sm text-gray-400">({total})</span>}
          </h2>
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-500">Loading history...</div>
        ) : posts.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <p className="text-4xl mb-3">📝</p>
            <p>No posts generated yet</p>
            <p className="text-sm mt-1">Create your first post to see it here!</p>
          </div>
        ) : (
          <>
            {/* Grid */}
            <div className="grid grid-cols-3 gap-4">
              {posts.map((post) => (
                <div
                  key={post.id}
                  className="bg-[#1e293b] rounded-xl border border-white/10 overflow-hidden group hover:border-blue-500/50 transition"
                >
                  {/* Thumbnail */}
                  <div className="aspect-square bg-gray-800 relative overflow-hidden">
                    <img
                      src={`http://127.0.0.1:8000/${post.image_path}`}
                      alt={post.topic}
                      className="w-full h-full object-cover"
                    />
                    
                    {/* Hover overlay */}
                    <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition flex items-center justify-center gap-2">
                      <button
                        onClick={() => toggleFavorite(post.id)}
                        className={`p-2 rounded-lg transition ${
                          post.favorite ? "bg-yellow-500/30 text-yellow-400" : "bg-white/10 text-white hover:bg-yellow-500/30 hover:text-yellow-400"
                        }`}
                        title={post.favorite ? "Remove from favorites" : "Add to favorites"}
                      >
                        {post.favorite ? "★" : "☆"}
                      </button>
                      <a
                        href={`http://127.0.0.1:8000/${post.image_path}`}
                        download
                        target="_blank"
                        className="p-2 rounded-lg bg-white/10 hover:bg-green-500/30 hover:text-green-400 transition"
                        title="Download"
                      >
                        📥
                      </a>
                      <button
                        onClick={() => handleDelete(post.id, post.topic)}
                        className="p-2 rounded-lg bg-white/10 hover:bg-red-500/30 hover:text-red-400 transition"
                        title="Delete"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>

                  {/* Info */}
                  <div className="p-3">
                    <p className="text-xs text-gray-400 mb-1">{post.topic}</p>
                    <p className="text-sm text-white truncate">{post.headline}</p>
                    <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                      <span>👁️ {post.view_count}</span>
                      {post.favorite && <span className="text-yellow-400">★</span>}
                      <span className="ml-auto">
                        {new Date(post.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center items-center gap-2 mt-6">
                <button
                  onClick={() => fetchHistory(page - 1)}
                  disabled={page <= 1}
                  className="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 disabled:opacity-30 text-sm transition"
                >
                  ← Previous
                </button>
                <span className="text-sm text-gray-400">
                  Page {page} of {totalPages}
                </span>
                <button
                  onClick={() => fetchHistory(page + 1)}
                  disabled={page >= totalPages}
                  className="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 disabled:opacity-30 text-sm transition"
                >
                  Next →
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}