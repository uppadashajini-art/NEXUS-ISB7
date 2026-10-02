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
        message: "Please enter your Supabase Project URL (e.g. https://your-id.supabase.co).",
      });
      setTesting(false);
      return;
    }

    try {
      // Direct REST health check to Supabase table
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

-- 1. Create table for storing validated ideas & activity logs
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

-- 2. Enable Row Level Security (RLS)
alter table public.idea_validations enable row level security;

-- 3. RLS Policies
drop policy if exists "Enable read access for validations" on public.idea_validations;
create policy "Enable read access for validations"
  on public.idea_validations for select
  using (true);

drop policy if exists "Enable insert access for validations" on public.idea_validations;
create policy "Enable insert access for validations"
  on public.idea_validations for insert
  with check (true);

drop policy if exists "Enable update access for validations" on public.idea_validations;
create policy "Enable update access for validations"
  on public.idea_validations for update
  using (true);

drop policy if exists "Enable delete access for validations" on public.idea_validations;
create policy "Enable delete access for validations"
  on public.idea_validations for delete
  using (true);

-- 4. High-performance Indexes
create index if not exists idx_validations_user_id on public.idea_validations(user_id);
create index if not exists idx_validations_created_at on public.idea_validations(created_at desc);
create index if not exists idx_validations_starred on public.idea_validations(is_starred);
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
      >
        {/* Header */}
        <div className="modal-header">
          <div className="modal-header-icon-badge supabase-badge-glow">
            <DatabaseIcon size={20} />
          </div>
          <div className="modal-header-info">
            <h3 className="modal-title">Supabase Cloud Database Connection</h3>
            <p className="modal-subtitle">
              Store real-time validated ideas, research logs, and agent dossiers in Supabase.
            </p>
          </div>
          <button type="button" className="modal-close-btn" onClick={onClose}>
            <CloseIcon size={18} />
          </button>
        </div>

        {/* Status Strip */}
        <div className="connection-status-strip">
          <div className="status-strip-left">
            <span
              className={`status-light ${isSupabaseConnected ? "green" : "yellow"}`}
            ></span>
            <span className="status-label">
              {isSupabaseConnected
                ? "Active Supabase Cloud Storage Connected"
                : "Awaiting Supabase Project URL"}
            </span>
          </div>
          <span className="status-pill-badge">
            {isSupabaseConnected ? "Cloud Active" : "Key Configured"}
          </span>
        </div>

        {/* Modal Tabs */}
        <div className="auth-tab-switch">
          <button
            type="button"
            className={`auth-tab-btn ${activeTab === "connect" ? "active" : ""}`}
            onClick={() => setActiveTab("connect")}
          >
            Connection Settings
          </button>
          <button
            type="button"
            className={`auth-tab-btn ${activeTab === "sql" ? "active" : ""}`}
            onClick={() => setActiveTab("sql")}
          >
            1-Click SQL Schema Setup
          </button>
        </div>

        {/* Tab 1: Connect Settings */}
        {activeTab === "connect" && (
          <form onSubmit={handleSave} className="supabase-form">
            <div className="input-group">
              <div className="label-with-hint">
                <label htmlFor="supabase-url">Supabase Project URL (Required)</label>
                <a
                  href="https://supabase.com/dashboard"
                  target="_blank"
                  rel="noreferrer"
                  className="external-docs-link"
                >
                  <span>Open Supabase Dashboard</span>
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
              />
              <span style={{ fontSize: "0.74rem", color: "#94a3b8" }}>
                Found in: Supabase Dashboard → Project Settings → API → Project URL
              </span>
            </div>

            <div className="input-group">
              <label htmlFor="supabase-anon-key">
                Publishable API Key (Configured)
              </label>
              <input
                id="supabase-anon-key"
                type="text"
                value={anonKey}
                onChange={(e) => setAnonKey(e.target.value)}
                placeholder="sb_publishable_..."
              />
            </div>

            {testResult && (
              <div
                className={`modal-alert ${
                  testResult.success ? "success" : "error"
                }`}
              >
                {testResult.success ? <CheckIcon size={16} /> : <span>!</span>}
                <p>{testResult.message}</p>
              </div>
            )}

            <div className="form-action-row">
              <button
                type="button"
                className="secondary-outline-btn"
                onClick={handleTestConnection}
                disabled={testing}
              >
                {testing ? (
                  <>
                    <span className="spinner-sm"></span>
                    <span>Testing...</span>
                  </>
                ) : (
                  <>
                    <RefreshIcon size={14} />
                    <span>Test Ping</span>
                  </>
                )}
              </button>

              <button type="submit" className="auth-submit-btn">
                <span>Save & Connect Supabase</span>
              </button>
            </div>
          </form>
        )}

        {/* Tab 2: SQL Schema Generator */}
        {activeTab === "sql" && (
          <div className="sql-schema-container">
            <div className="sql-schema-instructions">
              <p>
                Run this SQL script in your Supabase project to create the <code>idea_validations</code> table and RLS policies:
              </p>
              <ol>
                <li>Open your <strong>Supabase Dashboard → SQL Editor</strong>.</li>
                <li>Click <strong>New query</strong>.</li>
                <li>Paste the script below and click <strong>RUN</strong>.</li>
              </ol>
            </div>

            <div className="code-block-wrapper">
              <div className="code-block-header">
                <span>idea_validations_schema.sql</span>
                <button
                  type="button"
                  className="copy-code-btn"
                  onClick={copySqlSchema}
                >
                  {copiedSchema ? (
                    <>
                      <CheckIcon size={14} />
                      <span>Copied to Clipboard!</span>
                    </>
                  ) : (
                    <>
                      <CopyIcon size={14} />
                      <span>Copy SQL Script</span>
                    </>
                  )}
                </button>
              </div>
              <pre className="code-snippet">{sqlSchemaText}</pre>
            </div>
          </div>
        )}

        {/* Modal Footer */}
        <div className="modal-footer-note">
          <ShieldIcon size={14} />
          <span>
            Connected table <code>idea_validations</code> persists all startup ideas and research dossiers.
          </span>
        </div>
      </div>
    </div>
  );
}

export default SupabaseConfigModal;
