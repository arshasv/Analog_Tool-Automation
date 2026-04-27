# rerender-functional-setstate

**Category:** Re-render Optimization

Use functional updates when next state depends on previous state.

- Prefer `setState(prev => next(prev))`.
- Avoid stale-closure bugs and unstable callbacks.
