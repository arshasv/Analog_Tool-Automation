# Layout

## Purpose
This document defines the spatial structure of xEDA screens so the application feels consistent, readable, and efficient.

## Layout Principles
- Present the most important job state first
- Group controls close to the data they affect
- Preserve enough horizontal space for technical readouts and plots
- Avoid wasting space with overly decorative chrome

## Recommended Page Structure

### Desktop
- Global header at the top
- Primary navigation on the left or in a compact top row
- Main work area in a flexible content column
- Supporting panels for status, parameters, and results

### Tablet
- Collapse navigation when needed
- Stack panels vertically in a meaningful order
- Keep action controls visible without excessive scrolling

### Mobile
- Prioritize submission, status, and the latest result summary
- Collapse detailed views into tabs or accordions
- Keep controls large enough for touch interaction

## Section Order
1. Page title and context
2. Current status or summary
3. Primary action area
4. Detailed configuration or analysis panels
5. Output and results

## Content Density
- Technical interfaces may be dense, but hierarchy must remain obvious
- Use spacing, borders, and headings to separate logical groups
- Dense tables should remain readable at common viewport sizes

## Grid and Containers
- Use a predictable max width for general screens
- Allow specialized analysis views to expand wider when plots or tables need room
- Keep card widths and vertical spacing aligned across the application
