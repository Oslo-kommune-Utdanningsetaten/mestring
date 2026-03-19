# Footer

Footer is part of the standard page template and is placed at the bottom of the page. It gives the user access to important links like contact information, privacy, and accessibility. Together with the header, the footer establishes Oslo municipality as the sender.

## Availability

| Package        | Available | Tag / Import                                                                                                  |
| -------------- | --------- | ------------------------------------------------------------------------------------------------------------- |
| React          | Yes       | `<PktFooter>` / `<PktFooterSimple>` — `import { PktFooter, PktFooterSimple } from '@oslokommune/punkt-react'` |
| Elements       | No        | —                                                                                                             |
| Elements (CDN) | No        | —                                                                                                             |

Dark mode: Yes

## Variants

| Variant | Use                                                                                         |
| ------- | ------------------------------------------------------------------------------------------- |
| Normal  | Standard footer with three columns — for solutions closely tied to oslo.kommune.no          |
| Simple  | Simpler footer with fewer links — for smaller, standalone solutions with limited navigation |

## Usage guidelines

**Use footer when:**

- You're building solutions where Oslo municipality is the sender (in practice, footer should always be used)
- You need a fixed area for links to privacy, accessibility, and contact information
- You want to make it clear the solution belongs to Oslo municipality

**Content guidelines:**

- The footer must always include links to privacy ("Personvern og informasjonskapsler") and accessibility ("Tilgjengelighet")
- Other links in the footer should also be available elsewhere on the site
- Avoid images or icons in the footer
- Don't fill the footer with too many links
- Remove language links if only one language version exists
- Social media links should only be used if relevant to the solution

**Normal vs Simple:** Use Normal if the solution is part of oslo.kommune.no or needs multiple link columns. Use Simple for standalone solutions with limited navigation needs.

## Props / Attributes — PktFooter

| Prop (React)           | Type                                                            | Default        | Description                                 |
| ---------------------- | --------------------------------------------------------------- | -------------- | ------------------------------------------- |
| `personvernOgInfoLink` | string                                                          | —              | URL to privacy and cookie information page  |
| `tilgjengelighetLink`  | string                                                          | —              | URL to accessibility statement page         |
| `openLinksInNewTab`    | boolean                                                         | —              | Open links in a new tab                     |
| `includeConsent`       | boolean                                                         | —              | Include the Consent component in the footer |
| `googleAnalyticsId`    | string                                                          | —              | Google Analytics ID (when using Consent)    |
| `hotjarId`             | string                                                          | —              | Hotjar ID (when using Consent)              |
| `columnOne`            | `{ title: string, links?: LinkItem[], text?: string }`          | **(required)** | Content for the first column                |
| `columnTwo`            | `{ title: string, links?: LinkItem[] }`                         | **(required)** | Content for the second column               |
| `socialLinks`          | `Array<{ href: string, iconName?: string, language?: string }>` | —              | Social media links                          |

### LinkItem shape

```ts
{
  href: string        // URL (required)
  text: string        // Link text (required)
  external?: boolean  // Is an external link
  openInNewTab?: boolean // Open in new tab
}
```

## Props / Attributes — PktFooterSimple

| Prop (React)           | Type              | Default | Description                                |
| ---------------------- | ----------------- | ------- | ------------------------------------------ |
| `personvernOgInfoLink` | string            | —       | URL to privacy and cookie information page |
| `tilgjengelighetLink`  | string            | —       | URL to accessibility statement page        |
| `includeConsent`       | boolean           | —       | Include the Consent component              |
| `googleAnalyticsId`    | string            | —       | Google Analytics ID (when using Consent)   |
| `hotjarId`             | string            | —       | Hotjar ID (when using Consent)             |
| `links`                | `Array<LinkItem>` | —       | Additional links in the footer             |

## Accessibility

- The footer must be responsive — on mobile and tablet, content is displayed in a single column
- All links must have sufficient spacing and be keyboard-accessible
- Test the footer at different screen sizes, including portrait and landscape orientations

## Examples

### React

```jsx
import { PktFooter, PktFooterSimple } from '@oslokommune/punkt-react'

{
  /* Standard footer */
}
;<PktFooter
  personvernOgInfoLink="/personvern"
  tilgjengelighetLink="/tilgjengelighet"
  columnOne={{
    title: 'Oslo kommune',
    links: [{ href: 'https://www.oslo.kommune.no', text: 'oslo.kommune.no' }],
    text: 'Oslo kommune, Rådhuset, 0037 Oslo',
  }}
  columnTwo={{
    title: 'Kontakt',
    links: [{ href: 'tel:21802180', text: 'Telefon: 21 80 21 80' }],
  }}
  socialLinks={[
    { href: 'https://facebook.com/oslokommune', iconName: 'facebook' },
    { href: 'https://instagram.com/oslokommune', iconName: 'instagram' },
  ]}
/>

{
  /* Simple footer */
}
;<PktFooterSimple
  personvernOgInfoLink="/personvern"
  tilgjengelighetLink="/tilgjengelighet"
  includeConsent
  googleAnalyticsId="G-XXXXXXXXXX"
/>
```
