# Input Wrapper

Input Wrapper provides the standard label, help text, error messages, character counter, and optional/required tags around a form element. Most Punkt form components (Text Input, Textarea, Select, etc.) use Input Wrapper internally via the `useWrapper` prop. Use it directly when wrapping custom or third-party form elements.

## Availability

| Package        | Available | Tag / Import                                                                                          |
| -------------- | --------- | ----------------------------------------------------------------------------------------------------- |
| React          | Yes       | `<PktInputWrapper>` — `import { PktInputWrapper } from '@oslokommune/punkt-react'`                    |
| Elements       | Yes       | `<pkt-input-wrapper>` — `import '@oslokommune/punkt-elements/dist/pkt-input-wrapper.js'`              |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-input-wrapper.js" type="module">` |

Dark mode: No

## Usage guidelines

**Use Input Wrapper when:**

- You're wrapping a custom or third-party form element that needs standard Punkt labels, help text, and error messages
- You need a `fieldset`/`legend` wrapper for a group of checkboxes or radio buttons

**You usually don't need to use it directly** because Punkt form components (Text Input, Textarea, Select, Datepicker, etc.) include it via the `useWrapper` prop (enabled by default).

## Props / Attributes

| Prop (React)             | Attribute (Elements)     | Type                  | Default          | Description                                                   |
| ------------------------ | ------------------------ | --------------------- | ---------------- | ------------------------------------------------------------- |
| `forId`                  | `forId`                  | string                | **(required)**   | ID of the form element being wrapped                          |
| `label`                  | `label`                  | string                | **(required)**   | Label text for the form element                               |
| `helptext`               | `helptext`               | string                | —                | Help text below the label                                     |
| `helptextDropdown`       | `helptextDropdown`       | string                | —                | Expandable help text content                                  |
| `helptextDropdownButton` | `helptextDropdownButton` | string                | `"Les mer"`      | Button text for expandable help                               |
| `ariaDescribedby`        | `ariaDescribedby`        | string                | —                | ID of the element that describes the form element             |
| `counter`                | `counter`                | boolean               | `false`          | Show character counter                                        |
| `counterCurrent`         | `counterCurrent`         | number                | —                | Current character count                                       |
| `counterMaxLength`       | `counterMaxLength`       | number                | —                | Maximum character count                                       |
| `counterPosition`        | `counterPosition`        | `"top"` \| `"bottom"` | `"bottom"`       | Position of the counter                                       |
| `optionalTag`            | `optionalTag`            | boolean               | `false`          | Show "Optional" tag next to label                             |
| `optionalText`           | `optionalText`           | string                | `"Valgfritt"`    | Text in the optional tag                                      |
| `requiredTag`            | `requiredTag`            | boolean               | `false`          | Show "Required" tag next to label                             |
| `requiredText`           | `requiredText`           | string                | `"Må fylles ut"` | Text in the required tag                                      |
| `tagText`                | `tagText`                | string                | —                | Custom tag text next to label                                 |
| `hasError`               | `hasError`               | boolean               | `false`          | Shows error state                                             |
| `errorMessage`           | `errorMessage`           | string                | —                | Error message shown below the field                           |
| `disabled`               | `disabled`               | boolean               | `false`          | Disables the wrapper (visual state)                           |
| `inline`                 | `inline`                 | boolean               | `false`          | Display inline with page content                              |
| `hasFieldset`            | `hasFieldset`            | boolean               | `false`          | Render as a `fieldset` with `legend` instead of `div`/`label` |
| `useWrapper`             | `useWrapper`             | boolean               | `true`           | Enable/disable the wrapper                                    |
| `role`                   | `role`                   | string                | `"group"`        | ARIA role for the wrapper element                             |

## Events

| Event (React)      | Event (Elements) | Description                                                         |
| ------------------ | ---------------- | ------------------------------------------------------------------- |
| `onToggleHelpText` | `toggleHelpText` | Fires when expandable help text opens/closes. `{ isOpen: boolean }` |

## Slots

| Slot    | Description                                   |
| ------- | --------------------------------------------- |
| default | The form element or group of elements to wrap |

## Accessibility

- The label is automatically connected to the form element via `forId`
- Help text and error messages are connected via `aria-describedby` (handled automatically)
- Use `hasFieldset` when wrapping groups of checkboxes or radio buttons — renders a `fieldset` with `legend` for proper screen reader grouping
- Error messages should be specific and explain how to fix the issue

## Examples

### React

```jsx
import { PktInputWrapper } from '@oslokommune/punkt-react'

{
  /* Wrapping a custom input */
}
;<PktInputWrapper forId="custom-field" label="Custom field" helptext="Enter a value" requiredTag>
  <input type="text" id="custom-field" name="custom-field" />
</PktInputWrapper>

{
  /* Fieldset for a checkbox group */
}
;<PktInputWrapper
  forId="colors"
  label="Choose colors"
  hasFieldset
  hasError={hasError}
  errorMessage="Please select at least one color"
>
  <PktCheckbox label="Red" name="color" id="color-red" value="red" />
  <PktCheckbox label="Blue" name="color" id="color-blue" value="blue" />
  <PktCheckbox label="Green" name="color" id="color-green" value="green" />
</PktInputWrapper>
```

### Elements

```html
<pkt-input-wrapper forId="custom-field" label="Custom field" helptext="Enter a value">
  <input type="text" id="custom-field" name="custom-field" />
</pkt-input-wrapper>
```
