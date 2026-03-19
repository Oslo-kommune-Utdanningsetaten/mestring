# Consent

Consent (cookie banner) lets the user give consent to cookies and other data collection. It informs the user about how their data is used and gives them the option to accept or decline cookies. On first page load, the modal opens automatically if the user hasn't previously given consent.

You can also use Oslo municipality's cookie banner directly without this component — see [Oslo kommune cookie banner on GitHub](https://github.com/oslokommune/ukeweb_cookie_banner).

## Availability

| Package        | Available | Tag / Import                                                                                    |
| -------------- | --------- | ----------------------------------------------------------------------------------------------- |
| React          | Yes       | `<PktConsent>` — `import { PktConsent } from '@oslokommune/punkt-react'`                        |
| Elements       | Yes       | `<pkt-consent>` — `import '@oslokommune/punkt-elements/dist/pkt-consent.js'`                    |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-consent.js" type="module">` |

Dark mode: Yes

## Variants

The consent modal itself is always the same, but the trigger to reopen settings can vary:

| Trigger type | Description                       |
| ------------ | --------------------------------- |
| `button`     | Opens consent settings via button |
| `link`       | Opens consent settings via link   |
| `icon`       | Opens consent settings via icon   |

## Usage guidelines

**Use consent when:**

- You need to collect or update consent for cookies and tracking
- You must give the user clear information about how data is used

**Avoid consent when:**

- You don't handle data or tracking that requires consent
- You want to inform about something other than cookies and privacy — use Modal instead

**Content guidelines:**

- Use clear language explaining what the user is consenting to
- Always provide the option to decline or change consent later
- Make the settings trigger easily accessible (e.g. in the footer)

## Props / Attributes

| Prop (React)        | Attribute (Elements) | Type                               | Default | Description                                     |
| ------------------- | -------------------- | ---------------------------------- | ------- | ----------------------------------------------- |
| `triggerType`       | `triggerType`        | `"button"` \| `"link"` \| `"icon"` | —       | Type of element used to reopen consent settings |
| `triggerText`       | `triggerText`        | string                             | —       | Text displayed on the trigger element           |
| `googleAnalyticsId` | `googleAnalyticsId`  | string                             | —       | Google Analytics or Google Tag Manager ID       |
| `hotjarId`          | `hotjarId`           | string                             | —       | Hotjar ID                                       |
| `devMode`           | `devMode`            | boolean                            | —       | Enables dev mode for testing consent settings   |
| `cookieDomain`      | `cookieDomain`       | string                             | —       | Domain for cookies                              |
| `cookieSecure`      | `cookieSecure`       | boolean                            | —       | Set cookies as secure (HTTPS only)              |
| `cookieExpiryDays`  | `cookieExpiryDays`   | string                             | —       | Number of days before cookies expire            |

## Events

| Event (React)     | Event (Elements) | Description                                  |
| ----------------- | ---------------- | -------------------------------------------- |
| `onToggleConsent` | `toggle-consent` | Fires when the user saves or updates consent |

## Accessibility

- The button/link to change or decline consent must be clearly visible and accessible
- Use plain language so the content is easy to understand
- On mobile the consent opens as a full-screen modal

## Examples

### React

```jsx
import { PktConsent } from '@oslokommune/punkt-react'

{
  /* Basic consent with Google Analytics */
}
;<PktConsent
  googleAnalyticsId="G-XXXXXXXXXX"
  triggerType="link"
  triggerText="Cookie settings"
  onToggleConsent={(e) => console.log('Consent updated', e)}
/>

{
  /* In footer with button trigger */
}
;<PktConsent
  googleAnalyticsId="G-XXXXXXXXXX"
  hotjarId="1234567"
  triggerType="button"
  triggerText="Manage cookies"
/>
```

### Elements

```html
<pkt-consent
  googleAnalyticsId="G-XXXXXXXXXX"
  triggerType="link"
  triggerText="Cookie settings"
></pkt-consent>
```
