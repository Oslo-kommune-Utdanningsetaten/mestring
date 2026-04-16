<script lang="ts">
  import { dataStore } from '../stores/data'
  import { observationsList } from '../generated/sdk.gen'
  import type { GroupType, ObservationType, SubjectType } from '../generated/types.gen'
  import GroupRow from './GroupRow.svelte'
  import { GROUP_TYPE_BASIS, GROUP_TYPE_TEACHING } from '../utils/constants'

  const { groupIds } = $props<{
    groupIds: string[]
  }>()
  let isLoading = $state<boolean>(true)
  let currentSchool = $derived($dataStore.currentSchool)
  let groups = $derived<GroupType[]>(
    $dataStore.currentUser.allGroups.filter((group: GroupType) => groupIds.includes(group.id))
  )
  let areAllGroupsOfSameType = $derived(
    groups.length > 0 ? groups.every(group => group.type === groups[0].type) : true
  )
  let groupType = $derived(areAllGroupsOfSameType ? groups[0].type : null)
  let observationsByGroupId = $derived<Record<string, ObservationType[]>>({})
  let uniqueSubjectIds = $derived<Set<string>>(new Set())
  let uniqueSubjects = $derived(
    $dataStore.subjects.filter(subject => uniqueSubjectIds.has(subject.id))
  )

  const fetchGroups = async () => {
    try {
      isLoading = true
      await Promise.all(
        groups.map(async (group: GroupType) => {
          const observationsResult = await observationsList({
            query: { group: group.id, school: currentSchool.id },
          })
          // All observations for this group, accross subjects
          const observations = observationsResult.data || []
          // Observations by subect id
          observationsByGroupId = {
            ...observationsByGroupId,
            [group.id]: observations,
          }
          // Subject ids
          const groupSubjectIds = new Set(
            observations.map(obs => obs.subjectId).filter(Boolean) as string[]
          )
          // Unique subject ids across all groups
          uniqueSubjectIds = new Set([...uniqueSubjectIds, ...groupSubjectIds])
        })
      )
    } catch (error) {
      console.error('Error fetching groups', { groupIds, error })
      groups = []
    } finally {
      isLoading = false
    }
  }

  $effect(() => {
    fetchGroups()
  })
</script>

<section class="py-3">
  {#if isLoading}
    <div class="mt-3">Laster...</div>
  {:else}
    <h2>Sammenligner {groupType === GROUP_TYPE_BASIS ? 'basis' : 'undervisnings'}grupper</h2>
    <p class="text-muted">{groups.map(group => group.displayName).join(', ')}</p>
    {#if groups.length === 0}
      <div class="mt-3">Ingen grupper å sammenligne 🫤</div>
    {:else if !areAllGroupsOfSameType}
      <p class="mt-3">
        Du kan bare sammenligne grupper av samme type: Enten basis eller undervisning.
      </p>
    {:else if groupType === GROUP_TYPE_TEACHING}
      <p class="mt-3">Sammenligning av undervisningsgrupper er ikke støttet ennå.</p>
    {:else if groupType === GROUP_TYPE_BASIS}
      <div
        class="groups-grid"
        aria-label="Gruppeliste"
        style="--columns-count: {uniqueSubjects.length}"
      >
        <span class="item header header-row">Group</span>
        {#each uniqueSubjects as subject (subject.id)}
          <span class="item header header-row">
            <span class="column-header">
              {#if subject.ownedBySchoolId}
                {subject.shortName}
              {:else}
                {subject.grepCode}
              {/if}
            </span>
          </span>
        {/each}
        {#each groups as group (group.id)}
          <GroupRow
            {group}
            subjects={uniqueSubjects.map(subject => {
              const hasObservationsForSubject = observationsByGroupId[group.id].some(
                obs => obs.subjectId === subject.id
              )
              return hasObservationsForSubject ? subject : null
            })}
            observations={observationsByGroupId[group.id]}
          />
        {/each}
      </div>
    {:else}
      <p class="mt-3">Ukjent gruppetype: {groupType}</p>
    {/if}
  {/if}
</section>

<style>
  .groups-grid {
    margin-top: 2rem;
    display: grid;
    grid-template-columns: auto repeat(var(--columns-count, 8), 1fr);
    align-items: start;
    gap: 0;
  }

  .groups-grid :global(.item) {
    padding: 0.5rem;
    border-bottom: 1px solid var(--bs-border-color);
    min-height: 4rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .groups-grid .item.header-row {
    background-color: var(--bs-light);
    font-weight: 800;
    max-height: 4rem;
    margin-bottom: 0.5rem;
  }

  .groups-grid :global(.item.header:first-child),
  .groups-grid :global(.item.group-name) {
    justify-content: flex-start;
  }

  .column-header {
    overflow-wrap: break-word;
    width: 100%;
    font-size: 0.8rem;
    padding: 0.1rem 0.5rem 0.1rem 0.5rem;
    background-color: color-mix(
      in srgb,
      var(--pkt-color-surface-strong-light-green) 70%,
      transparent
    );
    border: 1px solid var(--pkt-color-grays-gray-100);
    z-index: 2;
  }
</style>
