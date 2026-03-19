# Button

Button lets the user perform an action, such as submitting a form, starting a process, or confirming a choice. It should be clear, give good feedback, and be placed where the action belongs.

## Availability

| Package        | Available | Tag / Import                                                                                   |
| -------------- | --------- | ---------------------------------------------------------------------------------------------- |
| React          | Yes       | `<PktButton>` — `import { PktButton } from '@oslokommune/punkt-react'`                         |
| Elements       | Yes       | `<pkt-button>` — `import '@oslokommune/punkt-elements/dist/pkt-button.js'`                     |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-button.js" type="module">` |

Dark mode: Yes

## Variants

### Skins

| Skin        | Use                                                      |
| ----------- | -------------------------------------------------------- |
| `primary`   | Main action on the page. Use once per view               |
| `secondary` | Alternative or less important actions                    |
| `tertiary`  | When the button should not draw attention, e.g. "Cancel" |

### Sizes

| Size               | Use                               |
| ------------------ | --------------------------------- |
| `small`            | Tight spaces like tables          |
| `medium` (default) | Standard size, use as the default |
| `large`            | For extra emphasis                |

### Colors

The `color` prop overrides `skin`. Prefer the default Oslo blue. Use other colors only when they carry specific meaning.

| Color                | Use                                |
| -------------------- | ---------------------------------- |
| `blue`               | Standard. Use this by default      |
| `blue-outline`       | Special cases, use sparingly       |
| `green`              | Confirm success, e.g. "Complete"   |
| `green-outline`      | Special cases, use sparingly       |
| `green-dark`         | Special cases, use sparingly       |
| `green-dark-outline` | Special cases, use sparingly       |
| `beige-light`        | Special cases, use sparingly       |
| `beige-dark-outline` | Special cases, use sparingly       |
| `yellow`             | Special cases, use sparingly       |
| `yellow-outline`     | Special cases, use sparingly       |
| `red`                | Destructive actions, e.g. "Delete" |
| `red-outline`        | Special cases, use sparingly       |

### Icon variants

| Variant                | Description                             |
| ---------------------- | --------------------------------------- |
| `label-only` (default) | Text only                               |
| `icon-left`            | Text + icon to the left                 |
| `icon-right`           | Text + icon to the right                |
| `icons-right-and-left` | Text + icons on both sides              |
| `icon-only`            | Icon only — avoid unless no alternative |

## Usage guidelines

**Use button when:**

- The user should perform a concrete action on the page
- The action does not involve navigating to a new page

**Avoid button when:**

- The action is navigation to a new page — use Link instead
- You want to show status or information — use Tag or Tabs instead

**Button vs Link:** Use Link for navigation, Button for actions (log in, submit, upload, etc.). This is a guideline, not a strict rule — sometimes a button works better even for navigation, e.g. when there is a single primary action.

**Content guidelines:**

- Use clear, active language with imperative verbs
- Keep text to 2–3 words maximum
- The text should describe what happens when clicked

**Buttons are brand-bearing:** Use the primary color (dark blue) as default. Avoid strong colors (green, red, yellow) unless they carry a specific message. Do not use rounded corners.

## Props / Attributes

| Prop (React)        | Attribute (Elements)   | Type                                                                                           | Default        | Description                              |
| ------------------- | ---------------------- | ---------------------------------------------------------------------------------------------- | -------------- | ---------------------------------------- |
| `skin`              | `skin`                 | `"primary"` \| `"secondary"` \| `"tertiary"`                                                   | `"primary"`    | Visual style of the button               |
| `size`              | `size`                 | `"small"` \| `"medium"` \| `"large"`                                                           | `"medium"`     | Button size                              |
| `color`             | `color`                | See color table above                                                                          | —              | Overrides skin with a specific color     |
| `variant`           | `variant`              | `"label-only"` \| `"icon-left"` \| `"icon-right"` \| `"icon-only"` \| `"icons-right-and-left"` | `"label-only"` | Icon placement variant                   |
| `type`              | `type`                 | `"button"` \| `"submit"` \| `"reset"`                                                          | `"button"`     | HTML button type                         |
| `fullWidth`         | `full-width`           | boolean                                                                                        | `false`        | Button takes full width of container     |
| `fullWidthOnMobile` | `full-width-on-mobile` | boolean                                                                                        | `false`        | Full width on small screens only         |
| `iconName`          | `iconName`             | string (icon name)                                                                             | —              | Name of the icon to display              |
| `secondIconName`    | `secondIconName`       | string (icon name)                                                                             | —              | Second icon (for `icons-right-and-left`) |
| `iconPath`          | `iconPath`             | string                                                                                         | —              | Custom path to icon SVG                  |
| `secondIconPath`    | `secondIconPath`       | string                                                                                         | —              | Custom path to second icon SVG           |
| `isLoading`         | `isLoading`            | boolean                                                                                        | `false`        | Shows a loading spinner                  |
| `disabled`          | `disabled`             | boolean                                                                                        | `false`        | Disables the button                      |

## Events

| Event (React) | Event (Elements) | Description                      |
| ------------- | ---------------- | -------------------------------- |
| `onClick`     | `click`          | Fires when the button is clicked |

## Slots

| Slot    | Description          |
| ------- | -------------------- |
| default | Button label content |

## Accessibility

- Keyboard: activated with Enter or Space
- Shows clear focus indicator when focused
- Avoid disabled buttons — prefer showing an error message or help text explaining why the action is unavailable
- If you must disable a button, make it clear to the user why and what must change to enable it
- On mobile, use `fullWidth` or `fullWidthOnMobile` to ensure sufficient touch target size (WCAG 2.5.8)

## Examples

### React

```jsx
import { PktButton } from '@oslokommune/punkt-react'

{
  /* Primary button */
}
;<PktButton skin="primary">Submit</PktButton>

{
  /* Secondary with icon */
}
;<PktButton skin="secondary" variant="icon-left" iconName="download">
  Download
</PktButton>

{
  /* Destructive action */
}
;<PktButton color="red">Delete</PktButton>

{
  /* Full width on mobile */
}
;<PktButton fullWidthOnMobile>Continue</PktButton>

{
  /* Loading state */
}
;<PktButton isLoading>Saving...</PktButton>
```

### Elements

```html
<pkt-button skin="primary">
  <span>Submit</span>
</pkt-button>

<pkt-button skin="secondary" variant="icon-left" iconName="download">
  <span>Download</span>
</pkt-button>

<pkt-button color="red">
  <span>Delete</span>
</pkt-button>

<pkt-button full-width-on-mobile>
  <span>Continue</span>
</pkt-button>
```

## Notes

The loading animation path can be overridden globally by setting `window.pktAnimationPath`.
