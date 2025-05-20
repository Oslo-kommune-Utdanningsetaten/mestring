import { mount } from 'svelte'
import './styles/main.scss'

import '@oslokommune/punkt-elements/dist/pkt-card.js'
import '@oslokommune/punkt-elements/dist/pkt-link.js'
import '@oslokommune/punkt-elements/dist/pkt-select.js'

import App from './App.svelte'

const app = mount(App, {
  target: document.getElementById('app')!,
})

export default app
