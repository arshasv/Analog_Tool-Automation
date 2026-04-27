---
name: vercel-react-best-practices-xeda
description: React frontend performance optimization guidelines for the xEDA project, curated from Vercel best practices.
license: MIT
metadata:
	author: vercel
	version: "1.0.0"
	curated_for: xEDA
---

# Vercel React Best Practices (xEDA Curated)

This is a curated subset of the Vercel React/Next.js guidance for the xEDA codebase.

## Scope for xEDA

xEDA is currently a Python backend project with planned React UI integration (see project docs).  
Because there is no Next.js app in this repository yet, **Next.js server/RSC/API-route-specific rules are removed**.

## Kept Categories and Rules

### 1. Eliminating Waterfalls (Keep)

- `async-cheap-condition-before-await`
- `async-defer-await`
- `async-parallel`
- `async-dependencies`
- `async-suspense-boundaries`

### 2. Bundle Size Optimization (Keep: React-applicable subset)

- `bundle-barrel-imports`
- `bundle-analyzable-paths`
- `bundle-dynamic-imports`
- `bundle-conditional`
- `bundle-preload`

### 3. Client-Side Data Fetching (Keep)

- `client-swr-dedup`
- `client-event-listeners`
- `client-passive-event-listeners`
- `client-localstorage-schema`

### 4. Re-render Optimization (Keep)

- `rerender-defer-reads`
- `rerender-memo`
- `rerender-memo-with-default-value`
- `rerender-dependencies`
- `rerender-derived-state`
- `rerender-derived-state-no-effect`
- `rerender-functional-setstate`
- `rerender-lazy-state-init`
- `rerender-simple-expression-in-memo`
- `rerender-split-combined-hooks`
- `rerender-move-effect-to-event`
- `rerender-transitions`
- `rerender-use-deferred-value`
- `rerender-use-ref-transient-values`
- `rerender-no-inline-components`

### 5. Rendering Performance (Keep: React-applicable subset)

- `rendering-animate-svg-wrapper`
- `rendering-content-visibility`
- `rendering-hoist-jsx`
- `rendering-svg-precision`
- `rendering-conditional-render`
- `rendering-usetransition-loading`
- `rendering-script-defer-async`

### 6. JavaScript Performance (Keep)

- `js-batch-dom-css`
- `js-index-maps`
- `js-cache-property-access`
- `js-cache-function-results`
- `js-cache-storage`
- `js-combine-iterations`
- `js-length-check-first`
- `js-early-exit`
- `js-hoist-regexp`
- `js-min-max-loop`
- `js-set-map-lookups`
- `js-tosorted-immutable`
- `js-flatmap-filter`
- `js-request-idle-callback`

### 7. Advanced Patterns (Keep)

- `advanced-effect-event-deps`
- `advanced-event-handler-refs`
- `advanced-init-once`
- `advanced-use-latest`

## Rule Files

Each kept rule now has a dedicated file in `rules/` using this naming convention:

- `rules/<rule-id>.md`

Examples:

- `rules/async-parallel.md`
- `rules/bundle-dynamic-imports.md`
- `rules/rerender-transitions.md`
- `rules/rendering-content-visibility.md`
- `rules/js-set-map-lookups.md`
- `rules/advanced-use-latest.md`

## Removed as Not Related to Current xEDA Repo

### Next.js / Server-specific rules removed

- `async-api-routes`
- All `server-*` rules:
	- `server-auth-actions`
	- `server-cache-react`
	- `server-cache-lru`
	- `server-dedup-props`
	- `server-hoist-static-io`
	- `server-no-shared-module-state`
	- `server-serialization`
	- `server-parallel-fetching`
	- `server-parallel-nested-fetching`
	- `server-after-nonblocking`

### Hydration/resource-hint rules removed (not relevant without SSR/RSC setup)

- `bundle-defer-third-party`
- `rendering-hydration-no-flicker`
- `rendering-hydration-suppress-warning`
- `rendering-activity`
- `rendering-resource-hints`

## Notes for Future

If xEDA adds a Next.js frontend (SSR/RSC or route handlers), restore removed `server-*`, hydration, and API-route rules.
