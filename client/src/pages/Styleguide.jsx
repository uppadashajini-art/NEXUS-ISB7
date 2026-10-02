import React, { useState } from 'react';
import {
  Button,
  Card,
  Badge,
  Input,
  Textarea,
  Tag,
  Tooltip,
} from '../components/primitives';

export default function Styleguide({ onNavigateToApp }) {
  const [inputValue, setInputValue] = useState('');
  const [textareaValue, setTextareaValue] = useState('');
  const [selectedTag, setSelectedTag] = useState('DevOps');
  const [tagsList, setTagsList] = useState(['B2B SaaS', 'DevOps', 'HealthTech', 'FinTech']);

  const handleDismissTag = (tagToRemove) => {
    setTagsList(tagsList.filter((t) => t !== tagToRemove));
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--surface-bg)', color: 'var(--text-primary)' }}>
      {/* Header */}
      <header
        style={{
          borderBottom: '1px solid var(--surface-border)',
          background: 'var(--surface)',
          position: 'sticky',
          top: 0,
          zIndex: 100,
        }}
      >
        <div
          style={{
            maxWidth: '1200px',
            margin: '0 auto',
            padding: 'var(--space-3) var(--space-6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <img
              src="/logo.png"
              alt="NEXUS"
              style={{ width: '28px', height: '28px', objectFit: 'contain' }}
            />
            <span style={{ fontWeight: 700, fontSize: '16px', letterSpacing: '-0.01em' }}>
              NEXUS AI
            </span>
            <span
              style={{
                fontSize: '11px',
                fontFamily: 'var(--font-family-base)',
                background: 'var(--surface-2)',
                border: '1px solid var(--surface-border)',
                padding: '2px 8px',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--text-tertiary)',
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
                fontWeight: 600,
              }}
            >
              Design System Foundation
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <Button
              variant="secondary"
              size="sm"
              onClick={onNavigateToApp}
            >
              Back to Application
            </Button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: 'var(--space-10) var(--space-6) var(--space-16)',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-12)',
        }}
      >
        {/* Intro */}
        <div>
          <span className="type-label">FOUNDATION TOKENS & PRIMITIVES</span>
          <h1 className="type-display" style={{ marginTop: 'var(--space-2)' }}>
            Enterprise Design System
          </h1>
          <p className="type-body" style={{ marginTop: 'var(--space-2)', maxWidth: '680px' }}>
            Restrained, minimal, high-density component primitives built on a single font family (Montserrat),
            structured surfaces, explicit type scale, and accessible focus states.
          </p>
        </div>

        {/* 1. TYPOGRAPHY SCALE */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          <div>
            <span className="type-label">01 / TYPOGRAPHY</span>
            <h2 className="type-h2" style={{ marginTop: 'var(--space-1)' }}>
              Type Scale
            </h2>
            <p className="type-body" style={{ fontSize: '13px' }}>
              Single font family (Montserrat) applied to html, body, headings, and all form controls.
            </p>
          </div>

          <Card variant="surface" elevation={1} padding="lg">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
              <div>
                <span className="type-label">Display (48px / 56px - 700)</span>
                <div className="type-display">Autonomous Market Intelligence</div>
              </div>

              <div>
                <span className="type-label">H1 (32px / 40px - 700)</span>
                <div className="type-h1">Market Demand & Competitor Radar</div>
              </div>

              <div>
                <span className="type-label">H2 (20px / 28px - 600)</span>
                <div className="type-h2">Target Customer Segments & Unit Economics</div>
              </div>

              <div>
                <span className="type-label">Body (15px / 24px - 400)</span>
                <div className="type-body">
                  NEXUS validates early-stage startup assumptions using real-time search data and competitor heuristics.
                  Built with disciplined enterprise SaaS tokens, zero diffuse glows, and functional typography.
                </div>
              </div>

              <div>
                <span className="type-label">Label (11px / 16px - 600 uppercase tracking 0.08em)</span>
                <div className="type-label" style={{ color: 'var(--text-primary)', marginTop: 'var(--space-1)' }}>
                  TECHNICAL FEASIBILITY MATRIX
                </div>
              </div>
            </div>
          </Card>
        </section>

        {/* 2. DESIGN TOKENS & ACCENTS */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          <div>
            <span className="type-label">02 / COLOR & ELEVATIONS</span>
            <h2 className="type-h2" style={{ marginTop: 'var(--space-1)' }}>
              Surfaces, Accents & Brand Gradient
            </h2>
          </div>

          {/* Surfaces */}
          <div>
            <span className="type-label" style={{ display: 'block', marginBottom: 'var(--space-3)' }}>
              SURFACES & BORDERS
            </span>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 'var(--space-4)' }}>
              <div
                style={{
                  background: 'var(--surface-bg)',
                  border: '1px solid var(--surface-border)',
                  borderRadius: 'var(--radius-md)',
                  padding: 'var(--space-4)',
                }}
              >
                <div style={{ fontWeight: 600, fontSize: '13px' }}>Background</div>
                <div style={{ fontSize: '12px', color: 'var(--text-tertiary)', marginTop: '2px' }}>#0B0B0E</div>
              </div>

              <div
                style={{
                  background: 'var(--surface)',
                  border: '1px solid var(--surface-border)',
                  borderRadius: 'var(--radius-md)',
                  padding: 'var(--space-4)',
                }}
              >
                <div style={{ fontWeight: 600, fontSize: '13px' }}>Surface</div>
                <div style={{ fontSize: '12px', color: 'var(--text-tertiary)', marginTop: '2px' }}>#121217</div>
              </div>

              <div
                style={{
                  background: 'var(--surface-2)',
                  border: '1px solid var(--surface-border)',
                  borderRadius: 'var(--radius-md)',
                  padding: 'var(--space-4)',
                }}
              >
                <div style={{ fontWeight: 600, fontSize: '13px' }}>Surface-2</div>
                <div style={{ fontSize: '12px', color: 'var(--text-tertiary)', marginTop: '2px' }}>#17171E</div>
              </div>

              <div
                style={{
                  background: 'var(--surface)',
                  border: '1px solid var(--surface-border-strong)',
                  borderRadius: 'var(--radius-md)',
                  padding: 'var(--space-4)',
                }}
              >
                <div style={{ fontWeight: 600, fontSize: '13px' }}>Border</div>
                <div style={{ fontSize: '12px', color: 'var(--text-tertiary)', marginTop: '2px' }}>rgba(255,255,255,0.07)</div>
              </div>
            </div>
          </div>

          {/* Brand Gradient */}
          <div>
            <span className="type-label" style={{ display: 'block', marginBottom: 'var(--space-3)' }}>
              BRAND GRADIENT (#FFC72C → #FF8A1F → #F23D5C)
            </span>
            <div
              style={{
                height: '48px',
                borderRadius: 'var(--radius-md)',
                background: 'var(--brand-gradient)',
                border: '1px solid rgba(255, 255, 255, 0.15)',
              }}
            />
          </div>

          {/* Domain Accents */}
          <div>
            <span className="type-label" style={{ display: 'block', marginBottom: 'var(--space-3)' }}>
              DOMAIN ACCENT TOKENS
            </span>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: 'var(--space-3)' }}>
              {[
                { name: 'Idea', hex: '#FFC72C', var: '--accent-idea' },
                { name: 'Market', hex: '#FF8A1F', var: '--accent-market' },
                { name: 'Customer', hex: '#FF5A4E', var: '--accent-customer' },
                { name: 'Competitor', hex: '#F23D5C', var: '--accent-competitor' },
                { name: 'Feasibility', hex: '#2DD4BF', var: '--accent-feasibility' },
                { name: 'Advisory', hex: '#8B7CF6', var: '--accent-advisory' },
              ].map((accent) => (
                <div
                  key={accent.name}
                  style={{
                    background: 'var(--surface)',
                    border: '1px solid var(--surface-border)',
                    borderRadius: 'var(--radius-sm)',
                    padding: 'var(--space-3)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--space-3)',
                  }}
                >
                  <div
                    style={{
                      width: '16px',
                      height: '16px',
                      borderRadius: '4px',
                      backgroundColor: `var(${accent.var})`,
                    }}
                  />
                  <div>
                    <div style={{ fontSize: '13px', fontWeight: 600 }}>{accent.name}</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>{accent.hex}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Elevation Levels */}
          <div>
            <span className="type-label" style={{ display: 'block', marginBottom: 'var(--space-3)' }}>
              THREE ELEVATION LEVELS (ARCHITECTURAL & RESTRAINED)
            </span>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-4)' }}>
              <Card variant="surface" elevation={1} padding="md">
                <div className="type-label">Elevation 1</div>
                <div style={{ fontSize: '13px', fontWeight: 600, marginTop: 'var(--space-1)' }}>
                  Subtle Resting Layer
                </div>
                <p className="type-body" style={{ fontSize: '12px', marginTop: 'var(--space-1)' }}>
                  0 1px 2px rgba(0,0,0,0.35)
                </p>
              </Card>

              <Card variant="surface" elevation={2} padding="md">
                <div className="type-label">Elevation 2</div>
                <div style={{ fontSize: '13px', fontWeight: 600, marginTop: 'var(--space-1)' }}>
                  Hover & Dropdown Layer
                </div>
                <p className="type-body" style={{ fontSize: '12px', marginTop: 'var(--space-1)' }}>
                  0 4px 12px rgba(0,0,0,0.45)
                </p>
              </Card>

              <Card variant="surface" elevation={3} padding="md">
                <div className="type-label">Elevation 3</div>
                <div style={{ fontSize: '13px', fontWeight: 600, marginTop: 'var(--space-1)' }}>
                  Modal & Dialog Layer
                </div>
                <p className="type-body" style={{ fontSize: '12px', marginTop: 'var(--space-1)' }}>
                  0 12px 32px rgba(0,0,0,0.60)
                </p>
              </Card>
            </div>
          </div>
        </section>

        {/* 3. BUTTONS */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          <div>
            <span className="type-label">03 / BUTTON PRIMITIVE</span>
            <h2 className="type-h2" style={{ marginTop: 'var(--space-1)' }}>
              Button Variants & States
            </h2>
            <p className="type-body" style={{ fontSize: '13px' }}>
              Primary (brand gradient with dark text), Secondary (surface-2), and Ghost. Includes 2px accent focus-visible ring.
            </p>
          </div>

          <Card variant="surface" elevation={1} padding="lg">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
              {/* Row: Variants */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', flexWrap: 'wrap' }}>
                <Button variant="primary">Primary Action</Button>
                <Button variant="secondary">Secondary Action</Button>
                <Button variant="ghost">Ghost Action</Button>
                <Button variant="primary" disabled>
                  Disabled Primary
                </Button>
                <Button variant="secondary" disabled>
                  Disabled Secondary
                </Button>
              </div>

              {/* Row: Sizes */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', flexWrap: 'wrap' }}>
                <Button variant="secondary" size="sm">
                  Small (32px)
                </Button>
                <Button variant="secondary" size="md">
                  Medium (40px)
                </Button>
                <Button variant="secondary" size="lg">
                  Large (48px)
                </Button>
                <Button variant="primary" size="lg">
                  Large Primary
                </Button>
              </div>
            </div>
          </Card>
        </section>

        {/* 4. BADGES & TAGS */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          <div>
            <span className="type-label">04 / BADGES & TAGS</span>
            <h2 className="type-h2" style={{ marginTop: 'var(--space-1)' }}>
              Status Badges & Categorization Tags
            </h2>
          </div>

          <Card variant="surface" elevation={1} padding="lg">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
              {/* Badges */}
              <div>
                <span className="type-label" style={{ display: 'block', marginBottom: 'var(--space-3)' }}>
                  DOMAIN ACCENT BADGES
                </span>
                <div style={{ display: 'flex', gap: 'var(--space-3)', flexWrap: 'wrap' }}>
                  <Badge variant="idea">Idea Synthesis</Badge>
                  <Badge variant="market">Market Dynamics</Badge>
                  <Badge variant="customer">Customer ICP</Badge>
                  <Badge variant="competitor">Competitor Moat</Badge>
                  <Badge variant="feasibility">Feasibility 92/100</Badge>
                  <Badge variant="advisory">Advisory Engine</Badge>
                  <Badge variant="neutral">Neutral Status</Badge>
                </div>
              </div>

              {/* Tags */}
              <div>
                <span className="type-label" style={{ display: 'block', marginBottom: 'var(--space-3)' }}>
                  INTERACTIVE & DISMISSABLE TAGS
                </span>
                <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap' }}>
                  {tagsList.map((tag) => (
                    <Tag
                      key={tag}
                      selected={selectedTag === tag}
                      onClick={() => setSelectedTag(tag)}
                      onDismiss={() => handleDismissTag(tag)}
                    >
                      {tag}
                    </Tag>
                  ))}
                  <Tag onClick={() => alert('New tag added')}>+ Add Tag</Tag>
                </div>
              </div>
            </div>
          </Card>
        </section>

        {/* 5. FORM CONTROLS: INPUT & TEXTAREA */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          <div>
            <span className="type-label">05 / FORM CONTROLS</span>
            <h2 className="type-h2" style={{ marginTop: 'var(--space-1)' }}>
              Input & Textarea
            </h2>
            <p className="type-body" style={{ fontSize: '13px' }}>
              Clean borders, Montserrat font inheritance, error states, and 2px accent focus-visible ring.
            </p>
          </div>

          <Card variant="surface" elevation={1} padding="lg">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-6)' }}>
              <Input
                label="Startup Idea Title"
                placeholder="e.g. Autonomous AI Site Reliability Engineer"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                helperText="Enter a concise product or service title."
                required
              />

              <Input
                label="Target Domain"
                placeholder="e.g. Cloud Infrastructure"
                disabled
                helperText="Disabled field state."
              />

              <Input
                label="Validation Error State"
                defaultValue="invalid_input_format"
                error="Domain must contain at least 3 alphanumeric characters."
              />

              <div style={{ gridColumn: '1 / -1' }}>
                <Textarea
                  label="Product Concept & Problem Description"
                  placeholder="Describe the target customer problem, business model, and value proposition..."
                  value={textareaValue}
                  onChange={(e) => setTextareaValue(e.target.value)}
                  rows={4}
                  helperText="Specific niche problems produce higher fidelity benchmark results."
                  required
                />
              </div>
            </div>
          </Card>
        </section>

        {/* 6. TOOLTIP */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          <div>
            <span className="type-label">06 / TOOLTIP PRIMITIVE</span>
            <h2 className="type-h2" style={{ marginTop: 'var(--space-1)' }}>
              Accessible Tooltip
            </h2>
            <p className="type-body" style={{ fontSize: '13px' }}>
              Triggers on hover and keyboard focus. Rendered with Elevation-2 and 150ms motion timing.
            </p>
          </div>

          <Card variant="surface" elevation={1} padding="lg">
            <div style={{ display: 'flex', gap: 'var(--space-6)', flexWrap: 'wrap', alignItems: 'center' }}>
              <Tooltip content="Tooltip placed on top" position="top">
                <Button variant="secondary" size="md">
                  Hover Top
                </Button>
              </Tooltip>

              <Tooltip content="Tooltip placed on bottom" position="bottom">
                <Button variant="secondary" size="md">
                  Hover Bottom
                </Button>
              </Tooltip>

              <Tooltip content="Tooltip placed on left" position="left">
                <Button variant="secondary" size="md">
                  Hover Left
                </Button>
              </Tooltip>

              <Tooltip content="Tooltip placed on right" position="right">
                <Button variant="secondary" size="md">
                  Hover Right
                </Button>
              </Tooltip>
            </div>
          </Card>
        </section>

        {/* 7. BRAND MARK */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          <div>
            <span className="type-label">07 / BRAND MARK</span>
            <h2 className="type-h2" style={{ marginTop: 'var(--space-1)' }}>
              Official Brand Mark
            </h2>
            <p className="type-body" style={{ fontSize: '13px' }}>
              Utilizes /logo.png as the favicon and header brand icon.
            </p>
          </div>

          <Card variant="surface" elevation={1} padding="lg">
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-6)' }}>
              <div
                style={{
                  width: '64px',
                  height: '64px',
                  borderRadius: 'var(--radius-md)',
                  background: 'var(--surface-2)',
                  border: '1px solid var(--surface-border)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <img
                  src="/logo.png"
                  alt="NEXUS Brand Mark"
                  style={{ width: '48px', height: '48px', objectFit: 'contain' }}
                />
              </div>

              <div>
                <div className="type-h2" style={{ fontSize: '18px' }}>
                  NEXUS AI
                </div>
                <div className="type-body" style={{ fontSize: '13px' }}>
                  Market & Competitor Analysis Engine for Founders
                </div>
                <div className="type-label" style={{ marginTop: '4px' }}>
                  Asset: /logo.png • Favicon: Active
                </div>
              </div>
            </div>
          </Card>
        </section>
      </main>
    </div>
  );
}
