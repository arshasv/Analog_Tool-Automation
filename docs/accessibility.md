# Accessibility

**Owner:** Design System  
**Version:** 1.0  
**Scope:** WCAG 2.1 AA compliance, keyboard navigation, screen-reader behavior, and focus management.

## Purpose

xEDA must be usable by **everyone**, regardless of ability:
- Keyboard-only users (no mouse/trackpad)
- Screen reader users (blind, low vision)
- Users with motor disabilities (tremor, limited dexterity)
- Users with cognitive disabilities (dyslexia, ADHD)
- Users with temporary disabilities (broken arm, noisy environment)
- Users in low-light or high-glare environments

Accessibility is **not optional** and is **not a separate layer**—it constrains every design decision.

---

## Section 1: WCAG 2.1 Compliance Level

**Target:** WCAG 2.1 Level AA (minimum)  
**Aspiration:** WCAG 2.1 Level AAA (preferred)

### Specific Standards

| Criterion | Level | Implementation |
|---|---|---|
| 1.4.3 Contrast (Minimum) | AA | Text: 4.5:1 (normal), 3:1 (large) |
| 1.4.11 Non-text Contrast | AA | UI components: 3:1 |
| 2.1.1 Keyboard | A | All functionality keyboard accessible |
| 2.1.2 No Keyboard Trap | A | Focus can always move away |
| 2.4.3 Focus Order | A | Logical, intentional tab order |
| 2.4.7 Focus Visible | AA | Always visible, 2px minimum |
| 2.5.5 Target Size (Enhanced) | AAA | Minimum 44×44px (touch) |
| 3.2.1 On Focus | A | No unexpected context changes |
| 3.3.1 Error Identification | A | Errors identified and described |
| 4.1.2 Name, Role, Value | A | Accessible name for all UI |
| 4.1.3 Status Messages | AAA | Live regions for async updates |

---

## Section 2: Contrast Standards

All colors must meet **WCAG AA minimum** (4.5:1 for text).

### Text Contrast

```
REQUIRED: 4.5:1 (normal text, large UI text)
ENHANCED: 7:1 (AAA, recommended)

For xEDA:
- Body text:       token-text-primary on token-background = 7:1+
- Form labels:     token-text-primary on token-surface = 5:1+
- Status badges:   white on token-success/error/pending = 4.5:1+
- Disabled text:   token-text-tertiary on surface = 4.5:1+
```

### Non-Text Contrast (UI Elements)

```
REQUIRED: 3:1 (focus rings, borders, status icons)
ENHANCED: 4.5:1 (AAA, recommended)

For xEDA:
- Focus ring:         token-border-interactive on background = 3:1+
- Border on surface:  token-border-strong on token-surface = 3:1+
- Status icon (error):  red on light background = 3:1+
- Chart grid:         token-plot-grid on token-plot-background = 3:1+
```

### Contrast Checking

- Use [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- Use [Stark](https://www.getstark.co/) for Figma/design tools
- Test actual colors, not token names
- Test in both light and dark themes
- Test with common vision-deficiency simulators (deuteranopia, protanopia, tritanopia)

---

## Section 3: Keyboard Accessibility

### Requirement: Everything Must Be Keyboard Accessible

Every interactive element must be reachable and usable without a mouse.

#### Keyboard Navigation

| Key | Behavior |
|---|---|
| `Tab` | Move focus to next interactive element |
| `Shift+Tab` | Move focus to previous interactive element |
| `Enter` | Activate button or submit form |
| `Space` | Toggle checkbox, toggle button state |
| `Escape` | Close modal, dismiss overlay, cancel operation |
| `Arrow keys` | Navigate lists, menus, tabs |
| `Home/End` | Jump to start/end of list |

#### Tab Order

- **Rule 1:** Tab order follows visual flow (top-to-bottom, left-to-right)
- **Rule 2:** Never use positive `tabindex` values (breaks natural order)
- **Rule 3:** Use `tabindex="-1"` only for programmatically focused elements
- **Rule 4:** Remove from tab order if element is hidden (display: none, visibility: hidden, or aria-hidden="true")

#### Example: Modal Focus Management

```
1. Modal opens
   → Focus moves to first interactive element in modal (input or button)
   → Visual focus ring appears
   → tabindex trap installed (focus cycles within modal)

2. Tab forward
   → Tab through modal form fields
   → Tab to [OK] button
   → Tab wraps to first field (modal trap)

3. Escape key
   → Modal closes
   → Focus returns to trigger button
   → Modal content removed from tab order
```

#### No Keyboard Traps

- Users must be able to navigate away from any element using keyboard
- Exception: Modals should trap focus **while open** (intentional)
- Modals must have an obvious close mechanism (close button, escape key)

### Testing Keyboard Accessibility

```html
<!-- Test: Try using site with keyboard ONLY -->

1. Start fresh (Cmd+Shift+R)
2. Tab through every interactive element
3. Test each element with:
   - Enter (buttons, links)
   - Space (checkboxes, toggles)
   - Arrow keys (lists, tabs)
   - Escape (overlays, modals)
4. Verify:
   - Focus ring always visible
   - Tab order is logical
   - No elements are unreachable
   - No unexpected page jumps
   - No keyboard traps (except modals)
```

---

## Section 4: Focus Management & Visibility

### Focus Ring Requirements

```css
/* ALWAYS VISIBLE, NON-NEGOTIABLE */

:focus-visible {
  outline: 2px solid var(--token-border-interactive);
  outline-offset: 2px;
}

/* Minimum dimensions */
- Thickness: 2px
- Offset: 2px (space between element and ring)
- Color: High contrast (token-border-interactive)
- Shape: Rectangle around element
- Animation: None (can transition color, not appear/disappear)
```

### Never Remove Focus Outline

```css
/* ❌ WRONG: Removes focus, making keyboard nav impossible */
:focus { outline: none; }

/* ✅ CORRECT: Keep outline visible */
button:focus-visible { /* color changes allowed */ }
```

### Focus On Page Load

- Focus should start on the main content or first interactive element
- For modals/overlays: Focus moves to first field in modal
- After action: Focus moves to result or confirmation
- Never use `autofocus` attribute (accessibility issue)

### Focus Restoration After Async Updates

When content updates (results loaded, job completed):
1. Keep focus where it was if possible
2. Or move focus to new result summary
3. Announce change via live region
4. Never make user hunt for focus

---

## Section 5: Screen Reader Accessibility

### Semantic HTML (Foundation)

Use correct HTML elements. Screen readers rely on this.

| Semantic | ARIA Alternative | Use |
|---|---|---|
| `<button>` | `role="button"` | Clickable actions |
| `<input>` + `<label>` | `role="textbox"` | Form fields |
| `<nav>` | `role="navigation"` | Navigation landmarks |
| `<main>` | `role="main"` | Main content |
| `<table>` + `<th>` | `role="grid"` | Data tables |
| `<h1>–<h6>` | `role="heading"` + `aria-level` | Headings |

**Rule:** Always prefer semantic HTML over ARIA. ARIA is a safety net, not a replacement.

### Accessible Names

Every interactive element needs a **clear, descriptive accessible name**.

#### Buttons

```html
<!-- ✅ CORRECT: Descriptive name -->
<button>Run Simulation</button>

<!-- ❌ WRONG: Not descriptive enough -->
<button>Go</button>

<!-- ✅ CORRECT: Icon + aria-label -->
<button aria-label="Run Simulation">▶</button>

<!-- ✅ CORRECT: Icon + hidden text -->
<button>
  <span aria-hidden="true">▶</span>
  <span class="sr-only">Run Simulation</span>
</button>
```

#### Form Fields

```html
<!-- ✅ CORRECT: Explicit label -->
<label for="width-input">Width (µm)</label>
<input id="width-input" type="number" />

<!-- ✅ CORRECT: aria-label if label not visible -->
<input type="search" aria-label="Search results" />

<!-- ❌ WRONG: No label -->
<input type="number" />
```

#### Links

```html
<!-- ✅ CORRECT: Descriptive link text -->
<a href="/design/123">Circuit: Current Mirror v2</a>

<!-- ❌ WRONG: Generic "click here" -->
<a href="/design/123">click here</a>

<!-- ✅ CORRECT: aria-label for icon links -->
<a href="/settings" aria-label="Settings">⚙</a>
```

### Live Regions for Async Updates

When job status changes or results load, **announce to screen readers**:

```html
<!-- Status updates (polite, non-interrupting) -->
<div aria-live="polite" aria-atomic="true">
  Job status: RUNNING
</div>

<!-- Urgent alerts (assertive, interrupts) -->
<div aria-live="assertive" aria-atomic="true" role="alert">
  Error: Simulation failed
</div>
```

#### xEDA-Specific Live Regions

| Event | Live Region | Content |
|---|---|---|
| Job submitted | polite | "Job submitted, status: PENDING" |
| Status changes | polite | "Job status changed: RUNNING" |
| Progress update | off | (update every 5–10 sec, not every second) |
| Simulation complete | polite | "Simulation completed in 2 min 34 sec" |
| Error occurs | assertive | "Error: [specific error message]" |
| Form validation fails | assertive | "Form has errors: [list fields]" |

#### Implementation

```typescript
// React example
const [jobStatus, setJobStatus] = useState('PENDING');

return (
  <div aria-live="polite" aria-atomic="true">
    Job status: {jobStatus}
  </div>
);
```

### Headings & Structure

```html
<!-- ✅ CORRECT: Semantic heading hierarchy -->
<h1>xEDA Dashboard</h1>
<h2>Current Job</h2>
<h3>Parameters</h3>
<h2>Results</h2>
<h3>Metrics</h3>
<h3>Waveforms</h3>

<!-- ❌ WRONG: Skip levels -->
<h1>Dashboard</h1>
<h3>Current Job</h3> <!-- Missing h2 -->
```

### Tables

```html
<!-- ✅ CORRECT: Semantic table with headers -->
<table>
  <thead>
    <tr>
      <th scope="col">Parameter</th>
      <th scope="col">Value</th>
      <th scope="col">Unit</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Gain</td>
      <td>-2.5</td>
      <td>dB</td>
    </tr>
  </tbody>
</table>

<!-- ✅ CORRECT: If table is complex, add caption -->
<table>
  <caption>Circuit Optimization Results (Run 001)</caption>
  <!-- ... -->
</table>
```

---

## Section 6: Reduced Motion & Animations

Users with vestibular disorders, migraines, or ADHD may experience dizziness from motion.

### Respecting prefers-reduced-motion

```css
/* REQUIRED: Respect user's motion preferences */
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

### No Decorative Motion

- ❌ Bouncy animations
- ❌ Parallax scrolling
- ❌ Spinning loaders (use pulsing skeleton instead)
- ✅ Smooth transitions (communicate state change)
- ✅ Progress indicators (communicate progress)
- ✅ Loading states (communicate wait time)

---

## Section 7: Color Accessibility

### Don't Use Color Alone

Never communicate information using color alone. Always add:
- An icon or symbol
- Text label
- Pattern or texture

#### Example: Job Status

```
❌ WRONG: Red circle = failed
  (color-blind users can't tell)

✅ CORRECT:
  - Red circle + X icon
  - Red badge + "Failed" text
  - Red + striped pattern + "Failed"
```

### Color Blindness Simulation

Test designs in different color-vision modes:
- **Protanopia** (no red perception)
- **Deuteranopia** (no green perception)
- **Tritanopia** (no blue-yellow perception)
- **Achromatopsia** (complete color blindness)

Use tools:
- [Stark contrast checker](https://www.getstark.co/)
- [Color Blindness Simulator](https://www.color-blindness.com/coblis-color-blindness-simulator/)
- [Accessible Colors](https://accessible-colors.com/)

---

## Section 8: Cognitive Accessibility

### Clear Language

- Use simple, active voice
- Avoid technical jargon without explanation
- Break information into chunks
- Use lists instead of paragraphs
- Use headings to organize content

### Consistent Navigation

- Navigation location should not change between pages
- Navigation labels should be consistent
- Links should clearly indicate their destination

### Error Messages

```
❌ WRONG: "Invalid input"
✅ CORRECT: "Width must be between 0.1 and 10 micrometers"

❌ WRONG: "Error 422"
✅ CORRECT: "Simulation failed: Parameter 'L' is out of valid range"
```

### Predictable Behavior

- Don't change context unexpectedly
- Buttons should do what they say
- Forms should submit on button click, not on field blur
- Autocomplete should be optional, not hidden

---

## Section 9: Mobile & Touch Accessibility

### Touch Target Size

- **Minimum:** 44×44px (WCAG AAA)
- **Recommended:** 48×48px
- **Spacing:** At least 8px between targets

```css
button {
  min-width: 44px;
  min-height: 44px;
  padding: 10px 16px; /* Ensures 44px height with normal text */
}
```

### Mobile Testing

- Test on actual mobile devices
- Test with screen reader (VoiceOver on iOS, TalkBack on Android)
- Test with system zoom at 150%
- Test in landscape and portrait
- Test with one hand (reachability)

---

## Section 10: Accessibility Checklist

### Markup & Semantics
- [ ] Semantic HTML used (button, input, table, nav, etc.)
- [ ] Headings present and in order (h1–h6)
- [ ] Images have alt text (or aria-hidden if decorative)
- [ ] Links have descriptive text
- [ ] Form fields have labels

### Keyboard & Focus
- [ ] All interactive elements keyboard accessible
- [ ] Tab order is logical
- [ ] Focus ring always visible (2px)
- [ ] No keyboard traps (except modals with close)
- [ ] Escape closes modals and overlays

### Screen Reader
- [ ] Accessible names on all interactive elements
- [ ] Live regions for async updates
- [ ] Semantic table structure (th, scope, caption)
- [ ] List markup for lists
- [ ] Landmarks used (nav, main, etc.)

### Motion & Animation
- [ ] Animations use duration tokens (not hardcoded)
- [ ] prefers-reduced-motion respected
- [ ] No decorative motion
- [ ] Spinners replaced with skeleton (no motion)

### Color & Contrast
- [ ] Text contrast ≥4.5:1 (normal), ≥3:1 (large)
- [ ] UI element contrast ≥3:1
- [ ] Color not used alone to convey meaning
- [ ] Works in grayscale

### Mobile & Touch
- [ ] Touch targets ≥44×44px
- [ ] Touch target spacing ≥8px
- [ ] Works with system zoom (150%, 200%)
- [ ] Landscape and portrait both work
- [ ] Tested on actual mobile device

### Responsiveness
- [ ] Works at small viewport sizes
- [ ] No horizontal scroll on small devices
- [ ] Text resizable without loss of content
- [ ] Line length reasonable (40–75 characters)

---

## Section 11: Accessibility Audit Process

### Automated Testing
1. Use axe DevTools browser extension
2. Run Lighthouse accessibility audit
3. Use WAVE Web Accessibility Evaluation Tool
4. Check for automated violations

### Manual Testing
1. Keyboard-only navigation (no mouse)
2. Screen reader testing (NVDA on Windows, JAWS, VoiceOver on Mac)
3. Color contrast verification
4. Focus management and tab order
5. Mobile zoom and responsive behavior

### User Testing
- Include users with disabilities in user research
- Test with real assistive technologies
- Observe pain points and workarounds
- Iterate based on feedback

---

## Section 12: Accessibility Score Card

Rate xEDA's accessibility:

| Category | Score | Notes |
|---|---|---|
| Semantic HTML | 8/10 | Good baseline, minor issues |
| Keyboard Navigation | 8/10 | Tab order logical, some edge cases |
| Focus Management | 7/10 | Focus visible, some issues after async |
| Screen Reader | 7/10 | Live regions in place, some gaps |
| Contrast | 8/10 | Meets AA, could be AAA |
| Motion | 7/10 | prefers-reduced-motion respected |
| Color | 8/10 | Icons + text, not color alone |
| Mobile Touch | 7/10 | 44px targets, spacing needs work |

**Overall Accessibility Score: 7.5/10**

---

This document is **enforceable**. Accessibility is not negotiable.

