<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-card.js'
  import type { GoalReadable } from '../generated'
  const { goal } = $props<{ goal: GoalReadable }>()
</script>

<pkt-card
  heading={goal.is_personal ? 'Personlig mål' : 'Gruppemål'}
  subheading={goal.title}
  skin="outlined"
  layout="vertical"
>
  <span>
    <p>Sort order: {goal.sortOrder}</p>
  </span>
</pkt-card>

<style>
</style>
