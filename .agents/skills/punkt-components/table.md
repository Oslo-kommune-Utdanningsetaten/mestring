# Table

Table displays structured data in rows and columns. It can be used as a React compound component or with plain HTML and CSS classes.

## Availability

| Package  | Available | Tag / Import                                                                                                                           |
| -------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| React    | Yes       | `import { PktTable, PktTableHeader, PktTableHeaderCell, PktTableBody, PktTableRow, PktTableDataCell } from '@oslokommune/punkt-react'` |
| CSS only | Yes       | Apply `pkt-table` classes to standard `<table>` HTML                                                                                   |
| Elements | No        | —                                                                                                                                      |

Dark mode: No

## Sub-components (React)

| Component         | React                  | HTML equivalent | CSS class                |
| ----------------- | ---------------------- | --------------- | ------------------------ |
| Table             | `<PktTable>`           | `<table>`       | `pkt-table`              |
| Table Header      | `<PktTableHeader>`     | `<thead>`       | `pkt-table__header`      |
| Table Header Cell | `<PktTableHeaderCell>` | `<th>`          | `pkt-table__header-cell` |
| Table Body        | `<PktTableBody>`       | `<tbody>`       | `pkt-table__body`        |
| Table Row         | `<PktTableRow>`        | `<tr>`          | `pkt-table__row`         |
| Table Data Cell   | `<PktTableDataCell>`   | `<td>`          | `pkt-table__data-cell`   |

## CSS classes

| Class                     | Description                                         |
| ------------------------- | --------------------------------------------------- |
| `pkt-table`               | Base table class (required)                         |
| `pkt-table--basic`        | Default skin with bottom borders on rows            |
| `pkt-table--zebra-blue`   | Alternating blue background on odd rows             |
| `pkt-table--compact`      | Reduced padding                                     |
| `pkt-table--responsive`   | Enables responsive stacking on mobile (≤768px)      |
| `pkt-table__header`       | Header section (`<thead>`)                          |
| `pkt-table__header-cell`  | Header cell (`<th>`)                                |
| `pkt-table__body`         | Body section (`<tbody>`)                            |
| `pkt-table__row`          | Table row (`<tr>`)                                  |
| `pkt-table__data-cell`    | Data cell (`<td>`)                                  |
| `pkt-table__cell-wrapper` | Wrapper for multiple elements in a cell (e.g. tags) |

## Responsive view

When `pkt-table--responsive` is added to the table, cells stack vertically on screens ≤768px. Each cell shows a label from its `data-label` attribute next to the cell content in a two-column grid layout.

**Requirements for responsive to work:**

1. Add `pkt-table--responsive` class to the `<table>` (or set `responsiveView` prop in React — enabled by default)
2. Every `<td>` must have a `data-label` attribute matching its column header text
3. For cells with multiple inline elements (e.g. tags), wrap them in a `<span class="pkt-table__cell-wrapper">`

On mobile, headers are hidden and each row becomes a card-like block with label–value pairs.

## Props / Attributes — PktTable (React)

| Prop (React)     | Type                        | Default   | Description                          |
| ---------------- | --------------------------- | --------- | ------------------------------------ |
| `skin`           | `"basic"` \| `"zebra-blue"` | `"basic"` | Visual style                         |
| `compact`        | boolean                     | `false`   | Compact mode with less padding       |
| `responsiveView` | boolean                     | `true`    | Enable responsive stacking on mobile |

## Props / Attributes — PktTableDataCell (React)

| Prop (React) | Type   | Default | Description                                                 |
| ------------ | ------ | ------- | ----------------------------------------------------------- |
| `dataLabel`  | string | —       | Label shown on mobile — should match the column header text |

## Accessibility

- Use `<thead>`/`<th>` (or `PktTableHeader`/`PktTableHeaderCell`) for column headings — screen readers use these to announce cell context
- Add `role="table"` on the table and `role="row"` on rows for explicit semantics

## Examples

### React

```jsx
import {
  PktTable,
  PktTableHeader,
  PktTableHeaderCell,
  PktTableBody,
  PktTableRow,
  PktTableDataCell,
} from '@oslokommune/punkt-react'

{
  /* responsiveView is true by default — dataLabel is needed on each cell */
}
;<PktTable skin="basic">
  <PktTableHeader>
    <PktTableRow>
      <PktTableHeaderCell>Name</PktTableHeaderCell>
      <PktTableHeaderCell>Email</PktTableHeaderCell>
      <PktTableHeaderCell>Role</PktTableHeaderCell>
    </PktTableRow>
  </PktTableHeader>
  <PktTableBody>
    <PktTableRow>
      <PktTableDataCell dataLabel="Name">Ola Nordmann</PktTableDataCell>
      <PktTableDataCell dataLabel="Email">ola@example.com</PktTableDataCell>
      <PktTableDataCell dataLabel="Role">Admin</PktTableDataCell>
    </PktTableRow>
    <PktTableRow>
      <PktTableDataCell dataLabel="Name">Kari Hansen</PktTableDataCell>
      <PktTableDataCell dataLabel="Email">kari@example.com</PktTableDataCell>
      <PktTableDataCell dataLabel="Role">User</PktTableDataCell>
    </PktTableRow>
  </PktTableBody>
</PktTable>
```

### CSS only (HTML)

```html
<table class="pkt-table pkt-table--basic pkt-table--responsive">
  <thead class="pkt-table__header">
    <tr class="pkt-table__row" role="row">
      <th class="pkt-table__header-cell">Date</th>
      <th class="pkt-table__header-cell">Status</th>
      <th class="pkt-table__header-cell">Description</th>
      <th class="pkt-table__header-cell">Reviewed by</th>
    </tr>
  </thead>
  <tbody class="pkt-table__body">
    <tr class="pkt-table__row" role="row">
      <td class="pkt-table__data-cell" data-label="Date">19.01.2023 08:08</td>
      <td class="pkt-table__data-cell" data-label="Status">
        <span class="pkt-table__cell-wrapper">
          <span class="pkt-tag pkt-tag--thin-text pkt-tag--yellow">Normal</span>
        </span>
      </td>
      <td class="pkt-table__data-cell" data-label="Description">Summary of the item</td>
      <td class="pkt-table__data-cell" data-label="Reviewed by">Ola Nordmann</td>
    </tr>
  </tbody>
</table>
```

The BEM classes (`pkt-table__header`, `pkt-table__row`, etc.) are optional — the CSS also targets standard `<thead>`, `<tr>`, `<th>`, `<td>` elements within `.pkt-table`. A minimal CSS-only table can use just the base class:

```html
<table class="pkt-table pkt-table--zebra-blue pkt-table--compact">
  <thead>
    <tr>
      <th>Column A</th>
      <th>Column B</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Column A">Value 1</td>
      <td data-label="Column B">Value 2</td>
    </tr>
  </tbody>
</table>
```
