import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { DEFAULT_PUBLISHABLE_KEY } from "../services/supabaseClient";
import {
  CloseIcon,
  DatabaseIcon,
  CheckIcon,
  CopyIcon,
  ExternalLinkIcon,
  ShieldIcon,
  RefreshIcon,
} from "./Icons";

export function SupabaseConfigModal({ isOpen, onClose }) {
  const { supabaseConfig, saveConfig, isSupabaseConnected } = useAuth();

  const [url, setUrl] = useState(supabaseConfig.url || "");
  const [anonKey, setAnonKey] = useState(supabaseConfig.anonKey || DEFAULT_PUBLISHABLE_KEY);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [copiedSchema, setCopiedSchema] = useState(false);
  const [activeTab, setActiveTab] = useState("connect"); // "connect" | "sql"

  const [showDeveloperSettings, setShowDeveloperSettings] = useState(false);

  if (!isOpen) return null;

  const handleSave = (e) => {
    e.preventDefault();
    setTestResult(null);
    saveConfig(url, anonKey);
    setTestResult({
      success: true,
      message: "Configuration saved! Connecting to Supabase...",
    });
    setTimeout(() => {
      onClose();
    }, 1000);
  };

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);

    if (!url) {
      setTestResult({
        success: false,
        message: "Please enter your Supabase Project URL in Developer Settings.",
      });
      setTesting(false);
      return;
    }

    try {
      const cleanUrl = url.replace(/\/+$/, "");
      const res = await fetch(`${cleanUrl}/rest/v1/idea_validations?select=id&limit=1`, {
        headers: {
          apikey: anonKey,
        },
      });

      if (res.ok || res.status === 200) {
        setTestResult({
          success: true,
          message: "Connection verified! Supabase database table `idea_validations` is live and reachable.",
        });
      } else {
        setTestResult({
          success: false,
          message: `Supabase responded with status ${res.status}. Please check your Project URL.`,
        });
      }
    } catch (err) {
      setTestResult({
        success: false,
        message: `Connection failed: ${err.message || "Network error. Check Project URL."}`,
      });
    } finally {
      setTesting(false);
    }
  };

  const sqlSchemaText = `-- ==============================================================================
-- NEXUS AI STARTUP VALIDATOR - SUPABASE DATABASE SCHEMA
-- ==============================================================================
-- Run this in your Supabase Dashboard -> SQL Editor -> New Query -> Run

create table if not exists public.idea_validations (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  user_email text,
  idea_title text not null,
  idea text not null,
  domain text,
  target_customer text,
  validation_type text default 'all',
  viability_score integer default 85,
  feasibility_score numeric default 7.5,
  summary text,
  full_result jsonb not null default '{}'::jsonb,
  is_starred boolean default false,
  tags text[] default array[]::text[],
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.idea_validations enable row level security;

drop policy if exists "Enable read access for validations" on public.idea_validations;
create policy "Enable read access for validations" on public.idea_validations for select using (true);

drop policy if exists "Enable insert access for validations" on public.idea_validations;
create policy "Enable insert access for validations" on public.idea_validations for insert with check (true);

create index if not exists idx_validations_user_id on public.idea_validations(user_id);
create index if not exists idx_validations_created_at on public.idea_validations(created_at desc);
`;

  const copySqlSchema = () => {
    navigator.clipboard.writeText(sqlSchemaText);
    setCopiedSchema(true);
    setTimeout(() => setCopiedSchema(false), 2500);
  };

  return (
    <div className="nexus-modal-overlay" onClick={onClose}>
      <div
        className="nexus-modal-card supabase-modal-card"
        onClick={(e) => e.stopPropagation()}
        style={{ maxWidth: "540px", overflow: "hidden" }}
      >
        {/* Header */}
        <div
          className="modal-header"
          style={{
            position: "relative",
            display: "flex",
            alignItems: "flex-start",
            gap: "14px",
            padding: "20px 20px 14px",
            borderBottom: "1px solid var(--surface-border)",
          }}
        >
          <div
            className="modal-header-icon-badge supabase-badge-glow"
            style={{
              width: "38px",
              height: "38px",
              borderRadius: "10px",
              background: "rgba(255, 199, 44, 0.1)",
              border: "1px solid rgba(255, 199, 44, 0.25)",
              color: "var(--accent-idea)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexShrink: 0,
            }}
          >
            <DatabaseIcon size={20} />
          </div>

          <div className="modal-header-info" style={{ flex: 1, paddingRight: "32px" }}>
            <h3 className="modal-title" style={{ margin: "0 0 4px 0", fontSize: "1.08rem", fontWeight: 700, color: "var(--text-primary)" }}>
              Cloud Vault & Data Sync
            </h3>
            <p className="modal-subtitle" style={{ margin: 0, fontSize: "0.82rem", color: "var(--text-secondary)", lineHeight: 1.4 }}>
              Encrypted persistence for your startup validation reports and AI dossiers
            </p>
          </div>

          <button
            type="button"
            className="modal-close-btn"
            onClick={onClose}
            aria-label="Close modal"
            style={{
              position: "absolute",
              top: "16px",
              right: "16px",
              background: "rgba(255,255,255,0.06)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: "8px",
              color: "var(--text-secondary)",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              width: "30px",
              height: "30px",
              transition: "all 0.2s ease",
            }}
          >
            <CloseIcon size={16} />
          </button>
        </div>

        {/* Status Hero Card */}
        <div
          className="connection-status-strip"
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "12px",
            padding: "16px",
            margin: "16px 20px 12px",
            background: "var(--surface-2)",
            border: "1px solid var(--surface-border-strong)",
            borderRadius: "12px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%" }}>
            <div className="status-strip-left" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span
                className={`status-light ${isSupabaseConnected ? "green" : "yellow"}`}
                style={{
                  width: "8px",
                  height: "8px",
                  borderRadius: "50%",
                  background: isSupabaseConnected ? "#2DD4BF" : "#FFC72C",
                  boxShadow: isSupabaseConnected ? "0 0 10px rgba(45,212,191,0.8)" : "0 0 10px rgba(255,199,44,0.8)",
                  display: "inline-block",
                  flexShrink: 0,
                }}
              />
              <span className="status-label" style={{ fontWeight: 600, fontSize: "0.88rem", color: "var(--text-primary)" }}>
                {isSupabaseConnected ? "Supabase Cloud Vault Active" : "Local Browser Storage Active"}
              </span>
            </div>
            <span
              className="status-pill-badge"
              style={{
                background: isSupabaseConnected ? "rgba(45,212,191,0.12)" : "rgba(255,199,44,0.12)",
                color: isSupabaseConnected ? "#2DD4BF" : "#FFC72C",
                border: `1px solid ${isSupabaseConnected ? "rgba(45,212,191,0.3)" : "rgba(255,199,44,0.3)"}`,
                padding: "4px 10px",
                borderRadius: "12px",
                fontSize: "0.75rem",
                fontWeight: 700,
                display: "inline-flex",
                alignItems: "center",
                gap: "4px",
              }}
            >
              {isSupabaseConnected ? "⚡ Cloud Connected" : "📁 Local Mode"}
            </span>
          </div>

          {/* Sync Stats Grid */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "10px",
              width: "100%",
              paddingTop: "12px",
              borderTop: "1px solid var(--surface-border)",
            }}
          >
            <div style={{ background: "rgba(255,255,255,0.03)", padding: "10px 12px", borderRadius: "8px", border: "1px solid var(--surface-border)" }}>
              <div style={{ fontSize: "0.68rem", color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.05em", fontWeight: 600 }}>SECURITY</div>
              <div style={{ fontSize: "0.82rem", fontWeight: 600, color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "6px", marginTop: "4px" }}>
                <ShieldIcon size={13} /> SSL Encrypted
              </div>
            </div>
            <div style={{ background: "rgba(255,255,255,0.03)", padding: "10px 12px", borderRadius: "8px", border: "1px solid var(--surface-border)" }}>
              <div style={{ fontSize: "0.68rem", color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.05em", fontWeight: 600 }}>PERSISTENCE TABLE</div>
              <div style={{ fontSize: "0.82rem", fontWeight: 600, color: "var(--text-primary)", marginTop: "4px" }}>
                <code style={{ background: "rgba(255,255,255,0.06)", padding: "2px 6px", borderRadius: "4px", fontSize: "0.8rem" }}>idea_validations</code>
              </div>
            </div>
          </div>
        </div>

        {/* Action & Developer Toggle */}
        <div style={{ padding: "0 20px 20px", display: "flex", flexDirection: "column", gap: "12px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <button
              type="button"
              className="secondary-outline-btn"
              onClick={handleTestConnection}
              disabled={testing}
              style={{
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
                fontSize: "0.8rem",
                fontWeight: 600,
                padding: "8px 16px",
                borderRadius: "8px",
                background: "var(--surface-2)",
                border: "1px solid var(--surface-border-strong)",
                color: "var(--text-primary)",
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
            >
              {testing ? (
                <>
                  <span className="spinner-sm" style={{ width: "14px", height: "14px" }} />
                  <span>Verifying Ping...</span>
                </>
              ) : (
                <>
                  <RefreshIcon size={14} />
                  <span>Check Storage Health</span>
                </>
              )}
            </button>

            <button
              type="button"
              onClick={() => setShowDeveloperSettings(!showDeveloperSettings)}
              style={{
                background: "none",
                border: "none",
                color: "var(--accent-idea)",
                fontSize: "0.78rem",
                fontWeight: 600,
                cursor: "pointer",
                textDecoration: "underline",
              }}
            >
              {showDeveloperSettings ? "Hide Developer Settings" : "⚙️ Developer Connection Settings"}
            </button>
          </div>

          {testResult && (
            <div
              className={`modal-alert ${testResult.success ? "success" : "error"}`}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "10px",
                padding: "10px 14px",
                borderRadius: "8px",
                background: testResult.success ? "rgba(45,212,191,0.1)" : "rgba(242,61,92,0.1)",
                border: `1px solid ${testResult.success ? "rgba(45,212,191,0.3)" : "rgba(242,61,92,0.3)"}`,
                color: testResult.success ? "#2DD4BF" : "#F23D5C",
                fontSize: "0.82rem",
                lineHeight: "1.4",
              }}
            >
              <div style={{ flexShrink: 0, display: "flex", alignItems: "center" }}>
                {testResult.success ? <CheckIcon size={16} /> : <span>!</span>}
              </div>
              <span style={{ margin: 0 }}>{testResult.message}</span>
            </div>
          )}

          {/* Collapsible Developer Section */}
          {showDeveloperSettings && (
            <div
              style={{
                background: "var(--surface-2)",
                border: "1px solid var(--surface-border-strong)",
                borderRadius: "12px",
                padding: "16px",
                marginTop: "4px",
              }}
            >
              <div className="auth-tab-switch" style={{ marginBottom: "12px", display: "flex", gap: "8px" }}>
                <button
                  type="button"
                  className={`auth-tab-btn ${activeTab === "connect" ? "active" : ""}`}
                  onClick={() => setActiveTab("connect")}
                  style={{
                    flex: 1,
                    padding: "6px 12px",
                    borderRadius: "6px",
                    fontSize: "0.78rem",
                    fontWeight: 600,
                    background: activeTab === "connect" ? "var(--surface)" : "transparent",
                    color: activeTab === "connect" ? "var(--accent-idea)" : "var(--text-secondary)",
                    border: activeTab === "connect" ? "1px solid rgba(255,199,44,0.3)" : "1px solid transparent",
                    cursor: "pointer",
                  }}
                >
                  Connection Settings
                </button>
                <button
                  type="button"
                  className={`auth-tab-btn ${activeTab === "sql" ? "active" : ""}`}
                  onClick={() => setActiveTab("sql")}
                  style={{
                    flex: 1,
                    padding: "6px 12px",
                    borderRadius: "6px",
                    fontSize: "0.78rem",
                    fontWeight: 600,
                    background: activeTab === "sql" ? "var(--surface)" : "transparent",
                    color: activeTab === "sql" ? "var(--accent-idea)" : "var(--text-secondary)",
                    border: activeTab === "sql" ? "1px solid rgba(255,199,44,0.3)" : "1px solid transparent",
                    cursor: "pointer",
                  }}
                >
                  1-Click SQL Setup
                </button>
              </div>

              {activeTab === "connect" && (
                <form onSubmit={handleSave} className="supabase-form" style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                  <div className="input-group" style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                    <div className="label-with-hint" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <label htmlFor="supabase-url" style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>Supabase Project URL</label>
                      <a
                        href="https://supabase.com/dashboard"
                        target="_blank"
                        rel="noreferrer"
                        className="external-docs-link"
                        style={{ fontSize: "0.74rem", color: "var(--accent-idea)", display: "flex", alignItems: "center", gap: "4px" }}
                      >
                        <span>Dashboard</span>
                        <ExternalLinkIcon size={12} />
                      </a>
                    </div>
                    <input
                      id="supabase-url"
                      type="url"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      placeholder="https://xyzabcdefgh.supabase.co"
                      required
                      style={{
                        padding: "8px 12px",
                        borderRadius: "6px",
                        background: "var(--surface)",
                        border: "1px solid var(--surface-border)",
                        color: "var(--text-primary)",
                        fontSize: "0.82rem",
                      }}
                    />
                  </div>

                  <div className="input-group" style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                    <label htmlFor="supabase-anon-key" style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>Publishable API Key</label>
                    <input
                      id="supabase-anon-key"
                      type="text"
                      value={anonKey}
                      onChange={(e) => setAnonKey(e.target.value)}
                      placeholder="sb_publishable_..."
                      style={{
                        padding: "8px 12px",
                        borderRadius: "6px",
                        background: "var(--surface)",
                        border: "1px solid var(--surface-border)",
                        color: "var(--text-primary)",
                        fontSize: "0.82rem",
                      }}
                    />
                  </div>

                  <button
                    type="submit"
                    className="auth-submit-btn"
                    style={{
                      marginTop: "6px",
                      padding: "8px 16px",
                      borderRadius: "6px",
                      background: "var(--brand-gradient)",
                      border: "none",
                      color: "#000",
                      fontWeight: 700,
                      fontSize: "0.82rem",
                      cursor: "pointer",
                    }}
                  >
                    <span>Save Credentials</span>
                  </button>
                </form>
              )}

              {activeTab === "sql" && (
                <div className="sql-schema-container">
                  <div className="code-block-wrapper">
                    <div className="code-block-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                      <span style={{ fontSize: "0.76rem", color: "var(--text-tertiary)" }}>idea_validations.sql</span>
                      <button
                        type="button"
                        className="copy-code-btn"
                        onClick={copySqlSchema}
                        style={{
                          background: "none",
                          border: "none",
                          color: "var(--accent-idea)",
                          fontSize: "0.74rem",
                          fontWeight: 600,
                          cursor: "pointer",
                        }}
                      >
                        {copiedSchema ? <span>Copied!</span> : <span>Copy SQL</span>}
                      </button>
                    </div>
                    <pre
                      className="code-snippet"
                      style={{
                        maxHeight: "140px",
                        overflowY: "auto",
                        fontSize: "0.72rem",
                        padding: "10px",
                        background: "var(--surface)",
                        borderRadius: "6px",
                        border: "1px solid var(--surface-border)",
                        margin: 0,
                      }}
                    >
                      {sqlSchemaText}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SupabaseConfigModal;
