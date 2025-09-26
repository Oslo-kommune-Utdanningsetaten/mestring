<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-tag.js'
  import type { GroupReadable } from '../generated/types.gen'

  const { group } = $props<{ group: GroupReadable | null }>()
  const label = $derived(
    group ? (group.type === 'basis' ? 'Basisgruppe' : 'Undervisningsgruppe') : ''
  )
</script>

{#if group}
  <pkt-tag iconName="two-people-dancing" skin="blue" class="me-1">
    <span>{label}</span>
  </pkt-tag>
{/if}
