# Layout

**Owner:** Design System  
**Version:** 1.0  
**Scope:** Spatial structure, grid, density rules, and responsive behavior.

## Purpose

Layout defines **how space is organized** on every page and screen size. For xEDA—a professional engineering dashboard—layout must:

1. Support high information density without losing readability
2. Remain responsive from mobile to ultra-wide workstations
3. Handle long-running job monitoring workflows
4. Scale with large result datasets without degrading performance

---

## Section 1: Layout Principles

### Principle 1: Hierarchy First
Present the most important job state first. Always.
- Status badge → Parameters → Results
- Current job → Job history → Settings

### Principle 2: Proximity & Grouping
Group controls close to the data they affect.
- Run button next to mode toggle
- Parameters grouped above results
- Status badge with progress bar

### Principle 3: Information Density
Engineering dashboards are dense. That's intentional.
- **Don't** add whitespace for aesthetic reasons
- **Do** use visual hierarchy and grouping to maintain readability
- **Do** respect user preferences for compact vs. comfortable layouts

### Principle 4: Responsiveness
Layouts degrade gracefully from ultra-wide to mobile.
- Never hide critical controls
- Collapse non-essential panels on smaller screens
- Prioritize running job status above all else

### Principle 5: Long-Running Workflow Context
Users will keep this page open for hours.
- Status must be glanceable at any time
- Side navigation must stay visible (or quickly accessible)
- Results must fit without constant scrolling

---

## Section 2: Page Structure (Desktop)

### Global Layout Grid

```
┌─────────────────────────────────────────────────────────┐
│                     HEADER / NAV                        │
├──────────────┬──────────────────────────────────────────┤
│              │                                          │
│  SIDEBAR     │           MAIN CONTENT                   │
│  (240–280px) │         (flexible width)                 │
│              │                                          │
│              │                                          │
└──────────────┴──────────────────────────────────────────┘
```

### Header
- **Height:** 56–64px (density-comfortable default)
- **Sticky:** Always visible at top
- **Contents:** Logo, page title, user menu, backend status
- **Spacing:** `var(--spacing-md)` horizontal padding

### Sidebar
- **Width:** 240–280px (collapsed: 56px with icon-only nav)
- **Sticky:** Height: 100vh
- **Contents:** Primary navigation (Home, Dashboard, History, Settings)
- **Collapse trigger:** Available on tablet and smaller
- **Accessibility:** Landmarks and ARIA labels

### Main Content Area
- **Max width:** `var(--max-width-wide)` (1400px)
- **Padding:** `var(--spacing-lg)` (24px) on desktop
- **Breakpoint:** Full-width on ultra-wide (>1600px)

---

## Section 3: Dashboard Page Structure

### Recommended Section Order

1. **Page Title & Context** (32px height)
2. **Current Status Panel** (96–120px, sticky)
3. **Primary Action Area** (File upload, controls)
4. **Parameters Panel** (Collapsible or sticky form)
5. **Job Status & Progress** (Update every 1–5 seconds)
6. **Results Section** (Lazy-loaded, tabbed)
7. **Job History** (Optional, below fold)

### Status Panel (Sticky)

```
┌──────────────────────────────────────────────────────┐
│  Status: RUNNING ● | 52% | Started 2 min ago | ↓ 📥 │
├──────────────────────────────────────────────────────┤
│  [====================================>          ] 52% │
│  Simulation progress: DC analysis → AC sweep         │
└──────────────────────────────────────────────────────┘
```

- **Height:** 64–96px (density-comfortable)
- **Sticky:** Until job completes or user scrolls past results
- **Contents:** Status badge, progress bar, timestamps, cancel/download buttons
- **Background:** Slightly elevated with subtle shadow

### Parameters Panel

```
┌──────────────────────────────────────────────────────┐
│  ⚙ Circuit Parameters                          ☑ 🔒  │
├──────────────────────────────────────────────────────┤
│  W (Width)       │ 1.0  µm         │ Default | Lock  │
│  L (Length)      │ 0.18 µm         │ Default | Lock  │
│  Vdd             │ 3.3  V          │ Default | Lock  │
│  Mode            │ Simulate        │ (Optimize)     │
├──────────────────────────────────────────────────────┤
│  [Run]  [Reset]  [Load Template...]                  │
└──────────────────────────────────────────────────────┘
```

- **Collapsible:** Can collapse after parameters are set
- **Max height:** 360–480px (before scroll within panel)
- **Density:** Rows are compact (`row-height: 36px` comfortable)
- **Fields:** Two-column layout on desktop, stack on tablet

### Results Section

- **Tab 1:** Metrics (KPI cards)
- **Tab 2:** Plots (waveforms, frequency response)
- **Tab 3:** Raw Data (JSON or CSV)
- **Tab 4:** Logs (simulation/optimization output)
- **Min height:** 400px (leave room for interaction)
- **Lazy-load:** Plots load only when tab is selected

---

## Section 4: Density Modes

xEDA supports three density settings to balance information and accessibility.

### Density: Compact
**Target:** Power users analyzing large datasets  
**Row height:** 28px  
**Padding:** `var(--spacing-xs)` (8px)  
**Font size:** `typography-body-sm` (12–13px)

**Use cases:**
- Detailed result tables (100+ rows)
- Dense parameter grids
- Circuit analysis with many metrics

**Risks:**
- Lower accessibility for visually impaired users
- May require higher screen zoom
- Touch targets smaller than recommended

### Density: Comfortable (Default)
**Target:** Most users, balanced experience  
**Row height:** 36px  
**Padding:** `var(--spacing-sm)` (12px)  
**Font size:** `typography-body` (14–16px)

**Use cases:**
- Standard dashboards
- Most workflows
- Recommended default

### Density: Expanded
**Target:** Accessibility-first, touch-friendly  
**Row height:** 44px  
**Padding:** `var(--spacing-md)` (16px)  
**Font size:** `typography-body` (16px)

**Use cases:**
- Touch devices (tablets, laptops with touchscreen)
- Users with vision or motor impairments
- Focused single-circuit analysis

### Density Toggle
- **Location:** Settings or preferences (top-right)
- **Label:** "Density: Comfortable" (current setting)
- **Persist:** Store in localStorage/preferences
- **Apply to:** All tables, lists, parameter editors globally

---

## Section 5: Responsive Breakpoints

xEDA must work across all device sizes, with graceful degradation.

### Breakpoint: Ultra-Wide (>1600px)
- **Typical:** Multi-monitor workstations
- **Layout:** Full-width with expanded sidebars
- **Max content width:** `var(--max-width-ultra)` (1600px)
- **Sidebar:** Always visible (280px)
- **Side-by-side:** Results and job history side-by-side

### Breakpoint: Laptop (1280–1600px)
- **Typical:** 13–15" laptops with normal zoom
- **Layout:** Standard two-column (sidebar + content)
- **Sidebar:** Always visible (240px)
- **Max width:** `var(--max-width-wide)` (1400px)

### Breakpoint: Tablet (1024–1280px)
- **Typical:** 10–11" tablets, split-screen laptop
- **Layout:** Collapsible sidebar (icon-only nav, expand on click)
- **Content:** Full-width with reduced padding
- **Panels:** Stack vertically or tab-switch
- **Parameters:** May collapse to accordion

### Breakpoint: Mobile (640–1024px)
- **Typical:** Large phones, small tablets
- **Layout:** Sidebar hidden (hamburger menu)
- **Content:** Full-width, single column
- **Status panel:** Always visible at top
- **Parameters:** Collapsible, full-width
- **Results:** Tab-switch between metrics, plots, logs
- **Touch targets:** Min 44×44px (even on compact density)

### Breakpoint: Small Mobile (<640px)
- **Typical:** Small phones (iPhone SE, etc.)
- **Layout:** Minimalist, focus on current job
- **Content:** Single column, vertical stack
- **Status:** Large, easy to read and interact with
- **Parameters:** Hidden behind "Edit" button
- **Results:** Full-width, single tab at a time
- **Navigation:** Bottom nav or slide-out menu

---

## Section 6: Overflow & Scrolling Behavior

### Horizontal Scrolling

Tables and plots may exceed viewport width on smaller screens.

#### Rules
- Table headers remain sticky when scrolling
- First column (row labels) remain sticky
- Horizontal scrollbar only if needed
- Touch: Swipe to scroll tables (if small)

#### Implementation
```css
.data-table {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch; /* Smooth momentum on iOS */
}

.data-table thead {
  position: sticky;
  top: 0;
  z-index: 10;
}

.data-table th:first-child {
  position: sticky;
  left: 0;
  z-index: 11;
}
```

### Vertical Scrolling

Content flows naturally. Use these constraints:

| Area | Max Height | Behavior |
|---|---|---|
| Header | 56–64px | Sticky, scrolls away |
| Status panel | 96–120px | Sticky until results |
| Parameters | 360–480px | Scroll within panel |
| Results | Flexible | Full-height scroll |
| Sidebar | 100vh | Fixed, internal scroll if needed |

---

## Section 7: Workflow-Specific Layouts

### Upload & Configure Workflow

```
┌─────────────────────────────────────────┐
│  New Simulation                         │
├─────────────────────────────────────────┤
│                                         │
│  📁 Upload Circuit File                 │
│  [Drag and drop or click to select]     │
│                                         │
│  Circuit: (none selected)               │
│  📝 Select template: [dropdown]         │
│                                         │
├─────────────────────────────────────────┤
│  ⚙ Circuit Parameters                   │
│  W: 1.0 µm  | L: 0.18 µm               │
│  Vdd: 3.3 V | CL: 10 pF               │
├─────────────────────────────────────────┤
│  [Run Simulation]  [Optimize]  [Reset] │
└─────────────────────────────────────────┘
```

- **Primary:** Upload and parameters
- **Secondary:** Mode selection, action buttons
- **Below fold:** Template library, advanced options

### Job Monitoring Workflow

```
┌─────────────────────────────────────────┐
│ 🟢 Running | 45% | Started 5 min ago   │
├─────────────────────────────────────────┤
│ [=============================> ] 45%   │
│ AC sweep: 50–500MHz in progress        │
├─────────────────────────────────────────┤
│ 📊 Live Metrics              │ [Cancel] │
│ Gain:    -2.5 dB            │ [Pause]  │
│ Phase:   -45.2°             │          │
│ BW:      250 MHz            │          │
├─────────────────────────────────────────┤
│ 📋 Log Output (last 10 lines)           │
│ > Running AC analysis...                │
│ > Frequency sweep 1/100                │
│ > Analyzing node: Vout                 │
│ [↓ View Full Log]                      │
└─────────────────────────────────────────┘
```

- **Always visible:** Status, progress, current metrics
- **Collapsible:** Full parameter details (scroll down)
- **Tab area:** Plots available but not auto-shown
- **After completion:** Results fade in, tabs become active

### Results Review Workflow

```
┌─────────────────────────────────────────┐
│ ✅ Completed | 100% | 12 min 34 sec   │
├─────────────────────────────────────────┤
│ [📊 Metrics] [📈 Plots] [📋 Raw] [💾 Download] │
├─────────────────────────────────────────┤
│  KEY RESULTS                            │
│  Gain:    -2.3 dB  ✓ (target: -3 dB)  │
│  GBW:     250 MHz   ✓ (target: 200MHz) │
│  Phase margin: 65°  ✓ (target: >60°)   │
│  Power:   12.5 mW   ⚠ (target: 10mW)  │
├─────────────────────────────────────────┤
│ [▶ Run Again] [📁 Load Design] [Optimize] │
└─────────────────────────────────────────┘
```

- **Metrics:** Summary cards with pass/fail
- **Actions:** Easy access to next steps
- **Download:** Immediate availability
- **Comparison:** Link to previous runs

---

## Section 8: Mobile-Specific Behavior

### Sidebar Collapse (Mobile)

On tablet and smaller:
- Sidebar collapses to icon-only nav (56px)
- Tap hamburger to expand in overlay
- Overlay covers content (not push-aside)
- Closes on selection or escape

### Bottom Navigation (Optional)

On very small screens, consider bottom nav:
- Dashboard, History, Settings
- Always visible, consistent
- No redundancy with sidebar

### Touch Targets

- Minimum 44×44px (WCAG 2.5 target size)
- Even on compact density
- Spacing: At least 8px between targets

---

## Section 9: Content Constraints

### Text Width
- Body text: 40–75 characters per line
- Use max-width on content containers
- Avoid full-window text (too hard to read)

### Table Widths
- Min column width: 60px
- Max column width: 300px
- Overflow: Horizontal scroll or collapse

### Plot/Chart Dimensions
- Aspect ratio: 16:9 (waveforms), 4:3 (histograms)
- Min height: 200px
- Max height: 600px (scrollable if needed)
- Responsive: Maintain aspect on resize

---

## Section 10: Sticky Elements & Z-Index

### Z-Index Stack

```
1000 → Modals, overlays (highest)
 500 → Dropdowns, popovers
 100 → Sticky headers, status panel
  10 → Sidebar (if fixed)
   0 → Base content
```

### Sticky Header Best Practices

- Sticky: Status panel, table headers
- Not sticky: Sidebar on desktop (fixed is better)
- Not sticky: Main navigation (confusing on scroll)
- Test: Scrolling performance with 500+ rows

---

## Section 11: Layout Testing Checklist

- [ ] Desktop (1920×1080, 1440×900): No horizontal scroll
- [ ] Laptop (1366×768): Sidebar visible, content readable
- [ ] Tablet (1024×768): Sidebar collapsed, content fills width
- [ ] Large phone (414×896): Touch targets ≥44×44px
- [ ] Small phone (375×667): Content readable, no hidden controls
- [ ] Zoom 150%: No broken layouts, still usable
- [ ] Zoom 200%: No missing content, can scroll to access
- [ ] Rotated: Layout adapts (landscape ↔ portrait)
- [ ] High DPI (240dpi): Spacing looks intentional, not bloated

---

## Appendix: Spacing Reference

All layout spacing uses the modular spacing scale from tokens:

| Token | Value | Use |
|---|---|---|
| `--spacing-2xs` | 4px | Component internals |
| `--spacing-xs` | 8px | Tight spacing (compact density) |
| `--spacing-sm` | 12px | Item spacing |
| `--spacing-md` | 16px | Section spacing (default) |
| `--spacing-lg` | 24px | Major sections |
| `--spacing-xl` | 32px | Page margins |
| `--spacing-2xl` | 48px | Full-page margins |

This document is **enforceable**. All layouts must follow these patterns.

