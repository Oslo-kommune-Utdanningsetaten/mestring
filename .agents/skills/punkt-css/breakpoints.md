# Breakpoints

## Breakpoint scale

| Name         | Min-width | Pixels  |
| ------------ | --------- | ------- |
| `mobile`     | 0         | 0       |
| `phablet`    | 36rem     | ~576px  |
| `tablet`     | 48rem     | ~768px  |
| `tablet-big` | 64rem     | ~1024px |
| `laptop`     | 80rem     | ~1280px |
| `desktop`    | 100rem    | ~1600px |

## Usage in CSS classes

Breakpoints are used via the `--{breakpoint}-up` suffix on utility classes. This applies the style at the named breakpoint **and above** (min-width).

### Which classes support responsive suffixes

| Class type      | Example                                      |
| --------------- | -------------------------------------------- |
| Typography      | `.pkt-txt-36--tablet-up`                     |
| Spacing         | `.mb-size-24--laptop-up`                     |
| Grid cell spans | `.pkt-cell--span6-tablet-up`                 |
| Grid gaps       | `.pkt-grid--gap-size-32-tablet-up`           |
| Visibility      | `.pkt-hide-tablet-up`, `.pkt-show-laptop-up` |

### Mobile-first pattern

Set the base (mobile) style without a suffix, then override at larger breakpoints:

```html
<!-- Text: 36px mobile, 54px from tablet up -->
<h1 class="pkt-txt-36 pkt-txt-54--tablet-up">Heading</h1>

<!-- Margin: 16px mobile, 32px from tablet, 64px from laptop -->
<div class="mb-size-16 mb-size-32--tablet-up mb-size-64--laptop-up">...</div>

<!-- Grid: full-width mobile, 2 columns from tablet -->
<div class="pkt-cell pkt-cell--span12 pkt-cell--span6-tablet-up">...</div>
```

## Custom breakpoints in CSS

There is no CSS-only mechanism for custom breakpoints. The `--{breakpoint}-up` suffixes use the fixed scale above. For custom breakpoints in plain CSS, write your own media queries:

```css
@media (min-width: 48rem) {
  .my-element {
    /* tablet and up */
  }
}
```

## SCSS breakpoint mixin

> Requires SCSS embedding method.

```scss
@use '@oslokommune/punkt-css/dist/scss/abstracts/mixins/breakpoints' as *;
```

### Min-width queries (most common)

```scss
@include bp('phablet-up') {
  /* 576px+ */
}
@include bp('tablet-up') {
  /* 768px+ */
}
@include bp('tablet-big-up') {
  /* 1024px+ */
}
@include bp('laptop-up') {
  /* 1280px+ */
}
@include bp('desktop-up') {
  /* 1600px+ */
}
```

### Exact range queries

```scss
@include bp('mobile') {
  /* 0 – 575px */
}
@include bp('phablet') {
  /* 576 – 767px */
}
@include bp('tablet') {
  /* 768 – 1023px */
}
@include bp('tablet-big') {
  /* 1024 – 1279px */
}
@include bp('laptop') {
  /* 1280 – 1599px */
}
```

### Range queries

```scss
@include bp("mobile-to-phablet") { ... }
@include bp("mobile-to-tablet") { ... }
@include bp("mobile-to-laptop") { ... }
@include bp("phablet-to-tablet-big") { ... }
@include bp("tablet-to-tablet-big") { ... }
@include bp("tablet-to-laptop") { ... }
@include bp("tablet-big-to-laptop") { ... }
```

### Custom value

Pass any rem value for a custom min-width query:

```scss
@include bp(50rem) {
  /* 800px+ */
}
```

### Example

```scss
.my-component {
  padding: 1rem;

  @include bp('tablet-up') {
    padding: 2rem;
  }

  @include bp('laptop-up') {
    padding: 3rem;
    max-width: 60rem;
  }
}
```

## SCSS container query mixin

> Requires SCSS embedding method.

For container queries with a media query fallback:

```scss
@use '@oslokommune/punkt-css/dist/scss/abstracts/mixins/container-queries' as *;

.parent {
  container-type: inline-size;
  container-name: my-container;
}

.child {
  @include cq('my-container', 48rem) {
    /* Styles when container is >= 768px wide */
  }
}
```
