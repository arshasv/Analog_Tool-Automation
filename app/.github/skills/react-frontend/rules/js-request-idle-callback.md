# js-request-idle-callback

**Category:** JavaScript Performance

Defer non-critical work to browser idle time.

- Prefer `requestIdleCallback` (or fallback scheduling) for low-priority tasks.
- Avoid competing with critical render/input work.
