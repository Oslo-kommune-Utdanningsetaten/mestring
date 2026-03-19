# Modal

Modal displays content in an overlay dialog or drawer that requires the user's attention. Use it for confirmations, detailed content, or actions that need focus without leaving the current page.

## Availability

| Package        | Available | Tag / Import                                                                                  |
| -------------- | --------- | --------------------------------------------------------------------------------------------- |
| React          | Yes       | `<PktModal>` — `import { PktModal } from '@oslokommune/punkt-react'`                          |
| Elements       | Yes       | `<pkt-modal>` — `import '@oslokommune/punkt-elements/dist/pkt-modal.js'`                      |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-modal.js" type="module">` |

Dark mode: No

## Variants

### Types

| Variant  | Use                                          |
| -------- | -------------------------------------------- |
| `dialog` | Centered overlay dialog (default)            |
| `drawer` | Side panel that slides in from left or right |

### Sizes

| Size               | Use                 |
| ------------------ | ------------------- |
| `small`            | Short confirmations |
| `medium` (default) | Standard dialogs    |
| `large`            | Detailed content    |

### Close button skins

| Skin            | Description          |
| --------------- | -------------------- |
| `blue`          | Default close button |
| `yellow-filled` | Yellow close button  |

## Usage guidelines

**Use modal when:**

- You need to display detailed content without taking the user out of context
- You need a confirmation before a destructive or important action
- You want the user to focus on a specific task or form

**Avoid modal when:**

- The content can be shown inline on the page
- You only need to show a short message — use Alert or Messagebox instead

## Props / Attributes

| Prop (React)           | Attribute (Elements)   | Type                                 | Default    | Description                                                  |
| ---------------------- | ---------------------- | ------------------------------------ | ---------- | ------------------------------------------------------------ |
| `headingText`          | `headingText`          | string                               | —          | Heading text for the modal                                   |
| `hideCloseButton`      | `hideCloseButton`      | boolean                              | `false`    | Hides the close button — provide an alternative way to close |
| `closeOnBackdropClick` | `closeOnBackdropClick` | boolean                              | `false`    | Close modal when clicking the backdrop                       |
| `closeButtonSkin`      | `closeButtonSkin`      | `"blue"` \| `"yellow-filled"`        | `"blue"`   | Style of the close button                                    |
| `size`                 | `size`                 | `"small"` \| `"medium"` \| `"large"` | `"medium"` | Modal size                                                   |
| `variant`              | `variant`              | `"dialog"` \| `"drawer"`             | `"dialog"` | Modal type                                                   |
| `drawerPosition`       | `drawerPosition`       | `"left"` \| `"right"`                | `"right"`  | Position of the drawer (when variant is `"drawer"`)          |
| `transparentBackdrop`  | `transparentBackdrop`  | boolean                              | `false`    | Make the backdrop transparent                                |
| `removePadding`        | `removePadding`        | boolean                              | `false`    | Remove inner padding from the modal content                  |

## Events

| Event (React)       | Event (Elements)   | Description                        |
| ------------------- | ------------------ | ---------------------------------- |
| `onClose`           | `close`            | Fires when the modal is closed     |
| `onBackgroundClick` | `background-click` | Fires when the backdrop is clicked |

## Slots

| Slot    | Description                                                            |
| ------- | ---------------------------------------------------------------------- |
| default | Modal content. CSS helper classes are provided for styling 1–3 buttons |

## Accessibility

- The modal traps focus when open — Tab cycles through focusable elements inside the modal
- Close the modal with Esc
- If `hideCloseButton` is true, you must provide an alternative way to close the modal
- The heading should be clear and descriptive

## Examples

### React

```jsx
import { PktModal, PktButton } from '@oslokommune/punkt-react'

{
  /* Confirmation dialog */
}
{
  isOpen && (
    <PktModal headingText="Delete item?" size="small" onClose={() => setIsOpen(false)}>
      <p>This action cannot be undone.</p>
      <div className="pkt-modal__buttons">
        <PktButton color="red" onClick={handleDelete}>
          Delete
        </PktButton>
        <PktButton skin="tertiary" onClick={() => setIsOpen(false)}>
          Cancel
        </PktButton>
      </div>
    </PktModal>
  )
}

{
  /* Drawer */
}
{
  drawerOpen && (
    <PktModal
      headingText="Filters"
      variant="drawer"
      drawerPosition="right"
      onClose={() => setDrawerOpen(false)}
    >
      <p>Filter options here.</p>
    </PktModal>
  )
}
```

### Elements

```html
<pkt-modal headingText="Delete item?" size="small">
  <p>This action cannot be undone.</p>
  <div class="pkt-modal__buttons">
    <pkt-button color="red"><span>Delete</span></pkt-button>
    <pkt-button skin="tertiary"><span>Cancel</span></pkt-button>
  </div>
</pkt-modal>
```
