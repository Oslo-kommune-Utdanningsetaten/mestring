import type { deploymentEnvironment } from '../types/models'
import { getCookie } from './cookieJar'
import { CookieConsent } from '../utils/constants'

const currentDeploymentEnv = import.meta.env.VITE_SERVER_DEPLOYMENT as deploymentEnvironment
const analyticsEnvironments: deploymentEnvironment[] = ['production', 'development']
const matomoSiteId = import.meta.env.VITE_MATOMO_SITE_ID
const matomoUrl = import.meta.env.VITE_MATOMO_URL
const scriptId = 'matomo-script'
const currentWindow: any = window

// Module-level state for singleton behavior
let isInitialized = false
let isEnabled = false

const init = () => {
  // Lazy initialization, only set up stuff on first pass
  if (isInitialized) return
  isEnabled =
    analyticsEnvironments.includes(currentDeploymentEnv) &&
    getCookie('cookie_consent') === CookieConsent.ALL

  if (isEnabled) {
    // Initialize the _paq array (piwik asynchronous queue)
    currentWindow._paq = [
      ['enableLinkTracking'],
      ['setTrackerUrl', matomoUrl + 'matomo.php'],
      ['setSiteId', matomoSiteId],
    ]

    // Insert Matomo script tag if not present
    if (!document.getElementById(scriptId)) {
      const script = document.createElement('script')
      script.async = true
      script.src = matomoUrl + 'matomo.js'
      script.id = scriptId
      document.head.appendChild(script)
    }
  }
  isInitialized = true
}

// Flag that there might have been a change to cookie consent settings
export const reconsiderCookieConsent = () => {
  isInitialized = false
  isEnabled = false
}

// Queue a command for Matomo to execute
export const addAnalyticsCommand = (command: any[]) => {
  init()
  if (!isEnabled) return
  currentWindow._paq.push(command)
}

// Track a custom event
// Only support detailed tracking of Goals for now: Use name (type) and value (1=group, 2=individual)
export const trackEvent = (
  category: 'Goals' | 'Observations' | 'Status',
  action: 'Create' | 'Update' | 'Delete',
  name?: 'type',
  value?: 1 | 2
) => {
  addAnalyticsCommand(['trackEvent', category, action, name, value])
}

// Track a page view, needed on SPA route changes
export const trackPageView = (pageUrl?: string) => {
  // Matomo's setCustomUrl expects an absolute URL. Prepend the origin when missing.
  const resolvedUrl = pageUrl
    ? pageUrl.startsWith('http')
      ? pageUrl
      : new URL(pageUrl, window.location.origin).href
    : window.location.href
  addAnalyticsCommand(['setCustomUrl', resolvedUrl])
  addAnalyticsCommand(['trackPageView'])
}
