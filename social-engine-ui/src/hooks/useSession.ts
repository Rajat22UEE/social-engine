"use client";

import { useState, useEffect } from "react";

interface SessionData {
  session_id: string;
  created_at: string;
  last_activity: string;
}

export function useSession() {
  const [session, setSession] = useState<SessionData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchSession() {
      try {
        const res = await fetch("http://127.0.0.1:8000/session", {
          credentials: "include", // Include cookies in request
        });
        const data = await res.json();
        if (data.session_id) {
          setSession(data);
          // Also store in localStorage as backup
          localStorage.setItem("session_id", data.session_id);
        }
      } catch (err) {
        console.error("Error fetching session:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchSession();
  }, []);

  const refreshSession = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/session", {
        credentials: "include",
      });
      const data = await res.json();
      if (data.session_id) {
        setSession(data);
        localStorage.setItem("session_id", data.session_id);
      }
    } catch (err) {
      console.error("Error refreshing session:", err);
    }
  };

  return {
    session,
    loading,
    refreshSession,
  };
}
