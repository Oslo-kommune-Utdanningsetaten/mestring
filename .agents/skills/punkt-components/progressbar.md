# Progress Bar

Progress Bar shows the user how far along a process or measurement is. It can be used for actual progress (e.g. file upload, step completion) or for displaying a static measurement (e.g. capacity used).

## Availability

| Package        | Available | Tag / Import                                                                                        |
| -------------- | --------- | --------------------------------------------------------------------------------------------------- |
| React          | Yes       | `<PktProgressbar>` — `import { PktProgressbar } from '@oslokommune/punkt-react'`                    |
| Elements       | Yes       | `<pkt-progressbar>` — `import '@oslokommune/punkt-elements/dist/pkt-progressbar.js'`                |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-progressbar.js" type="module">` |

Dark mode: Yes

## Variants

### Skins

| Skin                  | Use                       |
| --------------------- | ------------------------- |
| `dark-blue` (default) | Standard progress bar     |
| `light-blue`          | Lighter alternative       |
| `green`               | Positive progress/success |
| `red`                 | Warning or limit reached  |

### Status display

| Status type            | Description                            |
| ---------------------- | -------------------------------------- |
| `percentage` (default) | Shows progress as percentage           |
| `fraction`             | Shows progress as fraction (e.g. 3/10) |
| `none`                 | No status text                         |

### Status placement

| Placement             | Description                    |
| --------------------- | ------------------------------ |
| `following` (default) | Follows the progress indicator |
| `left`                | Placed to the left             |
| `center`              | Centered                       |

### Roles

| Role                    | Use                                |
| ----------------------- | ---------------------------------- |
| `progressbar` (default) | Active progress towards completion |
| `meter`                 | Static measurement or gauge        |

## Props / Attributes

| Prop (React)      | Attribute (Elements) | Type                                                    | Default            | Description                                    |
| ----------------- | -------------------- | ------------------------------------------------------- | ------------------ | ---------------------------------------------- |
| `title`           | `title`              | string                                                  | —                  | Title displayed above the bar                  |
| `titlePosition`   | `titlePosition`      | `"left"` \| `"center"`                                  | `"left"`           | Title text alignment                           |
| `skin`            | `skin`               | `"dark-blue"` \| `"light-blue"` \| `"green"` \| `"red"` | `"dark-blue"`      | Color of the progress bar                      |
| `valueCurrent`    | `valueCurrent`       | number                                                  | `0` **(required)** | Current progress value                         |
| `valueMin`        | `valueMin`           | number                                                  | `0`                | Minimum value                                  |
| `valueMax`        | `valueMax`           | number                                                  | `100`              | Maximum value                                  |
| `statusType`      | `statusType`         | `"none"` \| `"percentage"` \| `"fraction"`              | `"percentage"`     | How progress is displayed as text              |
| `statusPlacement` | `statusPlacement`    | `"left"` \| `"following"` \| `"center"`                 | `"following"`      | Where the status text is placed                |
| `role`            | `role`               | `"progressbar"` \| `"meter"`                            | `"progressbar"`    | ARIA role                                      |
| `id`              | `id`                 | string                                                  | —                  | Unique identifier                              |
| `ariaLabel`       | `ariaLabel`          | string                                                  | —                  | Screen reader label                            |
| `ariaLabelledby`  | `ariaLabelledby`     | string                                                  | —                  | ID of the element that labels this bar         |
| `ariaValueText`   | `ariaValueText`      | string                                                  | —                  | Screen reader description of the current value |
| `ariaLive`        | `ariaLive`           | `"off"` \| `"polite"` \| `"assertive"`                  | `"polite"`         | How screen readers announce updates            |

## Accessibility

- Uses native ARIA roles (`progressbar` or `meter`) for screen reader support
- `ariaLive` announces progress updates — use `"polite"` for non-urgent, `"assertive"` for critical
- Provide `ariaLabel` or `ariaLabelledby` for screen reader context
- Use `ariaValueText` to give a human-readable description (e.g. "3 of 10 steps completed")

## Examples

### React

```jsx
import { PktProgressbar } from '@oslokommune/punkt-react'

{
  /* Basic progress bar */
}
;<PktProgressbar title="Upload progress" valueCurrent={65} skin="dark-blue" />

{
  /* Fraction display */
}
;<PktProgressbar
  title="Steps completed"
  valueCurrent={3}
  valueMax={10}
  statusType="fraction"
  skin="green"
/>

{
  /* Meter role (static measurement) */
}
;<PktProgressbar
  title="Storage used"
  valueCurrent={80}
  role="meter"
  skin="red"
  ariaValueText="80% of storage used"
/>
```

### Elements

```html
<pkt-progressbar title="Upload progress" valueCurrent="65" skin="dark-blue"></pkt-progressbar>

<pkt-progressbar
  title="Steps completed"
  valueCurrent="3"
  valueMax="10"
  statusType="fraction"
  skin="green"
></pkt-progressbar>
```
