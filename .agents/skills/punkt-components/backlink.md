# Backlink

Backlink (back link) helps the user understand where they are and provides a simple way to navigate back to the previous step in the structure. It contributes to better overview and predictability, especially on sub-pages or when navigating deep in a hierarchy.

## Availability

| Package        | Available | Tag / Import                                                                                     |
| -------------- | --------- | ------------------------------------------------------------------------------------------------ |
| React          | Yes       | `<PktBackLink>` — `import { PktBackLink } from '@oslokommune/punkt-react'`                       |
| Elements       | Yes       | `<pkt-backlink>` — `import '@oslokommune/punkt-elements/dist/pkt-backlink.js'`                   |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-backlink.js" type="module">` |

Dark mode: Yes

## Usage guidelines

**Use backlink when:**

- The user has navigated from a list or overview page
- You don't use breadcrumbs but need local back-navigation
- You want to reinforce the information hierarchy on the page

**Avoid backlink when:**

- Other navigation already covers the same need (e.g. the top menu)
- The user's path back is not clear or obvious
- You don't know which way back makes sense

**Backlink vs Breadcrumbs:** Punkt supports both backlink and breadcrumbs as navigation patterns. Be consistent in your solution — use only one. If your solution is used together with Oslo municipality's public websites (www.oslo.kommune.no), always use backlink, never breadcrumbs.

**Content guidelines:**

- The link text should describe where the user will go — avoid vague text like just "Back"
- Good examples: "Back to overview", "Back to search results"

## Props / Attributes

| Prop (React) | Attribute (Elements) | Type   | Default                         | Description                                     |
| ------------ | -------------------- | ------ | ------------------------------- | ----------------------------------------------- |
| `href`       | `href`               | string | `"/"`                           | URL the link points to                          |
| `text`       | `text`               | string | `"Forsiden"`                    | Text displayed in the back link                 |
| `ariaLabel`  | `ariaLabel`          | string | `"Gå tilbake til forrige side"` | Text read by screen readers for the nav element |

## Events

| Event (React) | Event (Elements) | Description                         |
| ------------- | ---------------- | ----------------------------------- |
| `onClick`     | —                | Fires when the back link is clicked |

## Accessibility

- The link text must make sense on its own — describe where the link goes
- Keyboard: navigate with Tab, activate with Enter. The component has a visible focus indicator
- Do not use backlink as the only way to navigate back — it should supplement, not replace, the main navigation

## Examples

### React

```jsx
import { PktBackLink } from '@oslokommune/punkt-react'

{
  /* Basic backlink */
}
;<PktBackLink href="/overview" text="Back to overview" />

{
  /* With click handler (e.g. for router navigation) */
}
;<PktBackLink
  text="Back to search results"
  onClick={(e) => {
    e.preventDefault()
    navigate('/search')
  }}
/>
```

### Elements

```html
<pkt-backlink href="/overview" text="Back to overview"></pkt-backlink>
```
