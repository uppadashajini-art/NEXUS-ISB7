import React, { useState, useRef, useEffect, useCallback } from "react";
import { useAuth } from "../context/AuthContext";
import {
  DatabaseIcon,
  HistoryIcon,
  UserIcon,
  LogOutIcon,
} from "./Icons";

export function Navbar({
  onOpenAuth,
  onOpenHistory,
  onOpenSupabase,
  activeTab = "validator",
  setActiveTab,
  onNavigateToStyleguide,
}) {
  const { user, isAuthenticated, isSupabaseConnected, activityCount = 0, signOut } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navContainerRef = useRef(null);
  const btnRefs = useRef({});
  const [indicatorStyle, setIndicatorStyle] = useState({
    left: 0,
    width: 0,
    opacity: 0,
  });

  // Calculate sliding pill coordinates based on the active tab button
  const updateIndicator = useCallback(() => {
    const container = navContainerRef.current;
    if (!container) return;

    const currentKey = activeTab in btnRefs.current ? activeTab : "validator";
    const activeEl = btnRefs.current[currentKey];

    if (activeEl) {
      const containerRect = container.getBoundingClientRect();
      const elRect = activeEl.getBoundingClientRect();

      setIndicatorStyle({
        left: Math.round(elRect.left - containerRect.left),
        width: Math.round(elRect.width),
        opacity: 1,
      });
    }
  }, [activeTab]);

  useEffect(() => {
    updateIndicator();
    // Re-check shortly after mount in case web fonts finish loading layout
    const t1 = setTimeout(updateIndicator, 60);
    const t2 = setTimeout(updateIndicator, 250);

    window.addEventListener("resize", updateIndicator);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      window.removeEventListener("resize", updateIndicator);
    };
  }, [updateIndicator, activityCount]);

  const handleSelectTab = (tab) => {
    setActiveTab(tab);
    if (tab === "history" && onOpenHistory) {
      onOpenHistory();
    }
  };

  const displayName = isAuthenticated
    ? user?.user_metadata?.full_name || user?.email?.split("@")[0] || "Founder"
    : "Guest Founder";

  const userInitials = isAuthenticated
    ? (user?.email ? user.email.slice(0, 2).toUpperCase() : "NX")
    : "NX";

  return (
    <header className="nexus-shell-header">
      <div className="nexus-shell-header-inner">
        {/* Left: Logo + "NEXUS" wordmark + "v2.5" badge */}
        <div
          className="shell-brand-group"
          onClick={() => handleSelectTab("validator")}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === "Enter" && handleSelectTab("validator")}
          aria-label="NEXUS Home"
        >
          <div className="shell-brand-logo-frame">
            <img
              src="/logo.png"
              alt="NEXUS Logo"
              className="shell-brand-logo-img"
              onError={(e) => {
                e.currentTarget.style.display = "none";
              }}
            />
          </div>
          <span className="shell-brand-wordmark">NEXUS</span>
          <span className="shell-brand-badge">v2.5</span>
        </div>

        {/* Center: Centered segmented control (Analysis Studio / Activity Log with count badge) */}
        <nav
          className="shell-center-nav"
          ref={navContainerRef}
          role="tablist"
          aria-label="Application views"
        >
          {/* Active nav indicator: sliding pill using brand gradient at 12% opacity with 1px gradient border */}
          <div
            className="shell-sliding-pill"
            style={{
              transform: `translateX(${indicatorStyle.left}px)`,
              width: `${indicatorStyle.width}px`,
              opacity: indicatorStyle.opacity,
            }}
            aria-hidden="true"
          />

          <button
            ref={(el) => (btnRefs.current["validator"] = el)}
            type="button"
            role="tab"
            aria-selected={activeTab === "validator"}
            className={`shell-segment-btn ${activeTab === "validator" ? "active" : ""}`}
            onClick={() => handleSelectTab("validator")}
          >
            <span>Analysis Studio</span>
          </button>

          <button
            ref={(el) => (btnRefs.current["history"] = el)}
            type="button"
            role="tab"
            aria-selected={activeTab === "history"}
            className={`shell-segment-btn ${activeTab === "history" ? "active" : ""}`}
            onClick={() => handleSelectTab("history")}
          >
            <span>Activity Log</span>
            <span className="shell-segment-counter">{activityCount}</span>
          </button>

          {onNavigateToStyleguide && (
            <button
              ref={(el) => (btnRefs.current["styleguide"] = el)}
              type="button"
              role="tab"
              aria-selected={activeTab === "styleguide"}
              className={`shell-segment-btn ${activeTab === "styleguide" ? "active" : ""}`}
              onClick={onNavigateToStyleguide}
            >
              <span>Styleguide</span>
            </button>
          )}
        </nav>

        {/* Right side: Supabase status pill and user avatar menu */}
        <div className="shell-header-actions">
          {/* Supabase Status Pill */}
          <button
            type="button"
            className="shell-status-pill"
            onClick={onOpenSupabase}
            title={
              isSupabaseConnected
                ? "Connected to Supabase Cloud Database"
                : "Local session • Click to configure Supabase Cloud"
            }
            aria-label="Supabase database status"
          >
            <span
              className={`shell-status-dot ${isSupabaseConnected ? "" : "shell-status-dot--warning"}`}
              aria-hidden="true"
            />
            <DatabaseIcon size={14} />
            <span>{isSupabaseConnected ? "Supabase Cloud" : "Connect Cloud"}</span>
          </button>

          {/* User Avatar Menu with Fixed User Chip (No Overlap) */}
          <div className="shell-user-menu-wrapper">
            <button
              type="button"
              className="shell-user-chip-btn"
              onClick={() => setDropdownOpen(!dropdownOpen)}
              aria-expanded={dropdownOpen}
              aria-haspopup="true"
              aria-label="User profile and settings menu"
            >
              <div className="shell-user-avatar">
                {isAuthenticated && user?.user_metadata?.avatar_url ? (
                  <img
                    src={user.user_metadata.avatar_url}
                    alt={displayName}
                    className="shell-user-avatar-img"
                  />
                ) : (
                  <span>{userInitials}</span>
                )}
              </div>

              {/* Bug Fix: Explicit flex column ensures name and secondary status NEVER overlap */}
              <div className="shell-user-info-col">
                <span className="shell-user-name">{displayName}</span>
                <span className="shell-user-secondary-label">
                  {isSupabaseConnected ? "Supabase Cloud" : "Local Mode"}
                </span>
              </div>
            </button>

            {/* Dropdown Menu */}
            {dropdownOpen && (
              <>
                <div
                  className="shell-backdrop"
                  onClick={() => setDropdownOpen(false)}
                  aria-hidden="true"
                />
                <div
                  className="shell-dropdown-menu"
                  role="menu"
                  aria-label="User account actions"
                >
                  <div className="shell-dropdown-header" style={{ padding: "6px 12px 8px" }}>
                    <p
                      style={{
                        margin: 0,
                        fontSize: "12px",
                        fontWeight: 600,
                        color: "var(--text-primary)",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {isAuthenticated ? user?.email : "Guest Founder Session"}
                    </p>
                    <span
                      style={{
                        fontSize: "10px",
                        color: "var(--text-tertiary)",
                        display: "block",
                        marginTop: "2px",
                      }}
                    >
                      {isSupabaseConnected ? "Connected to Cloud Database" : "Using Local In-Memory Cache"}
                    </span>
                  </div>

                  <div className="shell-dropdown-divider" />

                  {isAuthenticated ? (
                    <>
                      <button
                        type="button"
                        className="shell-dropdown-item"
                        role="menuitem"
                        onClick={() => {
                          setDropdownOpen(false);
                          if (onOpenHistory) onOpenHistory();
                        }}
                      >
                        <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                          <HistoryIcon size={14} />
                          <span>Activity Log</span>
                        </span>
                        <span className="shell-segment-counter">{activityCount}</span>
                      </button>

                      <button
                        type="button"
                        className="shell-dropdown-item"
                        role="menuitem"
                        onClick={() => {
                          setDropdownOpen(false);
                          if (onOpenSupabase) onOpenSupabase();
                        }}
                      >
                        <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                          <DatabaseIcon size={14} />
                          <span>Supabase Settings</span>
                        </span>
                      </button>

                      <div className="shell-dropdown-divider" />

                      <button
                        type="button"
                        className="shell-dropdown-item danger"
                        role="menuitem"
                        onClick={() => {
                          setDropdownOpen(false);
                          signOut();
                        }}
                      >
                        <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                          <LogOutIcon size={14} />
                          <span>Sign Out</span>
                        </span>
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        type="button"
                        className="shell-dropdown-item"
                        role="menuitem"
                        onClick={() => {
                          setDropdownOpen(false);
                          if (onOpenAuth) onOpenAuth();
                        }}
                      >
                        <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                          <UserIcon size={14} />
                          <span>Sign In / Register</span>
                        </span>
                      </button>

                      <button
                        type="button"
                        className="shell-dropdown-item"
                        role="menuitem"
                        onClick={() => {
                          setDropdownOpen(false);
                          if (onOpenHistory) onOpenHistory();
                        }}
                      >
                        <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                          <HistoryIcon size={14} />
                          <span>Activity Log</span>
                        </span>
                        <span className="shell-segment-counter">{activityCount}</span>
                      </button>

                      <button
                        type="button"
                        className="shell-dropdown-item"
                        role="menuitem"
                        onClick={() => {
                          setDropdownOpen(false);
                          if (onOpenSupabase) onOpenSupabase();
                        }}
                      >
                        <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                          <DatabaseIcon size={14} />
                          <span>Supabase Settings</span>
                        </span>
                      </button>
                    </>
                  )}
                </div>
              </>
            )}
          </div>

          {/* Mobile Menu Hamburger Button (< 860px) */}
          <button
            type="button"
            className="shell-mobile-menu-btn"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle navigation menu"
            aria-expanded={mobileMenuOpen}
          >
            {mobileMenuOpen ? (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            ) : (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="3" y1="12" x2="21" y2="12" />
                <line x1="3" y1="6" x2="21" y2="6" />
                <line x1="3" y1="18" x2="21" y2="18" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Navigation (< 860px) */}
      {mobileMenuOpen && (
        <>
          <div
            className="shell-backdrop"
            onClick={() => setMobileMenuOpen(false)}
            aria-hidden="true"
          />
          <nav className="shell-mobile-drawer" aria-label="Mobile navigation">
            <button
              type="button"
              className={`shell-mobile-nav-item ${activeTab === "validator" ? "active" : ""}`}
              onClick={() => {
                setMobileMenuOpen(false);
                handleSelectTab("validator");
              }}
            >
              <span>Analysis Studio</span>
            </button>

            <button
              type="button"
              className={`shell-mobile-nav-item ${activeTab === "history" ? "active" : ""}`}
              onClick={() => {
                setMobileMenuOpen(false);
                handleSelectTab("history");
              }}
            >
              <span style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%" }}>
                <span>Activity Log</span>
                <span className="shell-segment-counter">{activityCount}</span>
              </span>
            </button>

            {onNavigateToStyleguide && (
              <button
                type="button"
                className="shell-mobile-nav-item"
                onClick={() => {
                  setMobileMenuOpen(false);
                  onNavigateToStyleguide();
                }}
              >
                <span>Styleguide</span>
              </button>
            )}

            <div className="shell-dropdown-divider" />

            <button
              type="button"
              className="shell-mobile-nav-item"
              onClick={() => {
                setMobileMenuOpen(false);
                if (onOpenSupabase) onOpenSupabase();
              }}
            >
              <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <DatabaseIcon size={14} />
                <span>{isSupabaseConnected ? "Supabase Cloud (Connected)" : "Connect Supabase"}</span>
              </span>
            </button>

            {!isAuthenticated && (
              <button
                type="button"
                className="shell-mobile-nav-item"
                onClick={() => {
                  setMobileMenuOpen(false);
                  if (onOpenAuth) onOpenAuth();
                }}
              >
                <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <UserIcon size={14} />
                  <span>Sign In / Register</span>
                </span>
              </button>
            )}
          </nav>
        </>
      )}
    </header>
  );
}

export default Navbar;
