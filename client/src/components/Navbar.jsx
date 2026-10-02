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
  theme = "light",
  onToggleTheme,
}) {
  const {
    user,
    isAuthenticated,
    isSupabaseConnected,
    activityCount = 0,
    signOut,
  } = useAuth();

  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeSection, setActiveSection] = useState("overview");

  const navContainerRef = useRef(null);
  const btnRefs = useRef({});

  const [indicatorStyle, setIndicatorStyle] = useState({
    left: 0,
    width: 0,
    opacity: 0,
  });

  const isDarkMode = theme === "dark";

  // =========================================================
  // Navigation sections
  // =========================================================

  const navigationSections = [
    {
      id: "overview",
      label: "Overview",
      description: "Validation score & executive synthesis",
      keywords: [
        "Executive Validation Synthesis",
        "Validation Results",
      ],
    },
    {
      id: "research",
      label: "Research",
      description: "Web intelligence & research sources",
      keywords: [
        "Research Sources",
        "Web Sources",
      ],
    },
    {
      id: "analysis",
      label: "Analysis",
      description: "Market, customers & competitors",
      keywords: [
        "Deep Validation Matrix",
        "Market Intelligence",
        "Market Analysis",
        "Customer Segments",
        "Competitor",
      ],
    },
    {
      id: "strategy",
      label: "Strategy",
      description: "Risks, MVP & go-to-market",
      keywords: [
        "Risk Analysis",
        "MVP Recommendations",
        "Go-To-Market",
        "GTM Strategy",
      ],
    },
    {
      id: "report",
      label: "Report",
      description: "Complete startup validation report",
      keywords: [
        "Startup Validation Report",
        "Validation Report",
      ],
    },
  ];

  // =========================================================
  // Find content section and scroll to it
  // =========================================================

  const scrollToSection = useCallback((section) => {
    setActiveSection(section.id);

    /*
      We try to find a matching heading/content area.

      If your existing page does not have IDs yet, the fallback
      simply returns to the main validator view.
    */
    const allElements = Array.from(
      document.querySelectorAll(
        "h1, h2, h3, h4, section, article, [data-section]"
      )
    );

    const target = allElements.find((element) => {
      const text = element.textContent?.trim().toLowerCase() || "";

      return section.keywords.some((keyword) =>
        text.includes(keyword.toLowerCase())
      );
    });

    if (target) {
      const headerOffset = 90;

      const targetPosition =
        target.getBoundingClientRect().top +
        window.scrollY -
        headerOffset;

      window.scrollTo({
        top: Math.max(0, targetPosition),
        behavior: "smooth",
      });
    } else {
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    }

    if (setActiveTab) {
      setActiveTab("validator");
    }
  }, [setActiveTab]);

  // =========================================================
  // Sliding indicator
  // =========================================================

  const updateIndicator = useCallback(() => {
    const container = navContainerRef.current;

    if (!container) return;

    const activeEl = btnRefs.current[activeSection];

    if (activeEl) {
      const containerRect = container.getBoundingClientRect();
      const elementRect = activeEl.getBoundingClientRect();

      setIndicatorStyle({
        left: Math.round(elementRect.left - containerRect.left),
        width: Math.round(elementRect.width),
        opacity: 1,
      });
    }
  }, [activeSection]);

  useEffect(() => {
    updateIndicator();

    const timer1 = setTimeout(updateIndicator, 50);
    const timer2 = setTimeout(updateIndicator, 250);

    window.addEventListener("resize", updateIndicator);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      window.removeEventListener("resize", updateIndicator);
    };
  }, [updateIndicator]);

  // =========================================================
  // User / account
  // =========================================================

  const displayName = isAuthenticated
    ? user?.user_metadata?.full_name ||
      user?.email?.split("@")[0] ||
      "Founder"
    : "Guest Founder";

  const userInitials = isAuthenticated
    ? user?.email
      ? user.email.slice(0, 2).toUpperCase()
      : "NX"
    : "NX";

  const themeLabel = isDarkMode
    ? "Switch to light mode"
    : "Switch to dark mode";

  // =========================================================
  // Utility actions
  // =========================================================

  const openHistory = () => {
    setDropdownOpen(false);

    if (onOpenHistory) {
      onOpenHistory();
    }
  };

  const openSupabase = () => {
    setDropdownOpen(false);

    if (onOpenSupabase) {
      onOpenSupabase();
    }
  };

  const openAuth = () => {
    setDropdownOpen(false);

    if (onOpenAuth) {
      onOpenAuth();
    }
  };

  const handleMobileNavigation = (section) => {
    setMobileMenuOpen(false);
    scrollToSection(section);
  };

  return (
    <header className="nexus-shell-header">
      <div className="nexus-shell-header-inner">

        {/* =====================================================
            BRAND
            ===================================================== */}

        <button
          type="button"
          className="shell-brand-group"
          onClick={() => {
            setActiveSection("overview");

            if (setActiveTab) {
              setActiveTab("validator");
            }

            window.scrollTo({
              top: 0,
              behavior: "smooth",
            });
          }}
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

          <span className="shell-brand-wordmark">
            NEXUS
          </span>

          <span className="shell-brand-badge">
            v2.5
          </span>
        </button>

        {/* =====================================================
            PRIMARY NAVIGATION
            ===================================================== */}

        <nav
          className="shell-center-nav"
          ref={navContainerRef}
          aria-label="Validation sections"
        >
          <div
            className="shell-sliding-pill"
            style={{
              transform: `translateX(${indicatorStyle.left}px)`,
              width: `${indicatorStyle.width}px`,
              opacity: indicatorStyle.opacity,
            }}
            aria-hidden="true"
          />

          {navigationSections.map((section) => (
            <button
              key={section.id}
              ref={(element) => {
                btnRefs.current[section.id] = element;
              }}
              type="button"
              className={`shell-segment-btn ${
                activeSection === section.id ? "active" : ""
              }`}
              onClick={() => scrollToSection(section)}
              title={section.description}
            >
              <span>{section.label}</span>
            </button>
          ))}
        </nav>

        {/* =====================================================
            RIGHT ACTIONS
            ===================================================== */}

        <div className="shell-header-actions">

          {/* History */}

          <button
            type="button"
            className="shell-history-btn"
            onClick={openHistory}
            title="Validation history"
            aria-label="Open validation history"
          >
            <HistoryIcon size={15} />

            <span className="shell-history-label">
              History
            </span>

            <span className="shell-segment-counter">
              {activityCount}
            </span>
          </button>

          {/* Theme */}

          <button
            type="button"
            className="shell-theme-toggle"
            onClick={onToggleTheme}
            aria-label={themeLabel}
            title={themeLabel}
          >
            <span
              className={`shell-theme-toggle-track ${
                isDarkMode ? "dark" : ""
              }`}
            >
              <span className="shell-theme-toggle-thumb">
                {isDarkMode ? "D" : "L"}
              </span>
            </span>
          </button>

          {/* Supabase */}

          <button
            type="button"
            className="shell-status-pill"
            onClick={onOpenSupabase}
            title={
              isSupabaseConnected
                ? "Connected to Supabase Cloud"
                : "Click to configure Supabase Cloud"
            }
          >
            <span
              className={`shell-status-dot ${
                isSupabaseConnected
                  ? ""
                  : "shell-status-dot--warning"
              }`}
            />

            <DatabaseIcon size={14} />

            <span className="shell-status-text">
              {isSupabaseConnected
                ? "Cloud"
                : "Connect"}
            </span>
          </button>

          {/* =================================================
              USER
              ================================================= */}

          <div className="shell-user-menu-wrapper">

            <button
              type="button"
              className="shell-user-chip-btn"
              onClick={() =>
                setDropdownOpen((value) => !value)
              }
              aria-expanded={dropdownOpen}
              aria-haspopup="true"
            >
              <div className="shell-user-avatar">
                {isAuthenticated &&
                user?.user_metadata?.avatar_url ? (
                  <img
                    src={user.user_metadata.avatar_url}
                    alt={displayName}
                    className="shell-user-avatar-img"
                  />
                ) : (
                  <span>{userInitials}</span>
                )}
              </div>

              <div className="shell-user-info-col">
                <span className="shell-user-name">
                  {displayName}
                </span>

                <span className="shell-user-secondary-label">
                  {isAuthenticated
                    ? "Founder"
                    : "Guest"}
                </span>
              </div>

              <span className="shell-user-chevron">
                {dropdownOpen ? "⌃" : "⌄"}
              </span>
            </button>

            {/* Backdrop */}

            {dropdownOpen && (
              <div
                className="shell-backdrop"
                onClick={() => setDropdownOpen(false)}
                aria-hidden="true"
              />
            )}

            {/* Dropdown */}

            {dropdownOpen && (
              <div
                className="shell-dropdown-menu"
                role="menu"
              >
                <div className="shell-dropdown-header">
                  <p className="shell-dropdown-email">
                    {isAuthenticated
                      ? user?.email
                      : "Guest Founder Session"}
                  </p>

                  <span className="shell-dropdown-status">
                    {isSupabaseConnected
                      ? "Supabase Cloud connected"
                      : "Local mode"}
                  </span>
                </div>

                <div className="shell-dropdown-divider" />

                <button
                  type="button"
                  className="shell-dropdown-item"
                  onClick={openHistory}
                >
                  <span className="shell-dropdown-item-left">
                    <HistoryIcon size={14} />
                    Activity Log
                  </span>

                  <span className="shell-segment-counter">
                    {activityCount}
                  </span>
                </button>

                <button
                  type="button"
                  className="shell-dropdown-item"
                  onClick={openSupabase}
                >
                  <span className="shell-dropdown-item-left">
                    <DatabaseIcon size={14} />
                    Supabase Settings
                  </span>
                </button>

                {!isAuthenticated && (
                  <button
                    type="button"
                    className="shell-dropdown-item"
                    onClick={openAuth}
                  >
                    <span className="shell-dropdown-item-left">
                      <UserIcon size={14} />
                      Sign In / Register
                    </span>
                  </button>
                )}

                {isAuthenticated && (
                  <>
                    <div className="shell-dropdown-divider" />

                    <button
                      type="button"
                      className="shell-dropdown-item danger"
                      onClick={() => {
                        setDropdownOpen(false);
                        signOut();
                      }}
                    >
                      <span className="shell-dropdown-item-left">
                        <LogOutIcon size={14} />
                        Sign Out
                      </span>
                    </button>
                  </>
                )}

                {onNavigateToStyleguide && (
                  <>
                    <div className="shell-dropdown-divider" />

                    <button
                      type="button"
                      className="shell-dropdown-item"
                      onClick={() => {
                        setDropdownOpen(false);
                        onNavigateToStyleguide();
                      }}
                    >
                      Styleguide
                    </button>
                  </>
                )}
              </div>
            )}
          </div>

          {/* =================================================
              MOBILE BUTTON
              ================================================= */}

          <button
            type="button"
            className="shell-mobile-menu-btn"
            onClick={() =>
              setMobileMenuOpen((value) => !value)
            }
            aria-label="Toggle navigation menu"
            aria-expanded={mobileMenuOpen}
          >
            {mobileMenuOpen ? (
              <span className="shell-menu-icon">×</span>
            ) : (
              <span className="shell-menu-icon">☰</span>
            )}
          </button>
        </div>
      </div>

      {/* =======================================================
          MOBILE NAVIGATION
          ======================================================= */}

      {mobileMenuOpen && (
        <>
          <div
            className="shell-backdrop"
            onClick={() => setMobileMenuOpen(false)}
            aria-hidden="true"
          />

          <nav
            className="shell-mobile-drawer"
            aria-label="Mobile navigation"
          >
            <div className="shell-mobile-heading">
              <span>Validation Workspace</span>
              <small>KubeSRE Copilot</small>
            </div>

            {navigationSections.map((section) => (
              <button
                key={section.id}
                type="button"
                className={`shell-mobile-nav-item ${
                  activeSection === section.id
                    ? "active"
                    : ""
                }`}
                onClick={() =>
                  handleMobileNavigation(section)
                }
              >
                <span className="shell-mobile-nav-copy">
                  <strong>{section.label}</strong>
                  <small>{section.description}</small>
                </span>

                <span className="shell-mobile-arrow">
                  →
                </span>
              </button>
            ))}

            <div className="shell-dropdown-divider" />

            <button
              type="button"
              className="shell-mobile-nav-item"
              onClick={() => {
                setMobileMenuOpen(false);
                openHistory();
              }}
            >
              <span className="shell-mobile-nav-copy">
                <strong>History</strong>
                <small>
                  Previous validation runs
                </small>
              </span>

              <span className="shell-segment-counter">
                {activityCount}
              </span>
            </button>

            <button
              type="button"
              className="shell-mobile-nav-item"
              onClick={() => {
                setMobileMenuOpen(false);
                onToggleTheme();
              }}
            >
              <span className="shell-mobile-nav-copy">
                <strong>
                  {isDarkMode
                    ? "Light Mode"
                    : "Dark Mode"}
                </strong>

                <small>
                  Change appearance
                </small>
              </span>

              <span className="shell-mobile-theme-indicator">
                {isDarkMode ? "DARK" : "LIGHT"}
              </span>
            </button>

            <button
              type="button"
              className="shell-mobile-nav-item"
              onClick={() => {
                setMobileMenuOpen(false);
                openSupabase();
              }}
            >
              <span className="shell-mobile-nav-copy">
                <strong>Supabase</strong>
                <small>
                  {isSupabaseConnected
                    ? "Cloud connected"
                    : "Connect cloud database"}
                </small>
              </span>

              <span
                className={`shell-status-dot ${
                  isSupabaseConnected
                    ? ""
                    : "shell-status-dot--warning"
                }`}
              />
            </button>

            {!isAuthenticated && (
              <button
                type="button"
                className="shell-mobile-nav-item"
                onClick={() => {
                  setMobileMenuOpen(false);
                  openAuth();
                }}
              >
                <span className="shell-mobile-nav-copy">
                  <strong>Sign In / Register</strong>
                  <small>
                    Access your founder account
                  </small>
                </span>

                <UserIcon size={15} />
              </button>
            )}

            {isAuthenticated && (
              <button
                type="button"
                className="shell-mobile-nav-item danger"
                onClick={() => {
                  setMobileMenuOpen(false);
                  signOut();
                }}
              >
                <span className="shell-mobile-nav-copy">
                  <strong>Sign Out</strong>
                  <small>
                    End your current session
                  </small>
                </span>

                <LogOutIcon size={15} />
              </button>
            )}
          </nav>
        </>
      )}
    </header>
  );
}

export default Navbar;