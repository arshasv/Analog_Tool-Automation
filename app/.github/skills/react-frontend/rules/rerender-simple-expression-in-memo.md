# rerender-simple-expression-in-memo

**Category:** Re-render Optimization

Do not memoize trivial primitive expressions.

- Prefer direct inline computation for cheap values.
- Avoid memo overhead where no benefit exists.
