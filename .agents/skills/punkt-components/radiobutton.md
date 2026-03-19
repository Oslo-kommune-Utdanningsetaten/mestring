# Radio Button

Radio Button lets the user select exactly one option from a group of mutually exclusive choices. All radio buttons in a group share the same `name`.

## Availability

| Package        | Available | Tag / Import                                                                                        |
| -------------- | --------- | --------------------------------------------------------------------------------------------------- |
| React          | Yes       | `<PktRadioButton>` — `import { PktRadioButton } from '@oslokommune/punkt-react'`                    |
| Elements       | Yes       | `<pkt-radiobutton>` — `import '@oslokommune/punkt-elements/dist/pkt-radiobutton.js'`                |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-radiobutton.js" type="module">` |

Dark mode: Yes

## Variants

| Variant            | Use                                                                    |
| ------------------ | ---------------------------------------------------------------------- |
| Standard           | Basic radio button with label                                          |
| Tile (with border) | Visual grouping with bordered box — gives clear separation and spacing |

## Usage guidelines

**Use radio button when:**

- The user must select exactly one option from a group
- The options are mutually exclusive

**Avoid radio button when:**

- The user can select multiple options — use Checkbox instead
- There are more than 7–10 options — use Select or Combobox instead
- It's a simple on/off toggle — use Switch instead

**Content guidelines:**

- Each radio button must have a clear, concrete label
- Place radio buttons vertically for better readability
- Use `fieldset` and `legend` (via Input Wrapper) to group radio buttons

## Props / Attributes

| Prop (React)     | Attribute (Elements) | Type    | Default        | Description                                       |
| ---------------- | -------------------- | ------- | -------------- | ------------------------------------------------- |
| `id`             | `id`                 | string  | **(required)** | Unique identifier                                 |
| `name`           | `name`               | string  | **(required)** | Group name (shared by all radio buttons in group) |
| `label`          | `label`              | string  | **(required)** | Label text                                        |
| `value`          | `value`              | string  | —              | Value submitted with the form                     |
| `checked`        | `checked`            | boolean | `false`        | Controlled checked state                          |
| `defaultChecked` | `defaultChecked`     | boolean | `false`        | Initially checked (uncontrolled)                  |
| `hasTile`        | `hasTile`            | boolean | `false`        | Wrap in a tile (bordered box)                     |
| `disabled`       | `disabled`           | boolean | `false`        | Disables the radio button                         |
| `checkHelptext`  | `checkHelptext`      | string  | —              | Help text shown below the radio button            |
| `hasError`       | `hasError`           | boolean | `false`        | Shows error state                                 |
| `requiredTag`    | `requiredTag`        | boolean | `false`        | Show "Required" tag next to label                 |
| `requiredText`   | `requiredText`       | string  | —              | Text in the required tag                          |
| `optionalTag`    | `optionalTag`        | boolean | —              | Show "Optional" tag next to label                 |
| `optionalText`   | `optionalText`       | string  | —              | Text in the optional tag                          |
| `tagText`        | `tagText`            | string  | —              | Custom tag text next to label                     |

## Events

| Event (React) | Event (Elements) | Description                                   |
| ------------- | ---------------- | --------------------------------------------- |
| `onChange`    | `change`         | Fires when the radio button selection changes |

## Accessibility

- Group radio buttons with `fieldset` and `legend` (via Input Wrapper)
- Keyboard: navigate within a group with arrow keys, select with Space
- Each radio button must have a visible and accessible label
- Avoid disabled radio buttons — prefer showing an error message explaining why. If you must disable, make it clear what must change to enable it

## Examples

### React

```jsx
import { PktRadioButton, PktInputWrapper } from '@oslokommune/punkt-react'

{
  /* Radio button group */
}
;<PktInputWrapper forId="contact-method" label="Preferred contact method" hasFieldset>
  <PktRadioButton label="Email" name="contact" id="contact-email" value="email" />
  <PktRadioButton label="Phone" name="contact" id="contact-phone" value="phone" />
  <PktRadioButton label="Letter" name="contact" id="contact-letter" value="letter" />
</PktInputWrapper>

{
  /* With tiles */
}
;<PktInputWrapper forId="size" label="Choose size" hasFieldset>
  <PktRadioButton label="Small" name="size" id="size-s" value="s" hasTile />
  <PktRadioButton label="Medium" name="size" id="size-m" value="m" hasTile defaultChecked />
  <PktRadioButton label="Large" name="size" id="size-l" value="l" hasTile />
</PktInputWrapper>
```

### Elements

```html
<pkt-input-wrapper forId="contact-method" label="Preferred contact method" hasFieldset>
  <pkt-radiobutton label="Email" name="contact" id="contact-email" value="email"></pkt-radiobutton>
  <pkt-radiobutton label="Phone" name="contact" id="contact-phone" value="phone"></pkt-radiobutton>
  <pkt-radiobutton
    label="Letter"
    name="contact"
    id="contact-letter"
    value="letter"
  ></pkt-radiobutton>
</pkt-input-wrapper>
```
