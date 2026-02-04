<script lang="ts">
  import { dataStore } from '../stores/data'
  import { addAnalyticsCommand } from '../stores/analytics'

  let schoolOrgNumber = $derived($dataStore.currentSchool?.orgNumber)

  $effect(() => {
    if (!schoolOrgNumber) return
    // Reset visit
    addAnalyticsCommand(['appendToTrackingUrl', 'new_visit=1'])
    // Update custom dimension with schoolOrgNumber
    addAnalyticsCommand(['setCustomDimension', 1, schoolOrgNumber])
    addAnalyticsCommand(['trackPageView'])
    // Remove new_visit params to avoid that all subsequent page views are marked as new visits
    addAnalyticsCommand(['appendToTrackingUrl', ''])
  })
</script>
