# Accordion

Accordion (also called expandable or collapsible panel) groups content that can be opened and closed. It helps users get an overview and focus on one thing at a time. Suitable when you have a lot of information but don't want to overwhelm the user.

## Availability

| Package        | Available | Tag / Import                                                                                                          |
| -------------- | --------- | --------------------------------------------------------------------------------------------------------------------- |
| React          | Yes       | `<PktAccordion>` + `<PktAccordionItem>` — `import { PktAccordion, PktAccordionItem } from '@oslokommune/punkt-react'` |
| Elements       | Yes       | `<pkt-accordion>` + `<pkt-accordion-item>` — `import '@oslokommune/punkt-elements/dist/pkt-accordion.js'`             |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-accordion.js" type="module">`                     |

Dark mode: Yes

## Variants

### Types

| Type              | Description                                                      |
| ----------------- | ---------------------------------------------------------------- |
| Standard          | Multiple rows can be open simultaneously                         |
| Single (one open) | Only one panel open at a time — useful for step-by-step guidance |

Single mode requires manual state management (see examples below).

### Sizes

| Size    | Description                                                     |
| ------- | --------------------------------------------------------------- |
| Default | Standard size, better readability                               |
| Compact | Saves space, good when accordion sits among many other elements |

Set compact mode with the `compact` prop/attribute (boolean).

### Skins

| Skin                   | Description                       |
| ---------------------- | --------------------------------- |
| `borderless` (default) | Simple background color and style |
| `outlined`             | Border on the rows                |
| `beige`                | Alternating beige rows            |
| `blue`                 | Alternating blue rows             |

## Usage guidelines

**Use accordion when:**

- You want to present a lot of information without overwhelming the user
- The user doesn't need to read everything to understand the whole picture
- You have related topics that can be grouped together

**Avoid accordion when:**

- All content must be read together to understand the whole
- You need more complex interactivity — use Modal or Tabs instead

**Content guidelines:**

- Titles must be short, descriptive, and cover a single topic — the user should understand what's behind each row without opening it
- Content should be 1–2 short sentences maximum; if longer, consider a separate page
- All items in an accordion should be logically related

## Props / Attributes

### PktAccordion

| Prop (React)     | Attribute (Elements) | Type                                                    | Default        | Description                                  |
| ---------------- | -------------------- | ------------------------------------------------------- | -------------- | -------------------------------------------- |
| `skin`           | `skin`               | `"borderless"` \| `"outlined"` \| `"beige"` \| `"blue"` | `"borderless"` | Visual style                                 |
| `compact`        | `compact`            | boolean                                                 | `false`        | Compact mode with less padding               |
| `ariaLabelledBy` | `ariaLabelledBy`     | string                                                  | —              | ID of the element that labels this accordion |
| `name`           | `name`               | string                                                  | —              | Group name for the accordion                 |

### PktAccordionItem

| Prop (React)  | Attribute (Elements) | Type    | Default        | Description                                      |
| ------------- | -------------------- | ------- | -------------- | ------------------------------------------------ |
| `title`       | `title`              | string  | —              | Title displayed in the row summary               |
| `id`          | `id`                 | string  | **(required)** | Unique ID for this item                          |
| `defaultOpen` | `defaultOpen`        | boolean | `false`        | Item is open when the page loads                 |
| `isOpen`      | `isOpen`             | boolean | —              | Controlled open state (overrides internal state) |
| `name`        | `name`               | string  | —              | Group name for grouping items together           |

### Events

#### PktAccordionItem

| Event (React) | Event (Elements) | Description                            |
| ------------- | ---------------- | -------------------------------------- |
| `onClick`     | `click`          | Fires when the item summary is clicked |

## Slots

| Component        | Slot    | Description                             |
| ---------------- | ------- | --------------------------------------- |
| PktAccordion     | default | AccordionItem children                  |
| PktAccordionItem | default | Content shown when the item is expanded |

## Accessibility

- Built on semantic `<details>` and `<summary>` HTML elements
- Keyboard: navigate between rows with Tab / Shift+Tab, open/close with Enter or Space
- Clear visual focus indicator and open/closed state
- Use `ariaLabelledBy` to connect the accordion to a heading that describes the group

## Examples

### React — standard (multiple open)

```jsx
import { PktAccordion, PktAccordionItem } from '@oslokommune/punkt-react'
;<PktAccordion skin="borderless">
  <PktAccordionItem id="item-1" title="What is Punkt?">
    Punkt is Oslo municipality's design system.
  </PktAccordionItem>
  <PktAccordionItem id="item-2" title="How do I get started?">
    Install the packages from NPM and follow the documentation.
  </PktAccordionItem>
</PktAccordion>
```

### React — single open (controlled)

```jsx
const [openedItem, setOpenedItem] = useState('')

const toggleItem = (e, id) => {
  if (openedItem === id) {
    setOpenedItem('')
  } else {
    setOpenedItem(id)
  }
}

;<PktAccordion compact skin="borderless">
  {items.map((item) => (
    <PktAccordionItem
      key={item.id}
      id={item.id}
      title={item.title}
      isOpen={openedItem === item.id}
      onClick={(e) => toggleItem(e, item.id)}
    >
      {item.content}
    </PktAccordionItem>
  ))}
</PktAccordion>
```

Note: In React, the component internally calls `e.preventDefault()` to prevent the native `<details>` toggle from conflicting with controlled state.

### Elements — standard

```html
<pkt-accordion skin="blue">
  <pkt-accordion-item id="item-1" title="What is Punkt?">
    <p>Punkt is Oslo municipality's design system.</p>
  </pkt-accordion-item>
  <pkt-accordion-item id="item-2" title="How do I get started?">
    <p>Install the packages from NPM and follow the documentation.</p>
  </pkt-accordion-item>
</pkt-accordion>
```

### Elements — single open (controlled)

For single-open mode in Elements, manage state and bind `isOpen` and a click handler:

```js
// In a Lit component or similar
@state() private openedItem = '';

toggleCurrentOpenItem(e, id) {
  e.preventDefault();
  this.openedItem = this.openedItem === id ? '' : id;
}
```

```html
<pkt-accordion skin="blue">
  <pkt-accordion-item
    id="item-1"
    title="First item"
    .isOpen="${this.openedItem"
    =""
    =""
    ="item-1"
    }
    @click="${(e)"
    =""
  >
    this.toggleCurrentOpenItem(e, 'item-1')} >
    <p>Content for first item.</p>
  </pkt-accordion-item>
</pkt-accordion>
```
