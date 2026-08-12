<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { subjectsDestroy, subjectsList, schoolsList, groupsList } from '../../generated/sdk.gen'
  import type { SubjectType, SchoolType, GroupType } from '../../generated/types.gen'
  import {
    GROUP_DELETED_OPTIONS,
    GROUP_VALIDITY_OPTIONS,
    SUBJECT_OWNERSHIP_OPTIONS,
  } from '../../utils/constants'
  import { urlStringFrom } from '../../utils/functions'
  import { dataStore } from '../../stores/data'
  import {
    getAllSchoolYears,
    getCurrentSchoolYear,
    inferCreatedParams,
    inferGroupValidityParams,
  } from '../../utils/schoolYear'

  import ButtonMini from '../../components/ButtonMini.svelte'
  import ButtonIcon from '../../components/ButtonIcon.svelte'
  import SubjectEdit from '../../components/SubjectEdit.svelte'
  import Offcanvas from '../../components/Offcanvas.svelte'
  import GroupTag from '../../components/GroupTag.svelte'

  const router = useTinyRouter()
  let subjects = $derived<SubjectType[]>([])
  let subjectWip = $state<SubjectType | null>(null)
  let isSubjectEditorOpen = $state(false)
  let schools = $state<SchoolType[]>([])
  let groupsBySubjectId = $state<Record<string, GroupType[]>>({})
  let nameFilter = $state<string>('')

  let selectedSchool = $derived.by(() => {
    const schoolIdFromUrl = router.getQueryParam('school')
    return schools.find(s => s.id === schoolIdFromUrl) || $dataStore.currentSchool
  })

  let selectedSubjectsFetchOption = $state<SUBJECT_OWNERSHIP_OPTIONS>(
    (router.getQueryParam('owner') as SUBJECT_OWNERSHIP_OPTIONS) || SUBJECT_OWNERSHIP_OPTIONS.ANY
  )

  let selectedDeletedOption = $state<GROUP_DELETED_OPTIONS>(
    (router.getQueryParam('deleted') as GROUP_DELETED_OPTIONS) || GROUP_DELETED_OPTIONS.EXCLUDE
  )

  let selectedYearOption = $state<string>(
    (router.getQueryParam('year') as string) || getCurrentSchoolYear()
  )

  // Radio options for subject filtering
  const subjectFetchOptions = [
    { value: SUBJECT_OWNERSHIP_OPTIONS.ANY, label: 'Alle fag' },
    { value: SUBJECT_OWNERSHIP_OPTIONS.ONLY_GLOBAL, label: 'Globale fag' },
    { value: SUBJECT_OWNERSHIP_OPTIONS.ONLY_SCHOOL_OWNED, label: 'Fag tilknyttet skolen' },
  ] as const

  // Options for filtering by deleted
  const deletedOptions = [
    { value: GROUP_DELETED_OPTIONS.INCLUDE, label: 'All' },
    { value: GROUP_DELETED_OPTIONS.ONLY, label: 'Deleted' },
    { value: GROUP_DELETED_OPTIONS.EXCLUDE, label: 'Not deleted' },
  ] as const

  // Options for filtering by groups by date validity
  const createdOptions = [
    { value: 'all', label: 'Any year' },
    ...getAllSchoolYears()
      .reverse()
      .map((year: string) => ({
        value: year,
        label: year,
      })),
  ] as const

  let subjectsQueryOptions = $derived.by(() => {
    const options: any = {
      school: selectedSchool.id,
      deleted: selectedDeletedOption,
    }
    if (selectedSubjectsFetchOption !== 'any') {
      options.isOwnedBySchool = selectedSubjectsFetchOption === 'only-school-owned'
    }
    return options
  })

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

  const getGroupsQueryOptions: any = (subjectId: string) => {
    return {
      subject: subjectId,
      school: selectedSchool.id,
      deleted: 'all',
      ...inferCreatedParams(selectedYearOption),
      ...inferGroupValidityParams(selectedYearOption),
    }
  }

  const fetchSchools = async () => {
    try {
      const result = await schoolsList({})
      schools = result.data || []
    } catch (error) {
      console.error('Error fetching schools:', error)
      schools = []
    }
  }

  const fetchGroups = async (subjectId: string) => {
    if (!selectedSchool) return
    if (Object.hasOwn(groupsBySubjectId, subjectId)) return
    groupsBySubjectId[subjectId] = []
    try {
      const result = await groupsList({ query: getGroupsQueryOptions(subjectId) })
      groupsBySubjectId[subjectId] = result.data || []
    } catch (error) {
      console.error('Error fetching group:', error)
    }
  }

  const fetchSubjects = async () => {
    if (!selectedSchool) return
    try {
      const result = await subjectsList({ query: subjectsQueryOptions })
      subjects = (result.data || []).sort((a, b) =>
        a.displayName.localeCompare(b.displayName, 'no', { sensitivity: 'base' })
      )
      // side effect: fetch groups for each subject
      subjects.forEach(subject => fetchGroups(subject.id))
    } catch (error) {
      console.error('Error fetching groups:', error)
      subjects = []
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
    if (selectedSchool) {
      fetchSubjects()
    }
  })

  $effect(() => {
    const url = urlStringFrom(
      {
        deleted: selectedDeletedOption || null,
        year: selectedYearOption || null,
        owner: selectedSubjectsFetchOption || null,
      },
      { path: '/admin/subjects', mode: 'merge' }
    )
    router.navigate(url)
  })
</script>

{#snippet groupsInfo(groups: GroupType[])}
  {#each groups as group, index (group.id)}
    <GroupTag {group} href="/groups/{group.id}" isGroupNameEnabled={true} />
  {/each}
{/snippet}

{#snippet subjectCodes(subject: SubjectType)}
  {#if !subject.grepCode && !subject.grepGroupCode}
    <span class="fst-italic">mangler</span>
  {:else}
    <!-- grep code -->
    {#if subject.grepCode}
      <span title="grepCode">{subject.grepCode}</span>
    {/if}
    <!-- Opplæringsfag / grepGroupCode -->
    {#if subject.grepGroupCode}
      <span title="grepGroupCode">({subject.grepGroupCode})</span>
    {/if}
  {/if}
{/snippet}

<section class="pt-3">
  <h2 class="py-3">{headerText}</h2>
  <!-- Filter groups -->
  <div class="filters-container mt-3">
    <div class="filter-item">
      <label for="schoolSelect" class="mb-1 visually-hidden">Filtrer på skole:</label>
      <select
        class="pkt-input"
        id="schoolSelect"
        onchange={(e: Event) => handleSchoolSelect((e.target as HTMLSelectElement).value)}
      >
        {#each schools as school}
          <option value={school.id} selected={school.id === selectedSchool?.id}>
            {school.displayName}
          </option>
        {/each}
      </select>
    </div>
    <div class="filter-item">
      <label for="subjectFilterInput" class="mb-1 visually-hidden">Filtrer på navn:</label>
      <input
        type="text"
        id="subjectFilterInput"
        class="group-filter-input"
        placeholder="Navn på fag"
        bind:value={nameFilter}
      />
    </div>
  </div>

  <div class="d-flex flex-wrap gap-3 mt-3">
    <!-- Radio buttons for filtering subjects -->
    <fieldset class="border p-3 rounded">
      <legend class="w-auto fs-6 pb-2">Filtrer fag</legend>
      {#each subjectFetchOptions as option}
        <label class="my-2 ms-1 d-block">
          <input
            type="radio"
            name="subjectFetchInclusion"
            value={option.value}
            bind:group={selectedSubjectsFetchOption}
          />
          <span class="ms-2">{option.label}</span>
        </label>
      {/each}
    </fieldset>

    <!-- Radio buttons for deleted status -->
    <fieldset class="border p-3 rounded">
      <legend class="w-auto fs-6">Deleted</legend>
      {#each deletedOptions as option}
        <label class="my-2 ms-1 d-block">
          <input
            type="radio"
            name="deletedOptions"
            value={option.value}
            bind:group={selectedDeletedOption}
          />
          <span class="ms-2">{option.label}</span>
        </label>
      {/each}
    </fieldset>

    <!-- Radio buttons for created in year -->
    <fieldset class="border p-3 rounded">
      <legend class="w-auto fs-6">Year created</legend>
      {#each createdOptions as option}
        <label class="my-2 ms-1 d-block">
          <input
            type="radio"
            name="createdOptions"
            value={option.value}
            bind:group={selectedYearOption}
          />
          <span class="ms-2">{option.label}</span>
        </label>
      {/each}
    </fieldset>
  </div>
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
      <span class="item header header-row">Grupper</span>
      <span class="item header header-row">Fagkode</span>
      <span class="item header header-row">Handlinger</span>
      {#each filteredSubjects as subject (subject.id)}
        <!-- Fag navn -->
        <div class="item">
          <div class="header">
            {subject.displayName}
          </div>
          <div class="text-muted small">{subject.id}</div>
        </div>

        <!-- Eies av -->
        <span class="item">
          {#if subject.ownedBySchoolId}
            {schools.find(s => s.id === subject.ownedBySchoolId)?.displayName}
          {:else}
            <span class="fst-italic">Globalt</span>
          {/if}
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
            <ButtonIcon
              options={{
                iconName: 'trash-can',
                title: 'Slett',
                classes: 'bordered',
                onClick: () => handleDeleteSubject(subject.id),
                delayActionFor: 3,
              }}
            />
            <ButtonIcon
              options={{
                iconName: 'edit',
                title: 'Rediger',
                classes: 'bordered',
                onClick: () => handleEditSubject(subject),
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
  .filters-container {
    display: flex;
    gap: 1rem;
    align-items: flex-end;
  }

  .filter-item {
    display: flex;
    flex-direction: column;
    flex: 1 1 20rem;
    min-width: 3rem;
    max-width: 25rem;
  }

  .group-filter-input {
    border: 2px solid var(--bs-primary);
    height: 48px;
    padding: 0 15px;
  }

  .subjects-grid {
    display: grid;
    grid-template-columns: 2fr 1fr 2fr 1fr 1fr;
    align-items: start;
    gap: 0;
    border-bottom: 1px solid var(--bs-border-color);
  }

  .item.header-row {
    background-color: var(--bs-light);
  }

  .item {
    padding: 0.5rem;
    border-top: 1px solid var(--bs-border-color);
  }

  .item.header {
    font-weight: 800;
  }
</style>
