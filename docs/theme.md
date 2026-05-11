# Theme

## Purpose
Theme defines the visual character of xEDA. The system should feel precise, engineered, and trustworthy while remaining usable for long technical sessions.

## Theme Direction
- Use a restrained, professional palette
- Favor contrast, clarity, and structure over decoration
- Make active states and critical statuses easy to distinguish

## Visual Identity
- Dark-mode support is strongly recommended for prolonged engineering work
- Surfaces should be layered with subtle separation
- Emphasis color should be used sparingly for actions and important state changes

## Theme Tokens
- Background and surface layers
- Text hierarchy
- Accent and interaction colors
- Semantic status colors
- Border and divider colors
- Shadow and elevation treatments

## Implementation Approach
- Store theme values as CSS variables
- Keep component styling semantic, not hard-coded to a single theme
- Ensure charts, tables, and code-like content adapt cleanly to the active theme

## Theming Rules
- Do not let theme changes alter layout behavior
- Preserve readability in both light and dark contexts
- Ensure status colors still work when viewed with limited color perception
