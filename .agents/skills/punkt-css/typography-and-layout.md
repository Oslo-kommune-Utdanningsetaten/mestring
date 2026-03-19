# Typography & Layout

## Body defaults

Punkt sets these defaults on `<body>`:

- **Font:** Oslo Sans, arial, sans-serif
- **Size:** 16px (1rem)
- **Weight:** light (300)
- **Line height:** 1.75rem (28px)
- **Color:** `var(--pkt-color-text-body-default)`

All heading elements (h1–h6) are **reset to body text size and weight** by the normalise layer. You must apply typography classes explicitly.

## Typography classes

### Format

`.pkt-txt-{size}` — regular weight at the given size
`.pkt-txt-{size}-{weight}` — specific weight at the given size

### Available sizes

12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 36, 40, 48, 54, 70

### Weight variants

| Suffix    | Weight        |
| --------- | ------------- |
| _(none)_  | regular (400) |
| `-light`  | light (300)   |
| `-medium` | medium (500)  |
| `-bold`   | bold (700)    |

### Examples

```html
<p class="pkt-txt-16-light">Body text</p>
<h2 class="pkt-txt-36">Section heading</h2>
<span class="pkt-txt-14-medium">Small label</span>
```

### Font weight utilities

Apply a weight without changing size:

- `.pkt-font-light` (300)
- `.pkt-font-regular` (400)
- `.pkt-font-medium` (500)
- `.pkt-font-bold` (700)

## Responsive typography

Add `--{breakpoint}-up` to apply a typography class at a specific breakpoint and above:

```html
<!-- 36px on mobile, 54px from tablet up -->
<h1 class="pkt-txt-36 pkt-txt-54--tablet-up">Page Title</h1>
```

Available breakpoints: `mobile`, `phablet`, `tablet`, `tablet-big`, `laptop`, `desktop` (see [Breakpoints](breakpoints.md)).

## Recommended heading sizes

| Level   | Mobile               | Desktop (tablet-up)             |
| ------- | -------------------- | ------------------------------- |
| h1      | `.pkt-txt-36`        | `.pkt-txt-54--tablet-up`        |
| h2      | `.pkt-txt-26`        | `.pkt-txt-36--tablet-up`        |
| h3      | `.pkt-txt-22`        | `.pkt-txt-30--tablet-up`        |
| h4      | `.pkt-txt-18-medium` | `.pkt-txt-24-medium--tablet-up` |
| h5      | `.pkt-txt-22-medium` | _(same)_                        |
| Ingress | `.pkt-txt-20-light`  | `.pkt-txt-24-light--tablet-up`  |
| Body    | `.pkt-txt-16-light`  | _(same)_                        |

### Example responsive heading

```html
<h1 class="pkt-txt-36 pkt-txt-54--tablet-up">Page Title</h1>
<h2 class="pkt-txt-26 pkt-txt-36--tablet-up">Section Title</h2>
<p class="pkt-txt-20-light pkt-txt-24-light--tablet-up">Ingress paragraph.</p>
<p class="pkt-txt-16-light">Body text stays the same across breakpoints.</p>
```

## Text alignment

- `.pkt-txt-start` — left-aligned
- `.pkt-txt-center` — centered
- `.pkt-txt-end` — right-aligned

## Links

- `.pkt-link` — styled inline link with underline and action colors
- `.pkt-link--icon-left` — link with icon on the left
- `.pkt-link--icon-right` — link with icon on the right
- `button.pkt-link` — button element styled as a link

## Text truncation

```html
<div class="pkt-truncate-text">This long text will be truncated with an ellipsis...</div>
```

Requires `display: block` or `display: inline-block` on the element.

## SCSS typography mixin

> Requires SCSS embedding method.

```scss
@use '@oslokommune/punkt-css/dist/scss/abstracts/mixins/typography' as *;
@use '@oslokommune/punkt-css/dist/scss/abstracts/mixins/breakpoints' as *;

.page-header {
  @include get-text('pkt-txt-36');

  @include bp('tablet-up') {
    @include get-text('pkt-txt-54');
  }
}
```

---

## Layout

### Page shell: `.pkt-layout`

The page shell class provides a header/content/footer structure with the footer always at the bottom of the viewport.

```html
<div class="pkt-layout">
  <header>...</header>
  <main>...</main>
  <footer>...</footer>
</div>
```

The three direct children map to grid rows: header (auto height), main (stretches to fill), footer (auto height, always at bottom).

Headers and footers (e.g., `<pkt-header>`, `<pkt-footer>`) are self-contained — they handle their own full-width backgrounds and padding. Never wrap them in a container.

### Layout patterns

Use `.pkt-container` and `.pkt-grid` inside `<main>` to control content width and columns.

#### Basic page

Content constrained to laptop width (80rem) by default:

```html
<div class="pkt-layout">
  <pkt-header>...</pkt-header>
  <main class="pkt-container">
    <h1 class="pkt-txt-36 pkt-txt-54--tablet-up">Page Title</h1>
    <p class="pkt-txt-16-light">Content goes here.</p>
  </main>
  <pkt-footer>...</pkt-footer>
</div>
```

#### Narrow article

Use a narrower container for readable article content:

```html
<div class="pkt-layout">
  <pkt-header>...</pkt-header>
  <main class="pkt-container pkt-container--tablet">
    <article>
      <h1 class="pkt-txt-36 pkt-txt-54--tablet-up">Article Title</h1>
      <p class="pkt-txt-20-light">Ingress paragraph...</p>
      <p class="pkt-txt-16-light">Body text...</p>
    </article>
  </main>
  <pkt-footer>...</pkt-footer>
</div>
```

#### Sidebar layout

Use `.pkt-grid` inside the container. Stacks vertically on mobile, side-by-side from laptop up:

```html
<div class="pkt-layout">
  <pkt-header>...</pkt-header>
  <main class="pkt-container">
    <div class="pkt-grid">
      <nav class="pkt-cell pkt-cell--span12 pkt-cell--span3-laptop-up">Side navigation</nav>
      <article class="pkt-cell pkt-cell--span12 pkt-cell--span9-laptop-up">Main content</article>
    </div>
  </main>
  <pkt-footer>...</pkt-footer>
</div>
```

#### Landing page with full-width sections

For alternating background colors, leave `<main>` unconstrained and place a `.pkt-container` inside each section:

```html
<div class="pkt-layout">
  <pkt-header>...</pkt-header>
  <main>
    <section class="pkt-color-bg-surface-subtle-grey py-size-64">
      <div class="pkt-container">
        <h2>Hero Section</h2>
      </div>
    </section>
    <section class="py-size-64">
      <div class="pkt-container">
        <div class="pkt-grid">
          <div class="pkt-cell pkt-cell--span12 pkt-cell--span4-tablet-up">Card 1</div>
          <div class="pkt-cell pkt-cell--span12 pkt-cell--span4-tablet-up">Card 2</div>
          <div class="pkt-cell pkt-cell--span12 pkt-cell--span4-tablet-up">Card 3</div>
        </div>
      </div>
    </section>
  </main>
  <pkt-footer>...</pkt-footer>
</div>
```

#### Dashboard / web app

Full-width container with a grid for sidebar navigation and content area:

```html
<div class="pkt-layout">
  <pkt-header>...</pkt-header>
  <main class="pkt-container pkt-container--full">
    <div class="pkt-grid pkt-grid--full pkt-grid--gap-size-0">
      <aside class="pkt-cell pkt-cell--span2-tablet-up pkt-color-bg-surface-subtle-grey">
        App navigation
      </aside>
      <div class="pkt-cell pkt-cell--span10-tablet-up p-size-24 p-size-32--laptop-up">
        Dashboard content
      </div>
    </div>
  </main>
  <pkt-footer>...</pkt-footer>
</div>
```

### Accessibility note

- Use light font weight carefully — it can be too thin for readability
- Text/background contrast must meet WCAG 4.5:1 ratio
- Headings must be in correct semantic order (h1, h2, h3, etc.)
