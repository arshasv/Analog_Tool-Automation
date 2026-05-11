# Brand & Visual Philosophy

**Owner:** Design System  
**Version:** 1.0  
**Scope:** Visual and conceptual foundation for xEDA's identity as a professional EDA tool.

## Purpose

xEDA is not a generic SaaS admin panel. It is **professional circuit design automation software**—used by analog engineers in serious work. The visual language must communicate:

- **Precision:** Every pixel intentional
- **Clarity:** No ambiguity, maximum signal-to-noise
- **Confidence:** Users trust the results
- **Depth:** Professional engineering tool, not toy
- **Efficiency:** Designed for workflow, not admiration

This document defines the **visual and conceptual DNA** of xEDA.

---

## Section 1: Visual Philosophy

### The xEDA Aesthetic

xEDA design draws inspiration from three worlds:

#### 1. Professional EDA Tools
- Dense, information-rich layouts
- Technical readouts and precise measurements
- Dark mode (reduces eye strain for long work sessions)
- Responsive, immediate feedback
- No "flashy" animations that distract from data

**Reference:** Cadence, Synopsys Virtuoso, open-source SPICE tools

#### 2. Modern Observability Platforms
- Real-time monitoring dashboards
- Job queues and status indicators
- Live log streaming
- Graceful error states
- Keyboard-first interaction

**Reference:** Datadog, Grafana, ELK Stack, observability UIs

#### 3. Scientific Workflow Platforms
- Parameter spaces and optimization
- Multi-modal outputs (metrics, plots, raw data)
- Reproducibility and versioning
- Clear cause-and-effect (input → simulation → result)

**Reference:** Jupyter notebooks, scientific computing platforms, physics simulations

### Design Principles

1. **Information Over Decoration**
   - No gradients for the sake of gradients
   - No animations that don't convey meaning
   - Typography should clarify, not ornament

2. **Dark Mode First**
   - xEDA defaults to dark mode
   - Reduces eye strain during long work sessions
   - Improves contrast of technical charts
   - Light mode available as accessibility option

3. **Density Without Clutter**
   - Engineering dashboards are dense by design
   - Use grouping, spacing, and hierarchy to prevent confusion
   - Every UI element must justify its space

4. **Precision in Measurement**
   - All spacing uses modular 4px scale
   - All colors are accessible (WCAG AA minimum)
   - All interactions have explicit timing (motion tokens)
   - All text is anti-aliased and readable at all zoom levels

5. **Keyboard-Centric**
   - Mouse is optional; keyboard is primary
   - All functions accessible via keyboard
   - Focus management is deliberate, never hidden

---

## Section 2: Color Philosophy

### Dark Mode is Default

xEDA uses a dark, high-contrast color palette optimized for technical work.

#### Color Hierarchy

1. **Background Layers** (visual foundation)
   - Canvas (darkest): `#0a0e27` or similar (99% of pixels)
   - Elevated surface: `#1a202c` (cards, panels)
   - Floating UI: `#2d3748` (modals, overlays)

2. **Semantic Status Colors** (functional, not decorative)
   - Success (green): `#10b981` — Simulation complete, parameter valid
   - Running (cyan): `#06b6d4` — Active job, animation in progress
   - Pending (blue): `#3b82f6` — Queued, awaiting action
   - Error (red): `#ef4444` — Failed simulation, invalid input
   - Warning (amber): `#f59e0b` — Convergence slow, unusual values

3. **Text & Borders** (hierarchy & structure)
   - Primary text (white): `#ffffff` — Important information
   - Secondary text (gray-300): `#d1d5db` — Supporting labels
   - Tertiary text (gray-500): `#6b7280` — Disabled, hints
   - Borders (gray-700): `#374151` — Subtle divisions

4. **Technical Colors** (charts & plots)
   - Waveform primary: `#00d9ff` (cyan, high contrast on dark)
   - Waveform secondary: `#a78bfa` (purple, secondary trace)
   - Plot grid: `#374151` (subtle, doesn't dominate)
   - Plot axis: `#9ca3af` (readable but recessive)

### Contrast Rules

- **Text on background:** 7:1 or higher (exceeds WCAG AAA)
- **Text on surface:** 5:1 or higher (WCAG AA+)
- **UI elements:** 3:1 or higher (WCAG AA)
- **Test all colors** in context, not in isolation

### Light Mode (Accessibility)

Light mode uses inverted principles but maintains:
- Same color semantics (green=success, red=error)
- Same contrast standards (WCAG AA minimum)
- Same visual hierarchy (dark text, light backgrounds)

---

## Section 3: Typography Philosophy

### Purpose of Typography

In xEDA, typography is **functional hierarchy**. Type size, weight, and color communicate:
- What is most important?
- What is a label vs. a value?
- What is interactive vs. static?
- What is an error vs. a success?

### Type Scale

All typography uses the 11-level semantic scale from [03-TOKENS.md](03-TOKENS.md):

| Semantic Name | Size | Weight | Use |
|---|---|---|---|
| display | 32–40px | 700 | Page titles, hero states |
| heading-1 | 24–28px | 700 | Section headers |
| heading-2 | 18–20px | 600 | Subsection headers |
| heading-3 | 16px | 600 | Minor headers, tab labels |
| body-lg | 16px | 400 | Primary body text, long-form content |
| body | 14px | 400 | Standard body text, most UI labels |
| body-sm | 12–13px | 400 | Compact UI, dense tables |
| label | 12px | 600 | Form labels, badge text |
| mono-data | 12–14px | 400 | Code, values, SPICE parameters |
| mono-code | 12–13px | 400 | Logs, stack traces, code blocks |
| caption | 11–12px | 400 | Hints, footnotes, timestamps |

### Font Families

#### Primary: System Sans
Use the device's native sans-serif font stack for maximum compatibility and performance:

```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
```

**Why:** Fast to render, native to each OS, excellent accessibility (designed for screen readers)

#### Monospace: For Technical Content
Code, values, SPICE parameters use monospace:

```css
font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, monospace;
```

**Why:** Clear distinction between code and text, easier to scan parameter values, familiar to engineers

### Font Weights

- **700 (Bold):** Headings, labels (minimal use, reserves emphasis)
- **600 (Semibold):** Subheadings, form labels (moderate emphasis)
- **400 (Regular):** Body text, data values (primary)

**Rule:** Avoid stacking weights. Use 400 as base; promote to 600 or 700 only for emphasis.

### Line Height

- **Display:** 1.2 (tight, energetic)
- **Headings:** 1.3 (readable, not too spacious)
- **Body:** 1.5–1.6 (comfortable, long-form readable)
- **Mono:** 1.4 (code needs slight looseness for readability)

### Letter Spacing

- **Display:** +0.5px (slightly spread for visual impact)
- **Body:** 0 (default, natural spacing)
- **Mono:** 0 (monospace already has natural spacing)

---

## Section 4: Spacing & Rhythm

### Design Grid

All spacing uses the modular 4px grid from [03-TOKENS.md](03-TOKENS.md):

```
4px   (1 unit)   —token-spacing-2xs
8px   (2 units)  —token-spacing-xs
12px  (3 units)  —token-spacing-sm
16px  (4 units)  —token-spacing-md
24px  (6 units)  —token-spacing-lg
32px  (8 units)  —token-spacing-xl
48px  (12 units) —token-spacing-2xl
64px  (16 units) —token-spacing-3xl
```

### Spacing Philosophy

- **Tight (8px):** Related controls, form rows, list items in compact mode
- **Medium (16px):** Section breaks, standard form spacing, breathing room
- **Loose (24–32px):** Major section breaks, panel separation
- **Extreme (48–64px):** Page-level margins, full-page breaks

### Proportional Spacing

Content follows the **golden ratio** where possible:
- Section spacing: `24 + 24 + 24` = `72px` (close to `16:9` rhythm)
- Panel heights: Multiples of grid (400px = 100 × 4px grid units)

---

## Section 5: Precision Rules

### Pixel-Perfect Implementation

1. **Alignment:** All elements align to 4px grid
2. **Borders:** 1px (hardware pixel on 1× displays)
3. **Shadows:** Subtle (avoid drop shadows; use elevation with color tint)
4. **Curves:** Use CSS border-radius (no custom graphics)
5. **Icons:** 20×20px, 24×24px, or 32×32px (multiples of 4)

### No Decorative Effects

- ❌ Gradients (unless functional)
- ❌ Glows or halos
- ❌ Skew or rotation
- ❌ Heavy shadows
- ✅ Solid colors
- ✅ Subtle borders
- ✅ Clear typography
- ✅ High contrast

### Responsive Precision

- **Desktop (1920px):** Full 16px padding, multi-column layouts
- **Tablet (1024px):** Reduced to 12px padding, 2-column where possible
- **Mobile (375px):** Reduced to 8px padding, single-column, touch targets 44×44px

---

## Section 6: Motion & Interaction Philosophy

### Motion Has Meaning

All motion from [motion.md](motion.md) serves a purpose:

1. **Transitions (240ms):** State change is visible
2. **Interactions (120–360ms):** User's action is acknowledged
3. **Loading (2s pulse):** System is working
4. **Errors (120ms shake):** Attention required

### No Decorative Motion

- ❌ Continuous animations (parallax, bouncing)
- ❌ Multiple simultaneous animations
- ❌ Slow, lingering transitions
- ✅ Quick, decisive transitions
- ✅ Purpose-driven animations
- ✅ Respectful of prefers-reduced-motion

---

## Section 7: Component Style Foundation

### Button Styling

**Base:**
- Padding: 10px 16px (44px height in comfortable density)
- Border-radius: `var(--radius-md)` (6px)
- Font-weight: 600 (semibold, scannable)
- Cursor: pointer

**Variants:**
- **Primary (Action):** Solid background (semantic color), white text
- **Secondary (Alternative):** Outline (border + transparent bg)
- **Tertiary (Subtle):** Text-only, no border
- **Disabled:** Gray text, no pointer, low opacity (0.5)

**States:**
- Hover: Lighten background 5%, cursor pointer
- Focus: 2px outline ring (accessible)
- Active: Darken background 10%
- Loading: Replace text with spinner, disable interaction

### Form Field Styling

**Input Fields:**
- Padding: 8px 12px (36px height)
- Border: 1px solid `token-border-strong`
- Border-radius: `var(--radius-sm)` (4px)
- Focus: 2px outline ring, border color to `token-border-interactive`
- Background: `token-surface` (elevated)

**Labels:**
- Font-weight: 600 (semibold)
- Color: `token-text-primary`
- Margin-bottom: 8px
- Required marker: Red asterisk (*) or "required"

### Card/Panel Styling

**Base:**
- Background: `token-surface` (elevated)
- Border: 1px solid `token-border` (subtle)
- Border-radius: `var(--radius-md)` (6px)
- Padding: 16–24px (breathing room)
- Shadow: None (flat design) or subtle elevation with color tint

---

## Section 8: Implementation Guardrails

### CSS Constraint Rules

```css
/* MUST-HAVES */
:root {
  /* Color scale must use semantic tokens */
  --token-background: #0a0e27;
  --token-surface: #1a202c;
  /* ... (see 03-TOKENS.md) */
  
  /* Spacing must use modular 4px scale */
  --spacing-2xs: 4px;
  --spacing-xs: 8px;
  /* ... (see 03-TOKENS.md) */
  
  /* Motion timing must use token durations */
  --duration-fast: 120ms;
  --duration-medium: 240ms;
  /* ... (see motion.md) */
}

/* Every component must use tokens, NOT hardcoded colors/spacing */
.button {
  /* ✅ CORRECT */
  background: var(--token-primary);
  padding: var(--spacing-md);
  
  /* ❌ WRONG */
  background: #3b82f6;
  padding: 16px;
}
```

### Component Consistency

- Every button uses button token library
- Every input uses input token library
- Every modal follows modal pattern (fade + slide)
- Every status badge uses status token colors

---

## Section 9: Brand Dos and Don'ts

### ✅ DO

- Use dark mode as primary experience
- Respect user's motion preferences
- Prioritize clarity over visual flash
- Make every interaction keyboard-accessible
- Test contrast on actual devices
- Use semantic colors (green=success, red=error)
- Create focused, scannable layouts
- Let data be the hero
- Respect the 4px grid
- Use subtle, purposeful motion

### ❌ DON'T

- Add decorative gradients or effects
- Animate for the sake of animation
- Use color alone to communicate status
- Require mouse for any function
- Break alignment to the 4px grid
- Use more than 2–3 font weights
- Hide important controls behind unnecessary clicks
- Make layouts so dense they're unreadable
- Add unnecessary shadows or depth
- Assume users can perceive all colors

---

## Section 10: Brand Checklist

- [ ] Dark mode is default, light mode is option
- [ ] All colors meet WCAG AA contrast minimum
- [ ] Typography uses semantic scale, not arbitrary sizes
- [ ] Spacing aligns to 4px grid
- [ ] All components keyboard accessible
- [ ] Icons are clear and consistent
- [ ] Motion respects prefers-reduced-motion
- [ ] No decorative effects (gradients, shadows)
- [ ] Button and form field styling consistent
- [ ] Error and success states are visually distinct and semantic
- [ ] Layouts are responsive but dense, not bloated
- [ ] Code uses token variables, never hardcoded values

---

This document is the **visual constitution** of xEDA. All design decisions must be justified against these principles.
