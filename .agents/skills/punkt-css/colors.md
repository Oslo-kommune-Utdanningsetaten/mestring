# Colors

## Two-tier color system

Punkt uses two levels of color tokens:

1. **Brand colors** — describe what the color _is_ (e.g., `brand-dark-blue-1000`)
2. **Semantic colors** — describe what the color is _used for_ (e.g., `text-body-default`)

**Always prefer semantic colors.** They adapt to dark mode automatically, and their names communicate intent rather than appearance.

## CSS custom properties

All colors are available as CSS custom properties on `:root`:

```css
/* Brand colors */
var(--pkt-color-brand-dark-blue-1000)    /* #2a2859 */
var(--pkt-color-brand-blue-1000)         /* #6fe9ff */
var(--pkt-color-brand-green-1000)        /* #43f8b6 */
var(--pkt-color-brand-red-1000)          /* #ff8274 */

/* Semantic colors */
var(--pkt-color-text-body-default)
var(--pkt-color-background-default)
var(--pkt-color-border-default)
var(--pkt-color-surface-default-light-blue)
```

### Usage in custom CSS

```css
.my-element {
  color: var(--pkt-color-text-body-default);
  background-color: var(--pkt-color-background-subtle);
  border: 1px solid var(--pkt-color-border-default);
}
```

## CSS helper classes

Apply colors directly with utility classes. All use `!important`.

| Prefix                     | Property           |
| -------------------------- | ------------------ |
| `.pkt-color-bg-{name}`     | `background-color` |
| `.pkt-color-txt-{name}`    | `color`            |
| `.pkt-color-border-{name}` | `border-color`     |

The `{name}` matches the CSS custom property name without the `--pkt-color-` prefix.

```html
<div class="pkt-color-bg-surface-default-faded-green">
  <p class="pkt-color-txt-text-body-dark">Dark text on green surface</p>
  <aside class="pkt-color-border-border-green">Green border</aside>
</div>
```

## Semantic color categories

### Naming convention

`{ui-element}-{situation}-{variant/state}`

### Background

Page-level backgrounds.

| Token                    | Use                             |
| ------------------------ | ------------------------------- |
| `background-default`     | Default page background (white) |
| `background-subtle`      | Slightly tinted background      |
| `background-card`        | Card background                 |
| `background-transparent` | Transparent                     |

### Surface

Element-level backgrounds (panels, buttons, sections).

**Default surfaces:**
`surface-default-light-blue`, `surface-default-faded-blue`, `surface-default-green`, `surface-default-faded-green`, `surface-default-light-beige`, `surface-default-yellow`, `surface-default-red`, `surface-default-faded-red`

**Strong surfaces (saturated):**
`surface-strong-dark-blue`, `surface-strong-blue`, `surface-strong-warm-blue`, `surface-strong-green`, `surface-strong-dark-green`, `surface-strong-yellow`, `surface-strong-red`, `surface-strong-beige`, `surface-strong-purple`

**Subtle surfaces:**
`surface-subtle-grey`, `surface-subtle-light-blue`, `surface-subtle-warm-blue`, `surface-subtle-green`

### Border

| Token                                                                                                             | Use                   |
| ----------------------------------------------------------------------------------------------------------------- | --------------------- |
| `border-default`                                                                                                  | Standard border       |
| `border-subtle`                                                                                                   | Subtle/lighter border |
| `border-beige`, `border-blue`, `border-gray`, `border-green`, `border-light-beige`, `border-red`, `border-yellow` | Colored borders       |
| `border-states-active`                                                                                            | Active state          |
| `border-states-disabled`                                                                                          | Disabled state        |
| `border-states-focus`                                                                                             | Focus ring            |
| `border-states-hover`                                                                                             | Hover state           |

### Text

| Token                  | Use                               |
| ---------------------- | --------------------------------- |
| `text-body-default`    | Default body text                 |
| `text-body-dark`       | Dark text (for light backgrounds) |
| `text-body-light`      | Light text (for dark backgrounds) |
| `text-placeholder`     | Placeholder text                  |
| `text-action-normal`   | Link/action default               |
| `text-action-hover`    | Link/action hover                 |
| `text-action-active`   | Link/action active                |
| `text-action-disabled` | Link/action disabled              |

### Input

Used internally by form components:

- `input-background-normal`
- `input-border-normal`, `input-border-hover`, `input-border-active`, `input-border-disabled`, `input-border-error`
- `input-text-normal`, `input-text-hover`, `input-text-active`, `input-text-disabled`, `input-text-error`, `input-text-open`
- `input-check-background`, `input-check-border`, `input-check-text-active`, `input-check-text-hover`

## Brand colors reference

### Blues

| Token                  | Hex     |
| ---------------------- | ------- |
| `brand-blue-100`       | #f1fdff |
| `brand-blue-200`       | #e5fcff |
| `brand-blue-300`       | #d1f9ff |
| `brand-blue-500`       | #b3f5ff |
| `brand-blue-1000`      | #6fe9ff |
| `brand-dark-blue-700`  | #6a698b |
| `brand-dark-blue-1000` | #2a2859 |
| `brand-warm-blue-1000` | #1f42aa |

### Greens

| Token                    | Hex     |
| ------------------------ | ------- |
| `brand-green-400`        | #c7fde9 |
| `brand-green-1000`       | #43f8b6 |
| `brand-light-green-400`  | #e5ffe6 |
| `brand-light-green-1000` | #c7f6c9 |
| `brand-dark-green-1000`  | #034b45 |

### Reds

| Token            | Hex     |
| ---------------- | ------- |
| `brand-red-100`  | #fff2f1 |
| `brand-red-400`  | #ffdfdc |
| `brand-red-600`  | #ffb4ac |
| `brand-red-1000` | #ff8274 |

### Yellows

| Token               | Hex     |
| ------------------- | ------- |
| `brand-yellow-500`  | #ffe7bc |
| `brand-yellow-1000` | #f9c66b |

### Others

| Token                    | Hex     |
| ------------------------ | ------- |
| `brand-light-beige-1000` | #f8f0dd |
| `brand-dark-beige-1000`  | #d0bfae |
| `brand-purple-1000`      | #e0adff |
| `brand-neutrals-white`   | #ffffff |
| `brand-neutrals-100`     | #f9f9f9 |
| `brand-neutrals-200`     | #f2f2f2 |
| `brand-neutrals-1000`    | #2c2c2c |
| `brand-neutrals-black`   | #000000 |

### Grays

`grays-gray-100` (#e6e6e6) through `grays-gray-1000` (#2c2c2c) in 10 steps (100–1000).

## Deprecated color classes

Old-style classes `.bg-{name}` and `.txt-{name}` (without the `pkt-color-` prefix) still exist but are deprecated. Do not use them in new code.

## SCSS usage

> Requires SCSS embedding method.

```scss
@use 'sass:map';
@use '@oslokommune/punkt-css/dist/scss/abstracts/variables';

.my-element {
  background-color: map.get(variables.$pkt-colors, 'brand-red-1000');
  color: map.get(variables.$pkt-colors, 'brand-neutrals-white');
}
```
