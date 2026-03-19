# Icon

Icon displays an SVG icon from the Punkt icon library. Icons are loaded from the Punkt CDN by default and can be sized using CSS classes.

## Availability

| Package        | Available | Tag / Import                                                                                 |
| -------------- | --------- | -------------------------------------------------------------------------------------------- |
| React          | Yes       | `<PktIcon>` — `import { PktIcon } from '@oslokommune/punkt-react'`                           |
| Elements       | Yes       | `<pkt-icon>` — `import '@oslokommune/punkt-elements/dist/pkt-icon.js'`                       |
| Elements (CDN) | Yes       | `<script src="https://punkt-cdn.oslo.kommune.no/latest/elements/pkt-icon.js" type="module">` |

Dark mode: No

## Sizes

| CSS class          | Size   |
| ------------------ | ------ |
| `pkt-icon--small`  | Small  |
| `pkt-icon--medium` | Medium |
| `pkt-icon--large`  | Large  |

Set the size by passing the CSS class via `className` (React) or `class` (Elements).

## Props / Attributes

| Prop (React) | Attribute (Elements) | Type                                                               | Default                                             | Description                   |
| ------------ | -------------------- | ------------------------------------------------------------------ | --------------------------------------------------- | ----------------------------- |
| `name`       | `name`               | string (icon name)                                                 | —                                                   | Name of the icon to display   |
| `path`       | `path`               | string                                                             | `"https://punkt-cdn.oslo.kommune.no/latest/icons/"` | Override the icon source path |
| `className`  | `class`              | `"pkt-icon--small"` \| `"pkt-icon--medium"` \| `"pkt-icon--large"` | —                                                   | CSS class for sizing the icon |

## Examples

### React

```jsx
import { PktIcon } from '@oslokommune/punkt-react'

<PktIcon name="chevron-right" />
<PktIcon name="download" className="pkt-icon--large" />
<PktIcon name="user" className="pkt-icon--small" />
```

### Elements

```html
<pkt-icon name="chevron-right"></pkt-icon>
<pkt-icon name="download" class="pkt-icon--large"></pkt-icon>
<pkt-icon name="user" class="pkt-icon--small"></pkt-icon>
```

## Notes

Icons are fetched from `https://punkt-cdn.oslo.kommune.no/latest/icons/` by default. If you need to serve icons from a different location (e.g. for CSP or offline use), override the `path` prop.

## Available icons

These are all the available icons. Do NOT use any other icons unless you use path override and point to an SVG you already know about.

'24h' | 'access-prohibited' | 'accessibility' | 'accessible-water-access' | 'achievement' | 'active-person' | 'adjust' | 'advice' | 'alcohol-prohibited' | 'alert-circle' | 'alert-error-system' | 'alert-error' | 'alert-information' | 'alert-success-system' | 'alert-success' | 'alert-warning' | 'ambulance' | 'apple' | 'archive' | 'arrow-circle' | 'arrow-return' | 'arrow' | 'arts-and-culture' | 'attachment' | 'audioguide' | 'baby-bottle' | 'baby-changing-room' | 'backpack-prohibited' | 'backpack' | 'ball-sports' | 'balloons' | 'bath' | 'bed' | 'beehive' | 'bicycle-parking' | 'bicycle-prohibited' | 'bicycle-service' | 'bicycle' | 'books' | 'boys-shower' | 'boys-toilet' | 'brain-heart' | 'brain-signal' | 'brain' | 'briefcase' | 'bulb' | 'bullseye' | 'bus' | 'cafe' | 'calendar' | 'camera-surveillance-CCTV' | 'camera' | 'campfire-site' | 'camping' | 'car' | 'character-exclamation-mark' | 'character-information' | 'charging-point' | 'check-big' | 'check-box-checked' | 'check-box-unchecked' | 'check-circle' | 'check-medium' | 'check' | 'chevron-down' | 'chevron-left' | 'chevron-right' | 'chevron-thin-down' | 'chevron-thin-left' | 'chevron-thin-right' | 'chevron-thin-up' | 'chevron-up-and-down' | 'chevron-up' | 'childrens-toilet' | 'circular-economy' | 'climbing' | 'clipboard' | 'clock-history' | 'clock' | 'close' | 'cloud' | 'code' | 'coffee' | 'cogwheel' | 'coin-stacks' | 'computer' | 'cookie' | 'copy' | 'crane' | 'crayfish' | 'cross-circle-big' | 'cross-circle-fill-large' | 'cross-circle-fill' | 'cross-circle' | 'cross' | 'cupboard' | 'dancing' | 'data' | 'deer' | 'defibrillators' | 'district' | 'diving-prohibited' | 'dock' | 'document-code' | 'document-pdf' | 'document-plain' | 'document-table' | 'document-text' | 'dog-forbidden' | 'dog-on-a-leash' | 'download' | 'drag' | 'drinking-area-refreshments' | 'drone' | 'drugs-prohibited' | 'ecg-heart' | 'edit' | 'education' | 'elderly' | 'electric-car' | 'electric-van' | 'elevator' | 'email' | 'escalator' | 'exclamation-mark-circle' | 'exclamation-mark-square' | 'exit-door' | 'exit' | 'expand' | 'eye' | 'face-almost-happy' | 'face-almost-sad' | 'face-happy' | 'face-neutral' | 'face-sad' | 'facebook' | 'factory-fill' | 'feedback' | 'figma' | 'filming-prohibited' | 'filter' | 'fire-prohibited' | 'fire-safety' | 'fireworks-prohibited' | 'fishing-prohibited' | 'fixed-bench' | 'fixed-grill' | 'flag' | 'flammable-waste' | 'flash-prohibited' | 'folder-pending' | 'folder-restricted' | 'folder' | 'food-and-drinks-prohibited' | 'fountain' | 'game-console' | 'gavel' | 'girls-shower' | 'girls-toilet' | 'github' | 'goal' | 'graffiti-allowed' | 'graffiti-prohibited' | 'graph' | 'grid' | 'group-pending' | 'group' | 'gym' | 'handicap-elevator' | 'handicap' | 'hands-globe' | 'headset' | 'heart-hand' | 'heart-plus' | 'heart' | 'height-restriction' | 'helmet' | 'hiking-trail' | 'holding-hands' | 'home' | 'horizontal-menu' | 'house-heart' | 'ice-skating' | 'incoming-mail' | 'indoor-pool' | 'information' | 'instagram' | 'invoice' | 'key' | 'ladies-toilet' | 'language' | 'law-paragraph' | 'layers' | 'lecture-workplace' | 'lecture' | 'life-ring' | 'link' | 'linkedin' | 'list' | 'living-room' | 'location-pin-filled' | 'location-pin' | 'lock-locked' | 'lock-unlocked' | 'luggage-prohibited' | 'magnifying-glass-big' | 'magnifying-glass-small' | 'map-cursor' | 'map-layers' | 'map' | 'matrix' | 'medicine-cabinet' | 'megaphone' | 'memorial-stone' | 'mens-toilet' | 'menu' | 'message' | 'microphone' | 'minimize' | 'minus-circle-fill' | 'minus-circle' | 'minus-sign' | 'mobile-phone' | 'moon' | 'motorcycle' | 'museum' | 'music-notes' | 'nature-plant-2' | 'nature-plant' | 'network' | 'new-window-small' | 'new-window' | 'no-walking' | 'nodejs' | 'obstacle' | 'organization' | 'outgoing-mail' | 'package' | 'paint-bucket' | 'palette' | 'paragraph' | 'park' | 'parking-meter' | 'partner-workout' | 'paste' | 'person' | 'picnic-table' | 'picture' | 'placeholder-icon' | 'planter-box' | 'playground' | 'plus-circle-fill' | 'plus-circle' | 'plus-sign' | 'pregnant' | 'pride-heart' | 'print' | 'privacy' | 'process-back' | 'process-forward' | 'process-iteration' | 'processing' | 'prohibited' | 'punkt-circle-blue' | 'qr-code' | 'question' | 'radio-checked' | 'radio-unchecked' | 'react' | 'receipt' | 'recycling' | 'restaurant' | 'roadblock' | 'ruler' | 'sass' | 'sauna' | 'save' | 'scooter-prohibited' | 'scooter' | 'search-icon-round-active' | 'search-icon-round-disabled' | 'search-icon-round-normal' | 'search-icon-square-active' | 'search-icon-square-disabled' | 'search-icon-square-normal' | 'shapes' | 'share-outline' | 'share' | 'shield-fire' | 'shield-law-paragraph' | 'shoes-prohibited' | 'shopping-bag' | 'shower' | 'signature' | 'skateboarding' | 'slack' | 'sledding' | 'smiley-neutral' | 'smiley-sad' | 'smiley-smile' | 'smoking-prohibited' | 'snow' | 'sort' | 'sound-off' | 'sound-on' | 'sparkles' | 'stairs-down' | 'stairs-up' | 'stairs' | 'stop' | 'street-vendor' | 'stroller-prohibited' | 'stroller' | 'studded-tires' | 'svg' | 'swimming-area' | 'swingset' | 'table' | 'tap' | 'target' | 'thumbs-down' | 'thumbs-up' | 'tickets' | 'toilet-unisex' | 'toilet' | 'tool' | 'touching-prohibited' | 'trail-gate' | 'trail' | 'tram' | 'trash-can' | 'trash' | 'twitter' | 'two-people-dancing' | 'two-people-talking' | 'umbrella-prohibited' | 'urban-landscape' | 'urinal' | 'user' | 'van' | 'vertical-menu' | 'viewpoint' | 'virus' | 'vue' | 'walking' | 'wardrobe-boys' | 'wardrobe-girls' | 'wardrobe' | 'waste-container' | 'water-faucet' | 'wheelchair-ramp' | 'wheelchair' | 'wifi' | 'wine-bottle' | 'workplace' | 'wrench' | 'x'
