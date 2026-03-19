# Helper Classes

## Text alignment

| Class             | Effect               |
| ----------------- | -------------------- |
| `.pkt-txt-start`  | `text-align: left`   |
| `.pkt-txt-center` | `text-align: center` |
| `.pkt-txt-end`    | `text-align: right`  |

```html
<p class="pkt-txt-center">Centered text</p>
```

## Text truncation

`.pkt-truncate-text` — truncates overflowing text with an ellipsis.

```html
<div class="pkt-truncate-text">
  This very long text will be cut off with an ellipsis when it overflows...
</div>
```

Requires `display: block` or `display: inline-block` on the element (block is the default for `<div>` and `<p>`).

## Display contents

`.pkt-display-contents` and `.pkt-contents` — sets `display: contents`, which makes the element's children behave as if they were direct children of the element's parent. Useful for wrapper elements that shouldn't affect layout.

```html
<div class="pkt-grid">
  <div class="pkt-contents">
    <!-- These cells act as direct children of .pkt-grid -->
    <div class="pkt-cell pkt-cell--span6">Cell 1</div>
    <div class="pkt-cell pkt-cell--span6">Cell 2</div>
  </div>
</div>
```

## Link styles

### Base link: `.pkt-link`

Styled inline link with underline and action color states (normal, hover, focus, active, visited).

```html
<a href="/about" class="pkt-link">About us</a>
```

### Link with icon

| Modifier                | Effect                                   |
| ----------------------- | ---------------------------------------- |
| `.pkt-link--icon-left`  | Icon positioned to the left of the text  |
| `.pkt-link--icon-right` | Icon positioned to the right of the text |

```html
<a href="/back" class="pkt-link pkt-link--icon-left">
  <pkt-icon name="chevron-thin-left"></pkt-icon>
  Go back
</a>
```

### Button as link

Apply `.pkt-link` to a `<button>` element to style it as a text link:

```html
<button class="pkt-link" onclick="...">Click me</button>
```

## Container

`.pkt-container` is covered in detail in [Grid System](grid-system.md). Brief reference:

```html
<div class="pkt-container">Centered, padded content (max 80rem)</div>
<div class="pkt-container pkt-container--tablet">Narrow content (max 48rem)</div>
<div class="pkt-container pkt-container--full">Full width</div>
```

## Layout

`.pkt-layout` is covered in detail in [Typography & Layout](typography-and-layout.md#layout). Brief reference:

```html
<div class="pkt-layout">
  <header>...</header>
  <main>...</main>
  <footer>...</footer>
</div>
```
