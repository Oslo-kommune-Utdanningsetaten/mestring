<script lang="ts">
  import { useTinyRouter } from 'svelte-tiny-router'
  import '@oslokommune/punkt-elements/dist/pkt-checkbox.js'
  import type { GroupType } from '../generated/types.gen'
  import { dataStore } from '../stores/data'
  import { GROUP_TYPE_BASIS, GROUP_TYPE_TEACHING } from '../utils/constants'
  import { getGroupLabel } from '../utils/functions'

  const router = useTinyRouter()
  const groupIds = $derived(router.getQueryParam('groups')?.split(',') || [])

  let groups = $derived<GroupType[]>(
    ($dataStore.currentUser?.allGroups ?? []).sort((a: GroupType, b: GroupType) =>
      b.createdAt.localeCompare(a.createdAt)
    )
  )
  let basisGroups = $derived(groups.filter((g: GroupType) => g.type === GROUP_TYPE_BASIS))
  let teachingGroups = $derived(groups.filter((g: GroupType) => g.type === GROUP_TYPE_TEACHING))

  let selectedGroups = $derived<GroupType[]>(
    groups.filter((group: GroupType) => groupIds.includes(group.id))
  )
  let compareUrl = $derived(`/groups-compare/?groups=${selectedGroups.map(g => g.id).join(',')}`)

  const handleToggleGroup = (id: string) => {
    const nextSelectionIds = new Set(selectedGroups.map(g => g.id))
    if (nextSelectionIds.has(id)) {
      nextSelectionIds.delete(id)
    } else {
      nextSelectionIds.add(id)
    }
    selectedGroups = groups.filter((g: GroupType) => nextSelectionIds.has(g.id))
    router.navigate(compareUrl)
  }
</script>

<section class="bg-light p-4 my-4">
  {#if basisGroups.length > 0}
    <fieldset class="mb-3">
      <legend class="fw-semibold mb-2">Basisgrupper</legend>
      <div class="d-flex flex-wrap gap-3">
        {#each basisGroups as group (group.id)}
          <pkt-checkbox
            id={`compare-group-${group.id}`}
            label={getGroupLabel(group, {
              isGroupNameEnabled: true,
              isGroupTypeNameEnabled: false,
              includeEarlierYear: true,
            })}
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
            label={getGroupLabel(group, {
              isGroupNameEnabled: true,
              isGroupTypeNameEnabled: false,
              includeEarlierYear: true,
            })}
            labelPosition="right"
            checked={selectedGroups.some(g => g.id === group.id)}
            onchange={() => handleToggleGroup(group.id)}
          ></pkt-checkbox>
        {/each}
      </div>
    </fieldset>
  {/if}
</section>

<style>
  legend {
    font-size: 1rem;
  }
</style>
