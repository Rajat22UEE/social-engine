"use client";

import { useState, useEffect } from "react";

const API_BASE = "http://127.0.0.1:8000";

export interface SessionData {
  session_id: string;
  user: {
    id: number;
    session_id: string;
    name: string;
    email: string;
    created_at: string;
  };
}

export function useSession() {
  const [session, setSession] = useState<SessionData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/api/session`, { credentials: "include" })
      .then((r) => r.json())
      .then((data) => {
        if (data.status === "success") {
          setSession(data);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return { session, loading };
}