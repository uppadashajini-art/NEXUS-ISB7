import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import {
  CloseIcon,
  UserIcon,
  ShieldIcon,
  CheckIcon,
} from "./Icons";

export function AuthModal({ isOpen, onClose }) {
  const {
    signIn,
    signUp,
    signInWithGoogle,
    isSupabaseConnected,
  } = useAuth();

  const [mode, setMode] = useState("signin"); // "signin" | "signup"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
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

        setSuccessMsg(
          "Account created successfully! You are now logged in."
        );

        setTimeout(() => {
          onClose();
        }, 1200);
      }
    } catch (err) {
      console.error("Auth error:", err);

      setError(
        err.message ||
          "Authentication failed. Please verify your credentials."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setError("");
    setSuccessMsg("");
    setGoogleLoading(true);

    try {
      if (!isSupabaseConnected) {
        throw new Error(
          "Supabase is not connected. Please connect Supabase first."
        );
      }

      await signInWithGoogle();
    } catch (err) {
      console.error("Google sign-in error:", err);

      setError(
        err.message || "Unable to sign in with Google."
      );

      setGoogleLoading(false);
    }
  };

  const isLoading = loading || googleLoading;

  return (
    <div
      className="nexus-modal-overlay"
      onClick={onClose}
    >
      <div
        className="nexus-modal-card auth-modal-card"
        onClick={(e) => e.stopPropagation()}
      >
        {/* =====================================================
            MODAL HEADER
        ====================================================== */}

        <div className="modal-header">
          <div className="modal-header-icon-badge">
            <UserIcon size={20} />
          </div>

          <div className="modal-header-info">
            <h3 className="modal-title">
              {mode === "signin"
                ? "Sign In to NEXUS"
                : "Create Founder Account"}
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
            aria-label="Close authentication dialog"
          >
            <CloseIcon size={18} />
          </button>
        </div>

        {/* =====================================================
            AUTH MODE TABS
        ====================================================== */}

        <div className="auth-tab-switch">
          <button
            type="button"
            className={`auth-tab-btn ${
              mode === "signin" ? "active" : ""
            }`}
            onClick={() => {
              setMode("signin");
              setError("");
              setSuccessMsg("");
            }}
            disabled={isLoading}
          >
            Sign In
          </button>

          <button
            type="button"
            className={`auth-tab-btn ${
              mode === "signup" ? "active" : ""
            }`}
            onClick={() => {
              setMode("signup");
              setError("");
              setSuccessMsg("");
            }}
            disabled={isLoading}
          >
            Create Account
          </button>
        </div>

        {/* =====================================================
            FEEDBACK ALERTS
        ====================================================== */}

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

        {/* =====================================================
            FORM
        ====================================================== */}

        <form
          onSubmit={handleSubmit}
          className="auth-form"
        >
          {/* Full Name - Signup Only */}
          {mode === "signup" && (
            <div className="input-group">
              <label htmlFor="auth-fullname">
                Full Name / Founder Handle
              </label>

              <input
                id="auth-fullname"
                type="text"
                value={fullName}
                onChange={(e) =>
                  setFullName(e.target.value)
                }
                placeholder="e.g. John Doe"
                required
                disabled={isLoading}
              />
            </div>
          )}

          {/* Email */}
          <div className="input-group">
            <label htmlFor="auth-email">
              Email Address
            </label>

            <input
              id="auth-email"
              type="email"
              value={email}
              onChange={(e) =>
                setEmail(e.target.value)
              }
              placeholder="founder@nexus-spring.io"
              required
              disabled={isLoading}
            />
          </div>

          {/* Password */}
          <div className="input-group">
            <label htmlFor="auth-password">
              Password
            </label>

            <input
              id="auth-password"
              type="password"
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
              placeholder="••••••••••••"
              required
              minLength={6}
              disabled={isLoading}
            />
          </div>

          {/* Submit */}
          <button
            type="submit"
            className="auth-submit-btn"
            disabled={isLoading}
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

        {/* =====================================================
            GOOGLE SIGN IN
        ====================================================== */}

        {mode === "signin" && (
          <>
            <div className="auth-divider">
              <span>OR</span>
            </div>

            <button
              type="button"
              className="google-auth-btn"
              onClick={handleGoogleSignIn}
              disabled={isLoading}
            >
              {googleLoading ? (
                <span className="spinner-sm"></span>
              ) : (
                <>
                  <svg
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      fill="#4285F4"
                      d="M21.35 12.2c0-.7-.06-1.37-.18-2H12v3.79h5.23a4.47 4.47 0 0 1-1.94 2.93v2.44h3.14c1.84-1.69 2.92-4.18 2.92-7.16z"
                    />

                    <path
                      fill="#34A853"
                      d="M12 21.75c2.63 0 4.84-.87 6.45-2.39l-3.14-2.44c-.87.58-1.98.92-3.31.92-2.55 0-4.71-1.72-5.49-4.04H3.27v2.52A9.75 9.75 0 0 0 12 21.75z"
                    />

                    <path
                      fill="#FBBC05"
                      d="M6.51 13.8A5.86 5.86 0 0 1 6.2 12c0-.62.11-1.22.31-1.8V7.68H3.27A9.75 9.75 0 0 0 2.25 12c0 1.57.38 3.05 1.02 4.32l3.24-2.52z"
                    />

                    <path
                      fill="#EA4335"
                      d="M12 6.16c1.43 0 2.72.49 3.74 1.46l2.8-2.8C16.84 3.26 14.63 2.25 12 2.25a9.75 9.75 0 0 0-8.73 5.43l3.24 2.52C7.29 7.88 9.45 6.16 12 6.16z"
                    />
                  </svg>

                  <span>Continue with Google</span>
                </>
              )}
            </button>
          </>
        )}

        {/* =====================================================
            FOOTER SECURITY NOTE
        ====================================================== */}

        <div className="modal-footer-note">
          <ShieldIcon size={14} />

          <span>
            Validated ideas and research activity logs
            are stored securely in Supabase.
          </span>
        </div>
      </div>
    </div>
  );
}

export default AuthModal;