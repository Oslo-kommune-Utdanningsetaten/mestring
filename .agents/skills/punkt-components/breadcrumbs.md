# Breadcrumbs

Breadcrumbs show the user where they are in the structure and make it possible to navigate back to a higher level. It helps the user understand the hierarchy and find their way back.

## Availability

| Package        | Available | Tag / Import                                                                     |
| -------------- | --------- | -------------------------------------------------------------------------------- |
| React          | Yes       | `<PktBreadcrumbs>` — `import { PktBreadcrumbs } from '@oslokommune/punkt-react'` |
| Elements       | No        | —                                                                                |
| Elements (CDN) | No        | —                                                                                |

Dark mode: Yes

## Usage guidelines

**Use breadcrumbs when:**

- The solution has a clear hierarchy
- You want to show the user where they are in the structure
- The user should be able to jump back to a higher level

**Avoid breadcrumbs when:**

- The hierarchy is shallow — use Backlink instead
- The user's path back is not clear
- Other navigation already covers the need

**Backlink vs Breadcrumbs:** Punkt supports both backlink and breadcrumbs. Be consistent — use only one. If your solution is used with Oslo municipality's public websites (www.oslo.kommune.no), always use backlink, never breadcrumbs.

**Content guidelines:**

- Each level should have a short, descriptive name
- Avoid technical or internal names (e.g. "/nav/root/sub/area")
- The component should be used with a maximum of 4 links

## Props / Attributes

| Prop (React)     | Type                                                                                                         | Default        | Description                                                                                                          |
| ---------------- | ------------------------------------------------------------------------------------------------------------ | -------------- | -------------------------------------------------------------------------------------------------------------------- |
| `breadcrumbs`    | `Array<{ text: string, href?: string }>`                                                                     | **(required)** | List of breadcrumb items. Each item needs `text`; `href` is optional (last item is typically the current page)       |
| `navigationType` | `"router"` \| `"anchor"`                                                                                     | `"anchor"`     | Navigation method — `"anchor"` for standard links, `"router"` for client-side routing                                |
| `renderLink`     | `(args: { href: string, className: string, children: ReactNode, props: AnchorHTMLAttributes }) => ReactNode` | —              | Custom link component (e.g. Next.js Link, Tanstack Router Link). When set, `navigationType` is implicitly `"router"` |

## Accessibility

- Link text must be clear and describe where the link goes
- Keyboard: navigate with Tab, activate with Enter. The component has a visible focus indicator
- Do not use breadcrumbs as the only way to navigate back — it should supplement the main navigation
- The last item in the trail (current page) is not clickable

## Examples

### React

```jsx
import { PktBreadcrumbs } from '@oslokommune/punkt-react'

{
  /* Basic breadcrumbs */
}
;<PktBreadcrumbs
  breadcrumbs={[
    { text: 'Home', href: '/' },
    { text: 'Services', href: '/services' },
    { text: 'Current page' },
  ]}
/>

{
  /* With React Router */
}
;<PktBreadcrumbs breadcrumbs={crumbs} navigationType="router" />

{
  /* With custom link component (e.g. Next.js) */
}
;<PktBreadcrumbs
  breadcrumbs={crumbs}
  renderLink={({ href, className, children }) => (
    <Link to={href} className={className}>
      {children}
    </Link>
  )}
/>
```

### HTML (with pkt-icon)

Breadcrumbs has no Elements/Web Component version, but you can build it with plain HTML using the CSS classes and `<pkt-icon>` for the separator icons. The component renders two views: a desktop list and a mobile back-link (CSS controls which is visible).

```html
<nav aria-label="brødsmulemeny" class="pkt-breadcrumbs">
  <!-- Desktop: full breadcrumb trail -->
  <ol class="pkt-breadcrumbs__list pkt-breadcrumbs--desktop">
    <li class="pkt-breadcrumbs__item">
      <a
        href="/"
        class="pkt-link pkt-link--icon-right pkt-breadcrumbs__label pkt-breadcrumbs__link"
      >
        <pkt-icon
          class="pkt-icon pkt-breadcrumbs__icon pkt-link__icon"
          name="chevron-thin-right"
        ></pkt-icon>
        <span class="pkt-breadcrumbs__text">Home</span>
      </a>
    </li>
    <li class="pkt-breadcrumbs__item">
      <a
        href="/services"
        class="pkt-link pkt-link--icon-right pkt-breadcrumbs__label pkt-breadcrumbs__link"
      >
        <pkt-icon
          class="pkt-icon pkt-breadcrumbs__icon pkt-link__icon"
          name="chevron-thin-right"
        ></pkt-icon>
        <span class="pkt-breadcrumbs__text">Services</span>
      </a>
    </li>
    <li class="pkt-breadcrumbs__item">
      <span class="pkt-breadcrumbs__label" aria-current="true">
        <span class="pkt-breadcrumbs__text">Current page</span>
      </span>
    </li>
  </ol>

  <!-- Mobile: back link to previous level -->
  <a href="/services" class="pkt-link pkt-link--icon-left pkt-breadcrumbs--mobile">
    <pkt-icon
      class="pkt-back-link__icon pkt-icon pkt-link__icon"
      name="chevron-thin-left"
    ></pkt-icon>
    <span class="pkt-breadcrumbs__text">Services</span>
  </a>
</nav>
```

Key points:

- The last item in the desktop list is a `<span>` with `aria-current="true"` (not a link)
- The mobile back-link points to the second-to-last item in the trail
- The icon is `chevron-thin-right` for desktop separators and `chevron-thin-left` for the mobile back-link
