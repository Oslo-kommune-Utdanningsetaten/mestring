<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { subjectsDestroy, subjectsList, schoolsList, groupsList } from '../../generated/sdk.gen'
  import type { SubjectReadable, SchoolReadable, GroupReadable } from '../../generated/types.gen'
  import { urlStringFrom } from '../../utils/functions'
  import ButtonMini from '../../components/ButtonMini.svelte'
  import SubjectEdit from '../../components/SubjectEdit.svelte'
  import Offcanvas from '../../components/Offcanvas.svelte'
  import { dataStore } from '../../stores/data'

  const router = useTinyRouter()
  let subjects = $derived<SubjectReadable[]>([])
  let subjectWip = $state<SubjectReadable | null>(null)
  let isSubjectEditorOpen = $state(false)
  let schools = $state<SchoolReadable[]>([])
  let selectedSchool = $derived<SchoolReadable | null>(null)
  let isLoadingSubjects = $state<boolean>(false)
  let isLoadingSchools = $state<boolean>(false)
  let subjectFetchSelection = $state<string>('only-school-owned')
  let groupsBySubjectId = $state<Record<string, GroupReadable[]>>({})
  let nameFilter = $state<string>('')

  // Radio options for subject filtering
  const subjectFetchOptions = [
    { value: 'all', label: 'Alle fag' },
    { value: 'only-global', label: 'Globale fag' },
    { value: 'only-school-owned', label: 'Fag tilknyttet skolen' },
  ] as const

  let subjectFetchOption = $derived(
    subjectFetchSelection === 'all'
      ? {}
      : subjectFetchSelection === 'only-global'
        ? { isOwnedBySchool: false }
        : { isOwnedBySchool: true }
  )

  let filteredSubjects = $derived(
    nameFilter
      ? subjects.filter(subject =>
          subject.displayName.toLowerCase().includes(nameFilter.toLowerCase())
        )
      : subjects
  )

  let headerText = $derived.by(() => {
    let text = selectedSchool ? `Fag ved ${selectedSchool.displayName}` : 'Alle fag'
    text = nameFilter ? `${text} som inneholder "${nameFilter}"` : text
    return text
  })

  const fetchSchools = async () => {
    isLoadingSchools = true
    try {
      const result = await schoolsList({})
      schools = result.data || []
    } catch (error) {
      console.error('Error fetching schools:', error)
      schools = []
    } finally {
      isLoadingSchools = false
    }
  }

  const fetchGroups = async (subjectId: string) => {
    if (!selectedSchool) return
    if (Object.hasOwn(groupsBySubjectId, subjectId)) return

    groupsBySubjectId[subjectId] = []
    try {
      const groupResult = await groupsList({
        query: { subject: subjectId, school: selectedSchool.id },
      })
      const groups = groupResult.data || []
      groups.forEach(group => groupsBySubjectId[subjectId].push(group))
      groupsBySubjectId = { ...groupsBySubjectId }
    } catch (error) {
      console.error('Error fetching group:', error)
    }
  }

  const fetchSubjects = async () => {
    if (!selectedSchool) return
    try {
      isLoadingSubjects = true
      const queryOption = { ...subjectFetchOption, school: selectedSchool.id }
      const result = await subjectsList({ query: queryOption })
      subjects = (result.data || []).sort((a, b) =>
        a.displayName.localeCompare(b.displayName, 'no', { sensitivity: 'base' })
      )
      // side effect: fetch groups for each subject
      subjects.forEach(subject => fetchGroups(subject.id))
    } catch (error) {
      console.error('Error fetching groups:', error)
      subjects = []
    } finally {
      isLoadingSubjects = false
    }
  }

  const handleSchoolSelect = (schoolId: string): void => {
    if (schoolId && schoolId !== '0') {
      router.navigate(
        urlStringFrom({ school: schoolId }, { path: '/admin/subjects', mode: 'merge' })
      )
    } else {
      router.navigate('/admin/subjects')
    }
  }

  const closeEditor = () => {
    isSubjectEditorOpen = false
  }

  const handleEditSubject = (subject: SubjectReadable | null) => {
    if (subject?.id) {
      subjectWip = { ...subject }
    } else {
      subjectWip = { ownedBySchoolId: selectedSchool?.id } as SubjectReadable
    }
    isSubjectEditorOpen = true
  }

  const handleDeleteSubject = async (subjectId: string) => {
    try {
      await subjectsDestroy({
        path: { id: subjectId },
      })
    } catch (error) {
      console.error('Error deleting schema:', error)
    } finally {
      await fetchSubjects()
    }
  }

  $effect(() => {
    fetchSchools()
  })

  $effect(() => {
    if (!router.getQueryParam('school') && $dataStore.currentSchool) {
      handleSchoolSelect($dataStore.currentSchool.id)
    }
  })

  $effect(() => {
    const schoolIdFromUrl = router.getQueryParam('school')
    const nextSchool = schoolIdFromUrl
      ? (schools.find(school => school.id === schoolIdFromUrl) ?? null)
      : null
    // Only assign school if it changed
    if (nextSchool?.id !== selectedSchool?.id) {
      selectedSchool = nextSchool
    }
  })

  $effect(() => {
    if (selectedSchool) {
      fetchSubjects()
    }
  })
</script>

{#snippet groupsInfo(groups: GroupReadable[])}
  {#each groups as group, index (group.id)}
    <a class="bg-info px-1 me-1" href="/groups/{group.id}">
      {group.displayName}
    </a>
  {/each}
{/snippet}

<section class="pt-3">
  <h2 class="py-3">{headerText}</h2>
  <!-- Filter groups -->
  <div class="d-flex align-items-center gap-2">
    <div class="pkt-inputwrapper">
      <select
        class="pkt-input"
        id="groupSelect"
        onchange={(e: Event) => handleSchoolSelect((e.target as HTMLSelectElement).value)}
      >
        <option value="0" selected={!selectedSchool?.id}>Velg skole</option>
        {#each schools as school}
          <option value={school.id} selected={school.id === selectedSchool?.id}>
            {school.displayName}
          </option>
        {/each}
      </select>
    </div>
    <input
      type="text"
      class="group-filter-input"
      placeholder="Navn på fag"
      bind:value={nameFilter}
    />
  </div>

  <!-- Radio buttons for filtering subjects -->
  <fieldset>
    <legend class="visually-hidden">Filtrer fag</legend>
    {#each subjectFetchOptions as option}
      <label class="my-2 ms-1 d-block">
        <input
          type="radio"
          name="subjectFetchInclusion"
          value={option.value}
          bind:group={subjectFetchSelection}
        />
        <span class="ms-2">{option.label}</span>
      </label>
    {/each}
  </fieldset>
</section>

<section class="py-4">
  <div class="d-flex align-items-center mt-2 mb-3 gap-2">
    <ButtonMini
      options={{
        title: 'Nytt fag',
        iconName: 'plus-sign',
        skin: 'primary',
        variant: 'icon-left',
        classes: 'add-subject-btn',
        onClick: () => handleEditSubject(null),
      }}
    />
  </div>

  {#if !filteredSubjects.length}
    <div class="alert alert-info mt-3">Ingen fag for valgt filter.</div>
  {:else}
    <div class="subjects-grid-wrapper mt-4">
      <div class="subjects-grid" role="table" aria-label="Fagliste">
        <div class="grid-header" role="row">
          <div role="columnheader">Fag</div>
          <div role="columnheader">Eies av</div>
          <div role="columnheader">Grupper</div>
          <div role="columnheader">Grepkode</div>
          <div role="columnheader">Opplæringsfag</div>
          <div role="columnheader" class="text-end">Handlinger</div>
        </div>

        {#each filteredSubjects as subject (subject.id)}
          <div class="grid-row" role="row">
            <!-- Fag navn -->
            <div class="cell subject-name" role="cell">{subject.displayName}</div>
            <!-- Eies av -->
            <div class="cell" role="cell">
              {#if subject.ownedBySchoolId}
                {schools.find(s => s.id === subject.ownedBySchoolId)?.displayName}
              {:else}
                <span class="fst-italic">Globalt</span>
              {/if}
            </div>
            <!-- Grupper -->
            <div class="cell groups-cell" role="cell">
              {#if (groupsBySubjectId[subject.id] || []).length > 0}
                {@render groupsInfo(groupsBySubjectId[subject.id])}
              {:else}
                <span class="fst-italic">ingen</span>
              {/if}
            </div>
            <!-- Grepkode -->
            <div class="cell" role="cell">
              {#if subject.grepCode}
                {subject.grepCode}
              {:else}
                <span class="fst-italic">ukjent</span>
              {/if}
            </div>
            <!-- Opplæringsfag / grepGroupCode -->
            <div class="cell" role="cell">
              {#if subject.grepGroupCode}
                {subject.grepGroupCode}
              {:else}
                <span class="fst-italic">ukjent</span>
              {/if}
            </div>
            <!-- Actions -->
            <div class="cell actions text-end" role="cell">
              {#if subject.ownedBySchoolId}
                <ButtonMini
                  options={{
                    title: 'Rediger',
                    iconName: 'edit',
                    skin: 'secondary',
                    variant: 'icon-only',
                    size: 'tiny',
                    classes: 'me-1',
                    onClick: () => handleEditSubject(subject),
                  }}
                />
                <ButtonMini
                  options={{
                    title: 'Slett',
                    iconName: 'trash-can',
                    skin: 'secondary',
                    variant: 'icon-only',
                    size: 'tiny',
                    classes: 'me-0',
                    onClick: () => handleDeleteSubject(subject.id),
                  }}
                />
              {/if}
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</section>

<!-- Offcanvas panel to create/edit subject -->
<Offcanvas
  bind:isOpen={isSubjectEditorOpen}
  ariaLabel="Rediger fag"
  onClosed={() => {
    subjectWip = null
    fetchSubjects()
  }}
>
  {#if subjectWip && selectedSchool}
    <SubjectEdit subject={subjectWip} school={selectedSchool} onDone={closeEditor} />
  {/if}
</Offcanvas>

<style>
  .group-filter-input {
    border: 2px solid var(--bs-primary);
    height: 48px;
    padding: 0 15px;
    margin-left: 10px;
  }

  .subjects-grid-wrapper {
    overflow-x: auto;
  }

  .subjects-grid {
    display: grid;
    gap: 0.5rem 1rem;
  }

  .subjects-grid > .grid-header,
  .subjects-grid > .grid-row {
    display: grid;
    grid-template-columns: 2fr 1.2fr 2fr 0.9fr 1fr auto;
    min-height: 2.1rem;
    align-items: center;
  }

  .subjects-grid > .grid-header {
    font-weight: 600;
    border-bottom: 1px solid var(--bs-border-color, #ccc);
    background: var(--bs-body-bg, #fff);
    position: sticky;
    top: 0;
    z-index: 1;
  }

  .subjects-grid > .grid-header > *,
  .subjects-grid .cell {
    padding: 0.25rem;
    text-align: left !important;
  }

  .subjects-grid > .grid-header > :first-child,
  .subjects-grid .grid-row > .cell:first-child {
    padding-left: 0;
  }

  .subjects-grid .cell {
    font-size: 0.85rem;
  }

  .subjects-grid .subject-name {
    font-weight: 500;
  }

  .subjects-grid .grid-row {
    border-bottom: 1px solid var(--bs-border-color, #e2e2e2);
  }

  .subjects-grid .grid-row:hover .cell {
    background: var(--bs-light, #f8f9fa);
  }

  .subjects-grid .actions,
  .subjects-grid > .grid-header > .text-end {
    text-align: right;
  }

  .groups-cell {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }

  .groups-cell a {
    background: var(--bs-info-bg-subtle, #e7f5ff);
    padding: 2px 4px;
    border-radius: 2px;
    white-space: nowrap;
    font-size: inherit;
  }

  @media (max-width: 780px) {
    .subjects-grid > .grid-header,
    .subjects-grid > .grid-row {
      grid-template-columns: 2fr 1.2fr 2fr 0.9fr auto;
    }

    .subjects-grid > .grid-header > :nth-child(5),
    .subjects-grid > .grid-row > :nth-child(5) {
      display: none;
    }
  }
</style>
