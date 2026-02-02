import type { deploymentEnvironment } from '../types/models'

const currentDeploymentEnv = import.meta.env.VITE_SERVER_DEPLOYMENT as deploymentEnvironment
const analyticsEnvironments: deploymentEnvironment[] = ['production', 'development', 'localhost']
const matomoSiteId = import.meta.env.VITE_MATOMO_SITE_ID
const matomoUrl = import.meta.env.VITE_MATOMO_URL
const scriptId = 'matomo-script'
const currentWindow: any = window

// Module-level state for singleton behavior
let isInitialized = false
let isEnabled = false

const init = () => {
  if (isInitialized) return
  // Lazy initialization, only set up stuff on first pass
  isEnabled = analyticsEnvironments.includes(currentDeploymentEnv)

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

export const addAnalyticsCommand = (command: any[]) => {
  init()
  if (!isEnabled) return
  currentWindow._paq.push(command)
}

export const trackEvent = (category: string, action: string, name?: string, value?: number) => {
  addAnalyticsCommand(['trackEvent', category, action, name, value])
}

export const trackPageView = (pageUrl?: string) => {
  addAnalyticsCommand(['setCustomUrl', pageUrl || window.location.href])
  addAnalyticsCommand(['trackPageView'])
}
