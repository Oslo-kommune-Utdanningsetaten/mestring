# Tag

Tag displays a short label, status, or category. It can include an icon and an optional close button. Use tags for filtering, categorization, or status indicators.

## Availability

| Package        | Available | Tag / Import                                                                                |
| -------------- | --------- | ------------------------------------------------------------------------------------------- |
| React          | Yes       | `<PktTag>` — `import { PktTag } from '@oslokommune/punkt-react'`                            |
| Elements       | Yes       | `<pkt-tag>` — `import '@oslokommune/punkt-elements/dist/pkt-tag.js'`                        |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-tag.js" type="module">` |

Dark mode: Yes

## Variants

### Skins

| Skin             | Use                         |
| ---------------- | --------------------------- |
| `blue` (default) | Standard tag                |
| `blue-light`     | Lighter blue                |
| `blue-dark`      | Darker blue                 |
| `green`          | Positive status or category |
| `red`            | Negative status or warning  |
| `beige`          | Neutral alternative         |
| `yellow`         | Attention or pending        |
| `gray`           | Inactive or secondary       |

### Sizes

| Size               | Use            |
| ------------------ | -------------- |
| `small`            | Compact spaces |
| `medium` (default) | Standard use   |
| `large`            | Emphasis       |

### Text styles

| Style                   | Description    |
| ----------------------- | -------------- |
| `normal-text` (default) | Normal weight  |
| `thin-text`             | Lighter weight |

## Props / Attributes

| Prop (React) | Attribute (Elements) | Type                                                                                                       | Default         | Description                |
| ------------ | -------------------- | ---------------------------------------------------------------------------------------------------------- | --------------- | -------------------------- |
| `skin`       | `skin`               | `"blue"` \| `"blue-light"` \| `"blue-dark"` \| `"green"` \| `"red"` \| `"beige"` \| `"yellow"` \| `"gray"` | `"blue"`        | Color/style of the tag     |
| `size`       | `size`               | `"small"` \| `"medium"` \| `"large"`                                                                       | `"medium"`      | Tag size                   |
| `iconName`   | `iconName`           | string (icon name)                                                                                         | —               | Icon displayed in the tag  |
| `closeTag`   | `closeTag`           | boolean                                                                                                    | `false`         | Show a close/remove button |
| `textStyle`  | `textStyle`          | `"thin-text"` \| `"normal-text"`                                                                           | `"normal-text"` | Text weight style          |
| `type`       | `type`               | `"button"` \| `"submit"` \| `"reset"`                                                                      | `"button"`      | Button type when closable  |
| `ariaLabel`  | `ariaLabel`          | string                                                                                                     | —               | Screen reader label        |

## Slots

| Slot    | Description |
| ------- | ----------- |
| default | Tag text    |

## Examples

### React

```jsx
import { PktTag } from '@oslokommune/punkt-react'

{
  /* Basic tag */
}
;<PktTag skin="blue">Active</PktTag>

{
  /* With icon */
}
;<PktTag skin="green" iconName="check">
  Completed
</PktTag>

{
  /* Closable tag */
}
;<PktTag skin="beige" closeTag onClick={() => removeTag(id)}>
  Filter item
</PktTag>

{
  /* Small tag */
}
;<PktTag size="small" skin="gray">
  Draft
</PktTag>
```

### Elements

```html
<pkt-tag skin="blue"><span>Active</span></pkt-tag>

<pkt-tag skin="green" iconName="check"><span>Completed</span></pkt-tag>

<pkt-tag skin="beige" closeTag><span>Filter item</span></pkt-tag>
```
