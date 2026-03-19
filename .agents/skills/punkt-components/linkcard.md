# Link Card

Link Card is a simple card-style link with a title, optional description, icon, and background color. The entire card is clickable and navigates to the specified URL. Use it for navigation-focused cards where the whole surface is one link.

## Availability

| Package        | Available | Tag / Import                                                                                     |
| -------------- | --------- | ------------------------------------------------------------------------------------------------ |
| React          | Yes       | `<PktLinkCard>` — `import { PktLinkCard } from '@oslokommune/punkt-react'`                       |
| Elements       | Yes       | `<pkt-linkcard>` — `import '@oslokommune/punkt-elements/dist/pkt-linkcard.js'`                   |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-linkcard.js" type="module">` |

Dark mode: Yes

## Variants

### Skins

| Skin            | Description       |
| --------------- | ----------------- |
| `normal`        | Default style     |
| `no-padding`    | No inner padding  |
| `blue`          | Blue background   |
| `beige`         | Beige background  |
| `green`         | Green background  |
| `gray`          | Gray background   |
| `beige-outline` | Beige with border |
| `gray-outline`  | Gray with border  |

## Usage guidelines

**Use link card when:**

- You need a navigation card where the entire surface is a single link
- You want a card without complex content — just title, description, and an icon

**Avoid link card when:**

- You need more flexible content (images, tags, actions) — use Card instead
- The card should contain multiple interactive elements

## Props / Attributes

| Prop (React)   | Attribute (Elements) | Type               | Default | Description                |
| -------------- | -------------------- | ------------------ | ------- | -------------------------- |
| `title`        | `title`              | string             | —       | Card title                 |
| `href`         | `href`               | string             | —       | URL the card links to      |
| `skin`         | `skin`               | See skins table    | —       | Visual style               |
| `iconName`     | `iconName`           | string (icon name) | —       | Icon displayed on the card |
| `openInNewTab` | `openInNewTab`       | boolean            | `false` | Open link in a new tab     |
| `external`     | `external`           | boolean            | `false` | Marks the link as external |

## Slots

| Slot    | Description                   |
| ------- | ----------------------------- |
| default | Description text for the card |

## Examples

### React

```jsx
import { PktLinkCard } from '@oslokommune/punkt-react'

<PktLinkCard
  title="Getting started"
  href="/docs/getting-started"
  skin="blue"
  iconName="chevron-right"
>
  Learn how to set up Punkt in your project.
</PktLinkCard>

<PktLinkCard
  title="GitHub"
  href="https://github.com/oslokommune/punkt"
  skin="beige"
  iconName="external-link"
  external
  openInNewTab
>
  View the source code on GitHub.
</PktLinkCard>
```

### Elements

```html
<pkt-linkcard
  title="Getting started"
  href="/docs/getting-started"
  skin="blue"
  iconName="chevron-right"
>
  <p>Learn how to set up Punkt in your project.</p>
</pkt-linkcard>
```
