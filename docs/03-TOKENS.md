# 03 Tokens

**Owner:** Design System  
**Version:** 1.0  
**Scope:** Semantic design token definitions and inventory.

## Purpose

Design tokens are the **semantic, reusable foundation** of the xEDA visual system. They decouple meaning from implementation, allowing themes to change appearance without affecting component logic.

Every visual property—color, spacing, motion, elevation—must reference a token. Hardcoded values are forbidden.

---

## Section 1: Color Tokens (Semantic)

### Status & State Colors

These represent job and component states.

```css
/* Job lifecycle states */
--token-pending:        /* Neutral blue, job is queued */
--token-running:        /* Bright cyan, simulation/optimization in progress */
--token-completed:      /* Green, job finished successfully */
--token-failed:         /* Red, job encountered an error */

/* Component interaction states */
--token-success:        /* Green, validation pass, affirmative action */
--token-warning:        /* Orange/yellow, non-critical alert */
--token-error:          /* Red, critical alert, invalid input */
--token-info:           /* Blue/cyan, informational message */

/* Optimization-specific */
--token-optimizing:     /* Bright cyan (same as running) */
--token-optimization-complete: /* Green (same as completed) */

/* Component states */
--token-disabled:       /* Gray/muted, unusable state */
--token-loading:        /* Neutral blue (same as pending) */
```

### UI Foundation Colors

```css
/* Background and surface layers */
--token-background:          /* Page background, darkest surface */
--token-background-secondary: /* Subtle background, secondary areas */
--token-surface:             /* Primary card/panel surface */
--token-surface-hover:       /* Surface on hover (darker/lighter by theme) */
--token-surface-active:      /* Surface on click/active state */
--token-surface-secondary:   /* Secondary panel surface (skeleton, divider) */

/* Text hierarchy */
--token-text-primary:        /* Main body text, highest contrast */
--token-text-secondary:      /* Labels, metadata, lower contrast */
--token-text-tertiary:       /* Hints, disabled text, lowest contrast */
--token-text-inverse:        /* Text on accent backgrounds */

/* Borders and dividers */
--token-border-subtle:       /* Faint dividers, low emphasis */
--token-border-strong:       /* Card borders, element separation */
--token-border-interactive:  /* Focus rings, interactive elements */

/* Accent and interaction */
--token-accent:              /* Primary action color, interactive */
--token-accent-strong:       /* Stronger accent, emphasis */
--token-accent-hover:        /* Accent on hover state */
```

### Chart and Visualization Colors

```css
/* Waveform and signal display */
--token-waveform-primary:     /* Primary signal line (e.g., Vout) */
--token-waveform-secondary:   /* Secondary signal line (e.g., Vin) */
--token-waveform-tertiary:    /* Tertiary signal for overlay */

/* Plot infrastructure */
--token-plot-grid:            /* Grid lines on charts */
--token-plot-axis:            /* Axis lines and labels */
--token-plot-background:      /* Chart background */

/* Failure and success regions */
--token-failure-region:       /* Region marking out-of-spec (red/pink) */
--token-success-region:       /* Region marking in-spec (green) */
--token-warning-region:       /* Region marking marginal (orange) */
```

### Overlay and Glass

```css
--token-modal-backdrop:       /* Dimmed overlay behind modals */
--token-glass-surface:        /* Semi-transparent overlay surface */
--token-glass-surface-strong: /* Higher opacity glass */
```

---

## Section 2: Typography Tokens

### Type Scale

```css
/* Display level (hero, major headings) */
--typography-display:        /* Largest: 42–96px, line-height 0.98 */
--typography-heading-1:      /* H1: 32–40px, line-height 1.1 */
--typography-heading-2:      /* H2: 24–28px, line-height 1.2 */
--typography-heading-3:      /* H3: 18–20px, line-height 1.3 */

/* Body and UI text */
--typography-body-lg:        /* Large body: 16–18px */
--typography-body:           /* Default body: 14–16px */
--typography-body-sm:        /* Small body: 12–13px */

/* Labels and metadata */
--typography-label-lg:       /* Large label: 14px, semi-bold */
--typography-label:          /* Default label: 12px, semi-bold */
--typography-label-sm:       /* Small label: 11px, semi-bold */

/* Monospace (numeric data, code) */
--typography-mono-data:      /* Monospace for parameters, values */
--typography-mono-code:      /* Monospace for code blocks */

/* Engineering-specific */
--typography-engineering-value: /* Numeric values in tables/forms */
--typography-engineering-unit:  /* Units and suffixes */
```

### Font Weight

```css
--font-weight-regular:  400   /* Body text, default */
--font-weight-medium:   500   /* Slightly emphasized */
--font-weight-semibold: 600   /* Labels, headings, emphasis */
--font-weight-bold:     700   /* Strong emphasis */
```

### Line Height

```css
--line-height-tight:    1.0   /* Display, headings */
--line-height-normal:   1.5   /* Body text */
--line-height-relaxed:  1.75  /* Large body, lists */
```

### Font Family

```css
/* UI and body text */
--font-family-ui: system-ui, -apple-system, "Segoe UI", sans-serif;

/* Monospace for technical data */
--font-family-mono: "Fira Code", "Monaco", "Courier New", monospace;
```

---

## Section 3: Spacing Tokens

Use a **modular scale** based on 4px increments.

```css
--spacing-2xs:  4px   /* Tight spacing, element internals */
--spacing-xs:   8px   /* Close spacing, related elements */
--spacing-sm:   12px  /* Small margin, item separation */
--spacing-md:   16px  /* Medium margin, section spacing */
--spacing-lg:   24px  /* Large margin, major sections */
--spacing-xl:   32px  /* Extra large, page-level spacing */
--spacing-2xl:  48px  /* Double extra large, major layout shifts */
--spacing-3xl:  64px  /* Maximum spacing for full-page margins */
```

**Usage:**
- Component internals (padding): `--spacing-xs` to `--spacing-md`
- Between components (margin): `--spacing-md` to `--spacing-lg`
- Section breaks: `--spacing-lg` to `--spacing-xl`
- Page margins: `--spacing-xl` to `--spacing-2xl`

---

## Section 4: Radius Tokens

```css
--radius-sm:    4px   /* Subtle rounding, inputs */
--radius-md:    8px   /* Standard rounding, buttons, cards */
--radius-lg:    12px  /* Strong rounding, larger cards */
--radius-full:  9999px /* Pills, fully rounded shapes */
```

---

## Section 5: Elevation / Shadow Tokens

```css
/* Subtle shadows for depth */
--shadow-sm:   0 2px 4px rgba(0, 0, 0, 0.08);
--shadow-md:   0 4px 8px rgba(0, 0, 0, 0.12);
--shadow-lg:   0 8px 16px rgba(0, 0, 0, 0.16);
--shadow-xl:   0 16px 32px rgba(0, 0, 0, 0.20);

/* Glass morphism (semi-transparent with blur) */
--glass-blur:  12px;
--glass-opacity: 0.8;
```

---

## Section 6: Motion Tokens

See [motion.md](motion.md) for full motion governance.

```css
/* Duration tokens (milliseconds) */
--duration-instant:  0ms
--duration-fast:     120ms
--duration-medium:   240ms
--duration-slow:     360ms

/* Easing functions */
--easing-standard:     cubic-bezier(0.4, 0, 0.2, 1);
--easing-emphasized:   cubic-bezier(0.05, 0.7, 0.1, 1);
--easing-decelerate:   cubic-bezier(0, 0, 0.2, 1);
```

---

## Section 7: Density Tokens

The dashboard supports three density modes for different use cases.

```css
/* Compact: High information density, professional analysis */
--density-compact: {
  row-height: 28px;
  padding: var(--spacing-xs);
  gap: var(--spacing-2xs);
}

/* Comfortable: Balanced, default mode */
--density-comfortable: {
  row-height: 36px;
  padding: var(--spacing-sm);
  gap: var(--spacing-xs);
}

/* Expanded: Accessible, touch-friendly */
--density-expanded: {
  row-height: 44px;
  padding: var(--spacing-md);
  gap: var(--spacing-sm);
}
```

---

## Section 8: Layout & Responsive Tokens

```css
/* Max content width */
--max-width-narrow:   800px   /* Focused single-column */
--max-width-standard: 1200px  /* Default */
--max-width-wide:     1400px  /* Analysis and wide screens */
--max-width-ultra:    1600px  /* Full-width data dashboards */

/* Breakpoints */
--breakpoint-mobile:  640px   /* Small phones */
--breakpoint-tablet:  1024px  /* Tablets and small laptops */
--breakpoint-laptop:  1280px  /* Laptops and desktops */
--breakpoint-ultra:   1600px  /* Workstations and monitors */
```

---

## Section 9: Focus and Interaction Tokens

```css
/* Focus ring appearance */
--focus-ring-width: 2px;
--focus-ring-offset: 2px;
--focus-ring-color: var(--token-border-interactive);

/* Hover overlay opacity */
--hover-overlay-opacity: 0.06;

/* Active/pressed state opacity */
--active-overlay-opacity: 0.12;

/* Disabled state opacity */
--disabled-opacity: 0.5;
```

---

## Section 10: Using Tokens (Implementation Rules)

### ✅ Correct
```css
button {
  background-color: var(--token-accent);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  transition: background-color var(--duration-fast) var(--easing-standard);
}
```

### ❌ Incorrect
```css
button {
  background-color: #0084ff;        /* Hardcoded color */
  padding: 12px 16px;               /* Hardcoded spacing */
  border-radius: 8px;               /* Hardcoded radius */
  transition: all 0.3s ease-in-out; /* Hardcoded motion */
}
```

---

## Section 11: Token Naming Convention

### Pattern: `--{category}-{semantic}-{variant}`

```
--token-success              /* Base semantic token */
--token-success-hover        /* Variant for hover state */
--token-success-disabled     /* Variant for disabled state */

--typography-body            /* Base typography token */
--typography-body-sm         /* Small variant */

--spacing-md                 /* Base spacing token */
--duration-fast              /* Base motion token */
--radius-md                  /* Base radius token */
```

### Naming Rules
- Use hyphen-separated lowercase
- Avoid ambiguous names (no "blue", use "pending", "info", "accent")
- One semantic meaning per token
- Suffixes indicate state or variant (hover, active, disabled, focus)

---

## Section 12: Token Consumption Map

| Layer | Consumes | Provides |
|---|---|---|
| Theme | Tokens | CSS variables |
| Components | Theme CSS vars | UI elements |
| Layout | Tokens | Spatial structure |
| Motion | Tokens | Transitions |
| Accessibility | Tokens | Contrast, focus |

---

## Section 13: Checklist for New Features

Before adding new UI, verify:

- [ ] All colors reference semantic color tokens
- [ ] All spacing references spacing tokens
- [ ] All motion uses duration and easing tokens
- [ ] All typography uses type scale tokens
- [ ] All shadows use shadow tokens
- [ ] No hardcoded values (px, colors, times)
- [ ] Reduced-motion respected for all motion
- [ ] Accessibility contrast checked against tokens
- [ ] Focus states use focus ring tokens

---

## Appendix: Quick Reference

| Category | Primary Tokens |
|---|---|
| Status | pending, running, completed, failed, success, warning, error |
| UI Surfaces | background, surface, surface-hover, surface-secondary |
| Text | text-primary, text-secondary, text-tertiary |
| Borders | border-subtle, border-strong, border-interactive |
| Accent | accent, accent-strong, accent-hover |
| Charts | waveform-primary, plot-grid, plot-axis |
| Typography | display, heading-1, body, label, mono-data |
| Spacing | 2xs (4px) through 3xl (64px) |
| Radius | sm (4px), md (8px), lg (12px), full (9999px) |
| Motion | fast (120ms), medium (240ms), slow (360ms) |
| Density | compact, comfortable, expanded |

This token inventory is **production-ready** and **enforceable**. All implementations must reference tokens, never hardcode values.

