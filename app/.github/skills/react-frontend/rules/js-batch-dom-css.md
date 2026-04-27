# js-batch-dom-css

**Category:** JavaScript Performance

Batch style/class DOM mutations to reduce layout thrash.

- Prefer grouped class toggles or single cssText update.
- Avoid repeated interleaved read/write DOM operations.
