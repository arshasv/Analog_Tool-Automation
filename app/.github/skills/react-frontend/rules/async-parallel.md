# async-parallel

**Category:** Eliminating Waterfalls

Run independent async work in parallel.

- Prefer `Promise.all` for unrelated calls.
- Avoid serial `await` chains when dependencies do not exist.
