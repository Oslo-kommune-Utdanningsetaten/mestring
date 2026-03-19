# Card

Card groups related content together and can contain text, images, icons, buttons, links, or a combination of these. Cards make it easier to scan, compare, and choose between multiple items.

## Availability

| Package        | Available | Tag / Import                                                                                 |
| -------------- | --------- | -------------------------------------------------------------------------------------------- |
| React          | Yes       | `<PktCard>` — `import { PktCard } from '@oslokommune/punkt-react'`                           |
| Elements       | Yes       | `<pkt-card>` — `import '@oslokommune/punkt-elements/dist/pkt-card.js'`                       |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-card.js" type="module">` |

Dark mode: Yes

## Variants

### Layouts

| Layout       | Use                                                                      |
| ------------ | ------------------------------------------------------------------------ |
| `vertical`   | Content stacked vertically — works well with multiple cards side by side |
| `horizontal` | When you want to use more of the width, e.g. in desktop view             |

Landscape cards automatically scale down to portrait on small screens.

### Skins

| Skin             | Use                                 |
| ---------------- | ----------------------------------- |
| `outlined`       | Border without background (default) |
| `outlined-beige` | Border with beige tint              |
| `gray`           | Gray filled background              |
| `blue`           | Blue filled background              |
| `beige`          | Beige filled background             |
| `green`          | Green filled background             |

### Image shapes

| Shape    | Use                                        |
| -------- | ------------------------------------------ |
| `square` | Tighter expression (default)               |
| `round`  | More playful, harmonizes with Oslo profile |

## Usage guidelines

**Use card when:**

- You want to group information
- You need clear choices in a grid or list layout
- You want flexible display with or without image, content, or action

**Avoid card when:**

- You're showing just one thing and don't need visual grouping
- The information is better suited for plain text or a table

**Content guidelines:**

- Keep content clean, clear, and concrete — avoid overloading the card
- Use consistent elements across cards in the same view
- Use short titles and clear actions
- If the card is clickable, make it clear where it leads

**Interactive vs non-interactive cards:**

- A card can either be fully clickable (the whole card is a link) or contain clickable elements inside it (buttons, links)
- Do not mix these — don't put buttons inside a clickable card. One action per area.

## Props / Attributes

| Prop (React)       | Attribute (Elements) | Type                                                                                 | Default      | Description                                                         |
| ------------------ | -------------------- | ------------------------------------------------------------------------------------ | ------------ | ------------------------------------------------------------------- |
| `heading`          | `heading`            | string                                                                               | —            | Card title                                                          |
| `headingLevel`     | `headingLevel`       | `1` \| `2` \| `3` \| `4` \| `5` \| `6`                                               | `3`          | HTML heading level for the title                                    |
| `subheading`       | `subheading`         | string                                                                               | —            | Subtitle displayed below the heading                                |
| `layout`           | `layout`             | `"vertical"` \| `"horizontal"`                                                       | `"vertical"` | Portrait or landscape layout                                        |
| `skin`             | `skin`               | `"outlined"` \| `"outlined-beige"` \| `"gray"` \| `"blue"` \| `"beige"` \| `"green"` | `"outlined"` | Visual style and color                                              |
| `padding`          | `padding`            | `"none"` \| `"default"`                                                              | `"default"`  | Inner padding                                                       |
| `metaLead`         | `metaLead`           | string                                                                               | —            | Bold metadata text (e.g. author)                                    |
| `metaTrail`        | `metaTrail`          | string                                                                               | —            | Normal-weight metadata text (e.g. date)                             |
| `tagPosition`      | `tagPosition`        | `"top"` \| `"bottom"`                                                                | `"top"`      | Position of tags in the card                                        |
| `clickCardlink`    | `clickCardlink`      | string                                                                               | —            | URL to make the entire card clickable. Heading is used as link text |
| `openLinkInNewTab` | `openLinkInNewTab`   | boolean                                                                              | `false`      | Open the card link in a new tab                                     |
| `borderOnHover`    | `borderOnHover`      | boolean                                                                              | `true`       | Show border on hover for clickable cards                            |
| `image`            | `image`              | `{ src: string, alt?: string }`                                                      | —            | Card image. Only set `alt` for non-decorative images                |
| `imageShape`       | `imageShape`         | `"square"` \| `"round"`                                                              | `"square"`   | Shape of the card image                                             |
| `tags`             | `tags`               | `Array<{ text: string, skin?: string, iconName?: string, ariaLabel?: string }>`      | —            | List of tags displayed on the card                                  |
| `ariaLabel`        | `ariaLabel`          | string                                                                               | —            | Screen reader label. Defaults to heading or subheading              |

## Slots

| Slot    | Description         |
| ------- | ------------------- |
| default | Content of the card |

## Accessibility

- Use the correct `headingLevel` for the context where the card is displayed — all cards at the same level should use the same heading level
- Interactive cards: the whole card is a tab stop, activated with Enter or Space
- Non-interactive cards: only buttons and links inside are focusable
- All focusable elements have a visible focus indicator
- Write clear link text that screen readers understand
- Only set `image.alt` for images that convey meaning — decorative images should omit it

## Examples

### React

```jsx
import { PktCard } from '@oslokommune/punkt-react'

{
  /* Basic card */
}
;<PktCard heading="My service" subheading="A brief description">
  <p>Card content goes here.</p>
</PktCard>

{
  /* Clickable card with image */
}
;<PktCard
  heading="Service name"
  clickCardlink="/services/detail"
  image={{ src: '/images/service.jpg', alt: 'Service illustration' }}
  skin="blue"
  tags={[{ text: 'New', skin: 'green' }]}
/>

{
  /* Horizontal layout */
}
;<PktCard
  heading="Article title"
  layout="horizontal"
  metaLead="Author name"
  metaTrail="2024-01-15"
  image={{ src: '/images/article.jpg' }}
>
  <p>Article summary text.</p>
</PktCard>
```

### Elements

```html
<pkt-card heading="My service" subheading="A brief description">
  <p>Card content goes here.</p>
</pkt-card>

<pkt-card heading="Service name" clickCardlink="/services/detail" skin="blue"> </pkt-card>

<pkt-card heading="Article title" layout="horizontal">
  <p>Article summary text.</p>
</pkt-card>
```

## Notes

For Elements, complex props like `image` and `tags` can be passed in several ways: as JavaScript properties, as JSON strings in HTML attributes (Lit will `JSON.parse` them internally), or directly as objects in frameworks like Vue that bind to properties.

```js
// As JavaScript properties
const card = document.querySelector('pkt-card')
card.image = { src: '/images/service.jpg', alt: 'Service illustration' }
card.tags = [{ text: 'New', skin: 'green' }]
```

```html
<!-- As JSON string attribute -->
<pkt-card image='{"src": "/images/service.jpg", "alt": "Service illustration"}'></pkt-card>
```
