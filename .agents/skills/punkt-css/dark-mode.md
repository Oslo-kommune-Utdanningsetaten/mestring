# Dark Mode

## Activation

Dark mode is activated by setting `data-mode="dark"` on any HTML element. Everything within that element receives dark mode colors.

```html
<!-- Global dark mode -->
<body data-mode="dark">
  ...
</body>

<!-- Scoped dark mode on a section -->
<section data-mode="dark" class="p-size-32">
  <h2>This section is in dark mode</h2>
  <p>Text and backgrounds adapt automatically.</p>
</section>
```

## How it works

Under `[data-mode="dark"]`, all **semantic color** CSS custom properties are overridden with dark-appropriate values. For example:

- `--pkt-color-background-default` changes from white to a dark color
- `--pkt-color-text-body-default` changes from dark blue to a light color
- `--pkt-color-border-default` adjusts for dark backgrounds

This means any element using semantic color variables or semantic color helper classes automatically adapts to dark mode without any additional CSS.

## What changes and what doesn't

|                                                                        | Dark mode behavior       |
| ---------------------------------------------------------------------- | ------------------------ |
| **Semantic colors**                                                    | Automatically overridden |
| **Brand colors**                                                       | Do NOT change            |
| **Semantic helper classes** (`.pkt-color-bg-background-default`, etc.) | Adapt automatically      |
| **Brand helper classes** (`.pkt-color-bg-brand-blue-1000`, etc.)       | Stay the same            |

This is the main reason to **prefer semantic colors over brand colors**: semantic colors respond to dark mode, brand colors do not.

## Usage with semantic colors

```html
<div data-mode="dark" class="pkt-color-bg-background-default p-size-32">
  <p class="pkt-color-txt-text-body-default">This text automatically uses light-on-dark colors.</p>
  <div class="pkt-color-bg-surface-subtle-grey p-size-16">Surface colors also adapt.</div>
</div>
```

## Custom CSS with dark mode

When writing custom CSS, use semantic color variables to get automatic dark mode support:

```css
.my-card {
  background-color: var(--pkt-color-background-card);
  color: var(--pkt-color-text-body-default);
  border: 1px solid var(--pkt-color-border-default);
}
```

This card will look correct in both light and dark mode without any additional rules.

If you need to target dark mode explicitly in custom CSS:

```css
[data-mode='dark'] .my-element {
  /* dark-mode-specific overrides */
}
```

## Toggling dark mode with JavaScript

```javascript
// Enable dark mode
document.body.setAttribute('data-mode', 'dark')

// Disable dark mode
document.body.removeAttribute('data-mode')

// Toggle
const isDark = document.body.getAttribute('data-mode') === 'dark'
document.body.setAttribute('data-mode', isDark ? '' : 'dark')

// Scope to a section
document.getElementById('sidebar').setAttribute('data-mode', 'dark')
```
