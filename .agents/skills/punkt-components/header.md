# Header

Header shows the sender and helps the user navigate a solution or website. It provides recognition and predictability, helping the user understand where they are and what they can do. The header should be consistent across all pages in the same context.

**Note:** This documentation covers the **service header** only. The global header (for open public sites tied to oslo.kommune.no) is developed separately.

## Availability

| Package        | Available | Tag / Import                                                                                   |
| -------------- | --------- | ---------------------------------------------------------------------------------------------- |
| React          | Yes       | `<PktHeader>` — `import { PktHeader } from '@oslokommune/punkt-react'`                         |
| Elements       | Yes       | `<pkt-header>` — `import '@oslokommune/punkt-elements/dist/pkt-header.js'`                     |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-header.js" type="module">` |

Dark mode: Yes

## Variants

| Type           | Use                                                                                              |
| -------------- | ------------------------------------------------------------------------------------------------ |
| Global header  | For open sites tied to oslo.kommune.no — includes global navigation and global search            |
| Service header | For logged-in solutions and internal tools — shows logo, service name, navigation, and user menu |

## Usage guidelines

**Use service header when:**

- The solution is an internal tool or a logged-in service
- The user needs to see who they are logged in as
- The solution has local navigation or limited functionality
- The service is not part of oslo.kommune.no

**Use global header when:**

- The solution is part of open public websites
- Content is published and available without login
- The user expects global navigation and global search

**Do not mix** global and service header. Don't combine global navigation with local service navigation, and don't use global search in logged-in services.

## Props / Attributes

| Prop (React)              | Attribute (Elements)        | Type                                                                       | Default       | Description                                                                                  |
| ------------------------- | --------------------------- | -------------------------------------------------------------------------- | ------------- | -------------------------------------------------------------------------------------------- |
| `hideLogo`                | `hide-logo`                 | boolean                                                                    | `false`       | Hide the Oslo logo                                                                           |
| `logoLink`                | `logo-link`                 | string                                                                     | —             | URL for the logo. For a button, use `logoClick` instead                                      |
| `logoClick`               | —                           | function (React only)                                                      | —             | Callback when logo is clicked (React). For Elements, listen to `logo-click` event            |
| `serviceName`             | `service-name`              | string                                                                     | —             | Service name displayed in the header                                                         |
| `serviceLink`             | `service-link`              | string                                                                     | —             | URL for the service name                                                                     |
| `serviceClick`            | —                           | function (React only)                                                      | —             | Callback when service name is clicked (React). For Elements, listen to `service-click` event |
| `compact`                 | `compact`                   | boolean                                                                    | `false`       | Use compact header height                                                                    |
| `position`                | `position`                  | `"fixed"` \| `"relative"`                                                  | `"fixed"`     | Header positioning                                                                           |
| `scrollBehavior`          | `scroll-behavior`           | `"hide"` \| `"none"`                                                       | `"hide"`      | `"hide"` hides header on scroll down, `"none"` keeps it visible                              |
| `user`                    | `user`                      | `{ name: string, lastLoggedIn?: string \| Date }`                          | —             | Logged-in user info                                                                          |
| `userMenu`                | `user-menu`                 | `Array<{ title: string, iconName?: string, target?: string \| function }>` | —             | Menu items shown when user button is clicked                                                 |
| `representing`            | `representing`              | `{ name: string, orgNumber?: string \| number }`                           | —             | Organization being represented                                                               |
| `canChangeRepresentation` | `can-change-representation` | boolean                                                                    | `false`       | Show "Change organization" button                                                            |
| `logOutButtonPlacement`   | `log-out-button-placement`  | `"userMenu"` \| `"header"` \| `"both"` \| `"none"`                         | `"none"`      | Where to show the logout button                                                              |
| `showSearch`              | `show-search`               | boolean                                                                    | `false`       | Show search field in the header                                                              |
| `searchPlaceholder`       | `search-placeholder`        | string                                                                     | `"Søk"`       | Placeholder text in the search field                                                         |
| `searchValue`             | `search-value`              | string                                                                     | —             | Controlled value for the search field                                                        |
| `mobileBreakpoint`        | `mobile-breakpoint`         | number                                                                     | `768`         | Custom breakpoint for mobile appearance (pixels)                                             |
| `tabletBreakpoint`        | `tablet-breakpoint`         | number                                                                     | `1280`        | Custom breakpoint for tablet appearance (pixels)                                             |
| `openedMenu`              | `opened-menu`               | `"none"` \| `"slot"` \| `"search"` \| `"user"`                             | `"none"`      | Which menu is open on load                                                                   |
| `slotMenuVariant`         | `slot-menu-variant`         | `"icon-only"` \| `"icon-right"`                                            | `"icon-only"` | Menu button variant on tablet/mobile                                                         |
| `slotMenuText`            | `slot-menu-text`            | string                                                                     | `"Meny"`      | Menu button text on tablet/mobile                                                            |

## Events

| Event (React)          | Event (Elements)        | Description                                                      |
| ---------------------- | ----------------------- | ---------------------------------------------------------------- |
| `changeRepresentation` | `change-representation` | User changes the represented organization                        |
| `logOut`               | `log-out`               | User clicks the logout button                                    |
| `onSearch`             | `search`                | User submits search (presses Enter in search field)              |
| `onSearchChange`       | `search-change`         | User changes the search text                                     |
| `logoClick`            | `logo-click`            | User clicks the logo (Elements only — use prop in React)         |
| `serviceClick`         | `service-click`         | User clicks the service name (Elements only — use prop in React) |

## Navigation slot

The header supports slotted navigation content (links, buttons) displayed in the header bar on desktop and in a collapsible menu on tablet/mobile.

### React

Pass navigation as children:

```jsx
<PktHeader serviceName="My Service" logoLink="/">
  <PktLink href="/dashboard">Dashboard</PktLink>
  <PktLink href="/settings">Settings</PktLink>
</PktHeader>
```

### Elements

Use the default slot:

```html
<pkt-header service-name="My Service" logo-link="/">
  <pkt-link href="/dashboard">Dashboard</pkt-link>
  <pkt-link href="/settings">Settings</pkt-link>
</pkt-header>
```

## Accessibility

- The header must be consistent across all pages in the same context
- Keyboard: all interactive elements are focusable and activatable
- The user menu and navigation must be navigable with Tab and activatable with Enter/Space
- On mobile, the menu collapses into a hamburger menu accessible via keyboard
- Test the header at different screen sizes

## Examples

### React

```jsx
import { PktHeader } from '@oslokommune/punkt-react'

{
  /* Basic service header */
}
;<PktHeader serviceName="My Service" logoLink="/" serviceLink="/" />

{
  /* With logged-in user and menu */
}
;<PktHeader
  serviceName="My Service"
  logoLink="/"
  user={{ name: 'Ola Nordmann', lastLoggedIn: '2024-01-15T10:30:00' }}
  userMenu={[
    { title: 'My profile', iconName: 'user', target: '/profile' },
    { title: 'Settings', iconName: 'settings', target: '/settings' },
  ]}
  logOutButtonPlacement="userMenu"
  onLogOut={() => handleLogout()}
>
  <PktLink href="/dashboard">Dashboard</PktLink>
  <PktLink href="/reports">Reports</PktLink>
</PktHeader>

{
  /* With organization representation */
}
;<PktHeader
  serviceName="Admin Portal"
  logoLink="/"
  user={{ name: 'Kari Hansen' }}
  representing={{ name: 'Oslo Bygg AS', orgNumber: '123456789' }}
  canChangeRepresentation
  onChangeRepresentation={() => showOrgPicker()}
  logOutButtonPlacement="header"
  onLogOut={() => handleLogout()}
/>
```

### Elements

```html
<pkt-header
  service-name="My Service"
  logo-link="/"
  service-link="/"
  log-out-button-placement="header"
>
  <pkt-link href="/dashboard">Dashboard</pkt-link>
  <pkt-link href="/reports">Reports</pkt-link>
</pkt-header>

<script>
  const header = document.querySelector('pkt-header')
  header.user = { name: 'Ola Nordmann' }
  header.userMenu = [{ title: 'My profile', iconName: 'user', target: '/profile' }]
  header.addEventListener('log-out', () => handleLogout())
</script>
```

## Notes

For Elements, complex props like `user`, `userMenu`, and `representing` can be passed as JavaScript properties, as JSON strings in HTML attributes (Lit will `JSON.parse` them internally), or directly as objects in frameworks like Vue that bind to properties.

Header has a "placeholder" spacer element that ensures that even when fixed and hide on scroll it will take up space in a relative layout, so no need to set relative position even when placing in a layout flow, like in .pkt-layout css helper.
