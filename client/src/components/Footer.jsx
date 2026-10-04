const CURRENT_YEAR = new Date().getFullYear();

export default function Footer() {
  return (
    <footer className="app-footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <span className="footer-logo">NEXUS AI</span>
          <span className="footer-tagline">Startup Intelligence Platform</span>
        </div>

        <div className="footer-license">
          <p>
            © {CURRENT_YEAR} NEXUS AI. All rights reserved.
          </p>
          <p>
            Licensed under the{" "}
            <a
              href="https://opensource.org/licenses/MIT"
              target="_blank"
              rel="noopener noreferrer"
            >
              MIT License
            </a>
            .
          </p>
          <p className="footer-disclaimer">
            AI-generated analysis is for informational purposes only and does not
            constitute financial, legal, or business advice.
          </p>
        </div>
      </div>

      <style>{`
        .app-footer {
          margin-top: 48px;
          padding: 28px 24px;
          border-top: 1px solid var(--border, #38342e);
          background: var(--card, #1c1a17);
        }
        .footer-inner {
          max-width: 1100px;
          margin: 0 auto;
          display: flex;
          flex-wrap: wrap;
          justify-content: space-between;
          align-items: flex-start;
          gap: 20px;
        }
        .footer-brand {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }
        .footer-logo {
          font-family: "Outfit", sans-serif;
          font-size: 1rem;
          font-weight: 700;
          color: var(--gold, #e8c77b);
          letter-spacing: 0.02em;
        }
        .footer-tagline {
          font-family: "Outfit", sans-serif;
          font-size: 0.78rem;
          color: var(--secondary, #a9a39a);
        }
        .footer-license {
          font-family: "Outfit", sans-serif;
          text-align: right;
        }
        .footer-license p {
          margin: 0 0 4px 0;
          font-size: 0.8rem;
          color: var(--secondary, #a9a39a);
        }
        .footer-license a {
          color: #e28743;
          text-decoration: none;
        }
        .footer-license a:hover {
          text-decoration: underline;
        }
        .footer-disclaimer {
          margin-top: 8px !important;
          font-size: 0.72rem !important;
          color: var(--muted, #777169) !important;
          max-width: 420px;
          line-height: 1.4;
        }
        @media (max-width: 600px) {
          .footer-inner {
            flex-direction: column;
            text-align: left;
          }
          .footer-license {
            text-align: left;
          }
          .footer-disclaimer {
            max-width: 100%;
          }
        }
      `}</style>
    </footer>
  );
}