# Combobox

Combobox (multiselect) combines a text field with a dropdown list. It lets the user search by typing text (to filter options), select one or more items from a predefined list, and optionally add custom values. Useful when there are many options to choose from.

## Availability

| Package        | Available | Tag / Import                                                                                     |
| -------------- | --------- | ------------------------------------------------------------------------------------------------ |
| React          | Yes       | `<PktCombobox>` — `import { PktCombobox } from '@oslokommune/punkt-react'`                       |
| Elements       | Yes       | `<pkt-combobox>` — `import '@oslokommune/punkt-elements/dist/pkt-combobox.js'`                   |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-combobox.js" type="module">` |

Dark mode: No

## Variants

| Type          | Use                              |
| ------------- | -------------------------------- |
| Single select | User can choose only one option  |
| Multi select  | User can choose multiple options |

When using multi select, selected values appear as tags. Tags can be placed inside or outside the field via `tagPlacement`.

## Usage guidelines

**Use combobox when:**

- The user has many options and can select more than one
- You want the user to search or filter options
- The user should be able to enter free text

**Avoid combobox when:**

- There are fewer than 3 options — use Checkbox or Radio Button instead
- It's important that the user only chooses from a fixed list — use Select
- Only search is needed — use Search Input instead

**Content guidelines:**

- Write clear, descriptive labels and help text
- Explain rules like max selections or free text input in the help text
- If you allow custom values, explain how the user should use the component

## Props / Attributes

| Prop (React)             | Attribute (Elements)       | Type                                         | Default     | Description                                          |
| ------------------------ | -------------------------- | -------------------------------------------- | ----------- | ---------------------------------------------------- |
| `name`                   | `name`                     | string                                       | —           | Form field name                                      |
| `id`                     | `id`                       | string                                       | —           | Unique identifier                                    |
| `label`                  | `label`                    | string                                       | —           | Label displayed above the field                      |
| `placeholder`            | `placeholder`              | string                                       | —           | Hint text shown when empty                           |
| `multiple`               | `multiple`                 | boolean                                      | `false`     | Allow selecting multiple options                     |
| `tagPlacement`           | `tag-placement`            | `"inside"` \| `"outside"`                    | —           | Where selected tags appear in multi select           |
| `maxlength`              | `maxlength`                | number                                       | —           | Max number of selections in multi select             |
| `typeahead`              | `typeahead`                | boolean                                      | `false`     | Auto-complete from the options list                  |
| `includeSearch`          | `include-search`           | boolean                                      | —           | Include a search field inside the dropdown           |
| `searchPlaceholder`      | `search-placeholder`       | string                                       | —           | Placeholder text for the search field in dropdown    |
| `allowUserInput`         | `allow-user-input`         | boolean                                      | —           | Allow the user to add custom values                  |
| `displayValueAs`         | `display-value-as`         | `"label"` \| `"value"` \| `"prefixAndValue"` | `"label"`   | How the selected value is displayed                  |
| `value`                  | `value`                    | string                                       | —           | Selected value (string for single, array for multi)  |
| `helptext`               | `helptext`                 | string                                       | —           | Help text below the label                            |
| `helptextDropdown`       | `helptextdropdown`         | string                                       | —           | Expandable help text content                         |
| `helptextDropdownButton` | `helptextdropdownbutton`   | string                                       | `"Les mer"` | Button text for expandable help                      |
| `disabled`               | `disabled`                 | boolean                                      | —           | Disables the field                                   |
| `hasError`               | `haserror`                 | boolean                                      | —           | Shows error state                                    |
| `errorMessage`           | `errormessage`             | string                                       | —           | Error message shown below the field                  |
| `required`               | `required`                 | boolean                                      | —           | Field is required                                    |
| `requiredTag`            | `requiredtag`              | boolean                                      | —           | Show "Required" tag next to label                    |
| `requiredText`           | `requiredtext`             | string                                       | —           | Text in the required tag                             |
| `optionalTag`            | `optionaltag`              | boolean                                      | —           | Show "Optional" tag next to label                    |
| `optionalText`           | `optionaltext`             | string                                       | —           | Text in the optional tag                             |
| `tagText`                | `tagtext`                  | string                                       | —           | Custom tag text next to label                        |
| `fullwidth`              | `fullwidth`                | boolean                                      | —           | Field takes full width                               |
| `defaultOptions`         | `default-options`          | `Array<OptionObject>`                        | `[]`        | Initial options list (not modified by the component) |
| `options`                | `options`                  | `Array<OptionObject>`                        | `[]`        | Current options list                                 |

### Option object shape

```ts
{
  value: string           // Value submitted on selection (required)
  label?: string          // Display text
  prefix?: string         // Text shown before the label
  description?: string    // Description of the option
  disabled?: boolean      // Option is disabled
  selected?: boolean      // Option is pre-selected
  tagSkinColor?: string   // Tag color: "blue" | "blue-dark" | "blue-light" | "green" | "red" | "yellow" | "beige" | "gray"
}
```

## Accessibility

- All fields must have a label — visible or hidden with `pkt-sr-only`
- Labels must be connected to the field in code so screen readers read the correct information
- Error messages must be visible text that identifies the specific field where the error occurred
- Use single-column layout for form elements
- Test that tags in multi select don't become visually overwhelming on small screens

## Examples

### React

```jsx
import { PktCombobox } from '@oslokommune/punkt-react'

{/* Single select (multiple defaults to false) */}
<PktCombobox
  label="District"
  name="district"
  id="district"
  options={[
    { value: 'frogner', label: 'Frogner' },
    { value: 'gamle-oslo', label: 'Gamle Oslo' },
    { value: 'grorud', label: 'Grorud' },
  ]}
/>

{/* Multi select with max 3 */}
<PktCombobox
  label="Choose districts"
  name="districts"
  id="districts-multi"
  multiple
  maxlength={3}
  helptext="Select up to 3 districts"
  options={[
    { value: 'frogner', label: 'Frogner' },
    { value: 'gamle-oslo', label: 'Gamle Oslo' },
    { value: 'grorud', label: 'Grorud' },
    { value: 'other', label: 'Other districts' },
  ]}
/>

{/* With custom user input allowed */}
<PktCombobox
  label="Tags"
  name="tags"
  id="tags"
  allowUserInput
  helptext="Select from the list or type to add your own"
  options={existingTags}
/>
```

### Elements

```html
<!-- Single select (multiple defaults to false) -->
<pkt-combobox label="District" name="district" id="district"></pkt-combobox>

<!-- Multi select with search -->
<pkt-combobox
  label="Choose districts"
  name="districts"
  id="districts-multi"
  multiple
  include-search
  search-placeholder="Search..."
></pkt-combobox>

<script>
  document.querySelectorAll('pkt-combobox').forEach((combobox) => {
    combobox.options = [
      { value: 'frogner', label: 'Frogner' },
      { value: 'gamle-oslo', label: 'Gamle Oslo' },
      { value: 'grorud', label: 'Grorud' },
    ]
  })
</script>
```

## Notes

For Elements, array/object props like `options` and `defaultOptions` can be passed as JavaScript properties, as JSON strings in HTML attributes (Lit will `JSON.parse` them internally), or directly as objects in frameworks like Vue that bind to properties.
