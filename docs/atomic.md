# Atomic Design

## Purpose
This document describes how xEDA UI should be assembled from small, reusable pieces into full pages.

## Atomic Structure

### Atoms
- Buttons
- Inputs
- Selects
- Checkboxes and toggles
- Badges and chips
- Icons
- Labels
- Divider lines

### Molecules
- Labeled form field
- Search or filter row
- Status chip with timestamp
- Metric pair
- File upload row
- Action group

### Organisms
- Parameter editor panel
- Upload and run panel
- Results summary panel
- Job status panel
- Navigation sidebar or top bar

### Templates
- Dashboard layout
- Results detail layout
- Empty-state layout
- Error-state layout

### Pages
- Home dashboard
- Circuit submission workflow
- Job detail view
- Results review view

## Composition Rules
- Build interfaces from the smallest practical reusable unit
- Keep atoms visually consistent across all pages
- Molecules should combine one clear task and one clear outcome
- Organisms should be reusable enough to serve multiple circuit types

## xEDA-Specific Guidance
- Circuit forms should not duplicate layout logic inside every page
- Status and metric displays should be reusable across simulation and optimization flows
- Plot containers should behave like a standard organism, even when the underlying chart changes
