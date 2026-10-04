// Place this file at: client/src/components/Footer.jsx
//
// Minimal single-bar footer matching the Navbar's pill-badge style
// (brand mark, version badge, rounded pill, Montserrat / tokens.css).
//
// Add to StartupValidator.jsx right before the closing </main> tag:
//   import Footer from "../components/Footer";
//   ... <Footer />  (right before </main>)

const CURRENT_YEAR = new Date().getFullYear();

export default function Footer() {
  return (
    <footer className="nexus-footer-minimal">
      <div className="footer-minimal-inner">

        <div className="footer-minimal-brand">
          <span className="footer-mark">N</span>
          <span className="footer-brand-name">NEXUS</span>
          <span className="footer-version-badge">V2.5</span>
        </div>

        <div className="footer-minimal-right">
          <a
            href="https://opensource.org/licenses/MIT"
            target="_blank"
            rel="noopener noreferrer"
            className="footer-pill"
          >
            <span className="footer-pill-dot" />
            MIT License
          </a>
          <span className="footer-copy">
            © {CURRENT_YEAR} NEXUS AI. All rights reserved.
          </span>
        </div>

      </div>

      <style>{`
        .nexus-footer-minimal {
          font-family: var(--font-family-base) !important;
          border-top: 1px solid var(--surface-border);
          background: var(--surface);
          padding: var(--space-4) var(--space-6);
        }
        .footer-minimal-inner {
          max-width: 1200px;
          margin: 0 auto;
          display: flex;
          align-items: center;
          justify-content: space-between;
          flex-wrap: wrap;
          gap: var(--space-3);
        }
        .footer-minimal-brand {
          display: flex;
          align-items: center;
          gap: var(--space-2);
        }
        .footer-mark {
          width: 22px;
          height: 22px;
          border-radius: 6px;
          background: var(--brand-gradient);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 11px;
          font-weight: 700;
          color: #0B0B0E;
        }
        .footer-brand-name {
          font-size: 13px;
          font-weight: 700;
          letter-spacing: 0.01em;
          color: var(--text-primary);
        }
        .footer-version-badge {
          font-size: 10px;
          font-weight: 600;
          color: var(--text-tertiary);
          background: var(--surface-2);
          border: 1px solid var(--surface-border);
          border-radius: var(--radius-sm);
          padding: 2px 6px;
        }
        .footer-minimal-right {
          display: flex;
          align-items: center;
          gap: var(--space-4);
          flex-wrap: wrap;
        }
        .footer-pill {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          font-size: 11px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.06em;
          color: var(--accent-idea);
          background: rgba(255, 199, 44, 0.08);
          border: 1px solid rgba(255, 199, 44, 0.25);
          border-radius: 999px;
          padding: 5px 12px;
          text-decoration: none;
          transition: background var(--transition-fast);
        }
        .footer-pill:hover {
          background: rgba(255, 199, 44, 0.14);
        }
        .footer-pill-dot {
          width: 5px;
          height: 5px;
          border-radius: 50%;
          background: var(--accent-idea);
        }
        .footer-copy {
          font-size: 11.5px;
          color: var(--text-tertiary);
        }
        @media (max-width: 560px) {
          .footer-minimal-inner {
            flex-direction: column;
            align-items: flex-start;
          }
        }
      `}</style>
    </footer>
  );
}