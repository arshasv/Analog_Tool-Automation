# Components

## Purpose
This document defines the key reusable UI components for xEDA and the behavior each one should expose.

## Core Component Set

### Application Shell
- Header
- Sidebar or global navigation
- Main content region
- Footer or utility bar when needed

### Job Submission
- File uploader
- Parameter editor
- Mode selector for simulate or optimize
- Run action button
- Reset or clear action

### Status and Monitoring
- Status badge
- Progress bar
- Timestamp row
- Polling indicator
- Error alert

### Results
- Metric cards
- Plot container
- Tabbed output panel
- Raw JSON viewer
- Download button

### Feedback
- Toast notifications
- Inline validation messages
- Loading skeletons
- Empty states
- Confirmation dialogs

## Behavior Guidelines
- Buttons should show loading states when an action is in flight
- Inputs should support validation feedback without layout shift
- Tables and result panels should scale to larger data sets without breaking the page shell
- Components should expose clear states: default, hover, focus, active, disabled, loading, and error

## Implementation Notes
- Prefer composable props over one-off variants when the same structure recurs across views
- Keep circuit-specific logic outside presentational components whenever possible
- Shared result widgets should work for both simulation and optimization outputs
