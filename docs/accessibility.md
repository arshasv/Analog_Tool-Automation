# Accessibility

## Goal
xEDA should be usable by keyboard-only users, screen reader users, and users working in low-light or high-glare environments.

## Baseline Requirements
- All interactive elements must be reachable by keyboard
- Focus states must be visible and consistent
- Color alone must not communicate critical status
- Form fields must have explicit labels and helper text where needed
- Errors must be understandable without relying on visual styling alone

## Contrast and Readability
- Maintain sufficient contrast for text, icons, borders, and status indicators
- Prefer large enough type for technical content and dense data tables
- Avoid conveying important information only through low-contrast color chips

## Keyboard Behavior
- Tab order must follow the visual and logical order of the page
- Modal dialogs must trap focus while open
- Escape should dismiss overlays when appropriate
- Buttons, tabs, and menus should have predictable activation behavior

## Forms and Parameters
- Every input needs a clear label
- Defaults should be visible and editable
- Validation messages should appear near the field that needs attention
- Technical fields should preserve units and expected value ranges when relevant

## Status and Feedback
- Job states such as running, completed, and failed should be announced clearly
- Progress indicators should include text, not only visual bars
- Download and run actions should provide clear confirmation or failure states

## Testing Checklist
- Keyboard navigation works across the full dashboard
- Focus order remains stable after modal open/close
- Text remains legible at common browser zoom levels
- Critical statuses remain understandable in grayscale
