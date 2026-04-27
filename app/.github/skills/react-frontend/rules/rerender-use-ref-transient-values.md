# rerender-use-ref-transient-values

**Category:** Re-render Optimization

Store transient frequently changing values in refs.

- Prefer refs for non-visual mutable values.
- Avoid state updates when UI does not need rerender.
