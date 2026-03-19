# Getting Started

## Setup Methods

### CDN (recommended for quick start)

Add the stylesheet to your HTML `<head>`. Fonts are served from the CDN automatically.

```html
<link href="https://punkt-cdn.oslo.kommune.no/latest/css/pkt.min.css" rel="stylesheet" />
```

This includes everything: normalise, base styles, element styles, and component styles.

### SCSS (embedded)

For projects with a Sass build step. This gives access to SCSS variables, mixins, and functions.

**Install:**

```sh
npm add @oslokommune/punkt-css @oslokommune/punkt-assets
npm add -D sass
```

**Import in your main SCSS file:**

```scss
/* Override font path to point to the punkt-assets package */
@use '@oslokommune/punkt-css/dist/scss/abstracts/variables' with (
  $font-path: '@oslokommune/punkt-assets/dist'
);

/* Import all Punkt styles */
@use '@oslokommune/punkt-css/dist/scss/pkt';
```

The `$font-path` override is required so the font-face declarations resolve to the correct package.

## What pkt.css includes

The full stylesheet is composed of four layers, loaded in order:

1. **Normalise** — CSS reset (box-sizing, form normalization, reduced motion support)
2. **Base** — Fonts, colors, typography classes, spacing utilities, containers, grid, layouts, visibility, accessibility helpers
3. **Elements** — Styled HTML elements (buttons, inputs, checkboxes, selects, tables, etc.)
4. **Components** — Complex UI components (accordion, alert, header, footer, modal, tabs, etc.)

## Modular CSS

Individual module files exist in the distribution (`pkt-base.min.css`, `pkt-normalise.min.css`, per-component files like `components/alert.min.css`), but modular usage is not yet fully validated. Use `pkt.min.css` for now.

## Using SCSS abstracts

When using the SCSS method, you can import abstracts (variables, mixins, functions) in your own stylesheets without pulling in any CSS output:

```scss
@use '@oslokommune/punkt-css/dist/scss/abstracts/variables';
@use '@oslokommune/punkt-css/dist/scss/abstracts/mixins/breakpoints' as *;
@use '@oslokommune/punkt-css/dist/scss/abstracts/mixins/typography' as *;

.my-component {
  padding: map.get(variables.$spacing, 'size-24');

  @include bp('tablet-up') {
    padding: map.get(variables.$spacing, 'size-32');
  }
}
```

> **Note:** All SCSS features (mixins, variables, functions) require the SCSS embedding method. They are not available when using the CDN.

## Content Security Policy (CSP)

Punkt loads fonts, icons (SVG), and other resources from `https://punkt-cdn.oslo.kommune.no/`. If the application uses a Content Security Policy, the CSP must allow this origin.

**Required CSP directives:**

```
Content-Security-Policy:
  default-src 'self';
  font-src 'self' https://punkt-cdn.oslo.kommune.no/;
  img-src 'self' https://punkt-cdn.oslo.kommune.no/;
  script-src 'self' https://punkt-cdn.oslo.kommune.no/;
  style-src 'self' 'unsafe-inline' https://punkt-cdn.oslo.kommune.no/;
  connect-src 'self' https://punkt-cdn.oslo.kommune.no/;
```

**Why `'unsafe-inline'` in `style-src`?** Because of the intricacies of SVG styling and certain web component features, Punkt requires `'unsafe-inline'` in the `style-src` directive. Without it, some styles will be blocked by the browser. CSP nonces can be used as an alternative but require server-side configuration.

| Directive | Covers |
|---|---|
| `font-src` | Fonts (`.woff`, `.woff2`) |
| `img-src` | Images and SVG icons |
| `script-src` | JavaScript files (Elements components from CDN) |
| `style-src` | CSS stylesheets and inline styles |
| `connect-src` | Fetch/XHR requests (e.g. dynamic SVG icon loading) |

> **Important:** Always instruct users to configure CSP when setting up Punkt in a project. Missing CSP configuration is a common cause of broken fonts, missing icons, and invisible components.
