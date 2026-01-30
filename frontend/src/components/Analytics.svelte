<script lang="ts">
  import { dataStore } from '../stores/data'

  // Matomo Analytics
  const matomoSiteId = import.meta.env.VITE_MATOMO_SITE_ID
  const matomoUrl = import.meta.env.VITE_MATOMO_URL

  const currentWindow: any = window
  const scriptId = 'matomo-script'
  let schoolOrgNumber = $derived($dataStore.currentSchool?.orgNumber)

  const addCommand = (command: any[]) => {
    if (!currentWindow._paq) currentWindow._paq = [] // initialize the command queue
    currentWindow._paq.push(command)
  }

  if (!document.getElementById(scriptId)) {
    addCommand(['enableLinkTracking'])
    addCommand(['setTrackerUrl', matomoUrl + 'matomo.php'])
    addCommand(['setSiteId', matomoSiteId])

    const script = document.createElement('script')
    script.async = true
    script.src = matomoUrl + 'matomo.js'
    script.id = scriptId
    document.head.appendChild(script)
  }

  $effect(() => {
    if (!schoolOrgNumber) return
    console.log('Setting Matomo schoolOrgNumber to', schoolOrgNumber)
    // To reset the visit, set visit and delete existing cookies
    addCommand(['appendToTrackingUrl', 'new_visit=1'])
    addCommand(['deleteCookies'])
    // Update custom dimension with schoolOrgNumber
    addCommand(['setCustomDimension', 1, schoolOrgNumber])
    addCommand(['trackPageView'])
  })
</script>
