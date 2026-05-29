"use client";

import { useState, useRef, useEffect } from "react";
import { useBrandKit } from "../../hooks/useBrandKit";

export default function BrandKitManager() {
  const {
    brandKit,
    loading,
    saving,
    error,
    createBrandKit,
    uploadLogo,
    updateColors,
    deleteBrandKit,
  } = useBrandKit();

  const [brandName, setBrandName] = useState("");
  const [primaryColor, setPrimaryColor] = useState("#FFD700");
  const [secondaryColor, setSecondaryColor] = useState("#29BE71");
  const [accentColor, setAccentColor] = useState("#64C8FF");
  const [dragOver, setDragOver] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const hasSynced = useRef(false);

  // Sync state when brandKit loads (only once)
  useEffect(() => {
    if (brandKit && !hasSynced.current) {
      setBrandName(brandKit.brand_name || "");
      setPrimaryColor(brandKit.primary_color || "#FFD700");
      setSecondaryColor(brandKit.secondary_color || "#29BE71");
      setAccentColor(brandKit.accent_color || "#64C8FF");
      hasSynced.current = true;
    }
  }, [brandKit]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (!brandName.trim()) {
      setLocalError("Please enter a brand name");
      return;
    }

    const result = await createBrandKit({
      brand_name: brandName.trim(),
      primary_color: primaryColor,
      secondary_color: secondaryColor,
      accent_color: accentColor,
    });

    if (result) {
      alert("Brand kit saved successfully!");
    }
  };

  const handleLogoUpload = async (file: File) => {
    const validTypes = ["image/png", "image/jpeg", "image/gif", "image/webp"];
    if (!validTypes.includes(file.type)) {
      setLocalError("Please upload a PNG, JPG, GIF, or WebP image");
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setLocalError("Logo must be less than 5MB");
      return;
    }

    setLocalError(null);
    const result = await uploadLogo(file);
    if (!result) {
      setLocalError("Failed to upload logo");
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleLogoUpload(file);
  };

  const handleColorUpdate = async () => {
    setLocalError(null);
    const result = await updateColors({
      primary_color: primaryColor,
      secondary_color: secondaryColor,
      accent_color: accentColor,
    });
    if (result) {
      alert("Colors updated successfully!");
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete your brand kit?")) return;
    setLocalError(null);
    await deleteBrandKit();
    hasSynced.current = false;
    setBrandName("");
    setPrimaryColor("#FFD700");
    setSecondaryColor("#29BE71");
    setAccentColor("#64C8FF");
  };

  if (loading) {
    return (
      <div className="bg-white/5 border border-white/10 rounded-3xl p-8">
        <p className="text-gray-400">Loading brand kit...</p>
      </div>
    );
  }

  const displayError = error || localError;
  const hasBrandKit = !!brandKit;

  return (
    <div className="bg-white/5 border border-white/10 rounded-3xl p-8 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Brand Kit Manager</h2>
        {hasBrandKit && (
          <span className="bg-green-600/20 text-green-400 px-3 py-1 rounded-full text-xs border border-green-500/50">
            Active
          </span>
        )}
      </div>

      {displayError && (
        <div className="bg-red-600/20 text-red-400 p-3 rounded-xl border border-red-500/30 text-sm">
          {displayError}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Brand Name */}
        <div className="space-y-2">
          <label className="text-sm text-gray-400">Brand Name</label>
          <input
            value={brandName}
            onChange={(e) => setBrandName(e.target.value)}
            placeholder="Enter your brand name..."
            className="w-full bg-[#1e293b] p-3 rounded-xl border border-white/10 focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>

        {/* Logo Upload */}
        <div className="space-y-2">
          <label className="text-sm text-gray-400">Brand Logo</label>
          <div
            onDrop={handleDrop}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition ${
              dragOver
                ? "border-blue-500 bg-blue-600/10"
                : "border-white/20 hover:border-white/40 bg-white/5"
            }`}
          >
            {brandKit?.logo_path ? (
              <div className="space-y-2">
                <img
                  src={`http://127.0.0.1:8000/${brandKit.logo_path}`}
                  alt="Brand logo"
                  className="max-h-24 mx-auto rounded-lg"
                />
                <p className="text-xs text-gray-400">{brandKit.logo_filename}</p>
                <p className="text-xs text-blue-400">Click or drag to replace</p>
              </div>
            ) : (
              <div className="text-gray-400">
                <p className="text-lg mb-1">📁</p>
                <p className="text-sm">Drop your logo here or click to browse</p>
                <p className="text-xs mt-1">PNG, JPG, GIF, WebP up to 5MB</p>
              </div>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept=".png,.jpg,.jpeg,.gif,.webp"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleLogoUpload(file);
              }}
            />
          </div>
        </div>

        {/* Color Pickers */}
        <div className="space-y-3">
          <label className="text-sm text-gray-400">Brand Colors</label>
          
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="text-xs text-gray-500">Primary</label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={primaryColor}
                  onChange={(e) => setPrimaryColor(e.target.value)}
                  className="w-10 h-10 rounded-lg cursor-pointer border border-white/10"
                />
                <input
                  value={primaryColor}
                  onChange={(e) => setPrimaryColor(e.target.value)}
                  className="flex-1 bg-[#1e293b] p-2 rounded-lg border border-white/10 text-xs outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="#FFD700"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs text-gray-500">Secondary</label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={secondaryColor}
                  onChange={(e) => setSecondaryColor(e.target.value)}
                  className="w-10 h-10 rounded-lg cursor-pointer border border-white/10"
                />
                <input
                  value={secondaryColor}
                  onChange={(e) => setSecondaryColor(e.target.value)}
                  className="flex-1 bg-[#1e293b] p-2 rounded-lg border border-white/10 text-xs outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="#29BE71"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs text-gray-500">Accent</label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={accentColor}
                  onChange={(e) => setAccentColor(e.target.value)}
                  className="w-10 h-10 rounded-lg cursor-pointer border border-white/10"
                />
                <input
                  value={accentColor}
                  onChange={(e) => setAccentColor(e.target.value)}
                  className="flex-1 bg-[#1e293b] p-2 rounded-lg border border-white/10 text-xs outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="#64C8FF"
                />
              </div>
            </div>
          </div>

          {/* Color Preview */}
          <div className="flex gap-2 p-3 bg-[#1e293b] rounded-xl">
            <div className="flex-1 h-4 rounded" style={{ backgroundColor: primaryColor }}></div>
            <div className="flex-1 h-4 rounded" style={{ backgroundColor: secondaryColor }}></div>
            <div className="flex-1 h-4 rounded" style={{ backgroundColor: accentColor }}></div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            type="submit"
            disabled={saving}
            className="flex-1 bg-blue-600 hover:bg-blue-500 py-3 rounded-xl font-bold transition disabled:opacity-50"
          >
            {saving
              ? "Saving..."
              : hasBrandKit
              ? "Update Brand Kit"
              : "Create Brand Kit"}
          </button>

          {hasBrandKit && (
            <button
              type="button"
              onClick={handleColorUpdate}
              disabled={saving}
              className="bg-green-600 hover:bg-green-500 px-4 py-3 rounded-xl font-bold transition disabled:opacity-50"
              title="Update colors only"
            >
              🎨
            </button>
          )}
        </div>

        {hasBrandKit && (
          <button
            type="button"
            onClick={handleDelete}
            disabled={saving}
            className="w-full bg-red-600/20 hover:bg-red-600/30 text-red-400 py-2 rounded-xl text-sm transition disabled:opacity-50 border border-red-500/30"
          >
            Delete Brand Kit
          </button>
        )}
      </form>
    </div>
  );
}