# 03 Tokens

## Purpose
Design tokens define the visual system for xEDA. They provide a shared foundation for colors, typography, spacing, radius, elevation, and motion so the UI stays consistent across pages and components.

## Token Categories

### Color
- `background` for page shells
- `surface` for cards, panels, and modals
- `border` for separators and input outlines
- `text-primary` and `text-secondary` for hierarchy
- `accent` for actions, links, and selected states
- `success`, `warning`, `danger`, and `info` for status feedback

### Typography
- Use one display face and one UI face, or a single highly readable family if the system remains consistent
- Define scales for page titles, section headings, labels, body text, helper text, and monospace technical data

### Spacing
- Use a small, predictable spacing scale for layouts and component internals
- Prefer tokenized spacing values over ad hoc pixel values

### Radius
- Use a limited radius scale for cards, inputs, buttons, and chips
- Keep the look crisp and technical rather than overly soft

### Elevation
- Use subtle shadows or layered borders to separate panels
- Reserve stronger elevation for overlays and floating surfaces

### Motion
- Define tokenized durations and easing curves
- Keep motion purposeful: transitions should clarify change, not decorate it

## Recommended CSS Variable Groups
- Color primitives
- Semantic colors
- Typography scale
- Spacing scale
- Radius scale
- Shadow tokens
- Animation durations

## Usage Rules
- Components should reference semantic tokens, not raw color values
- Theme switching should re-map token values instead of changing component logic
- Experimental visuals should still resolve to the same semantic palette
