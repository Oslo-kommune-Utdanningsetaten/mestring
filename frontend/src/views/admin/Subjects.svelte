<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { subjectsDestroy, subjectsList, schoolsList } from '../../generated/sdk.gen'
  import type { SubjectType, SchoolType, GroupType } from '../../generated/types.gen'
  import { urlStringFrom } from '../../utils/functions'
  import ButtonMini from '../../components/ButtonMini.svelte'
  import SubjectEdit from '../../components/SubjectEdit.svelte'
  import Offcanvas from '../../components/Offcanvas.svelte'
  import { dataStore } from '../../stores/data'

  const router = useTinyRouter()
  let subjects = $derived<SubjectType[]>([])
  let subjectWip = $state<SubjectType | null>(null)
  let isSubjectEditorOpen = $state(false)
  let schools = $state<SchoolType[]>([])
  let selectedSchool = $derived<SchoolType | null>(null)
  let isLoadingSubjects = $state<boolean>(false)
  let isLoadingSchools = $state<boolean>(false)
  let subjectFetchSelection = $state<string>('only-school-owned')
  let groupsBySubjectId = $state<Record<string, GroupType[]>>({})
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
      const groups = $dataStore.currentUser.allGroups.filter(
        (group: GroupType) => group.subjectId === subjectId
      )
      groups.forEach((group: GroupType) => groupsBySubjectId[subjectId].push(group))
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

  const handleEditSubject = (subject: SubjectType | null) => {
    if (subject?.id) {
      subjectWip = { ...subject }
    } else {
      subjectWip = { ownedBySchoolId: selectedSchool?.id } as SubjectType
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

{#snippet groupsInfo(groups: GroupType[])}
  {#each groups as group, index (group.id)}
    <a class="bg-info px-1 group-link" href="/groups/{group.id}">
      {group.displayName}
    </a>
  {/each}
{/snippet}

{#snippet subjectCodes(subject: SubjectType)}
  {#if !subject.grepCode && !subject.grepGroupCode}
    <span class="fst-italic">mangler</span>
  {:else}
    <!-- grep code -->
    {#if subject.grepCode}
      <span title="grepCode">{subject.grepCode}</span>
    {:else}
      <span class="fst-italic">mangler</span>
    {/if}
    <!-- Opplæringsfag / grepGroupCode -->
    {#if subject.grepGroupCode}
      <span title="grepGroupCode">{subject.grepGroupCode}</span>
    {:else}
      <span class="fst-italic">mangler</span>
    {/if}
  {/if}
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
    <div class="subjects-grid" aria-label="Fagliste">
      <span class="item header header-row">Fag</span>
      <span class="item header header-row">Eies av</span>
      <span class="item header header-row">Elever</span>
      <span class="item header header-row">Grupper</span>
      <span class="item header header-row">Fagkode</span>
      <span class="item header header-row">Handlinger</span>
      {#each filteredSubjects as subject (subject.id)}
        <!-- Fag navn -->
        <span class="item header">{subject.displayName}</span>

        <!-- Eies av -->
        <span class="item">
          {#if subject.ownedBySchoolId}
            {schools.find(s => s.id === subject.ownedBySchoolId)?.displayName}
          {:else}
            <span class="fst-italic">Globalt</span>
          {/if}
        </span>

        <span class="item">
          <span class="fst-italic">0</span>
        </span>

        <!-- Grupper -->
        <span class="item">
          {#if (groupsBySubjectId[subject.id] || []).length > 0}
            {@render groupsInfo(groupsBySubjectId[subject.id])}
          {:else}
            <span class="fst-italic">ingen</span>
          {/if}
        </span>

        <!-- Grep code stuff -->
        <span class="item">
          {@render subjectCodes(subject)}
        </span>

        <!-- Actions -->
        <span class="item">
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
        </span>
      {/each}
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

  .subjects-grid {
    display: grid;
    grid-template-columns: 1.5fr 2fr 0.5fr 1.5fr 1fr 0.5fr;
    align-items: start;
    gap: 0;
  }

  .item.header-row {
    background-color: var(--bs-light);
  }

  .item {
    padding: 0.5rem;
    border-top: 1px solid var(--bs-border-color);
    min-height: 2.8rem;
  }

  .item:nth-last-child(-n + 6) {
    border-bottom: 1px solid var(--bs-border-color);
  }

  .item.header {
    font-weight: 800;
  }

  .group-link {
    display: inline-block;
    white-space: nowrap;
    font-size: 0.875rem;
    margin-right: 0.25rem;
  }
</style>
