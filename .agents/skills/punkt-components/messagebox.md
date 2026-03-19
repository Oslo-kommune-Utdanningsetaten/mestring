# Messagebox

Messagebox displays a highlighted informational message. Unlike Alert, it is not tied to a specific status or user action — use it for general information, tips, or callouts that are not critical or time-sensitive.

## Availability

| Package        | Available | Tag / Import                                                                                       |
| -------------- | --------- | -------------------------------------------------------------------------------------------------- |
| React          | Yes       | `<PktMessagebox>` — `import { PktMessagebox } from '@oslokommune/punkt-react'`                     |
| Elements       | Yes       | `<pkt-messagebox>` — `import '@oslokommune/punkt-elements/dist/pkt-messagebox.js'`                 |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-messagebox.js" type="module">` |

Dark mode: No

## Variants

### Skins

| Skin              | Use                          |
| ----------------- | ---------------------------- |
| `beige` (default) | Neutral, general information |
| `blue`            | Informational callout        |
| `red`             | Warning or important notice  |
| `green`           | Positive information or tip  |

### Sizes

| Size    | Use                                   |
| ------- | ------------------------------------- |
| Default | Standard size                         |
| Compact | Smaller message box with less padding |

## Usage guidelines

**Use messagebox when:**

- You want to display information that is not critical or time-sensitive
- You need visual grouping for a callout or tip

**Avoid messagebox when:**

- The message is a critical status, error, or confirmation — use Alert instead
- You need the user to take immediate action

## Props / Attributes

| Prop (React) | Attribute (Elements) | Type                                          | Default   | Description                    |
| ------------ | -------------------- | --------------------------------------------- | --------- | ------------------------------ |
| `title`      | `title`              | string                                        | —         | Title of the message box       |
| `skin`       | `skin`               | `"beige"` \| `"blue"` \| `"red"` \| `"green"` | `"beige"` | Color/style of the message box |
| `compact`    | `compact`            | boolean                                       | `false`   | Compact size with less padding |
| `closable`   | `closable`           | boolean                                       | `false`   | Show a close button            |

## Events

| Event (React) | Event (Elements) | Description                            |
| ------------- | ---------------- | -------------------------------------- |
| `onClose`     | `on-close`       | Fires when the close button is clicked |

## Slots

| Slot    | Description                |
| ------- | -------------------------- |
| default | Content of the message box |

## Examples

### React

```jsx
import { PktMessagebox } from '@oslokommune/punkt-react'

{
  /* Basic informational message */
}
;<PktMessagebox title="Good to know" skin="blue">
  You can find more information in the documentation.
</PktMessagebox>

{
  /* Closable message */
}
;<PktMessagebox title="Tip" skin="green" closable onClose={() => setVisible(false)}>
  Remember to save your progress regularly.
</PktMessagebox>

{
  /* Compact */
}
;<PktMessagebox skin="beige" compact>
  This service is in beta.
</PktMessagebox>
```

### Elements

```html
<pkt-messagebox title="Good to know" skin="blue">
  <p>You can find more information in the documentation.</p>
</pkt-messagebox>

<pkt-messagebox title="Tip" skin="green" closable>
  <p>Remember to save your progress regularly.</p>
</pkt-messagebox>
```
