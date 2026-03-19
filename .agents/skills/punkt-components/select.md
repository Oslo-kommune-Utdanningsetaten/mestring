# Select

Select lets the user choose one option from a dropdown list. It uses the native HTML `<select>` element under the hood, wrapped with Punkt's standard label, help text, and error handling.

## Availability

| Package        | Available | Tag / Import                                                                                   |
| -------------- | --------- | ---------------------------------------------------------------------------------------------- |
| React          | Yes       | `<PktSelect>` — `import { PktSelect } from '@oslokommune/punkt-react'`                         |
| Elements       | Yes       | `<pkt-select>` — `import '@oslokommune/punkt-elements/dist/pkt-select.js'`                     |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-select.js" type="module">` |

Dark mode: No

## Usage guidelines

**Use select when:**

- The user needs to choose one option from a predefined list
- There are more than 5–7 options (fewer options are better suited for Radio Button)

**Avoid select when:**

- The user can choose multiple options — use Combobox or Checkbox instead
- The user needs to search or filter — use Combobox instead
- There are very few options (2–4) — use Radio Button instead

## Props / Attributes

| Prop (React)             | Attribute (Elements)     | Type    | Default        | Description                                 |
| ------------------------ | ------------------------ | ------- | -------------- | ------------------------------------------- |
| `label`                  | `label`                  | string  | —              | Label displayed above the field             |
| `name`                   | `name`                   | string  | **(required)** | Form field name                             |
| `id`                     | `id`                     | string  | **(required)** | Unique identifier                           |
| `value`                  | `value`                  | string  | —              | Selected value                              |
| `helptext`               | `helptext`               | string  | —              | Help text below the label                   |
| `helptextDropdown`       | `helptextDropdown`       | string  | —              | Expandable help text content                |
| `helptextDropdownButton` | `helptextDropdownButton` | string  | —              | Button text for expandable help             |
| `hasError`               | `hasError`               | boolean | —              | Shows error state                           |
| `errorMessage`           | `errorMessage`           | string  | —              | Error message shown below the field         |
| `disabled`               | `disabled`               | boolean | `false`        | Disables the field                          |
| `inline`                 | `inline`                 | boolean | `false`        | Display inline with page content            |
| `fullwidth`              | `fullwidth`              | boolean | `false`        | Field takes full width                      |
| `requiredTag`            | `requiredTag`            | boolean | `false`        | Show "Required" tag next to label           |
| `requiredText`           | `requiredText`           | string  | —              | Text in the required tag                    |
| `optionalTag`            | `optionalTag`            | boolean | —              | Show "Optional" tag next to label           |
| `optionalText`           | `optionalText`           | string  | —              | Text in the optional tag                    |
| `tagText`                | `tagText`                | string  | —              | Custom tag text next to label               |
| `ariaDescribedBy`        | `ariaDescribedBy`        | string  | —              | ID of the element that describes this field |
| `ariaLabelledby`         | `ariaLabelledby`         | string  | —              | ID of the element that labels this field    |

## Slots

| Slot    | Description                        |
| ------- | ---------------------------------- |
| default | `<option>` elements for the select |

## Accessibility

- Always provide a label connected to the select field
- Use help text and error messages connected via `aria-describedby` (handled automatically by the wrapper)
- Keyboard: open with Enter/Space, navigate with arrow keys, select with Enter

## Examples

### React

```jsx
import { PktSelect } from '@oslokommune/punkt-react'

{
  /* Basic select */
}
;<PktSelect label="District" name="district" id="district">
  <option value="">Choose district...</option>
  <option value="frogner">Frogner</option>
  <option value="gamle-oslo">Gamle Oslo</option>
  <option value="grorud">Grorud</option>
</PktSelect>

{
  /* With error */
}
;<PktSelect
  label="Category"
  name="category"
  id="category"
  requiredTag
  hasError
  errorMessage="Please select a category"
>
  <option value="">Choose...</option>
  <option value="a">Category A</option>
  <option value="b">Category B</option>
</PktSelect>
```

### Elements

```html
<pkt-select label="District" name="district" id="district">
  <option value="">Choose district...</option>
  <option value="frogner">Frogner</option>
  <option value="gamle-oslo">Gamle Oslo</option>
  <option value="grorud">Grorud</option>
</pkt-select>
```
