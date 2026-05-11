# Navigation

## Purpose
Navigation should help users move quickly between circuit setup, execution, and results without losing context.

## Primary Information Architecture
- Home or overview
- Circuit submission and configuration
- Job monitoring and status
- Results and analysis views
- Documentation or help when available

## Navigation Rules
- The current location must always be obvious
- Users should be able to return to an in-progress job from anywhere in the app
- Navigation labels should use domain language that matches xEDA workflows
- Deep views should preserve a clear route back to the parent screen

## Recommended Patterns
- Top-level navigation for major areas
- Secondary tabs for switching between status, metrics, plots, and raw output
- Breadcrumbs or back affordances for deep result views
- Persistent access to submission and job history when possible

## State Awareness
- If a job is running, provide a direct path back to its status panel
- If the current circuit has unsaved parameter edits, warn before navigation away
- If data is unavailable, route users to a helpful empty or error state rather than a dead end
