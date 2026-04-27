# async-cheap-condition-before-await

**Category:** Eliminating Waterfalls

Check fast local conditions before awaiting remote values.

- Prefer early return for cheap sync guards.
- Avoid paying network/flag latency when feature is already off.