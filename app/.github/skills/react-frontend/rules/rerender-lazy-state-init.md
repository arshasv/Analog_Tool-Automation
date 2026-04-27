# rerender-lazy-state-init

**Category:** Re-render Optimization

Use lazy initialization for expensive initial state.

- Prefer `useState(() => computeInitial())`.
- Avoid recomputing heavy defaults on rerender.
