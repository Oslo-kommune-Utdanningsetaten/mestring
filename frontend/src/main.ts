import { mount } from 'svelte'
import './styles/main.scss'

import '@oslokommune/punkt-elements/dist/pkt-card.js'
import '@oslokommune/punkt-elements/dist/pkt-link.js'
import '@oslokommune/punkt-elements/dist/pkt-select.js'
import '@oslokommune/punkt-elements/dist/pkt-icon.js'
import '@oslokommune/punkt-elements/dist/pkt-button.js'
import '@oslokommune/punkt-elements/dist/pkt-combobox.js'
import '@oslokommune/punkt-elements/dist/pkt-textinput.js'
import '@oslokommune/punkt-elements/dist/pkt-input-wrapper.js'
import '@oslokommune/punkt-elements/dist/pkt-consent.js'

import './utils/configureHttpClient'

import App from './App.svelte'

const app = mount(App, {
  target: document.getElementById('app')!,
})

export default app
