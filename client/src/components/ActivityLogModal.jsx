import React, { useState, useEffect, useMemo } from "react";
import { useAuth } from "../context/AuthContext";
import {
  fetchValidationActivities,
  deleteValidationActivity,
} from "../services/supabaseClient";
import {
  Search,
  X,
  ExternalLink,
  Copy,
  Trash2,
  Database,
  ArrowRight,
} from "lucide-react";
import "../styles/activity-log.css";

const SCOPE_CONFIG = {
  all: {
    label: "Comprehensive",
    color: "var(--accent-idea)",
    bg: "rgba(255, 199, 44, 0.10)",
    border: "rgba(255, 199, 44, 0.25)",
  },
  idea: {
    label: "Idea Validation",
    color: "var(--accent-idea)",
    bg: "rgba(255, 199, 44, 0.10)",
    border: "rgba(255, 199, 44, 0.25)",
  },
  market: {
    label: "Market Sizing",
    color: "var(--accent-market)",
    bg: "rgba(255, 138, 31, 0.10)",
    border: "rgba(255, 138, 31, 0.25)",
  },
  customers: {
    label: "Customer ICP",
    color: "var(--accent-customer)",
    bg: "rgba(255, 90, 78, 0.10)",
    border: "rgba(255, 90, 78, 0.25)",
  },
  competitors: {
    label: "Competitors",
    color: "var(--accent-competitor)",
    bg: "rgba(242, 61, 92, 0.10)",
    border: "rgba(242, 61, 92, 0.25)",
  },
  feasibility: {
    label: "Feasibility",
    color: "var(--accent-feasibility)",
    bg: "rgba(45, 212, 191, 0.10)",
    border: "rgba(45, 212, 191, 0.25)",
  },
  mvp: {
    label: "MVP & Scope",
    color: "var(--accent-advisory)",
    bg: "rgba(139, 124, 246, 0.10)",
    border: "rgba(139, 124, 246, 0.25)",
  },
};

export function ActivityLogModal({
  isOpen,
  onClose,
  onLoadIdeaIntoCanvas,
  onDuplicateIdea,
}) {
  const { user, isSupabaseConnected, updateActivityCount } = useAuth();

  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedScope, setSelectedScope] = useState("all");

  // Load activities when modal opens
  useEffect(() => {
    if (!isOpen) return;

    let mounted = true;
    const load = async () => {
      setLoading(true);
      try {
        const data = await fetchValidationActivities(user?.id);
        if (mounted) {
          setActivities(data);
          updateActivityCount(data.length);
        }
      } catch (err) {
        console.error("Failed to load activity logs:", err);
      } finally {
        if (mounted) setLoading(false);
      }
    };

    load();
    return () => {
      mounted = false;
    };
  }, [isOpen, user?.id, updateActivityCount]);

  // Handle ESC key to close
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  // Handle Open
  const handleOpen = (activity) => {
    onLoadIdeaIntoCanvas(activity);
    onClose();
  };

  // Handle Duplicate
  const handleDuplicate = (activity, e) => {
    e.stopPropagation();
    if (onDuplicateIdea) {
      onDuplicateIdea(activity);
    } else {
      onLoadIdeaIntoCanvas(activity);
    }
    onClose();
  };

  // Handle Delete
  const handleDelete = async (id, title, e) => {
    e.stopPropagation();
    if (!window.confirm(`Delete "${title || "this analysis"}" from your history?`)) return;

    setActivities((prev) => prev.filter((item) => item.id !== id));
    try {
      await deleteValidationActivity(id, user?.id);
      updateActivityCount(Math.max(0, activities.length - 1));
    } catch (err) {
      console.error("Delete error:", err);
    }
  };

  // Filtered Activities
  const filteredActivities = useMemo(() => {
    return activities.filter((item) => {
      if (selectedScope !== "all") {
        const vType = item.validation_type || "all";
        if (vType !== selectedScope) return false;
      }
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const inTitle = item.idea_title?.toLowerCase().includes(q);
        const inIdea = item.idea?.toLowerCase().includes(q);
        const inDomain = item.domain?.toLowerCase().includes(q);
        const inCustomer = item.target_customer?.toLowerCase().includes(q);
        return inTitle || inIdea || inDomain || inCustomer;
      }
      return true;
    });
  }, [activities, selectedScope, searchQuery]);

  // Timeline grouping by date
  const groupedActivities = useMemo(() => {
    const groups = {};
    const now = new Date();
    const todayStr = now.toDateString();
    const yesterday = new Date(now);
    yesterday.setDate(now.getDate() - 1);
    const yesterdayStr = yesterday.toDateString();

    filteredActivities.forEach((act) => {
      const d = act.created_at ? new Date(act.created_at) : new Date();
      let label = "";

      if (d.toDateString() === todayStr) {
        label = "Today";
      } else if (d.toDateString() === yesterdayStr) {
        label = "Yesterday";
      } else {
        label = d.toLocaleDateString(undefined, {
          month: "short",
          day: "numeric",
          year: d.getFullYear() !== now.getFullYear() ? "numeric" : undefined,
        });
      }

      if (!groups[label]) groups[label] = [];
      groups[label].push(act);
    });

    return Object.entries(groups);
  }, [filteredActivities]);

  if (!isOpen) return null;

  return (
    <div
      className="activity-modal-overlay"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Activity Log"
    >
      <div
        className="activity-modal-dialog"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="activity-modal-head">
          <div className="activity-head-left">
            <span className="activity-eyebrow">
              <span className="activity-eyebrow-dot" aria-hidden="true" />
              <span>TIMELINE ARCHIVE</span>
            </span>
            <h2 className="activity-modal-title">Activity Log</h2>
          </div>

          <div className="activity-head-right">
            <div className="activity-sync-pill">
              <Database size={12} strokeWidth={1.5} />
              <span>{isSupabaseConnected ? "Supabase Cloud" : "Local Vault"}</span>
            </div>

            <button
              type="button"
              className="activity-close-btn"
              onClick={onClose}
              aria-label="Close Activity Log"
            >
              <X size={16} strokeWidth={1.5} />
            </button>
          </div>
        </div>

        {/* Search & Filter Bar */}
        <div className="activity-toolbar">
          <div className="activity-search-row">
            <Search className="activity-search-icon" size={15} strokeWidth={1.5} />
            <input
              type="text"
              className="activity-search-input"
              placeholder="Search validations by keyword, concept, or domain..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              aria-label="Search validations"
            />
          </div>

          <div className="activity-filter-pills" role="radiogroup" aria-label="Filter by scope">
            <button
              type="button"
              className={`activity-filter-pill ${selectedScope === "all" ? "active" : ""}`}
              onClick={() => setSelectedScope("all")}
            >
              All Scopes ({activities.length})
            </button>
            <button
              type="button"
              className={`activity-filter-pill ${selectedScope === "market" ? "active" : ""}`}
              onClick={() => setSelectedScope("market")}
            >
              Market Sizing
            </button>
            <button
              type="button"
              className={`activity-filter-pill ${selectedScope === "customers" ? "active" : ""}`}
              onClick={() => setSelectedScope("customers")}
            >
              Customer ICP
            </button>
            <button
              type="button"
              className={`activity-filter-pill ${selectedScope === "competitors" ? "active" : ""}`}
              onClick={() => setSelectedScope("competitors")}
            >
              Competitors
            </button>
            <button
              type="button"
              className={`activity-filter-pill ${selectedScope === "feasibility" ? "active" : ""}`}
              onClick={() => setSelectedScope("feasibility")}
            >
              Feasibility
            </button>
            <button
              type="button"
              className={`activity-filter-pill ${selectedScope === "mvp" ? "active" : ""}`}
              onClick={() => setSelectedScope("mvp")}
            >
              MVP & Scope
            </button>
          </div>
        </div>

        {/* Timeline Body */}
        <div className="activity-timeline-body">
          {loading ? (
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "48px 0", gap: "12px" }}>
              <div className="clean-spinner" style={{ width: "24px", height: "24px", borderWidth: "2px" }} />
              <span style={{ fontSize: "13px", color: "var(--text-secondary)" }}>Loading history records...</span>
            </div>
          ) : filteredActivities.length === 0 ? (
            /* Illustration-Free, Text-Led Empty State */
            <div className="activity-empty-text-wrap">
              <span className="activity-empty-eyebrow">NO VALIDATIONS RECORDED</span>
              <h3 className="activity-empty-heading">Activity archive is empty</h3>
              <p className="activity-empty-body">
                {searchQuery || selectedScope !== "all"
                  ? "No dossiers match your active search and scope criteria. Try broadening your query."
                  : "Run your first startup market & competitor validation in the Analysis Studio to automatically record audit snapshots and telemetry here."}
              </p>
              {searchQuery || selectedScope !== "all" ? (
                <button
                  type="button"
                  className="activity-btn-action"
                  onClick={() => {
                    setSearchQuery("");
                    setSelectedScope("all");
                  }}
                  style={{ marginTop: "8px" }}
                >
                  Clear Filters
                </button>
              ) : (
                <button
                  type="button"
                  className="activity-empty-cta"
                  onClick={onClose}
                >
                  <span>Open Analysis Studio</span>
                  <ArrowRight size={13} strokeWidth={2} />
                </button>
              )}
            </div>
          ) : (
            /* Timeline List Grouped By Date */
            groupedActivities.map(([dateGroup, items]) => (
              <div key={dateGroup} className="activity-date-group">
                <div className="activity-date-header">
                  <span className="activity-date-label">{dateGroup}</span>
                  <span className="activity-date-line" aria-hidden="true" />
                </div>

                <div className="activity-rows-list">
                  {items.map((act) => {
                    const scopeKey = act.validation_type || "all";
                    const scopeConf = SCOPE_CONFIG[scopeKey] || SCOPE_CONFIG.all;
                    const score = act.viability_score || 84;

                    return (
                      <div
                        key={act.id}
                        className="activity-timeline-row"
                        onClick={() => handleOpen(act)}
                        role="button"
                        tabIndex={0}
                        onKeyDown={(e) => e.key === "Enter" && handleOpen(act)}
                      >
                        {/* Row Left: Title, Scope Badge, Prompt Snippet */}
                        <div className="activity-row-left">
                          <div className="activity-row-info">
                            <div className="activity-row-title-row">
                              <span className="activity-row-title">
                                {act.idea_title || (act.idea ? act.idea.slice(0, 48) : "Startup Validation")}
                              </span>

                              {/* Scope Badge in its accent color */}
                              <span
                                className="activity-scope-badge"
                                style={{
                                  color: scopeConf.color,
                                  backgroundColor: scopeConf.bg,
                                  border: `1px solid ${scopeConf.border}`,
                                }}
                              >
                                <span className="activity-scope-dot" aria-hidden="true" />
                                <span>{scopeConf.label}</span>
                              </span>

                              {/* Score Pill */}
                              <span className="activity-score-pill">
                                <span>Score:</span>
                                <strong>{score}/100</strong>
                              </span>
                            </div>

                            <span className="activity-row-desc">
                              {act.idea ? act.idea.slice(0, 110) + (act.idea.length > 110 ? "..." : "") : "Validation dossier"}
                            </span>
                          </div>
                        </div>

                        {/* Actions: Open, Duplicate, Delete */}
                        <div className="activity-row-actions">
                          <button
                            type="button"
                            className="activity-btn-action activity-btn-open"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleOpen(act);
                            }}
                            title="Open in Analysis Studio"
                          >
                            <ExternalLink size={12} strokeWidth={1.5} />
                            <span>Open</span>
                          </button>

                          <button
                            type="button"
                            className="activity-btn-action"
                            onClick={(e) => handleDuplicate(act, e)}
                            title="Duplicate into form for iteration"
                          >
                            <Copy size={12} strokeWidth={1.5} />
                            <span>Duplicate</span>
                          </button>

                          <button
                            type="button"
                            className="activity-btn-action activity-btn-delete"
                            onClick={(e) => handleDelete(act.id, act.idea_title, e)}
                            title="Delete record"
                          >
                            <Trash2 size={13} strokeWidth={1.5} />
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default ActivityLogModal;
