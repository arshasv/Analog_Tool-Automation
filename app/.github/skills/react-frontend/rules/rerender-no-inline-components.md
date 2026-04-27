# rerender-no-inline-components

**Category:** Re-render Optimization

Do not define child components inline inside parent render.

- Prefer module-level or memoized component definitions.
- Avoid remount/churn from recreated component identities.
