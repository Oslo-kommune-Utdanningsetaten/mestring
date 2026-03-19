# Textarea

Textarea lets the user type longer free-form text, typically in forms. Use it when the expected input spans multiple lines, such as descriptions, comments, or messages.

## Availability

| Package        | Available | Tag / Import                                                                                     |
| -------------- | --------- | ------------------------------------------------------------------------------------------------ |
| React          | Yes       | `<PktTextarea>` — `import { PktTextarea } from '@oslokommune/punkt-react'`                       |
| Elements       | Yes       | `<pkt-textarea>` — `import '@oslokommune/punkt-elements/dist/pkt-textarea.js'`                   |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-textarea.js" type="module">` |

Dark mode: No

## Usage guidelines

**Use textarea when:**

- The user needs to enter multi-line text (descriptions, comments, messages)

**Avoid textarea when:**

- The expected input is short and fits on one line — use Text Input instead

**Content guidelines:**

- Keep labels short and precise
- Use help text to explain requirements (e.g. max length, expected format)
- Never rely on placeholder as the only instruction

## Props / Attributes

| Prop (React)             | Attribute (Elements)     | Type    | Default          | Description                             |
| ------------------------ | ------------------------ | ------- | ---------------- | --------------------------------------- |
| `label`                  | `label`                  | string  | —                | Label displayed above the field         |
| `name`                   | `name`                   | string  | **(required)**   | Form field name                         |
| `id`                     | `id`                     | string  | **(required)**   | Unique identifier                       |
| `value`                  | `value`                  | string  | —                | Current value                           |
| `placeholder`            | `placeholder`            | string  | —                | Hint text shown when empty              |
| `rows`                   | `rows`                   | number  | —                | Number of visible text rows             |
| `helptext`               | `helptext`               | string  | —                | Help text below the label               |
| `helptextDropdown`       | `helptextDropdown`       | string  | —                | Expandable help text content            |
| `helptextDropdownButton` | `helptextDropdownButton` | string  | `"Les mer"`      | Button text for expandable help         |
| `autocomplete`           | `autocomplete`           | string  | `"off"`          | HTML autocomplete attribute             |
| `ariaLabelledby`         | `ariaLabelledby`         | string  | —                | ID of an element that labels this field |
| `required`               | `required`               | boolean | `false`          | Field is required for form submission   |
| `requiredTag`            | `requiredTag`            | boolean | —                | Show "Required" tag next to label       |
| `requiredText`           | `requiredText`           | string  | `"Må fylles ut"` | Text in the required tag                |
| `optionalTag`            | `optionalTag`            | boolean | —                | Show "Optional" tag next to label       |
| `optionalText`           | `optionalText`           | string  | `"Valgfritt"`    | Text in the optional tag                |
| `tagText`                | `tagText`                | string  | —                | Custom tag text next to label           |
| `hasError`               | `hasError`               | boolean | —                | Shows error state                       |
| `errorMessage`           | `errorMessage`           | string  | —                | Error message shown below the field     |
| `disabled`               | `disabled`               | boolean | `false`          | Disables the field                      |
| `inline`                 | `inline`                 | boolean | `false`          | Display inline with page content        |
| `fullwidth`              | `fullwidth`              | boolean | `false`          | Field takes full width                  |
| `useWrapper`             | `useWrapper`             | boolean | `true`           | Show label, help text, and wrapper      |
| `counter`                | `counter`                | boolean | `false`          | Show character counter                  |
| `counterMaxLength`       | `counterMaxLength`       | number  | —                | Maximum character count for the counter |

## Accessibility

- Every textarea must have a label connected to the field in code
- Use `aria-describedby` to connect help text and error messages (handled automatically by the wrapper)
- Set `autocomplete` for fields where it applies
- Never rely on placeholder as the only instruction

## Examples

### React

```jsx
import { PktTextarea } from '@oslokommune/punkt-react'

{
  /* Basic textarea */
}
;<PktTextarea
  label="Description"
  name="description"
  id="description"
  rows={5}
  helptext="Write a brief description of your request"
/>

{
  /* With character counter */
}
;<PktTextarea
  label="Comment"
  name="comment"
  id="comment"
  counter
  counterMaxLength={500}
  requiredTag
  required
/>

{
  /* With error */
}
;<PktTextarea
  label="Message"
  name="message"
  id="message"
  hasError
  errorMessage="Please enter a message"
/>
```

### Elements

```html
<pkt-textarea
  label="Description"
  name="description"
  id="description"
  rows="5"
  helptext="Write a brief description of your request"
></pkt-textarea>

<pkt-textarea
  label="Comment"
  name="comment"
  id="comment"
  counter
  counterMaxLength="500"
  requiredTag
  required
></pkt-textarea>
```
