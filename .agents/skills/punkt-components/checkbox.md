# Checkbox

Checkbox lets the user select one or more options from a group of choices. You can also use a standalone checkbox to ask for confirmation, such as "I accept the terms" before submitting a form.

## Availability

| Package        | Available | Tag / Import                                                                                     |
| -------------- | --------- | ------------------------------------------------------------------------------------------------ |
| React          | Yes       | `<PktCheckbox>` — `import { PktCheckbox } from '@oslokommune/punkt-react'`                       |
| Elements       | Yes       | `<pkt-checkbox>` — `import '@oslokommune/punkt-elements/dist/pkt-checkbox.js'`                   |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-checkbox.js" type="module">` |

Dark mode: Yes

## Variants

| Variant            | Use                                                                            |
| ------------------ | ------------------------------------------------------------------------------ |
| Standard           | When the checkbox stands alone or in a simple list                             |
| Tile (with border) | When you want to visually group checkboxes. Gives clear separation and spacing |
| Standalone         | Single checkbox for confirmations (e.g. "I accept the terms")                  |
| Group              | Multiple checkboxes for selecting from a category of choices                   |

### States

| State         | Description                                                              |
| ------------- | ------------------------------------------------------------------------ |
| Default       | Unchecked                                                                |
| Checked       | Selected                                                                 |
| Indeterminate | Some but not all child items selected — useful for "select all" patterns |
| Error         | Field has a validation error                                             |
| Disabled      | Not available for interaction                                            |

## Usage guidelines

**Use checkbox when:**

- You have a group of choices within the same context
- The choices are not mutually exclusive
- The user should be able to select one or more options
- The user needs to toggle an option on/off (e.g. "accept terms")

**Avoid checkbox when:**

- The user can only pick one option — use Radio Button instead
- There are more than 10 options — consider using Select
- It's a binary on/off setting — use Switch instead
- There are very few options — consider Switch or Radio Button

**Content guidelines:**

- Each checkbox must have a clear, concrete label describing what the choice means
- Avoid labels like just "Yes" or "No"

**Opt-in, not opt-out:**

- Checkbox should always be used as opt-in — never pre-check a consent checkbox (GDPR requirement)

**Placement:**

- Place checkboxes vertically when possible for better readability
- Horizontal placement only for 2–3 short options
- On mobile, checkboxes should always be vertical

## Props / Attributes

| Prop (React)     | Attribute (Elements) | Type                  | Default        | Description                                                   |
| ---------------- | -------------------- | --------------------- | -------------- | ------------------------------------------------------------- |
| `label`          | `label`              | string                | —              | Text label for the checkbox                                   |
| `checkHelptext`  | `checkHelptext`      | string                | —              | Help text for the checkbox                                    |
| `name`           | `name`               | string                | **(required)** | Form field name                                               |
| `value`          | `value`              | string                | —              | Value submitted with the form                                 |
| `id`             | `id`                 | string                | **(required)** | Unique identifier                                             |
| `defaultChecked` | `defaultChecked`     | boolean               | `false`        | Initially checked (uncontrolled)                              |
| `checked`        | `checked`            | boolean               | `false`        | Controlled checked state                                      |
| `indeterminate`  | `indeterminate`      | boolean               | `false`        | Indeterminate state for "select all" patterns                 |
| `hasTile`        | `hasTile`            | boolean               | `false`        | Wrap checkbox in a tile (bordered box)                        |
| `disabled`       | `disabled`           | boolean               | `false`        | Disables the checkbox                                         |
| `hasError`       | `hasError`           | boolean               | `false`        | Shows error state                                             |
| `isSwitch`       | `isSwitch`           | boolean               | `false`        | Renders as a switch toggle (see Switch component)             |
| `labelPosition`  | `labelPosition`      | `"right"` \| `"left"` | —              | Position of the label relative to the checkbox                |
| `hideLabel`      | `hideLabel`          | boolean               | `false`        | Visually hides the label (still accessible to screen readers) |
| `requiredTag`    | `requiredTag`        | boolean               | `false`        | Show "Required" tag next to label                             |
| `requiredText`   | `requiredText`       | string                | —              | Text in the required tag                                      |
| `optionalTag`    | `optionalTag`        | boolean               | —              | Show "Optional" tag next to label                             |
| `optionalText`   | `optionalText`       | string                | —              | Text in the optional tag                                      |
| `tagText`        | `tagText`            | string                | —              | Custom tag text next to label                                 |

## Events

| Event (React) | Event (Elements) | Description                           |
| ------------- | ---------------- | ------------------------------------- |
| `onChange`    | `change`         | Fires when the checkbox value changes |

## Accessibility

- Every checkbox must have a label — visible or hidden with `pkt-sr-only` class
- Avoid pre-selected defaults — they can be misleading
- Avoid disabled checkboxes — prefer showing an error message or help text explaining why. If you must disable, make it clear why and what must change to enable it
- Use `fieldset` and `legend` (via Input Wrapper) when grouping checkboxes
- Keyboard: navigate with Tab, toggle with Space
- The indeterminate state is for "select all" patterns where some but not all children are selected

**Testing tip:** When testing `checked` state, test the visual state with `:checked` query rather than the `.checked` property. In punkt-testing-utils: `element.querySelectorAll(':checked').length`. Use `data-testid` (forwarded to the form element) or set `skipForwardTestid` to keep it on the `<pkt-checkbox>` element.

## Examples

### React

```jsx
import { PktCheckbox } from '@oslokommune/punkt-react'

{/* Basic checkbox */}
<PktCheckbox label="I accept the terms" name="terms" id="terms" />

{/* Checkbox group with tiles */}
<PktCheckbox label="Email" name="contact" id="contact-email" value="email" hasTile />
<PktCheckbox label="Phone" name="contact" id="contact-phone" value="phone" hasTile />
<PktCheckbox label="Letter" name="contact" id="contact-letter" value="letter" hasTile />

{/* Controlled checkbox with error */}
<PktCheckbox
  label="Subscribe to newsletter"
  name="newsletter"
  id="newsletter"
  checked={isChecked}
  hasError={showError}
  onChange={(e) => setIsChecked(e.target.checked)}
/>

{/* Indeterminate "select all" */}
<PktCheckbox
  label="Select all"
  name="selectAll"
  id="select-all"
  indeterminate={someSelected && !allSelected}
  checked={allSelected}
  onChange={handleSelectAll}
/>
```

### Elements

```html
<pkt-checkbox label="I accept the terms" name="terms" id="terms"></pkt-checkbox>

<pkt-checkbox label="Email" name="contact" id="contact-email" value="email" hasTile></pkt-checkbox>
<pkt-checkbox label="Phone" name="contact" id="contact-phone" value="phone" hasTile></pkt-checkbox>
<pkt-checkbox
  label="Letter"
  name="contact"
  id="contact-letter"
  value="letter"
  hasTile
></pkt-checkbox>
```
