# Alert

Alert (status message) gives the user a message — for example to inform about an important event, confirm an action, or warn about an error. The purpose is to help the user understand what has happened and what to do next.

## Availability

| Package        | Available | Tag / Import                                                                                  |
| -------------- | --------- | --------------------------------------------------------------------------------------------- |
| React          | Yes       | `<PktAlert>` — `import { PktAlert } from '@oslokommune/punkt-react'`                          |
| Elements       | Yes       | `<pkt-alert>` — `import '@oslokommune/punkt-elements/dist/pkt-alert.js'`                      |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-alert.js" type="module">` |

Dark mode: Yes

## Variants

### Skins (statuses)

| Skin      | Use                                                            |
| --------- | -------------------------------------------------------------- |
| `info`    | Additional information that doesn't require immediate action   |
| `success` | Confirms that an action was successful                         |
| `warning` | Warns the user about system errors or consequences of a choice |
| `error`   | Tells the user something went wrong — explain how to fix it    |

### Sizes

| Size    | Use                                                |
| ------- | -------------------------------------------------- |
| Default | Standard size                                      |
| Compact | For short, tighter messages (e.g. inline in forms) |

### Placement types

| Type         | Use                                             |
| ------------ | ----------------------------------------------- |
| Inline alert | Placed close to the content it relates to       |
| Banner alert | Placed above the content, with title and date   |
| Toast alert  | Brief status shown temporarily (e.g. auto-save) |

## Usage guidelines

**Use alert when:**

- You want to inform the user about an important status, change, or error
- You want to confirm that an action has been completed (e.g. saved, submitted, deleted)

**Avoid alert when:**

- The information is not critical to the user's task
- You only need visual grouping — use Messagebox instead
- There are already too many alerts on the page

**Content guidelines:**

- Write clear, direct messages — keep it short, especially for inline alerts
- Use a title when the message needs a summary (banner alerts)
- Show one alert at a time if possible — too many alerts overwhelm and confuse
- Place the alert close to the content or field it relates to
- If the alert is a close button, the user should always know how to fix the issue

## Props / Attributes

| Prop (React) | Attribute (Elements) | Type                                                | Default    | Description                               |
| ------------ | -------------------- | --------------------------------------------------- | ---------- | ----------------------------------------- |
| `title`      | `title`              | string                                              | —          | Title displayed at the top of the alert   |
| `skin`       | `skin`               | `"info"` \| `"success"` \| `"warning"` \| `"error"` | `"info"`   | Type and color of the alert               |
| `date`       | `date`               | string                                              | —          | Date displayed at the bottom of the alert |
| `ariaLive`   | `ariaLive`           | `"off"` \| `"polite"` \| `"assertive"`              | `"polite"` | How screen readers announce the alert     |
| `compact`    | `compact`            | boolean                                             | `false`    | Makes the alert smaller                   |
| `closeAlert` | `closeAlert`         | boolean                                             | `false`    | Shows a close button                      |

## Events

| Event (React) | Event (Elements) | Description                            |
| ------------- | ---------------- | -------------------------------------- |
| `onClose`     | `close`          | Fires when the close button is clicked |

## Slots

| Slot    | Description          |
| ------- | -------------------- |
| default | Content of the alert |

## Accessibility

- Uses `aria-live` to announce alerts to screen readers — use `"polite"` for non-urgent updates, `"assertive"` for critical messages
- The close button must be keyboard-accessible (focusable and activatable with keyboard)
- The message must not rely on color alone — both text and icon should convey the meaning
- For toast alerts that disappear automatically, ensure all users can perceive the message in time — when in doubt, keep the alert visible with a manual close option
- Test the component at different screen sizes and zoom levels

## Examples

### React

```jsx
import { PktAlert } from '@oslokommune/punkt-react'

{
  /* Info alert */
}
;<PktAlert skin="info" title="Information">
  Your application has been received.
</PktAlert>

{
  /* Success alert with close button */
}
;<PktAlert skin="success" closeAlert onClose={() => setVisible(false)}>
  Changes saved successfully.
</PktAlert>

{
  /* Error alert */
}
;<PktAlert skin="error" title="Error">
  Something went wrong. Please try again.
</PktAlert>

{
  /* Compact inline alert */
}
;<PktAlert skin="warning" compact>
  This field requires attention.
</PktAlert>
```

### Elements

```html
<pkt-alert skin="info" title="Information">
  <p>Your application has been received.</p>
</pkt-alert>

<pkt-alert skin="success" closeAlert>
  <p>Changes saved successfully.</p>
</pkt-alert>

<pkt-alert skin="error" title="Error">
  <p>Something went wrong. Please try again.</p>
</pkt-alert>

<pkt-alert skin="warning" compact>
  <p>This field requires attention.</p>
</pkt-alert>
```
