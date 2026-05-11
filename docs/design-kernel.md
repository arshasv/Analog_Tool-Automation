# Design Kernel

**Version:** 1.0  
**Status:** Canonical  
**Last Updated:** May 2026

## Purpose

This is the **constitutional document** for the xEDA design system. It defines:

- Ownership and authority of each layer
- Dependency hierarchy and data flow
- Rules for canonical vs. reference files
- Forbidden duplication patterns
- Reconciliation process for conflicts

All other design documentation inherits from this kernel.

---

## Section 1: Canonical Hierarchy

### Layer 1 — Product & Research (Foundation)
**Owner:** [README.md](../README.md)  
**Scope:** Product narrative, core features, and tech stack overview only.  
**Authority:** What is xEDA?

**Owner:** [02-RESEARCH.md](02-RESEARCH.md)  
**Scope:** User research, workflows, UX implications, and constraints.  
**Authority:** Who are we building for? What do they need?

**Rules:**
- README is **product overview only**. It does NOT define design system behavior.
- README must link to design documentation for implementation details.
- Research must capture workflow context that informs all downstream design decisions.

---

### Layer 2 — Design Tokens (Semantic Foundation)
**Owner:** [03-TOKENS.md](03-TOKENS.md)  
**Scope:** Semantic token definitions, inventory, and naming rules.  
**Authority:** What is the visual language?

**Token Categories (Canonical Inventory):**

#### Color Tokens
- **Primitives:** Base color palette (e.g., `color-blue-50` through `color-blue-900`)
- **Semantic status:** `token-success`, `token-warning`, `token-error`, `token-info`, `token-pending`
- **Semantic UI:** `token-background`, `token-surface`, `token-border`, `token-text-primary`, `token-text-secondary`
- **Accent:** `token-accent`, `token-accent-strong`
- **Chart colors:** `token-plot-grid`, `token-plot-axis`, `token-waveform-primary`, `token-waveform-secondary`

#### Typography Tokens
- **Scales:** `typography-display`, `typography-heading-1`, `typography-heading-2`, `typography-body`, `typography-label`, `typography-mono-data`
- **Sizing:** `font-size-xs`, `font-size-sm`, `font-size-base`, `font-size-lg`, `font-size-xl`
- **Weight:** `font-weight-regular`, `font-weight-semibold`, `font-weight-bold`
- **Line height:** `line-height-tight`, `line-height-normal`, `line-height-relaxed`

#### Spacing Tokens
- **Scale:** `spacing-2xs`, `spacing-xs`, `spacing-sm`, `spacing-md`, `spacing-lg`, `spacing-xl`, `spacing-2xl`
- **Values:** 4px, 8px, 12px, 16px, 24px, 32px, 48px (modular scale)

#### Radius Tokens
- **Interactive:** `radius-sm`, `radius-md`, `radius-lg`
- **Pills:** `radius-full`

#### Elevation Tokens
- **Shadows:** `shadow-sm`, `shadow-md`, `shadow-lg`, `shadow-xl`
- **Glass surface:** `glass-surface`, `glass-blur`

#### Motion Tokens
- **Durations:** `duration-fast` (120ms), `duration-medium` (240ms), `duration-slow` (360ms)
- **Easing:** `easing-standard` (cubic-bezier), `easing-emphasized` (ease-out), `easing-emphasized-in` (ease-in)

#### Density Tokens
- **Dashboard:** `density-compact`, `density-comfortable`, `density-expanded`
- **Table row height:** varies by density

#### State Tokens
- **Job states:** `state-pending`, `state-running`, `state-completed`, `state-failed`
- **Optimization states:** `state-optimizing`, `state-optimization-complete`
- **Component states:** `state-disabled`, `state-loading`, `state-error`, `state-success`

**Rules:**
- Every token must have a **semantic name**, not a brand name (e.g., `token-success`, not `token-green`).
- Tokens are the **single source of truth** for all visual properties.
- No component, theme, or layout file may define its own color or spacing values.
- All tokens must be implementable as CSS custom properties.

---

### Layer 3 — Theme (Appearance Mapping)
**Owner:** [theme.md](theme.md)  
**Scope:** Maps semantic tokens into implemented CSS variables for specific theme contexts (dark, light, etc.).  
**Authority:** How do we express the tokens visually?

**Theme Responsibilities:**
- Define `--token-success`, `--token-warning`, etc. as CSS custom properties.
- Support multiple themes (dark, light, high-contrast, etc.) by remapping the same tokens.
- Do **NOT** introduce new semantic meanings.
- Do **NOT** hardcode values that belong in tokens.

**Rules:**
- Themes **reference, never redefine** tokens.
- A theme is **never a source of truth** for semantic meaning.
- Theme switches must work without changing component logic.

---

### Layer 4 — Motion & Interaction (Dynamic Behavior)
**Owner:** [motion.md](motion.md)  
**Scope:** Duration tokens, easing curves, transition rules, async feedback, and accessibility.  
**Authority:** How should the system move and respond?

**Motion Responsibilities:**
- Define motion tokens (durations, easing).
- Specify async feedback behavior (skeleton, pulse, progress).
- Define reduced-motion fallbacks.
- Specify focus and hover motion.

**Rules:**
- All motion must use semantic motion tokens.
- No hardcoded `transition` values outside `motion.md`.
- Async state feedback **must** be documented here.

---

### Layer 5 — Atomic Hierarchy (Composition Model)
**Owner:** [atomic.md](atomic.md)  
**Scope:** Describes atoms, molecules, organisms, templates, and pages.  
**Authority:** How do we compose UI?

**Atomic Rules:**
- Atoms are the smallest reusable unit.
- Each level builds from the level below.
- Organisms must remain reusable across multiple page contexts.
- Pages are instances of templates with data.

---

### Layer 6 — Components (Reusable UI Units)
**Owner:** [components.md](components.md)  
**Scope:** Component definitions, props, states, and behavior contracts.  
**Authority:** What are the reusable pieces?

**Component Responsibilities:**
- Define every component that appears in UI.
- Specify component **states**: idle, hover, focus, active, disabled, loading, error, success.
- Define **interaction behavior**: what happens on click, focus, keyboard input.
- Reference tokens and motion, never hardcode values.

**Rules:**
- Components must map to atoms or molecules in [atomic.md](atomic.md).
- Every component must have a formal state matrix (see Layer 9).
- Components must **not** contain business logic—only UI concerns.
- Components must be backend-agnostic and accept data through props.

---

### Layer 7 — Layout & Responsiveness (Spatial Structure)
**Owner:** [layout.md](layout.md)  
**Scope:** Grid, spacing, breakpoints, responsive behavior, and density rules.  
**Authority:** How is space organized?

**Layout Responsibilities:**
- Define the grid and container widths.
- Specify breakpoints and responsive thresholds.
- Define density modes (compact, comfortable, expanded).
- Specify overflow and collapse behavior.
- Define sticky/fixed element behavior.

**Rules:**
- All spacing must reference spacing tokens.
- Breakpoints must be consistent across the system.
- Responsive behavior must be deterministic, not ad hoc.

---

### Layer 8 — Navigation & Information Architecture (Wayfinding)
**Owner:** [navigation.md](navigation.md)  
**Scope:** Routes, page hierarchy, navigation patterns, and state awareness.  
**Authority:** How do users move through the system?

**Rules:**
- Navigation must always be aware of the current job state.
- Deep links to running jobs must be possible.
- Unsaved state must trigger warnings.

---

### Layer 9 — Accessibility (Constraints on All Layers)
**Owner:** [accessibility.md](accessibility.md)  
**Scope:** WCAG compliance, keyboard navigation, focus management, screen-reader behavior, and contrast rules.  
**Authority:** How do we ensure the system is usable by everyone?

**Accessibility Constraints:**
- Every interactive element must be keyboard-accessible.
- Every color change must have a non-color affordance.
- Focus must be visible and managed predictably.
- Async state changes must be announced.
- Reduced motion must be respected.

**Rules:**
- Accessibility is **not optional** and is not a separate layer—it constrains all other layers.
- No component, color, or motion decision is valid if it breaks accessibility.

---

### Layer 10 — Brand Identity (Visual & Tonal Direction)
**Owner:** [brand.md](brand.md)  
**Scope:** Design philosophy, visual voice, engineering aesthetic, and design principles.  
**Authority:** What does xEDA feel like?

**Brand Direction:**
- Professional, engineering-first aesthetic
- Precision and clarity over decoration
- Technical trustworthiness
- Dark-mode optimized for long sessions
- Dense but readable information density

---

### Layer 11 — Async UX Philosophy (Backend-Driven States)
**Owner:** [design-kernel.md](design-kernel.md) Section 5 + [motion.md](motion.md)  
**Scope:** How the UI responds to backend state changes, including pending, running, failed, and completed states.  
**Authority:** What does it feel like to interact with a long-running system?

**Async UX Principles:**
- Job states must be immediately visible.
- Status changes must be animated smoothly.
- Failures must be understandable and recoverable.
- Long-running jobs must show progress.

---

### Layer 12 — Backend-to-UI Contracts (System Integration)
**Owner:** [UI_DOCUMENTATION.md](UI_DOCUMENTATION.md) + [BACKEND_API_DOCUMENTATION.md](BACKEND_API_DOCUMENTATION.md)  
**Scope:** Formal mapping of backend states to UI behaviors, component visual states, and accessibility announcements.  
**Authority:** How does the backend contract translate into observable UI?

---

## Section 2: Dependency Flow

```
README (product narrative)
    ↓
Research (workflows, user goals, constraints)
    ↓
Tokens (semantic foundation)
    ↓
Theme (semantic → visual mapping)
    ↓
Motion (dynamic behavior, async feedback)
    ↓
Atomic (composition structure)
    ↓
Components (reusable UI)
    ↓
Layout (spatial organization)
    ↓
Navigation (wayfinding)
    ↓
Backend-to-UI Contracts (async state behavior)
    ↓
Accessibility (constraints on all)
    ↓
Brand (overall direction)
```

**Key Rule:** Information flows downward. A lower layer must **never** redefine concepts from a higher layer.

---

## Section 3: Canonical vs. Reference Files

### Canonical Files (Source of Truth)
- `README.md` (product overview)
- `02-RESEARCH.md` (workflows)
- `03-TOKENS.md` (token inventory)
- `theme.md` (theme mapping)
- `motion.md` (motion philosophy)
- `atomic.md` (composition model)
- `components.md` (component contracts)
- `layout.md` (spatial rules)
- `navigation.md` (wayfinding)
- `accessibility.md` (WCAG compliance)
- `brand.md` (visual direction)
- `design-kernel.md` (this document)
- `UI_DOCUMENTATION.md` (frontend contract)
- `BACKEND_API_DOCUMENTATION.md` (backend contract)

### Reference-Only Files
- `dashboard-mockup.html` — Visual reference only. Must consume canonical tokens. May not define independent behavior.

---

## Section 4: Forbidden Duplication Rules

### ❌ Duplication is Forbidden Between:
- `03-TOKENS.md` and any component/layout file
- `theme.md` and any component file
- `motion.md` and any component file
- `components.md` and `layout.md`
- `BACKEND_API_DOCUMENTATION.md` and `UI_DOCUMENTATION.md` (must cross-reference, not duplicate)

### ✅ Cross-Reference is Required Between:
- `README.md` → links to documentation files
- `UI_DOCUMENTATION.md` → `BACKEND_API_DOCUMENTATION.md`
- `components.md` → `atomic.md`, `layout.md`, `accessibility.md`
- `layout.md` → `motion.md`, `accessibility.md`
- All files → `design-kernel.md` (this document)

---

## Section 5: Async UX Philosophy (xEDA-Specific)

xEDA is **not a static dashboard**. It is a **long-running workflow system**. The design system must accommodate:

### Backend States (from BACKEND_API_DOCUMENTATION.md)
- `PENDING` — Job is queued
- `RUNNING` — Simulation or optimization in progress
- `COMPLETED` — Successfully finished
- `FAILED` — Error occurred

### UI Expressions of Async States

#### PENDING
- Icon: Hourglass or queue icon
- Color: `token-pending` (blue/neutral)
- Animation: Static, no motion until RUNNING
- Message: "Job queued"
- Accessibility: "Job status: pending, queued"
- Button state: Run button disabled, cancel enabled

#### RUNNING
- Icon: Animated spinner or pulse
- Color: `token-info` or `token-running` (cyan/blue)
- Animation: Pulse or slow rotation (see `motion.md`)
- Message: "Running..." with progress percentage
- Accessibility: Live region announces progress at intervals
- Button state: Run button disabled, cancel enabled, rerun disabled
- Side effects: Enable live log, show progress bar, activate animation

#### COMPLETED
- Icon: Checkmark
- Color: `token-success` (green)
- Animation: Brief scale-up then settle (240ms)
- Message: "Completed in X seconds"
- Accessibility: "Job completed successfully"
- Button state: Run button enabled, download enabled, rerun enabled
- Side effects: Display results, show metric summary

#### FAILED
- Icon: Error X or alert triangle
- Color: `token-error` (red)
- Animation: Shake or brief highlight (see `motion.md`)
- Message: Error description with actionable next steps
- Accessibility: "Job failed: [error reason]"
- Button state: Run button enabled, retry enabled
- Side effects: Display error log, show recommendation

---

## Section 6: Reconciliation Process

### Conflict Resolution Order
1. Check this kernel document first.
2. Check the owning layer's canonical file.
3. If contradiction exists, the **higher layer** (earlier in the dependency flow) takes precedence.
4. If the higher layer is silent, the lower layer decides.
5. Document the decision in the owning file.

### Example Conflict Resolution

**Scenario:** Component says use `--color-blue`, but Tokens say use semantic token `--token-info`.

**Resolution:**
1. Check Kernel → Tokens own semantic names.
2. Check `03-TOKENS.md` → Semantic token `--token-info` is canonical.
3. Component must use `--token-info`, not `--color-blue`.
4. If component used a hardcoded value, it violated the kernel → refactor.

---

## Section 7: Governance Rules

### Rule 1: Semantic First
Every token, color, and motion decision must have a **semantic reason**. Never hardcode values.

### Rule 2: Downstream Reads Upstream
Lower layers read from higher layers. Higher layers never read from lower layers.

### Rule 3: No Shadows or Side Channels
Do not define design decisions in code comments, Slack threads, or examples outside the canonical files.

### Rule 4: Accessibility is Always On
Every decision must consider accessibility. If a decision breaks accessibility, it is invalid.

### Rule 5: Backend-Driven Behavior
UI state must be **derived from backend state**, not invented independently.

---

## Section 8: Versioning & Updates

This kernel document should be updated whenever:
- A new design layer is introduced
- Canonical ownership changes
- Major dependency relationships shift
- New reconciliation rules are needed

**Update Process:**
1. Propose the change in this file.
2. Update all affected downstream files.
3. Increment the version number at the top of this document.
4. Commit with a clear message explaining the governance change.

---

## Section 9: Using This Document

### For Designers
- Use the **Dependency Flow** section to understand which files inform your work.
- Use the **Canonical Hierarchy** to know which file you should edit.
- Use the **Forbidden Duplication** section to avoid conflicts.

### For Engineers
- Build components by reading the owning layer's file (usually `components.md`).
- Reference tokens from `03-TOKENS.md`, never hardcode values.
- Check `motion.md` for transition rules before writing `transition` CSS.
- Ensure keyboard and screen-reader behavior matches `accessibility.md`.

### For Architects
- This kernel is the **constitutional document**. Enforce it.
- Use the **Conflict Resolution** process when ambiguity arises.
- Keep layers aligned by auditing cross-references quarterly.

---

## Appendix: Quick Reference

| Layer | File | Authority | Cannot Redefine |
|---|---|---|---|
| Product | README.md | What is xEDA? | (foundation) |
| Research | 02-RESEARCH.md | Who & why? | Product |
| Tokens | 03-TOKENS.md | Semantic values | Research |
| Theme | theme.md | Visual mapping | Tokens |
| Motion | motion.md | Dynamic behavior | Tokens, Theme |
| Atomic | atomic.md | Composition | Motion |
| Components | components.md | UI contracts | Atomic |
| Layout | layout.md | Spatial rules | Components |
| Navigation | navigation.md | Wayfinding | Layout |
| Accessibility | accessibility.md | Constraints | (all layers) |
| Brand | brand.md | Visual voice | (foundation) |
| Backend-UI | UI + API docs | State contracts | Components |
| Kernel | design-kernel.md | Governance | (constitution) |

---

**This document is enforceable. Violations require kernel approval.**
