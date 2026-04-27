# async-defer-await

**Category:** Eliminating Waterfalls

Move `await` into the branch where data is actually needed.

- Prefer lazy awaiting near usage.
- Avoid blocking unrelated render or logic paths.
