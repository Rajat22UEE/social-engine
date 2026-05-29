"use client";

import { useState, useCallback } from "react";

interface Post {
  id: number;
  topic: string;
  headline: string;
  hook: string;
  caption: string;
  cta: string;
  hashtags: string[];
  image_path: string;
  template_id: number;
  liked: boolean;
  favorite: boolean;
  view_count: number;
  created_at: string;
}

interface Stats {
  total_posts: number;
  posts_today: number;
  posts_week: number;
  favorites: number;
  total_views: number;
  top_hashtags: { tag: string; count: number }[];
}

interface HistoryState {
  posts: Post[];
  stats: Stats | null;
  loading: boolean;
  page: number;
  totalPages: number;
  total: number;
}

const API_BASE = "http://127.0.0.1:8000";

export function useHistory() {
  const [state, setState] = useState<HistoryState>({
    posts: [],
    stats: null,
    loading: true,
    page: 1,
    totalPages: 1,
    total: 0,
  });

  const fetchHistory = useCallback(async (page: number = 1) => {
    setState((prev) => ({ ...prev, loading: true }));
    try {
      const res = await fetch(`${API_BASE}/api/v1/history?page=${page}&limit=12`, {
        credentials: "include",
      });
      const data = await res.json();
      if (data.status === "success") {
        setState((prev) => ({
          ...prev,
          posts: data.posts,
          page: data.page,
          totalPages: data.total_pages,
          total: data.total,
          loading: false,
        }));
      } else {
        setState((prev) => ({ ...prev, loading: false }));
      }
    } catch {
      setState((prev) => ({ ...prev, loading: false }));
    }
  }, []);

  const fetchStats = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/stats`, {
        credentials: "include",
      });
      const data = await res.json();
      if (data.status === "success") {
        setState((prev) => ({ ...prev, stats: data.stats }));
      }
    } catch {
      // ignore
    }
  }, []);

  const toggleFavorite = async (postId: number) => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/posts/${postId}/favorite`, {
        method: "POST",
        credentials: "include",
      });
      const data = await res.json();
      if (data.status === "success") {
        setState((prev) => ({
          ...prev,
          posts: prev.posts.map((p) =>
            p.id === postId ? { ...p, favorite: data.favorite } : p
          ),
        }));
        fetchStats();
      }
    } catch {
      // ignore
    }
  };

  const deletePost = async (postId: number) => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/posts/${postId}`, {
        method: "DELETE",
        credentials: "include",
      });
      const data = await res.json();
      if (data.status === "success") {
        setState((prev) => ({
          ...prev,
          posts: prev.posts.filter((p) => p.id !== postId),
          total: prev.total - 1,
        }));
        fetchStats();
      }
    } catch {
      // ignore
    }
  };

  return {
    posts: state.posts,
    stats: state.stats,
    loading: state.loading,
    page: state.page,
    totalPages: state.totalPages,
    total: state.total,
    fetchHistory,
    fetchStats,
    toggleFavorite,
    deletePost,
  };
}