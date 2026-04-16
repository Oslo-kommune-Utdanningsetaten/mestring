<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-checkbox.js'
  import type { GroupType } from '../generated/types.gen'
  import { dataStore } from '../stores/data'
  import Link from './Link.svelte'
  import { hasUserAccessToFeature } from '../stores/access'
  import { GROUP_TYPE_BASIS, GROUP_TYPE_TEACHING } from '../utils/constants'

  let groups = $derived<GroupType[]>($dataStore.currentUser.allGroups)
  let basisGroups = $derived(groups.filter((g: GroupType) => g.type === GROUP_TYPE_BASIS))
  let teachingGroups = $derived(groups.filter((g: GroupType) => g.type === GROUP_TYPE_TEACHING))

  let selectedGroups = $state<GroupType[]>([])
  let isCompareReady = $derived(
    selectedGroups.length > 0 &&
      selectedGroups.every((g: GroupType) => g.type === selectedGroups[0].type)
  )
  let compareUrl = $derived(`/groups-compare/?groups=${selectedGroups.map(g => g.id).join(',')}`)

  const handleToggleGroup = (id: string) => {
    const nextSelection = new Set(selectedGroups.map(g => g.id))
    if (nextSelection.has(id)) {
      nextSelection.delete(id)
    } else {
      nextSelection.add(id)
    }
    selectedGroups = groups.filter((g: GroupType) => nextSelection.has(g.id))
  }
</script>

{#if $hasUserAccessToFeature('group', 'compare')}
  <div class="mt-3">
    {#if basisGroups.length > 0}
      <fieldset class="mb-3">
        <legend class="fw-semibold mb-2">Basisgrupper</legend>
        <div class="d-flex flex-wrap gap-3">
          {#each basisGroups as group (group.id)}
            <pkt-checkbox
              id={`compare-group-${group.id}`}
              label={group.displayName}
              labelPosition="right"
              checked={selectedGroups.some(g => g.id === group.id)}
              onchange={() => handleToggleGroup(group.id)}
            ></pkt-checkbox>
          {/each}
        </div>
      </fieldset>
    {/if}

    {#if teachingGroups.length > 0}
      <fieldset class="mb-3">
        <legend class="fw-semibold mb-2">Undervisningsgrupper</legend>
        <div class="d-flex flex-wrap gap-3">
          {#each teachingGroups as group (group.id)}
            <pkt-checkbox
              id={`compare-group-${group.id}`}
              label={group.displayName}
              labelPosition="right"
              checked={selectedGroups.some(g => g.id === group.id)}
              onchange={() => handleToggleGroup(group.id)}
            ></pkt-checkbox>
          {/each}
        </div>
      </fieldset>
    {/if}

    <div class="mt-4">
      {#if isCompareReady}
        <Link to={compareUrl} disabled={true} className="btn btn-primary">
          Sammenlign valgte grupper
        </Link>
      {:else}
        <span class="text-warning-emphasis small mb-2">Velg grupper av samme type</span>
      {/if}
    </div>
  </div>
{/if}

<style>
  legend {
    font-size: 0.9rem;
  }
</style>
