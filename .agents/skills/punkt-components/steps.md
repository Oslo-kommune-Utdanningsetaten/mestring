# Steps (Stepper)

Steps (stepper) shows progress through a multi-step process. It indicates which step the user is on, which steps are completed, and which are still ahead. Use it for wizards, onboarding flows, or any multi-step form.

## Availability

| Package        | Available | Tag / Import                                                                                    |
| -------------- | --------- | ----------------------------------------------------------------------------------------------- |
| React          | Yes       | `<PktStepper>` + `<PktStep>` — `import { PktStepper, PktStep } from '@oslokommune/punkt-react'` |
| Elements       | No        | —                                                                                               |
| Elements (CDN) | No        | —                                                                                               |

Dark mode: No

## Variants

### Orientations

| Orientation            | Use                                           |
| ---------------------- | --------------------------------------------- |
| `horizontal` (default) | Steps displayed in a row — for wider layouts  |
| `vertical`             | Steps stacked vertically — for narrow layouts |

## Props / Attributes — PktStepper

| Prop (React)                | Type                           | Default        | Description                                  |
| --------------------------- | ------------------------------ | -------------- | -------------------------------------------- |
| `activeStep`                | number                         | **(required)** | Index of the currently active step (0-based) |
| `hideNonActiveStepsContent` | boolean                        | `true`         | Hide content of non-active steps             |
| `orientation`               | `"horizontal"` \| `"vertical"` | `"horizontal"` | Layout orientation                           |

## Props / Attributes — PktStep

| Prop (React) | Type                                           | Default        | Description               |
| ------------ | ---------------------------------------------- | -------------- | ------------------------- |
| `title`      | string                                         | **(required)** | Step title                |
| `status`     | `"completed"` \| `"current"` \| `"incomplete"` | —              | Visual status of the step |

## Slots

| Component  | Slot    | Description                           |
| ---------- | ------- | ------------------------------------- |
| PktStepper | default | PktStep children                      |
| PktStep    | default | Content shown when the step is active |

## Examples

### React

```jsx
import { PktStepper, PktStep } from '@oslokommune/punkt-react'

;<PktStepper activeStep={1}>
  <PktStep title="Personal info" status="completed">
    <p>Step 1 content</p>
  </PktStep>
  <PktStep title="Address" status="current">
    <p>Step 2 content</p>
  </PktStep>
  <PktStep title="Review" status="incomplete">
    <p>Step 3 content</p>
  </PktStep>
</PktStepper>

{
  /* Vertical orientation */
}
;<PktStepper activeStep={0} orientation="vertical">
  <PktStep title="Step one" status="current">
    <p>First step content</p>
  </PktStep>
  <PktStep title="Step two" status="incomplete">
    <p>Second step content</p>
  </PktStep>
</PktStepper>
```
