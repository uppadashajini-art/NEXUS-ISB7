import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import {
  getCurrentSession,
  signInUser,
  signUpUser,
  signOutUser,
  getSupabaseConfig,
  saveSupabaseConfig,
  getSupabase,
  fetchValidationActivities,
} from "../services/supabaseClient";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [supabaseConfig, setSupabaseConfig] = useState(getSupabaseConfig());
  const [activityCount, setActivityCount] = useState(0);

  // Initialize session
  const refreshSession = useCallback(async () => {
    try {
      const sess = await getCurrentSession();
      setUser(sess.user);
      setSession(sess.session);
      if (sess.user) {
        const activities = await fetchValidationActivities(sess.user.id);
        setActivityCount(activities.length);
      } else {
        setActivityCount(0);
      }
    } catch (err) {
      console.warn("Session refresh error:", err);
      setUser(null);
      setSession(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshSession();

    // Listen to Supabase Auth State changes if configured
    const supabase = getSupabase();
    let authListener = null;

    if (supabase) {
      const { data } = supabase.auth.onAuthStateChange(async (_event, newSession) => {
        if (newSession?.user) {
          setUser(newSession.user);
          setSession(newSession);
          const acts = await fetchValidationActivities(newSession.user.id);
          setActivityCount(acts.length);
        } else {
          setUser(null);
          setSession(null);
          setActivityCount(0);
        }
      });
      authListener = data?.subscription;
    }

    return () => {
      if (authListener?.unsubscribe) {
        authListener.unsubscribe();
      }
    };
  }, [refreshSession]);

  const handleSignIn = async (email, password) => {
    const res = await signInUser({ email, password });
    setUser(res.user);
    setSession(res.session);
    const acts = await fetchValidationActivities(res.user.id);
    setActivityCount(acts.length);
    return res;
  };

  const handleSignUp = async (email, password, fullName) => {
    const res = await signUpUser({ email, password, fullName });
    setUser(res.user);
    setSession(res.session);
    return res;
  };

  const handleSignOut = async () => {
    await signOutUser();
    setUser(null);
    setSession(null);
    setActivityCount(0);
  };

  const handleSaveSupabaseConfig = (url, anonKey) => {
    const updated = saveSupabaseConfig(url, anonKey);
    setSupabaseConfig(updated);
    refreshSession();
    return updated;
  };

  const updateActivityCount = (count) => {
    setActivityCount(count);
  };

  const value = {
    user,
    session,
    isAuthenticated: Boolean(user),
    isSupabaseConnected: supabaseConfig.isConfigured,
    supabaseConfig,
    loading,
    activityCount,
    signIn: handleSignIn,
    signUp: handleSignUp,
    signOut: handleSignOut,
    saveConfig: handleSaveSupabaseConfig,
    refreshSession,
    updateActivityCount,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
