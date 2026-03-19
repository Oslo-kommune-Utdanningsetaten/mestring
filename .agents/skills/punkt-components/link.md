# Link

Link is used for navigation to another page or resource. It can include an icon next to the text, positioned to the left or right.

## Availability

| Package        | Available | Tag / Import                                                                                 |
| -------------- | --------- | -------------------------------------------------------------------------------------------- |
| React          | Yes       | `<PktLink>` — `import { PktLink } from '@oslokommune/punkt-react'`                           |
| Elements       | Yes       | `<pkt-link>` — `import '@oslokommune/punkt-elements/dist/pkt-link.js'`                       |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-link.js" type="module">` |

Dark mode: Yes

## Usage guidelines

**Use link when:**

- The user should navigate to another page, section, or external resource

**Avoid link when:**

- The user should perform an action (submit, upload, delete) — use Button instead

**Button vs Link:** Use Link for navigation, Button for actions. This is a guideline, not a strict rule — sometimes a button works better even for navigation when there is a single primary action.

**Content guidelines:**

- Write clear link text that describes where the link goes
- Avoid generic text like "Click here" or "Read more" — the link text should make sense on its own

## Props / Attributes

| Prop (React)   | Attribute (Elements) | Type                                               | Default   | Description                          |
| -------------- | -------------------- | -------------------------------------------------- | --------- | ------------------------------------ |
| `href`         | `href`               | string                                             | `"#"`     | URL the link points to               |
| `target`       | `target`             | `"_blank"` \| `"_self"` \| `"_parent"` \| `"_top"` | `"_self"` | Link target                          |
| `iconName`     | `iconName`           | string (icon name)                                 | —         | Icon displayed next to the link text |
| `iconPosition` | `iconPosition`       | `"left"` \| `"right"`                              | —         | Position of the icon                 |

## Slots

| Slot    | Description       |
| ------- | ----------------- |
| default | Link text content |

## Accessibility

- Link text must describe the destination — avoid "Click here" or "Read more"
- When opening in a new tab (`target="_blank"`), indicate this to the user (e.g. with an external link icon)
- Links have a visible focus indicator for keyboard navigation

## Examples

### React

```jsx
import { PktLink } from '@oslokommune/punkt-react'

<PktLink href="/about">About us</PktLink>

<PktLink href="/download" iconName="download" iconPosition="right">
  Download report
</PktLink>

<PktLink href="https://example.com" target="_blank" iconName="external-link" iconPosition="right">
  External resource
</PktLink>
```

### Elements

```html
<pkt-link href="/about">About us</pkt-link>

<pkt-link href="/download" iconName="download" iconPosition="right">
  <span>Download report</span>
</pkt-link>

<pkt-link href="https://example.com" target="_blank" iconName="external-link" iconPosition="right">
  <span>External resource</span>
</pkt-link>
```
