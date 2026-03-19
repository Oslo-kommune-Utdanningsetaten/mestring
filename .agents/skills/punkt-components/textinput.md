# Text Input

Text input lets the user type free-form text, typically in forms. Use it for short values that fit on one line, such as names, email addresses, phone numbers, national IDs, or amounts.

## Availability

| Package        | Available | Tag / Import                                                                                      |
| -------------- | --------- | ------------------------------------------------------------------------------------------------- |
| React          | Yes       | `<PktTextinput>` — `import { PktTextinput } from '@oslokommune/punkt-react'`                      |
| Elements       | Yes       | `<pkt-textinput>` — `import '@oslokommune/punkt-elements/dist/pkt-textinput.js'`                  |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-textinput.js" type="module">` |

Dark mode: No

## Variants

Text input is typically used together with the built-in Input Wrapper (enabled by default via `useWrapper`). The wrapper provides label, help text, error messages, and optional/required tags.

| Variant                   | Description                                      |
| ------------------------- | ------------------------------------------------ |
| Standard                  | Label, placeholder, and text field               |
| With help text            | Short help text below the label                  |
| With expandable help text | Help text behind a "Read more" button            |
| Optional/required tag     | Shows "Optional" or "Required" next to the label |

### States

| State    | Description                                 |
| -------- | ------------------------------------------- |
| Default  | Normal state, ready for input               |
| Hover    | Mouse over the field                        |
| Focus    | Field is selected, ready for typing         |
| Active   | User is typing                              |
| Error    | Field has an error, error message displayed |
| Disabled | Field is not available for interaction      |

## Usage guidelines

**Use text input when:**

- The user should type short free text on one line (name, email, phone, amount)
- The value is unique and cannot be selected from a list

**Avoid text input when:**

- The user should choose from predefined options — use Select, Radio Button, or Checkbox
- The content is longer text or paragraphs — use Textarea

**Labels:**

- Keep labels short and precise: 1–3 words
- No colon at the end
- Don't use all caps or all lowercase

**Placeholders:**

- Never use placeholder as the only instruction — it disappears when the user types and is not always accessible to screen readers
- Use label and/or help text for guidance instead

**Width:**

- Match the field width to the expected input — a phone number field shouldn't be wider than needed
- Varying widths help users navigate forms with many fields

**Optional vs required:**

- Choose one method per solution: either show "Optional" on optional fields, or "Required" on required fields
- Never mix both approaches in the same form

**Prefix and suffix:**

- Use prefix for fixed characters before the value (e.g. country code)
- Use suffix for units, icons, or actions (e.g. show/hide password)

**Help text and error messages:**

- Help text should clarify, not repeat the label
- Error messages should be specific and explain how to fix the issue

## Props / Attributes

| Prop (React)             | Attribute (Elements)     | Type                                                                                                                                                                                    | Default          | Description                              |
| ------------------------ | ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ---------------------------------------- |
| `label`                  | `label`                  | string                                                                                                                                                                                  | —                | Text displayed above the field           |
| `name`                   | `name`                   | string                                                                                                                                                                                  | **(required)**   | Form field name                          |
| `id`                     | `id`                     | string                                                                                                                                                                                  | **(required)**   | Unique identifier for the field          |
| `type`                   | `type`                   | `"text"` \| `"email"` \| `"tel"` \| `"password"` \| `"number"` \| `"search"` \| `"url"` \| `"date"` \| `"datetime-local"` \| `"time"` \| `"month"` \| `"week"` \| `"color"` \| `"file"` | `"text"`         | HTML input type                          |
| `value`                  | `value`                  | string                                                                                                                                                                                  | —                | Current value of the field               |
| `placeholder`            | `placeholder`            | string                                                                                                                                                                                  | —                | Hint text shown when empty               |
| `helptext`               | `helptext`               | string                                                                                                                                                                                  | —                | Help text displayed below the label      |
| `helptextDropdown`       | `helptextDropdown`       | string                                                                                                                                                                                  | —                | Expandable help text content             |
| `helptextDropdownButton` | `helptextDropdownButton` | string                                                                                                                                                                                  | `"Les mer"`      | Button text for expandable help          |
| `size`                   | `size`                   | number                                                                                                                                                                                  | —                | Field width in character count           |
| `prefix`                 | `prefix`                 | string                                                                                                                                                                                  | —                | Text shown before the field              |
| `suffix`                 | `suffix`                 | string                                                                                                                                                                                  | —                | Text shown after the field               |
| `iconNameRight`          | `iconNameRight`          | string (icon name)                                                                                                                                                                      | —                | Icon displayed to the right of the field |
| `required`               | `required`               | boolean                                                                                                                                                                                 | `false`          | Field is required for form submission    |
| `requiredTag`            | `requiredTag`            | boolean                                                                                                                                                                                 | —                | Show "Required" tag next to label        |
| `requiredText`           | `requiredText`           | string                                                                                                                                                                                  | `"Må fylles ut"` | Text in the required tag                 |
| `optionalTag`            | `optionalTag`            | boolean                                                                                                                                                                                 | —                | Show "Optional" tag next to label        |
| `optionalText`           | `optionalText`           | string                                                                                                                                                                                  | `"Valgfritt"`    | Text in the optional tag                 |
| `tagText`                | `tagText`                | string                                                                                                                                                                                  | —                | Custom tag text next to label            |
| `hasError`               | `hasError`               | boolean                                                                                                                                                                                 | —                | Field is in error state                  |
| `errorMessage`           | `errorMessage`           | string                                                                                                                                                                                  | —                | Error message shown below the field      |
| `disabled`               | `disabled`               | boolean                                                                                                                                                                                 | `false`          | Disables the field                       |
| `inline`                 | `inline`                 | boolean                                                                                                                                                                                 | `false`          | Display the field inline                 |
| `fullwidth`              | `fullwidth`              | boolean                                                                                                                                                                                 | `false`          | Field takes full width                   |
| `useWrapper`             | `useWrapper`             | boolean                                                                                                                                                                                 | `true`           | Show label, help text, and wrapper       |
| `autocomplete`           | `autocomplete`           | string                                                                                                                                                                                  | `"off"`          | HTML autocomplete attribute              |
| `counter`                | `counter`                | boolean                                                                                                                                                                                 | `false`          | Show character counter                   |
| `counterMaxLength`       | `counterMaxLength`       | number                                                                                                                                                                                  | —                | Maximum character count for the counter  |
| `omitSearchIcon`         | `omitSearchIcon`         | boolean                                                                                                                                                                                 | `false`          | Hide search icon when type is "search"   |
| `ariaLabelledby`         | `ariaLabelledby`         | string                                                                                                                                                                                  | —                | ID of an element that labels this field  |

## Events

| Event (React)      | Event (Elements) | Description                                                                     |
| ------------------ | ---------------- | ------------------------------------------------------------------------------- |
| `onChange`         | `change`         | Fires when the value changes. Returns the value as a string                     |
| `onToggleHelpText` | `toggleHelpText` | Fires when expandable help text is opened/closed. Detail: `{ isOpen: boolean }` |

## Accessibility

- Every field must have a label — either visible or hidden with `pkt-sr-only` class. The label must be connected to the field in code
- Use `aria-describedby` to connect help text and error messages to the field (handled automatically by the component wrapper)
- Use the correct `type` for better accessibility and appropriate mobile keyboard (`email`, `tel`, `password`, etc.)
- Set `autocomplete` for personal information fields; use `autocomplete="off"` when asking about someone other than the user
- Clickable prefix/suffix elements (e.g. show/hide password) must be keyboard-focusable and have a screen reader description
- Never rely on placeholder as the only instruction
- Allow input format variations (spaces in phone numbers, dots in national IDs, trailing spaces in email)
- Don't show error messages before the user has attempted to fill in the field

## Examples

### React

```jsx
import { PktTextinput } from '@oslokommune/punkt-react'

{
  /* Basic text input */
}
;<PktTextinput label="First name" name="firstName" id="firstName" />

{
  /* With help text and required tag */
}
;<PktTextinput
  label="Email"
  name="email"
  id="email"
  type="email"
  autocomplete="email"
  helptext="We'll use this to send you a confirmation"
  requiredTag
  required
/>

{
  /* With error state */
}
;<PktTextinput
  label="Phone number"
  name="phone"
  id="phone"
  type="tel"
  autocomplete="tel"
  hasError
  errorMessage="Please enter a valid phone number"
/>

{
  /* With prefix and suffix */
}
;<PktTextinput label="Phone" name="phone" id="phone-prefix" type="tel" prefix="+47" />

{
  /* With character counter */
}
;<PktTextinput label="Title" name="title" id="title" counter counterMaxLength={100} />
```

### Elements

```html
<pkt-textinput label="First name" name="firstName" id="firstName"></pkt-textinput>

<pkt-textinput
  label="Email"
  name="email"
  id="email"
  type="email"
  autocomplete="email"
  helptext="We'll use this to send you a confirmation"
  requiredTag
  required
></pkt-textinput>

<pkt-textinput
  label="Phone number"
  name="phone"
  id="phone"
  type="tel"
  hasError
  errorMessage="Please enter a valid phone number"
></pkt-textinput>
```
