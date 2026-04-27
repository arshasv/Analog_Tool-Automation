# js-min-max-loop

**Category:** JavaScript Performance

Use a linear scan for min/max when sorting is unnecessary.

- Prefer O(n) loop for extrema.
- Avoid O(n log n) sort for single-value extraction.
