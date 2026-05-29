"use client";

import { useState, useEffect } from "react";

interface BrandKit {
  id: number;
  brand_name: string;
  logo_path: string | null;
  logo_filename: string | null;
  logo_filesize: number | null;
  primary_color: string;
  secondary_color: string;
  accent_color: string;
  created_at: string;
  updated_at: string;
}

interface BrandKitState {
  brandKit: BrandKit | null;
  loading: boolean;
  saving: boolean;
  error: string | null;
}

export function useBrandKit() {
  const [state, setState] = useState<BrandKitState>({
    brandKit: null,
    loading: true,
    saving: false,
    error: null,
  });

  const API_BASE = "http://127.0.0.1:8000";

  // Fetch brand kit on mount
  useEffect(() => {
    fetchBrandKit();
  }, []);

  const fetchBrandKit = async () => {
    try {
      setState((prev) => ({ ...prev, loading: true, error: null }));
      const res = await fetch(`${API_BASE}/api/v1/brand-kit/get`, {
        credentials: "include",
      });
      const data = await res.json();
      if (data.brand_kit) {
        setState((prev) => ({ ...prev, brandKit: data.brand_kit, loading: false }));
      } else {
        setState((prev) => ({ ...prev, brandKit: null, loading: false }));
      }
    } catch (err) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: "Failed to fetch brand kit",
      }));
    }
  };

  const createBrandKit = async (data: {
    brand_name: string;
    primary_color?: string;
    secondary_color?: string;
    accent_color?: string;
  }) => {
    try {
      setState((prev) => ({ ...prev, saving: true, error: null }));
      const res = await fetch(`${API_BASE}/api/v1/brand-kit/create`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      const result = await res.json();
      if (result.error) throw new Error(result.error);
      setState((prev) => ({
        ...prev,
        brandKit: result.brand_kit,
        saving: false,
      }));
      return result;
    } catch (err) {
      setState((prev) => ({
        ...prev,
        saving: false,
        error: (err as Error).message,
      }));
      return null;
    }
  };

  const uploadLogo = async (file: File) => {
    try {
      setState((prev) => ({ ...prev, saving: true, error: null }));
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API_BASE}/api/v1/brand-kit/upload-logo`, {
        method: "POST",
        credentials: "include",
        body: formData,
      });
      const result = await res.json();
      if (result.error) throw new Error(result.error);
      // Refresh brand kit to get updated state
      await fetchBrandKit();
      setState((prev) => ({ ...prev, saving: false }));
      return result;
    } catch (err) {
      setState((prev) => ({
        ...prev,
        saving: false,
        error: (err as Error).message,
      }));
      return null;
    }
  };

  const updateColors = async (colors: {
    primary_color?: string;
    secondary_color?: string;
    accent_color?: string;
  }) => {
    try {
      setState((prev) => ({ ...prev, saving: true, error: null }));
      const res = await fetch(`${API_BASE}/api/v1/brand-kit/update-colors`, {
        method: "PUT",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(colors),
      });
      const result = await res.json();
      if (result.error) throw new Error(result.error);
      await fetchBrandKit();
      setState((prev) => ({ ...prev, saving: false }));
      return result;
    } catch (err) {
      setState((prev) => ({
        ...prev,
        saving: false,
        error: (err as Error).message,
      }));
      return null;
    }
  };

  const deleteBrandKit = async () => {
    try {
      setState((prev) => ({ ...prev, saving: true, error: null }));
      const res = await fetch(`${API_BASE}/api/v1/brand-kit/delete`, {
        method: "DELETE",
        credentials: "include",
      });
      const result = await res.json();
      if (result.error) throw new Error(result.error);
      setState((prev) => ({
        ...prev,
        brandKit: null,
        saving: false,
      }));
      return result;
    } catch (err) {
      setState((prev) => ({
        ...prev,
        saving: false,
        error: (err as Error).message,
      }));
      return null;
    }
  };

  return {
    brandKit: state.brandKit,
    loading: state.loading,
    saving: state.saving,
    error: state.error,
    createBrandKit,
    uploadLogo,
    updateColors,
    deleteBrandKit,
    refreshBrandKit: fetchBrandKit,
  };
}