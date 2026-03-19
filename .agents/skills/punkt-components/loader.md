# Loader

Loader displays a loading animation while content is being fetched or processed. It can wrap content (showing the loader until loading is complete) or be displayed standalone.

## Availability

| Package        | Available | Tag / Import                                                                                   |
| -------------- | --------- | ---------------------------------------------------------------------------------------------- |
| React          | Yes       | `<PktLoader>` — `import { PktLoader } from '@oslokommune/punkt-react'`                         |
| Elements       | Yes       | `<pkt-loader>` — `import '@oslokommune/punkt-elements/dist/pkt-loader.js'`                     |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-loader.js" type="module">` |

Dark mode: Yes

## Variants

### Sizes

| Size               | Use                          |
| ------------------ | ---------------------------- |
| `small`            | Inline or tight spaces       |
| `medium` (default) | Standard use                 |
| `large`            | Full-page or section loading |

### Color variants

| Variant             | Description                |
| ------------------- | -------------------------- |
| `rainbow` (default) | Multi-color animation      |
| `blue`              | Blue monochrome animation  |
| `shapes`            | Geometric shapes animation |

## Props / Attributes

| Prop (React) | Attribute (Elements) | Type                                  | Default     | Description                                     |
| ------------ | -------------------- | ------------------------------------- | ----------- | ----------------------------------------------- |
| `message`    | `message`            | string                                | —           | Text displayed below the loader                 |
| `size`       | `size`               | `"small"` \| `"medium"` \| `"large"`  | `"medium"`  | Loader size                                     |
| `variant`    | `variant`            | `"rainbow"` \| `"blue"` \| `"shapes"` | `"rainbow"` | Color variant                                   |
| `delay`      | `delay`              | number                                | `0`         | Delay in milliseconds before the loader appears |
| `inline`     | `inline`             | boolean                               | `false`     | Display inline with page content                |
| `isLoading`  | `isLoading`          | boolean                               | `true`      | Whether the loader is active                    |

## Slots

| Slot    | Description                            |
| ------- | -------------------------------------- |
| default | Content shown when loading is complete |

## Examples

### React

```jsx
import { PktLoader } from '@oslokommune/punkt-react'

{
  /* Standalone loader */
}
;<PktLoader message="Loading data..." />

{
  /* Wrapping content */
}
;<PktLoader isLoading={isLoading} message="Loading...">
  <div>Content shown after loading</div>
</PktLoader>

{
  /* Small inline loader */
}
;<PktLoader size="small" variant="blue" inline />

{
  /* With delay to avoid flash for fast loads */
}
;<PktLoader isLoading={isLoading} delay={300} message="Loading..." />
```

### Elements

```html
<pkt-loader message="Loading data..."></pkt-loader>

<pkt-loader size="small" variant="blue" inline></pkt-loader>

<pkt-loader message="Loading...">
  <div>Content shown after loading</div>
</pkt-loader>
```
