# Visibility & Accessibility

## Visibility classes

### Base classes

| Class       | Effect           |
| ----------- | ---------------- |
| `.pkt-hide` | `display: none`  |
| `.pkt-show` | `display: block` |

### Responsive visibility

| Class                       | Effect                       |
| --------------------------- | ---------------------------- |
| `.pkt-hide-{breakpoint}-up` | Hide at breakpoint and above |
| `.pkt-show-{breakpoint}-up` | Show at breakpoint and above |

Available breakpoints: `mobile`, `phablet`, `tablet`, `tablet-big`, `laptop`, `desktop`.

### Common patterns

**Show only on mobile (hide from tablet up):**

```html
<p class="pkt-hide-tablet-up">Visible only on mobile and phablet</p>
```

**Hide on mobile, show from tablet up:**

```html
<p class="pkt-hide pkt-show-tablet-up">Hidden on mobile, visible from tablet</p>
```

**Show only on tablet range:**

```html
<p class="pkt-hide pkt-show-tablet-up pkt-hide-laptop-up">Visible only on tablet and tablet-big</p>
```

**Swap content between mobile and desktop:**

```html
<img class="pkt-hide-tablet-up" src="mobile-hero.jpg" alt="Hero" />
<img class="pkt-hide pkt-show-tablet-up" src="desktop-hero.jpg" alt="Hero" />
```

---

## Screen reader only: `.pkt-sr-only`

Hides content visually while keeping it accessible to screen readers and other assistive technology.

```html
<h2 class="pkt-sr-only">Navigation</h2>
<nav>
  <a href="/">Home</a>
  <a href="/about">About</a>
</nav>
```

### How it works

The class uses clipping, absolute positioning, and 1px dimensions to remove the element from visual flow without removing it from the accessibility tree:

- `clip-path: inset(50%)`
- `width: 1px; height: 1px`
- `position: absolute`
- `overflow: hidden`

### When to use

- **Skip links** — "Skip to main content" links
- **Form labels** — when the label is visually redundant but needed for accessibility
- **Section headings** — to give screen reader users context for navigation landmarks
- **Descriptive text** — additional context that sighted users can infer from visual layout

### Example: skip link

```html
<a href="#main-content" class="pkt-sr-only">Skip to main content</a>
<pkt-header>...</pkt-header>
<main id="main-content">...</main>
```
