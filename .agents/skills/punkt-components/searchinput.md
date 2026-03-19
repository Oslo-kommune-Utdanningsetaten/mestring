# Search Input

> **Recommendation:** For most search use cases, use [`<PktTextinput>`](textinput.md) with `type="search"` instead. It provides the same native search affordances (clear button, search icon) with less overhead. Use SearchInput only when you need built-in autocomplete suggestions or the `global` appearance.

Search Input provides a search field with optional autocomplete suggestions. It comes in different appearances for local in-page search and global site-wide search.

## Availability

| Package        | Available | Tag / Import                                                                     |
| -------------- | --------- | -------------------------------------------------------------------------------- |
| React          | Yes       | `<PktSearchInput>` — `import { PktSearchInput } from '@oslokommune/punkt-react'` |
| Elements       | No        | —                                                                                |
| Elements (CDN) | No        | —                                                                                |

Dark mode: No

## Variants

| Appearance          | Use                                           |
| ------------------- | --------------------------------------------- |
| `local` (default)   | In-page search, simple field with search icon |
| `local-with-button` | In-page search with a visible search button   |
| `global`            | Full-width search bar for site-wide search    |

## Props / Attributes

| Prop (React)  | Type                                                     | Default        | Description                                      |
| ------------- | -------------------------------------------------------- | -------------- | ------------------------------------------------ |
| `name`        | string                                                   | **(required)** | Form field name                                  |
| `id`          | string                                                   | **(required)** | Unique identifier                                |
| `appearance`  | `"local"` \| `"local-with-button"` \| `"global"`         | `"local"`      | Visual appearance                                |
| `placeholder` | string                                                   | —              | Hint text shown when empty                       |
| `value`       | string                                                   | —              | Controlled value                                 |
| `label`       | string                                                   | —              | Label for the search field                       |
| `disabled`    | boolean                                                  | `false`        | Disables the field                               |
| `fullwidth`   | boolean                                                  | `false`        | Field takes full width                           |
| `action`      | string                                                   | —              | Form action URL                                  |
| `suggestions` | `Array<{ title: string, text?: string, href?: string }>` | `[]`           | Autocomplete suggestions displayed in a dropdown |

## Events

| Event (React)       | Description                                    |
| ------------------- | ---------------------------------------------- |
| `onChange`          | Fires when the search value changes            |
| `onSearch`          | Fires when the user submits the search (Enter) |
| `onSuggestionClick` | Fires when a suggestion is clicked             |

## Examples

### React

```jsx
import { PktSearchInput } from '@oslokommune/punkt-react'

{
  /* Basic local search */
}
;<PktSearchInput
  name="search"
  id="search"
  placeholder="Search..."
  onSearch={(value) => handleSearch(value)}
/>

{
  /* With search button */
}
;<PktSearchInput
  name="search"
  id="search-btn"
  appearance="local-with-button"
  placeholder="Search..."
  onSearch={(value) => handleSearch(value)}
/>

{
  /* With suggestions */
}
;<PktSearchInput
  name="search"
  id="search-suggest"
  placeholder="Search cities..."
  suggestions={[
    { title: 'Oslo', text: 'Capital of Norway' },
    { title: 'Bergen', text: 'Western capital' },
    { title: 'Trondheim', text: 'Technology hub' },
  ]}
  onChange={(value) => updateSuggestions(value)}
  onSuggestionClick={(suggestion) => navigate(suggestion.href)}
/>

{
  /* Global search */
}
;<PktSearchInput
  name="global-search"
  id="global-search"
  appearance="global"
  placeholder="Search the site..."
  fullwidth
/>
```
