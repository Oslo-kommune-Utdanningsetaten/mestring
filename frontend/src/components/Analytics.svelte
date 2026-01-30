<script lang="ts">
  import { dataStore } from '../stores/data'

  // Matomo Analytics
  const matomoSiteId = import.meta.env.VITE_MATOMO_SITE_ID
  const matomoUrl = import.meta.env.VITE_MATOMO_URL
  const currentWindow: any = window
  const scriptId = 'matomo-script'
  let schoolOrgNumber = $derived($dataStore.currentSchool?.orgNumber)

  if (!currentWindow._paq) currentWindow._paq = []
  const _paq = currentWindow._paq

  _paq.push(['trackPageView'])
  _paq.push(['enableLinkTracking'])

  // Only inject the script once
  if (!document.getElementById(scriptId)) {
    _paq.push(['setTrackerUrl', matomoUrl + 'matomo.php'])
    _paq.push(['setSiteId', matomoSiteId])

    const script = document.createElement('script')
    script.async = true
    script.src = matomoUrl + 'matomo.js'
    script.id = scriptId
    document.head.appendChild(script)
  }

  $effect(() => {
    // Update custom dimension when schoolOrgNumber changes
    console.log('Updating Matomo custom dimension with schoolOrgNumber:', schoolOrgNumber)
    _paq.push(['setCustomDimension', 1, null])
    _paq.push(['setCustomDimension', 1, schoolOrgNumber])
  })
</script>
