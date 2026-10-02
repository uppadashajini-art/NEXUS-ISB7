import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { CloseIcon, UserIcon, ShieldIcon, CheckIcon } from "./Icons";

export function AuthModal({ isOpen, onClose }) {
  const { signIn, signUp, isSupabaseConnected } = useAuth();

  const [mode, setMode] = useState("signin"); // "signin" | "signup"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccessMsg("");
    setLoading(true);

    try {
      if (mode === "signin") {
        await signIn(email, password);
        onClose();
      } else {
        await signUp(email, password, fullName);
        setSuccessMsg("Account created successfully! You are now logged in.");
        setTimeout(() => {
          onClose();
        }, 1200);
      }
    } catch (err) {
      console.error("Auth error:", err);
      setError(err.message || "Authentication failed. Please verify your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="nexus-modal-overlay" onClick={onClose}>
      <div
        className="nexus-modal-card auth-modal-card"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="modal-header">
          <div className="modal-header-icon-badge">
            <UserIcon size={20} />
          </div>
          <div className="modal-header-info">
            <h3 className="modal-title">
              {mode === "signin" ? "Sign In to NEXUS" : "Create Founder Account"}
            </h3>
            <p className="modal-subtitle">
              {isSupabaseConnected
                ? "Connected directly to Supabase Cloud Authentication"
                : "Active user session for database history saving"}
            </p>
          </div>
          <button
            type="button"
            className="modal-close-btn"
            onClick={onClose}
          >
            <CloseIcon size={18} />
          </button>
        </div>

        {/* Auth Mode Toggle Tabs */}
        <div className="auth-tab-switch">
          <button
            type="button"
            className={`auth-tab-btn ${mode === "signin" ? "active" : ""}`}
            onClick={() => {
              setMode("signin");
              setError("");
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            className={`auth-tab-btn ${mode === "signup" ? "active" : ""}`}
            onClick={() => {
              setMode("signup");
              setError("");
            }}
          >
            Create Account
          </button>
        </div>

        {/* Feedback Alerts */}
        {error && (
          <div className="modal-alert error">
            <span>!</span>
            <p>{error}</p>
          </div>
        )}

        {successMsg && (
          <div className="modal-alert success">
            <CheckIcon size={16} />
            <p>{successMsg}</p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="auth-form">
          {mode === "signup" && (
            <div className="input-group">
              <label htmlFor="auth-fullname">Full Name / Founder Handle</label>
              <input
                id="auth-fullname"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="e.g. John Doe"
                required
                disabled={loading}
              />
            </div>
          )}

          <div className="input-group">
            <label htmlFor="auth-email">Email Address</label>
            <input
              id="auth-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="founder@nexus-spring.io"
              required
              disabled={loading}
            />
          </div>

          <div className="input-group">
            <label htmlFor="auth-password">Password</label>
            <input
              id="auth-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              required
              minLength={6}
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            className="auth-submit-btn"
            disabled={loading}
          >
            {loading ? (
              <span className="spinner-sm"></span>
            ) : mode === "signin" ? (
              "Sign In to NEXUS"
            ) : (
              "Create Account & Connect Database"
            )}
          </button>
        </form>

        {/* Footer Note */}
        <div className="modal-footer-note">
          <ShieldIcon size={14} />
          <span>Validated ideas and research activity logs are stored securely in Supabase.</span>
        </div>
      </div>
    </div>
  );
}

export default AuthModal;
