# Async UX Philosophy & Backend-to-UI Contracts

**Owner:** Design System + Backend API  
**Version:** 1.0  
**Scope:** How backend states map to UI appearance, behavior, and user messaging.

## Purpose

xEDA is a **long-running workflow system**. Users submit jobs that may take minutes or hours to complete. The design system must make this async reality **visible, predictable, and trustworthy**.

This document formalizes:
1. **Backend states** (from BACKEND_API_DOCUMENTATION.md)
2. **UI representation** (visual, textual, motion)
3. **Accessibility announcements** (screen readers)
4. **User messaging** (what to expect)
5. **Error recovery** (what to do next)

---

## Section 1: Backend Job States

From [BACKEND_API_DOCUMENTATION.md](BACKEND_API_DOCUMENTATION.md):

```python
class ProcessStatus(str, Enum):
    PENDING = "PENDING"      # Task is queued, waiting to start
    RUNNING = "RUNNING"      # Simulation or optimization in progress
    COMPLETED = "COMPLETED"  # Successfully finished
    FAILED = "FAILED"        # Error occurred
```

The UI must represent each state clearly and unambiguously.

---

## Section 2: State-by-State UI Contract

### State: PENDING

**Backend:** Job is queued, waiting for an available worker.

#### Visual Representation
```
Status Badge:
  Background: var(--token-pending)    [Neutral blue]
  Icon:       ⏱ (hourglass)
  Text:       "Pending"
  Pulse:      Static (no animation, not urgent)

Progress Bar:
  Progress:   0%
  Color:      var(--token-pending)
  Message:    "Your job is queued. Waiting to start..."

Layout:
  Status panel: Sticky, visible
  Parameters:   Locked (read-only)
  Results:      Hidden
  Controls:     [Cancel] enabled
```

#### User Messaging
- Primary: "Your job is in the queue"
- Secondary: "Expected wait time: ~2 minutes" (if available from backend)
- Reassurance: "You can leave this page; we'll notify you when it starts"
- Action: "Click Cancel to remove from queue"

#### Accessibility Announcement
```
Screen reader (ARIA live region, polite):
"Job status: pending. Your job is queued and waiting to start."
```

#### Motion
- No animation (pending is not urgent)
- Focus ring visible on status badge
- Badge color does not pulse

#### Transition to RUNNING
- **Duration:** 240ms (easing-decelerate)
- **Animation:** Badge background color transition, icon crossfade (hourglass → spinner)
- **Live region update:** Announce new status

---

### State: RUNNING

**Backend:** Simulation or optimization actively executing.

#### Visual Representation
```
Status Badge:
  Background: var(--token-running)    [Bright cyan]
  Icon:       ⟳ (animated spinner)
  Text:       "Running"
  Pulse:      Animated, 2s rotation

Progress Bar:
  Progress:   0–100% (actual from backend)
  Color:      var(--token-running)
  Message:    "Simulation in progress (DC analysis, AC sweep, Tran..."
  Update:     Every 1–5 seconds

Live Log:
  Enabled:    ✓
  Content:    Last 20 lines of simulation output
  Update:     Real-time or every 2 seconds
  Scroll:     Auto-scroll to latest (unless user scrolled)

Layout:
  Status panel: Sticky, always visible
  Parameters:   Locked (read-only, slightly muted)
  Results:      Placeholder or skeleton loading
  Controls:     [Cancel] enabled, [Pause] optional
```

#### User Messaging
- Primary: "Simulation running"
- Progress: "42% complete (Transient analysis)" with ETA if available
- Reassurance: "This usually takes 2–5 minutes"
- Live output: Show last few lines of simulation log
- Action: "Click Cancel to stop the simulation"

#### Accessibility Announcement
```
Screen reader (ARIA live region, polite):
First update:    "Job status: running. Simulation started."
Every 10 seconds: "Progress: 42 percent complete."
```

#### Motion
```css
/* Spinner rotation: continuous, non-intrusive */
@keyframes spinner-rotate {
  to { transform: rotate(360deg); }
}

.status-icon {
  animation: spinner-rotate 2s linear infinite;
}

/* Respect reduced motion */
@media (prefers-reduced-motion: reduce) {
  .status-icon {
    animation: none;
    content: "→"; /* Static arrow indicating progress */
  }
}
```

#### Progress Bar Fill
- **Duration:** 240ms per update (smooth fill)
- **Easing:** ease-out (slowing as approaching completion)
- **Stalling:** If progress stalls >30 sec, show warning: "Simulation taking longer than expected"

#### Transition to COMPLETED or FAILED
- **Duration:** 240ms (easing-emphasized, exit faster than enter)
- **Animation:** Spinner → checkmark or X, color transition
- **Live region:** Announce final status immediately

---

### State: COMPLETED

**Backend:** Job finished successfully. Results available.

#### Visual Representation
```
Status Badge:
  Background: var(--token-completed)  [Green]
  Icon:       ✓ (checkmark, briefly scales up)
  Text:       "Completed"
  Pulse:      Brief scale-up (240ms), then settle

Completion Message:
  Text:       "Simulation completed successfully in 4 min 32 sec"
  Timestamp:  Start and end times
  Summary:    Key metrics (gain, phase, etc.)

Results Panel:
  Fade-in:    240ms (staggered, after badge completes)
  Tabs:       [Metrics] [Plots] [Raw Data] [Logs] [Download]
  Active:     Metrics tab by default
  Content:    Pre-loaded from backend response

Download Button:
  Enabled:    ✓ (glowing slightly to draw attention)
  Filename:   "xeda_run_001_results.zip"

Layout:
  Status panel: Still visible but background optional (job done)
  Parameters:   May collapse, but still visible
  Results:      Expanded, full focus
  Controls:     [Run Again] [Optimize] [Load Template] [Download]
```

#### User Messaging
- Primary: "Simulation completed successfully"
- Performance: "Completed in 4 min 32 sec"
- Summary: "Gain: -2.3 dB | Phase: 65° | BW: 250 MHz"
- Action: "Review results below, or download ZIP"
- Next: "Want to optimize? Click Optimize to auto-tune parameters"

#### Accessibility Announcement
```
Screen reader (ARIA assertive, interrupts):
"Job completed successfully in 4 minutes and 32 seconds."
(Live region also updates with key metrics)
```

#### Motion
```css
/* Checkmark briefly bounces on completion */
@keyframes check-bounce {
  0% { transform: scale(0.8); opacity: 0; }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); opacity: 1; }
}

.status-icon.completed {
  animation: check-bounce 240ms var(--easing-emphasized) forwards;
}

/* Results fade in smoothly after badge completes */
.results-panel {
  animation: fade-in 360ms var(--easing-decelerate) forwards;
  animation-delay: 240ms;
}
```

#### Next Steps UI
- Prominent: "Download Results" button (green, glowing)
- Optional: "Optimize Further" button
- Optional: "Compare to Previous Run" link
- Optional: "Save as Template" button

---

### State: FAILED

**Backend:** Job encountered an error and stopped.

#### Visual Representation
```
Status Badge:
  Background: var(--token-failed)     [Red]
  Icon:       ✕ (error X, brief shake)
  Text:       "Failed"
  Pulse:      Brief shake (120ms), then settle

Error Message:
  Title:      "Simulation Failed"
  Description: Human-readable error
  Details:    Technical error details (expandable)
  Code:       Error code for reference

Error Example Panel:
  Title:      "What Went Wrong?"
  Message:    "Parameter 'L' (Length) is out of valid range"
  Valid:      "Valid range: 0.18 µm – 10 µm"
  Your value: "Entered: 0.12 µm"

Layout:
  Status panel: Sticky, error highlighted with red border
  Parameters:   Unlocked, error field highlighted
  Results:      Previous results shown (if any)
  Controls:     [Retry] [Edit Parameters] [Reset] [Cancel]
```

#### User Messaging
- Primary: "Simulation failed"
- Reason: Clear, technical error (in English, not error codes)
- Action: "Fix the error and try again:"
- Suggestion: "Try setting L to 0.18 µm or higher"
- Fallback: "Contact support with error code #NGSPICE_NONCONVERGENCE"

#### Accessibility Announcement
```
Screen reader (ARIA assertive, interrupts):
"Job failed. Error: Parameter L is out of range. 
 Valid range: 0.18 micrometers to 10 micrometers."
```

#### Motion
```css
/* Error shake: brief, emphatic */
@keyframes error-shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
}

.status-icon.failed {
  animation: error-shake 120ms var(--easing-standard) forwards;
}

/* Error panel slides in from below */
.error-message {
  animation: slide-up 240ms var(--easing-decelerate) forwards;
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

#### Recovery UI
- **Immediate Option:** "Retry" (uses same parameters)
- **Edit Option:** "Edit Parameters" (unlocks form for changes)
- **Reset Option:** "Reset to Defaults" (reload template)
- **Support Option:** "Help" (error documentation)
- **Context:** Show what changed since last successful run

#### Retry Behavior
- Clicking [Retry] immediately starts job
- Status transitions: FAILED → PENDING → RUNNING (same UI flow)
- If retry fails again, show: "Two consecutive failures. Check your circuit file."
- After 3 consecutive failures, suggest: "Contact support"

---

## Section 3: Progress Indication

### Progress Feedback Requirements

For RUNNING state, users must know:
1. Is the job still executing?
2. How much longer will it take?
3. What is the current step?
4. Are there any warnings?

#### Progress Bar
```
Visual:  [=========>           ] 45%
Label:   "AC Analysis: frequency sweep 1 of 20"
ETA:     "~3 minutes remaining"
Warning: (if any) "⚠ Convergence slow at 100 MHz"
```

#### Live Log
```
[Simulation Log - Last 10 lines]
> Running AC analysis...
> Frequency range: 50 MHz to 500 MHz
> Points per decade: 50
> Analysis 1/20: 50-100 MHz [==>     ] 33%
> Analysis 2/20: 100-150 MHz [=====>  ] 67%
[↓ Show Full Log]
```

#### Stalled Job Detection
- If progress hasn't changed in 60 seconds: "Simulation taking longer than expected"
- If job older than expected max time: "This is taking longer than usual. Job may be stuck."
- After 2 × expected time: "Job appears stalled. Click Cancel or Contact Support"

---

## Section 4: State Transitions & Timing

### Normal Happy Path
```
1. User clicks [Run]
   → POST /api/v1/run
   → Response: process_id, status=PENDING
   → UI: Update badge to PENDING

2. Poll GET /api/v1/status/{process_id}
   → Response: status=PENDING, progress=0%
   → Wait 2–5 seconds before next poll

3. Next poll:
   → Response: status=RUNNING, progress=15%
   → UI: Transition badge to RUNNING, spinner starts
   → Live region: "Job status: running"
   → Every poll after: Update progress bar

4. Final poll:
   → Response: status=COMPLETED, progress=100%, results={}
   → UI: Transition badge to COMPLETED, checkmark bounces
   → Live region: "Job completed"
   → Results fade in, download button highlights

Duration: 2–10 minutes (typical)
```

### Error Path
```
1. User runs job
   → status=PENDING

2. Polling shows:
   → status=RUNNING (simulation executing)

3. Next poll:
   → status=FAILED, error="Parameter L out of range"
   → UI: Badge transitions to FAILED, shake animation
   → Live region: "Job failed. Error: Parameter L out of range"
   → Error panel slides in with suggestion

4. User edits parameter or clicks [Retry]
   → Process repeats from step 1
```

### Polling Strategy

```typescript
// Pseudo-code for polling
const POLL_INTERVAL_PENDING = 5000;  // 5 seconds (job likely queued)
const POLL_INTERVAL_RUNNING = 2000;  // 2 seconds (active feedback)
const POLL_INTERVAL_RETRY = 10000;   // 10 seconds (after multiple failures)

while (job.status !== 'COMPLETED' && job.status !== 'FAILED') {
  const interval = job.status === 'RUNNING'
    ? POLL_INTERVAL_RUNNING
    : POLL_INTERVAL_PENDING;

  await sleep(interval);
  const update = await api.getStatus(job.id);
  updateUI(update);

  if (pollFailureCount > 3) {
    showWarning("Can't reach backend. Check connection.");
    increaseInterval(POLL_INTERVAL_RETRY);
  }
}
```

---

## Section 5: Error Messages & Recovery

### Error Classification

#### Critical Errors (Halt job)
- Circuit file syntax error
- Parameter out of valid range
- NGSpice convergence failure
- Out of memory

**Response:** Clear message + actionable fix

#### Warnings (Continue job, warn user)
- Simulation taking longer than expected
- Minor convergence issues
- Unusual parameter values

**Response:** Log in output, note in results

#### Retryable Errors (Automatic retry)
- Network timeout
- Temporary resource unavailable
- Rate limit (retry after delay)

**Response:** Retry automatically, show status

### Error Message Template

```
Title:        "Simulation Failed"
Category:     [Icon] "Parameter Error" | "Convergence Issue" | "System Error"
Description:  "Parameter 'L' (Length) is out of valid range."
Details:      "Valid range: 0.18 µm – 10 µm. You entered: 0.12 µm."
Suggestion:   "Try increasing L to 0.18 µm or higher."
Code:         "ERR_PARAM_OUT_OF_RANGE (code 1042)"
Support:      "Need help? [Contact Support] [View Docs]"

Actions:      [Edit Parameters] [Reset to Defaults] [Retry]
```

---

## Section 6: Optimization-Specific Async States

When mode="optimize", additional states apply:

### Optimization-Specific States

```
PENDING_OPTIMIZATION:   Optimization job queued
OPTIMIZING:             Coarse search in progress
REFINING:               Nelder-Mead local search
OPTIMIZATION_COMPLETE:  Best parameters found
OPTIMIZATION_FAILED:    Optimization did not converge
```

#### Optimization Progress Display
```
Status:    "Optimizing Parameters"
Progress:  "Coarse search: [=========>           ] 45%"
Progress:  "Global candidates: 342 evaluated"
Best so far: "Gain: -2.0 dB (target: -3 dB) | Phase: 62° (target: >60°)"
Time:      "Elapsed: 5 min 32 sec | Estimated: ~8 min total"
```

#### Optimization Results
```
Best Design Found:
  W:     1.2 µm  (↑ 20% from initial)
  L:     0.18 µm (unchanged)
  Vdd:   3.5 V   (↑ 6% from initial)
  CL:    12 pF   (↑ 20% from initial)

Performance Achieved:
  Gain:  -2.8 dB ✓ (target: -3 dB)
  Phase: 68°     ✓ (target: >60°)
  BW:    280 MHz ✓ (target: 200 MHz)
  Power: 11.2 mW ⚠ (target: 10 mW)

Actions: [Apply] [Simulate] [Export] [Download Log]
```

---

## Section 7: Connection & Polling Failures

What if the backend is unreachable?

### Backend Unreachable (No Response)

```
Scenario: Poll request times out 3 times in a row

UI Response:
  1. Show subtle warning in status area: "⚠ Connection unstable"
  2. Increase poll interval (back off)
  3. After 30 seconds: Show banner: "Can't reach backend. Retrying..."
  4. After 5 minutes: Show error: "Connection lost. Refresh page or contact support."

User Options:
  - [Retry Now] (manual retry)
  - [Refresh Page] (reload, reconnect)
  - [View Offline] (show cached results if available)

Live Region Announcement:
  "Backend unreachable. Job may still be running on the server."
```

### Stale Results (Cached vs. Backend)

If user refreshes or returns to dashboard:

```
1. Load cached job state from localStorage
2. Poll backend for current status
3. If statuses match: Show cached results
4. If backend has newer status: Update UI and show latest
5. If backend returns FAILED but cache shows RUNNING: Alert user

UI Pattern:
  "⚠ Job status updated: was RUNNING, now COMPLETED"
  [Refresh Results] [View New Results]
```

---

## Section 8: Accessibility Announcement Patterns

### Live Region Strategy

Use `aria-live="polite"` for non-urgent updates, `aria-live="assertive"` for urgent.

```html
<!-- Non-urgent job status updates -->
<div aria-live="polite" aria-atomic="true" role="status">
  {jobStatus}: {statusMessage}
</div>

<!-- Urgent errors and alerts -->
<div aria-live="assertive" aria-atomic="true" role="alert">
  {errorMessage}
</div>

<!-- Progress updates (every 10–30 seconds, not constant) -->
<div aria-live="polite" aria-atomic="true" role="progressbar"
     aria-valuenow={progress} aria-valuemin="0" aria-valuemax="100">
  Progress: {progress}% ({currentStep})
</div>
```

### Announcement Content

```
PENDING:       "Job status: pending. Waiting to start."
RUNNING:       "Job status: running. Progress: 45 percent."
COMPLETED:     "Job completed successfully in 4 minutes and 32 seconds."
FAILED:        "Job failed. Error: Parameter L is out of range."
```

---

## Section 9: Checklist: Async UX Implementation

- [ ] Backend states (PENDING, RUNNING, COMPLETED, FAILED) mapped to UI
- [ ] Status badge color changes per state (with icon, not color alone)
- [ ] Progress bar fills smoothly, updates every 1–5 seconds
- [ ] Live log shows last 20 lines, updates in real-time
- [ ] Live regions announce status changes (aria-live)
- [ ] Error messages are clear and actionable
- [ ] Spinner respects prefers-reduced-motion
- [ ] Polling increases interval if backend unreachable
- [ ] Results fade in after completion
- [ ] Download button prominent on success
- [ ] Retry logic works for both success and failure cases
- [ ] Optimization states show best parameters found so far
- [ ] No loss of feedback on page refresh (restore from cache)
- [ ] Keyboard accessible throughout (focus not lost on update)

---

This document is the **definitive backend-to-UI contract**. All async behavior must follow these patterns.
