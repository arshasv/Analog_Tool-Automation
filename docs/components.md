# Components

**Owner:** Design System  
**Version:** 1.0  
**Scope:** Component library, state definitions, and behavior contracts.

## Purpose

Components are **reusable UI units** that encapsulate specific behaviors and states. Every component must have:

1. **Visual specification** (from atomic.md)
2. **State matrix** (all valid states and transitions)
3. **Backend integration** (how it receives and displays data)
4. **Accessibility requirements** (keyboard, screen-reader)

---

## Section 1: Core Component Set

### Application Shell
- Header / Navigation bar
- Sidebar or global navigation
- Main content region
- Footer or utility bar

### Job Submission & Control
- File uploader (drag-and-drop)
- Parameter editor (JSON/form)
- Mode selector (simulate vs. optimize)
- Run button
- Reset / Cancel button

### Status & Monitoring
- Status badge
- Progress bar
- Timestamp row
- Live log / Output panel
- Error alert

### Results & Analysis
- Metric cards (key performance indicators)
- Plot container (waveform, frequency response)
- Tabbed output panel (results, logs, raw JSON)
- Raw JSON viewer
- Download button

### Feedback
- Toast notifications
- Inline validation messages
- Loading skeletons
- Empty states
- Confirmation dialogs

---

## Section 2: Component State Definitions

Every component exposes these standard states:

| State | Meaning | Styling | Interaction |
|---|---|---|---|
| `default` | Normal, ready for interaction | Base colors | Clickable / focusable |
| `hover` | Pointer over element (mouse only) | Surface highlight | Cursor change |
| `focus` | Keyboard or programmatic focus | Focus ring visible | Tab accessible |
| `active` | Element pressed / clicked | Darker/pressed state | Tactile feedback |
| `disabled` | Cannot be interacted with | Grayed out, lower opacity | No cursor change |
| `loading` | Async operation in progress | Spinner or skeleton | Non-interactive |
| `error` | Failed state or invalid input | Error color, icon | May show message |
| `success` | Operation succeeded | Success color, checkmark | Temporary or persistent |
| `pending` | Waiting for async action | Neutral color, no animation | May have indicator |

### Component-Specific States

#### Button Component

```
States:
  default → hover → active → (release) → default
  default → focus → (tab away) → default
  disabled (overrides all others)
  loading (show spinner, disable interaction)
  success (brief checkmark, then back to default)
  error (show error message, remain active for retry)

Duration: focus (120ms), active (60ms), loading (pulsing)
Motion: active scale(0.98), loading pulse 2s, success bounce 240ms
Accessibility:
  - Keyboard: Space, Enter to activate
  - Screen reader: Button label + state (e.g., "Run button, disabled")
  - Focus: Always visible, 2px ring
```

#### File Uploader Component

```
States:
  idle (ready to upload)
  drag-over (user dragging file over drop zone)
  loading (uploading)
  success (file accepted, show preview)
  error (invalid file, show message)

Duration: drag-over highlight (120ms), success checkmark (240ms)
Motion: drag-over background color transition, success scale-up
Accessibility:
  - Keyboard: Tab to uploader, Space/Enter to open file dialog
  - Screen reader: "File uploader, accepts .py and .spice files"
  - Error messages: Announce via live region
```

#### Status Badge Component

```
States & Backend Mapping:
  pending → background: var(--token-pending), icon: hourglass
  running → background: var(--token-running), icon: animated spinner
  completed → background: var(--token-completed), icon: checkmark
  failed → background: var(--token-failed), icon: X

Duration: state transitions 240ms (easing-standard)
Motion: spinner 2s rotation, success bounce 240ms, error shake 120ms
Accessibility:
  - Screen reader: "Job status: {state}" announced
  - Live region: Announce on state change
  - Color + icon: No color alone
```

#### Parameter Editor Component

```
States:
  default (empty, showing defaults)
  editing (user typing, show cursor)
  validating (checking input)
  valid (green checkmark)
  invalid (red error, show message)
  disabled (form locked during running job)

Duration: validation check 240ms, error highlight 120ms
Motion: input focus glow 120ms, error shake 240ms
Accessibility:
  - Keyboard: Tab through fields, Enter to validate
  - Screen reader: Label + value + error message (if any)
  - Focus: Visible 2px ring on each field
  - Error: Announced via aria-live region
```

#### Job Status Panel Component

```
States:
  idle (no job, show upload area)
  pending (job queued, badge shows pending)
  running (job executing, progress bar active, log live)
  completed (show results summary, enable download)
  failed (show error, enable retry)

Duration:
  pending → running: 240ms badge color change
  running → completed: 240ms badge color + icon transition
  running → failed: 120ms badge shake + color change

Motion:
  progress bar fills 240ms per update
  log lines slide in 120ms each
  result cards fade in 240ms staggered
  
Accessibility:
  - Status announced every 5–10 seconds during running
  - Progress percentage announced with update
  - Completion announced immediately
  - Errors announced with screen reader focus
```

#### Progress Bar Component

```
States:
  indeterminate (unknown duration, pulsing 0–50%)
  determinate (known %, filling to value)
  complete (100%, momentary emphasis)

Duration:
  indeterminate pulse: 2s (easing-standard)
  determinate fill: 240ms per update (easing-out)
  complete emphasis: 360ms (easing-emphasized)

Motion:
  indeterminate: width oscillates 0% → 50%
  determinate: smooth width transition
  complete: brief scale-up then settle

Accessibility:
  - aria-valuenow: Updated with percentage
  - Live region: Percentage announced every update
  - Label: "Simulation progress: X%"
```

#### Plot / Chart Container

```
States:
  loading (skeleton, pulsing placeholder)
  ready (plot rendered, interactive)
  error (failed to render, show message)
  empty (no data, show empty state)

Duration: skeleton 1.5s pulse, plot fade-in 360ms
Motion:
  skeleton: pulse animation respects prefers-reduced-motion
  plot: lines/bars grow in over 360ms staggered
  hover: axis labels highlight 120ms

Accessibility:
  - Title: Descriptive chart title
  - Description: alt text or ARIA description
  - Data table: Provide accessible table as fallback
  - Keyboard: Tab to zoom controls, arrow keys to pan
```

#### Modal / Dialog Component

```
States:
  closed (not visible)
  opening (0–100ms: opacity + transform)
  open (visible, interactive)
  closing (0–120ms: opacity + transform)

Duration:
  open: 240ms (easing-decelerate)
  close: 120ms (easing-emphasized)

Motion:
  backdrop: fade in/out 240ms
  modal: slide up + fade in 240ms, slide down + fade out 120ms
  
Accessibility:
  - Focus trap: Focus stays within modal while open
  - Escape: Closes modal (if appropriate)
  - Title: aria-labelledby points to modal title
  - Initial focus: Set to first interactive element
  - Announcement: "Modal opened, {title}" via live region
```

#### Result Table / Metrics

```
States:
  loading (skeleton rows, pulsing)
  loaded (rows visible)
  hovering (row highlights)
  selected (row selected if applicable)
  empty (no data, show placeholder)
  error (failed to load)

Duration:
  row enter: 120ms slide-in + fade (staggered 40ms between)
  row hover: 120ms background color change
  skeleton: 1.5s pulse

Motion:
  skeleton: respects prefers-reduced-motion
  row enter: stagger effect 40ms per row
  hover: smooth color transition

Accessibility:
  - Headers: <th> with scope
  - Rows: Semantic <tr>
  - Value cells: Numeric values right-aligned
  - Sortable: Button in header with aria-sort
  - Keyboard: Tab through cells, arrow keys to navigate
```

---

## Section 3: Component Behavior Guidelines

### Button Behavior

```
Buttons should show loading states when an action is in flight:
  - Label changes to "Loading..." or spinner appears
  - Disabled during action
  - Cursor changes to wait
  - Motion: spinner 2s rotation (respects prefers-reduced-motion)
```

### Input Behavior

```
Inputs should support validation feedback without layout shift:
  - Error icon appears inline
  - Error message in reserved space below
  - Border color changes to error
  - Screen reader announces error
  - No reflow of surrounding content
```

### Table & List Behavior

```
Tables and result panels should scale to larger data sets:
  - Virtual scrolling for 100+ rows
  - Sticky headers
  - Overflow handling (horizontal scroll or collapse)
  - Staggered row animation on load
  - No performance degradation with 500+ rows
```

### Async Feedback Behavior

```
Long-running operations need predictable feedback:
  - Icon state changes immediately (no delay)
  - Color transitions smoothly (240ms)
  - Progress updates every 1–5 seconds
  - Live region announces status changes
  - No loading spinners longer than needed
  - Clear error messages with next steps
```

---

## Section 4: Implementation Notes

### Composability
- Prefer composable props over one-off variants
- Button can be `<Button variant="primary" loading={true} />`
- Not: `<LoadingPrimaryButton />`

### Business Logic Isolation
- Keep circuit-specific logic **outside** components
- Components receive data through props
- Components emit events; parent handles logic
- Example: Badge receives `status` prop, doesn't know about jobs

### Backend Agnostic Components
- Components don't import backend services
- Data flows in through props
- Status/state derived from backend response
- Parent container manages polling, retry logic

### Shared Result Widgets
- `ResultsViewer` works for both simulate and optimize outputs
- Receives `mode` and `results` as props
- Conditionally renders based on mode

---

## Section 5: Accessibility in Components

### Keyboard Navigation
- All interactive elements reachable by Tab
- Logical tab order (top-to-bottom, left-to-right)
- Escape closes overlays (if appropriate)
- Enter/Space activates buttons

### Screen Reader Accessibility
- Semantic HTML (`<button>`, `<input>`, `<table>`)
- Descriptive labels or aria-label
- Status changes announced via aria-live
- Error messages linked via aria-describedby

### Focus Management
- Focus ring always visible (2px)
- Focus trap in modals
- Focus returned to trigger on close
- Focus restoration after asynchronous updates

### Reduced Motion
- `prefers-reduced-motion` respected globally (see motion.md)
- Skeletons show placeholder instead of pulsing
- Spinners removed or show static icon
- Duration set to 1ms (effectively instant)

---

## Section 6: State Matrix Template

Use this template for every new component:

| State | Background | Foreground | Icon | Motion | Accessibility |
|---|---|---|---|---|---|
| default | `var(--token-surface)` | `var(--token-text-primary)` | Primary | None | Focusable |
| hover | `var(--token-surface-hover)` | `var(--token-text-primary)` | Primary | 120ms color | Cursor change |
| focus | `var(--token-surface)` | `var(--token-text-primary)` | Primary | 2px focus ring | Tab stop |
| active | `var(--token-surface-active)` | `var(--token-text-primary)` | Primary | scale(0.98) | Pressed |
| disabled | `var(--token-surface)` opacity 0.5 | `var(--token-text-tertiary)` | Grayed | None | aria-disabled |
| loading | `var(--token-surface)` | `var(--token-text-secondary)` | Spinner | 2s rotation | aria-busy |
| error | `var(--token-surface)` | `var(--token-error)` | Error X | Shake 240ms | aria-invalid |
| success | `var(--token-surface)` | `var(--token-success)` | Checkmark | Bounce 240ms | aria-checked |

---

## Appendix: Component Checklist

Before shipping a component:

- [ ] All states defined and tested
- [ ] State transitions smooth (motion.md durations)
- [ ] Keyboard accessible (tab, focus, escape)
- [ ] Screen-reader announcements clear
- [ ] Error messages actionable
- [ ] Loading state prevents interaction
- [ ] Disabled state obvious
- [ ] Focus ring always visible
- [ ] Reduced motion respected
- [ ] No hardcoded colors/spacing (uses tokens)
- [ ] Accepts data via props
- [ ] No business logic (pure UI)
- [ ] Works with backend async states

This document is **enforceable**. All components must follow these patterns.

