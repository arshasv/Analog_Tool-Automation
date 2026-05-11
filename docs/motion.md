# Motion

**Owner:** Design System  
**Version:** 1.0  
**Scope:** Motion tokens, durations, easing, async feedback, and accessibility.

## Purpose

Motion in xEDA serves one purpose: **clarify state change and reduce cognitive friction**.

No motion is decorative. Every transition must:
- Communicate a state change
- Respect user preferences
- Remain purposeful and fast
- Be fully accessible

---

## Section 1: Motion Tokens

### Duration Tokens

These are the **only** allowed transition durations across xEDA.

| Token | Duration | Use Case |
|---|---|---|
| `duration-instant` | 0ms | No animation (skip transitions for reduced-motion) |
| `duration-fast` | 120ms | Button presses, focus rings, micro-interactions |
| `duration-medium` | 240ms | Modal open/close, list transitions, form validation |
| `duration-slow` | 360ms | Page transitions, major layout shifts |

**Implementation Rule:** All CSS `transition` values must reference these tokens. No hardcoded `300ms` or `0.3s`.

```css
button {
  transition: background-color var(--duration-fast) ease-in-out;
}

dialog {
  transition: opacity var(--duration-medium) ease-out, transform var(--duration-medium) ease-out;
}
```

### Easing Tokens

| Token | Curve | Purpose |
|---|---|---|
| `easing-standard` | `cubic-bezier(0.4, 0, 0.2, 1)` | Default, balanced easing for most interactions |
| `easing-emphasized` | `cubic-bezier(0.05, 0.7, 0.1, 1)` | Fast start, slow end—used for exits and overlays |
| `easing-decelerate` | `cubic-bezier(0, 0, 0.2, 1)` | Immediate response, decelerate end—used for entries |

**No easing values outside these three.** Avoid `ease`, `ease-in`, `ease-out`, `linear`.

---

## Section 2: Interaction Motion Rules

### Button & Control Interaction

#### Hover
- **Duration:** `duration-fast` (120ms)
- **Properties:** `background-color`, `box-shadow`
- **Easing:** `easing-standard`
- **No motion on:** disabled state

```css
button:not(:disabled):hover {
  background-color: var(--token-surface-hover);
  transition: background-color var(--duration-fast) var(--easing-standard);
}
```

#### Focus
- **Duration:** `duration-fast` (120ms)
- **Properties:** `box-shadow` (focus ring)
- **Easing:** `easing-standard`
- **Visible:** Always. No option to hide.

```css
button:focus-visible {
  outline: 2px solid var(--token-focus-ring);
  outline-offset: 2px;
  transition: outline-color var(--duration-fast) var(--easing-standard);
}
```

#### Active (Press)
- **Duration:** 60ms (instant feedback)
- **Properties:** `transform` (slight scale down)
- **Effect:** `scale(0.98)` to show tactile feedback
- **Easing:** `linear` (instant)

```css
button:active {
  transform: scale(0.98);
  transition: transform 60ms linear;
}
```

### Form Input Interaction

#### Focus Entry
- **Duration:** `duration-fast` (120ms)
- **Properties:** `border-color`, `box-shadow` (glow effect)
- **Easing:** `easing-standard`

```css
input:focus {
  border-color: var(--token-accent);
  box-shadow: 0 0 0 3px var(--token-accent-alpha-10);
  transition: border-color var(--duration-fast) var(--easing-standard),
              box-shadow var(--duration-fast) var(--easing-standard);
}
```

#### Validation Feedback
- **Duration:** `duration-medium` (240ms)
- **State change:** error → default or success
- **Easing:** `easing-standard`
- **No layout shift** — validation message area must be reserved

---

## Section 3: Async State Feedback (Long-Running Jobs)

This is **critical for xEDA**. Async feedback must be:
1. Immediate and visible
2. Respectful of reduced-motion
3. Accessible and announced
4. Non-distracting but clear

### Job State Transitions

#### PENDING → RUNNING
- **Duration:** `duration-medium` (240ms)
- **Animation:** Badge text transitions, icon dissolves in spinner
- **Color transition:** `pending` → `running`
- **Easing:** `easing-decelerate` (user sees response immediately)

```css
.job-status-badge {
  transition: background-color var(--duration-medium) var(--easing-decelerate),
              color var(--duration-medium) var(--easing-decelerate);
}

.job-status-icon {
  animation: spin 2s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

#### RUNNING Progress Update
- **Duration:** None (instant number updates)
- **Animation:** Progress bar smoothly fills
- **Motion:** `width` transition over `duration-medium` (240ms)

```css
.progress-bar {
  transition: width var(--duration-medium) ease-out;
}
```

#### RUNNING → COMPLETED
- **Duration:** `duration-medium` (240ms)
- **Animation:** Spinner → checkmark with scale bounce
- **Color transition:** `running` → `success`
- **Sound:** Optional, accessibility-friendly
- **Easing:** `easing-emphasized` (finish with deceleration)

```css
.job-status-icon {
  animation: complete 240ms var(--easing-emphasized) forwards;
}

@keyframes complete {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(1.1); opacity: 1; }
}
```

#### RUNNING → FAILED
- **Duration:** `duration-fast` (120ms)
- **Animation:** Brief shake or pulse (red)
- **Color transition:** `running` → `error`
- **Easing:** `easing-standard`
- **Alert:** Show error message below badge

```css
.job-status-icon {
  animation: alert-shake 120ms var(--easing-standard);
}

@keyframes alert-shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
}
```

### Skeleton Loading

When fetching data, use **skeleton screens** instead of spinners.

#### Rules
- Skeleton blocks match content shape
- Pulse animation: 1.5s cycle (slow, subtle)
- Easing: `easing-standard`
- Respect reduced-motion (no animation, show placeholder)

```css
.skeleton {
  background: linear-gradient(90deg,
    var(--token-skeleton-start) 0%,
    var(--token-skeleton-mid) 50%,
    var(--token-skeleton-start) 100%);
  background-size: 200% 100%;
  animation: skeleton-pulse 1.5s var(--easing-standard) infinite;
}

@keyframes skeleton-pulse {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@media (prefers-reduced-motion: reduce) {
  .skeleton {
    animation: none;
    background: var(--token-surface-secondary);
  }
}
```

### Progress Indicator

For long-running tasks, show actual progress.

#### Rules
- Progress bar fills smoothly (no jumpy jumps)
- Color: `token-accent` or `token-info`
- Animation: Indeterminate → determinate → complete
- Easing: `ease-out` (slowing as it completes)

```css
.progress-bar {
  transition: width var(--duration-medium) ease-out;
}

/* Indeterminate (unknown duration) */
.progress-bar.indeterminate {
  animation: progress-pulse 2s var(--easing-standard) infinite;
}

@keyframes progress-pulse {
  0% { width: 0; }
  50% { width: 40%; }
  100% { width: 100%; }
}
```

---

## Section 4: Modal & Overlay Transitions

### Modal Open
- **Duration:** `duration-medium` (240ms)
- **Backdrop:** Fade in (opacity 0 → 1)
- **Modal:** Slide up + fade in, or fade in with scale
- **Easing:** `easing-decelerate` (fast start)

```css
.modal-backdrop {
  animation: backdrop-in var(--duration-medium) var(--easing-decelerate) forwards;
}

.modal {
  animation: modal-in var(--duration-medium) var(--easing-decelerate) forwards;
}

@keyframes backdrop-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes modal-in {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### Modal Close
- **Duration:** `duration-fast` (120ms)
- **Backdrop:** Fade out (opacity 1 → 0)
- **Modal:** Slide down + fade out, or fade out with scale
- **Easing:** `easing-emphasized` (ease-out)

```css
.modal-backdrop.closing {
  animation: backdrop-out var(--duration-fast) var(--easing-emphasized) forwards;
}

.modal.closing {
  animation: modal-out var(--duration-fast) var(--easing-emphasized) forwards;
}

@keyframes backdrop-out {
  from { opacity: 1; }
  to { opacity: 0; }
}

@keyframes modal-out {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(16px);
  }
}
```

---

## Section 5: List & Data Table Transitions

### Item Enter
- **Duration:** `duration-medium` (240ms)
- **Animation:** Slide in from left + fade in
- **Easing:** `easing-decelerate`
- **Stagger:** 40ms between items for visual feedback

```css
.list-item {
  animation: item-in var(--duration-medium) var(--easing-decelerate) backwards;
}

.list-item:nth-child(1) { animation-delay: 0ms; }
.list-item:nth-child(2) { animation-delay: 40ms; }
.list-item:nth-child(3) { animation-delay: 80ms; }
/* ... etc ... */

@keyframes item-in {
  from {
    opacity: 0;
    transform: translateX(-16px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
```

### Item Remove (Swipe/Slide Out)
- **Duration:** `duration-fast` (120ms)
- **Animation:** Slide out right + fade out
- **Easing:** `easing-emphasized`

```css
.list-item.removing {
  animation: item-out var(--duration-fast) var(--easing-emphasized) forwards;
}

@keyframes item-out {
  to {
    opacity: 0;
    transform: translateX(32px);
  }
}
```

### Row Highlight (Hover State in Table)
- **Duration:** `duration-fast` (120ms)
- **Property:** `background-color`
- **Easing:** `easing-standard`

```css
.table-row:hover {
  background-color: var(--token-table-row-hover);
  transition: background-color var(--duration-fast) var(--easing-standard);
}
```

---

## Section 6: Chart & Plot Animations

### Chart Load
- **Duration:** `duration-slow` (360ms)
- **Animation:** Lines draw in, bars grow from baseline
- **Easing:** `easing-decelerate`
- **Effect:** Visual impact without being jarring

```css
.chart-bar {
  animation: bar-grow var(--duration-slow) var(--easing-decelerate) backwards;
}

.chart-bar:nth-child(1) { animation-delay: 0ms; }
.chart-bar:nth-child(2) { animation-delay: 60ms; }
/* ... stagger bars ... */

@keyframes bar-grow {
  from {
    height: 0;
    opacity: 0;
  }
  to {
    height: var(--bar-height);
    opacity: 1;
  }
}
```

### Chart Update (Value Change)
- **Duration:** `duration-medium` (240ms)
- **Animation:** Smooth height/width change
- **Easing:** `easing-standard`

```css
.chart-bar {
  transition: height var(--duration-medium) var(--easing-standard);
}
```

---

## Section 7: Reduced Motion Accessibility

**This is mandatory.** The system must respect `prefers-reduced-motion`.

### Media Query Rule

Apply this globally:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 1ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 1ms !important;
    scroll-behavior: auto !important;
  }
}
```

### Specific Reduced-Motion Behavior

For key interactions, define explicit fallback:

```css
/* Async status feedback: no spin, static icon with color change */
@media (prefers-reduced-motion: reduce) {
  .job-status-icon {
    animation: none;
    /* Show static checkmark, X, or hourglass depending on state */
  }

  .job-status-badge {
    /* Color change only, no transition */
    background-color: var(--token-running);
    color: var(--token-text);
  }
}
```

---

## Section 8: Motion Best Practices

### ✅ Do
- Use semantic motion tokens (not magic numbers)
- Stagger entry animations for lists (40–60ms between items)
- Reduce motion on exit (leave faster than enter)
- Announce state changes to screen readers (not via motion alone)
- Test with `prefers-reduced-motion` enabled

### ❌ Don't
- Hardcode transition durations (use tokens)
- Use `ease` or `linear` (use semantic easing tokens)
- Create bouncy or playful animations (keep it professional)
- Animate on every state change (only meaningful transitions)
- Ignore reduced-motion preferences

---

## Section 9: Implementation Checklist

- [ ] All `transition` values use `duration-*` and `easing-*` tokens
- [ ] Modal open/close transitions are smooth and fast
- [ ] Job status badge animates smoothly during state changes
- [ ] Progress bar fills smoothly, never jumpy
- [ ] Skeleton screens pulse appropriately
- [ ] `prefers-reduced-motion: reduce` is respected
- [ ] No decorative motion (every animation communicates change)
- [ ] Focus rings are visible and animated consistently
- [ ] Button presses have tactile feedback (scale)
- [ ] List items stagger on entry

---

## Appendix: Token Quick Reference

| Purpose | Token | Value |
|---|---|---|
| Instant feedback | `duration-instant` | 0ms |
| Micro-interactions | `duration-fast` | 120ms |
| Standard transitions | `duration-medium` | 240ms |
| Major transitions | `duration-slow` | 360ms |
| Standard easing | `easing-standard` | `cubic-bezier(0.4, 0, 0.2, 1)` |
| Fast exit easing | `easing-emphasized` | `cubic-bezier(0.05, 0.7, 0.1, 1)` |
| Fast entry easing | `easing-decelerate` | `cubic-bezier(0, 0, 0.2, 1)` |

This document is the **single source of truth** for all motion in xEDA.
