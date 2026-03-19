# Tabs

Tabs organize content into separate views where only one tab panel is visible at a time. Use them for switching between related sections without navigating to a new page. Tabs can also be used as a navigation menu with links.

## Availability

| Package        | Available | Tag / Import                                                                                    |
| -------------- | --------- | ----------------------------------------------------------------------------------------------- |
| React          | Yes       | `<PktTabs>` + `<PktTabItem>` — `import { PktTabs, PktTabItem } from '@oslokommune/punkt-react'` |
| Elements       | Yes       | `<pkt-tabs>` + `<pkt-tab-item>` — `import '@oslokommune/punkt-elements/dist/pkt-tabs.js'`       |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-tabs.js" type="module">`    |

Dark mode: No

## Usage

There are two ways to define tabs:

1. **Slot-based (recommended):** Use `<PktTabItem>` children inside `<PktTabs>`
2. **Props-based (legacy):** Pass a `tabs` array prop to `<PktTabs>`

The slot-based approach is recommended for new code.

## Props / Attributes — PktTabs

| Prop (React)      | Attribute (Elements) | Type               | Default | Description                                                                             |
| ----------------- | -------------------- | ------------------ | ------- | --------------------------------------------------------------------------------------- |
| `arrowNav`        | `arrow-nav`          | boolean            | `true`  | Enable arrow key navigation between tabs. Also enables `role="tab"` and `aria-selected` |
| `disableArrowNav` | `disable-arrow-nav`  | boolean            | `false` | Disable arrow navigation (e.g. for pure navigation menus). Overrides `arrowNav`         |
| `tabs`            | `tabs`               | `Array<TabObject>` | —       | Legacy: array of tab definitions (prefer using PktTabItem instead)                      |

### TabObject shape (legacy `tabs` prop)

```ts
{
  text: string           // Tab title (required)
  href?: string          // URL (renders as link)
  action?: () => void    // Click handler
  controls?: string      // aria-controls ID
  icon?: string          // Icon name
  active?: boolean       // Is this the active tab
  tag?: { text: string, skin?: string }  // Badge tag
}
```

## Props / Attributes — PktTabItem

| Prop (React) | Attribute (Elements) | Type                                                                                      | Default  | Description                                     |
| ------------ | -------------------- | ----------------------------------------------------------------------------------------- | -------- | ----------------------------------------------- |
| `active`     | `active`             | boolean                                                                                   | `false`  | Is this the active tab                          |
| `href`       | `href`               | string                                                                                    | —        | URL — renders the tab as a link                 |
| `icon`       | `icon`               | string (icon name)                                                                        | —        | Icon displayed in the tab                       |
| `tag`        | `tag`                | string                                                                                    | —        | Badge tag text                                  |
| `tagSkin`    | `tag-skin`           | `"blue"` \| `"green"` \| `"red"` \| `"beige"` \| `"yellow"` \| `"gray"` \| `"blue-light"` | `"blue"` | Badge tag color                                 |
| `index`      | `index`              | number                                                                                    | `0`      | Tab index — must be set explicitly when mapping |
| `controls`   | `controls`           | string                                                                                    | —        | `aria-controls` ID for the tab panel            |

## Events

| Event (React)   | Event (Elements) | Description                                    |
| --------------- | ---------------- | ---------------------------------------------- |
| `onTabSelected` | `tab-selected`   | Fires when a tab is clicked. Returns the index |

## Slots

| Component  | Slot    | Description            |
| ---------- | ------- | ---------------------- |
| PktTabs    | default | PktTabItem children    |
| PktTabItem | default | Tab label text/content |

## Examples

### React — slot-based (recommended)

```jsx
import { PktTabs, PktTabItem } from '@oslokommune/punkt-react'

const [activeTab, setActiveTab] = useState(0)

<PktTabs onTabSelected={(index) => setActiveTab(index)}>
  <PktTabItem active={activeTab === 0} index={0}>Overview</PktTabItem>
  <PktTabItem active={activeTab === 1} index={1}>Details</PktTabItem>
  <PktTabItem active={activeTab === 2} index={2} tag="3" tagSkin="red">Notifications</PktTabItem>
</PktTabs>

{activeTab === 0 && <div>Overview content</div>}
{activeTab === 1 && <div>Details content</div>}
{activeTab === 2 && <div>Notifications content</div>}
```

### React — navigation tabs

```jsx
<PktTabs disableArrowNav>
  <PktTabItem href="/dashboard" active={pathname === '/dashboard'} index={0}>
    Dashboard
  </PktTabItem>
  <PktTabItem href="/reports" active={pathname === '/reports'} index={1}>
    Reports
  </PktTabItem>
  <PktTabItem href="/settings" active={pathname === '/settings'} index={2}>
    Settings
  </PktTabItem>
</PktTabs>
```

### Elements

```html
<pkt-tabs>
  <pkt-tab-item active index="0">Overview</pkt-tab-item>
  <pkt-tab-item index="1">Details</pkt-tab-item>
  <pkt-tab-item index="2" tag="3" tag-skin="red">Notifications</pkt-tab-item>
</pkt-tabs>
```
