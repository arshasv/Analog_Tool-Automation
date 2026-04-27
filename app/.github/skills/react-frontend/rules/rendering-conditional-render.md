# rendering-conditional-render

**Category:** Rendering Performance

Prefer explicit ternary rendering for clear branch behavior.

- Prefer `condition ? <A /> : null` for optional elements.
- Avoid ambiguous `&&` branches for non-boolean values.
