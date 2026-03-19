# Switch

Switch lets the user toggle a setting on or off. It is visually a toggle slider, but is implemented as a **Checkbox with the `isSwitch` prop** set to `true`. Use it for binary settings that take effect immediately.

## Availability

| Package        | Available | Tag / Import                                                                                     |
| -------------- | --------- | ------------------------------------------------------------------------------------------------ |
| React          | Yes       | `<PktCheckbox isSwitch>` — `import { PktCheckbox } from '@oslokommune/punkt-react'`              |
| Elements       | Yes       | `<pkt-checkbox isSwitch>` — `import '@oslokommune/punkt-elements/dist/pkt-checkbox.js'`          |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-checkbox.js" type="module">` |

Dark mode: Yes

## Implementation

Switch is not a separate component — it is the Checkbox component with `isSwitch` set to `true`. All Checkbox props and events apply. See the [Checkbox](./checkbox.md) documentation for the full props reference.

## Usage guidelines

**Use switch when:**

- The user is toggling a binary setting on or off (e.g. notifications, dark mode)
- The change should take effect immediately without submitting a form

**Avoid switch when:**

- The user needs to confirm their choice before it takes effect — use Checkbox instead
- There are multiple related options — use Checkbox group instead
- The choice is between two distinct options (not on/off) — use Radio Button instead

## Key props

| Prop (React)     | Attribute (Elements) | Type                  | Default        | Description                                    |
| ---------------- | -------------------- | --------------------- | -------------- | ---------------------------------------------- |
| `isSwitch`       | `isSwitch`           | boolean               | `false`        | **Set to `true`** to render as a switch toggle |
| `label`          | `label`              | string                | —              | Text label for the switch                      |
| `name`           | `name`               | string                | **(required)** | Form field name                                |
| `id`             | `id`                 | string                | **(required)** | Unique identifier                              |
| `checked`        | `checked`            | boolean               | `false`        | Controlled on/off state                        |
| `defaultChecked` | `defaultChecked`     | boolean               | `false`        | Initially on (uncontrolled)                    |
| `disabled`       | `disabled`           | boolean               | `false`        | Disables the switch                            |
| `labelPosition`  | `labelPosition`      | `"right"` \| `"left"` | —              | Position of the label                          |

## Events

| Event (React) | Event (Elements) | Description                      |
| ------------- | ---------------- | -------------------------------- |
| `onChange`    | `change`         | Fires when the switch is toggled |

## Examples

### React

```jsx
import { PktCheckbox } from '@oslokommune/punkt-react'

{
  /* Basic switch */
}
;<PktCheckbox isSwitch label="Enable notifications" name="notifications" id="notifications" />

{
  /* Controlled switch */
}
;<PktCheckbox
  isSwitch
  label="Dark mode"
  name="dark-mode"
  id="dark-mode"
  checked={isDarkMode}
  onChange={(e) => setIsDarkMode(e.target.checked)}
/>

{
  /* Label on the left */
}
;<PktCheckbox
  isSwitch
  label="Auto-save"
  name="autosave"
  id="autosave"
  labelPosition="left"
  defaultChecked
/>
```

### Elements

```html
<pkt-checkbox
  isSwitch
  label="Enable notifications"
  name="notifications"
  id="notifications"
></pkt-checkbox>

<pkt-checkbox
  isSwitch
  label="Dark mode"
  name="dark-mode"
  id="dark-mode"
  labelPosition="left"
></pkt-checkbox>
```
