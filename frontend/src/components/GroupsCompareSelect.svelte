<script lang="ts">
  import { useTinyRouter } from 'svelte-tiny-router'
  import '@oslokommune/punkt-elements/dist/pkt-checkbox.js'
  import type { GroupType } from '../generated/types.gen'
  import { dataStore } from '../stores/data'
  import { GROUP_TYPE_BASIS, GROUP_TYPE_TEACHING } from '../utils/constants'
  import { getGroupLabel, urlStringFrom } from '../utils/functions'

  const router = useTinyRouter()

  const selectedGroupIds = $derived(router.getQueryParam('groups')?.split(',') || [])
  let allGroupsSorted = $derived<GroupType[]>(
    ($dataStore.currentUser?.allGroups ?? [])
      .sort((a: GroupType, b: GroupType) => b.createdAt.localeCompare(a.createdAt))
      .sort((a: GroupType, b: GroupType) => a.displayName.localeCompare(b.displayName))
  )
  let basisGroups = $derived(allGroupsSorted.filter((g: GroupType) => g.type === GROUP_TYPE_BASIS))
  let teachingGroups = $derived(
    allGroupsSorted.filter((g: GroupType) => g.type === GROUP_TYPE_TEACHING)
  )
  let selectedGroups = $derived<GroupType[]>(
    allGroupsSorted.filter((group: GroupType) => selectedGroupIds.includes(group.id))
  )

  const handleToggleGroup = (id: string) => {
    const nextSelectionIds = new Set(selectedGroups.map(g => g.id))
    if (nextSelectionIds.has(id)) {
      nextSelectionIds.delete(id)
    } else {
      nextSelectionIds.add(id)
    }
    const nextUrl = [...nextSelectionIds].length
      ? urlStringFrom(
          { groups: [...nextSelectionIds].join(',') },
          { path: '/groups-compare/', mode: 'merge' }
        )
      : urlStringFrom({}, { path: '/groups-compare/' })
    router.navigate(nextUrl)
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
