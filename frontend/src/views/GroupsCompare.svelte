<script lang="ts">
  import { useTinyRouter } from 'svelte-tiny-router'
  import type { GroupType, ObservationType, SubjectType } from '../generated/types.gen'
  import { observationsList } from '../generated/sdk.gen'
  import { dataStore, currentSchool, currentUser } from '../stores/data'
  import { hasUserAccessToFeature } from '../stores/access'
  import { getPreferredCreatedParams } from '../stores/localStorageFunctions'
  import { GROUP_TYPE_BASIS, GROUP_TYPE_TEACHING } from '../utils/constants'

  import GroupRow from '../components/GroupRow.svelte'
  import GroupsCompareSelect from '../components/GroupsCompareSelect.svelte'

  const router = useTinyRouter()

  let isLoading = $state<boolean>(true)
  let observationsByGroupId = $state<Record<string, ObservationType[]>>({})
  let uniqueSubjectIds = $state<Set<string>>(new Set())

  let uniqueSubjects = $derived(
    $dataStore.subjects?.filter(subject => uniqueSubjectIds.has(subject.id))
  )
  const selectedGroupIds = $derived(router.getQueryParam('groups')?.split(',') || [])
  let selectedGroups = $derived<GroupType[]>(
    $currentUser?.allGroups?.filter((group: GroupType) => selectedGroupIds.includes(group.id)) ?? []
  )
  let areAllGroupsOfSameType: Boolean = $derived(
    selectedGroups.length > 0
      ? selectedGroups.every(group => group.type === selectedGroups[0].type)
      : true
  )
  let groupType = $derived(areAllGroupsOfSameType ? selectedGroups[0].type : null)

  const fetchObservationsForSelectedGroups = async () => {
    try {
      isLoading = true
      await Promise.all(
        selectedGroups.map(async (group: GroupType) => {
          const observationsResult = await observationsList({
            query: { group: group.id, school: $currentSchool.id, ...getPreferredCreatedParams() },
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
      console.error('Error fetching groups', { selectedGroupIds, error })
      observationsByGroupId = {}
      uniqueSubjectIds = new Set()
    } finally {
      isLoading = false
    }
  }

  $effect(() => {
    if (selectedGroupIds.length > 0) {
      fetchObservationsForSelectedGroups()
    }
  })
</script>

<section>
  <h2>Sammenlign grupper [BETA]</h2>
  {#if $hasUserAccessToFeature('group', 'compare')}
    <GroupsCompareSelect />
    <p class="text-muted">Valgt: {selectedGroups?.map(g => g.displayName).join(', ')}</p>
    <!-- eslint-disable-next-line svelte/no-at-html-tags -->
    <p>
      {@html 'Diagrammene viser tre kategorier: Antall mål der elever beveger seg <span class="fw-bold">ned</span>, <span class="fw-bold">er uforandret</span>, eller <span class="fw-bold">opp</span>.'}
    </p>
    {#if isLoading}
      <div class="mt-3">Laster...</div>
    {:else if selectedGroups.length === 0}
      <div class="mt-3">Ingen grupper å sammenligne 🫤</div>
    {:else if !areAllGroupsOfSameType}
      <p class="text-danger mb-2">Valgte grupper må være av samme type (basis/undervisning)</p>
    {:else if groupType === GROUP_TYPE_TEACHING}
      <p class="text-danger mt-3">Sammenligning av undervisningsgrupper er ikke støttet ennå.</p>
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
        {#each selectedGroups as group (group.id)}
          <GroupRow
            {group}
            observations={observationsByGroupId[group.id]}
            allSubjects={uniqueSubjects}
          />
        {/each}
      </div>
    {:else}
      <p class="mt-3">Ukjent gruppetype: {groupType}</p>
    {/if}
  {:else}
    <p class="mt-3">Du har visst ikke tilgang til å sammenligne grupper.</p>
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
    min-height: 4.5rem;
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
