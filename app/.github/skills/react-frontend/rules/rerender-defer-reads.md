# rerender-defer-reads

**Category:** Re-render Optimization

Do not subscribe to state you only need inside callbacks.

- Prefer reading at interaction time.
- Avoid render-time subscriptions that trigger extra updates.
