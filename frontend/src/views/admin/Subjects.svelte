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
  <ButtonMini
    options={{
      title: 'Nytt fag',
      iconName: 'plus-sign',
      skin: 'primary',
      variant: 'label-only',
      classes: '',
      onClick: () => handleEditSubject(null),
    }}
  >
    Nytt fag
  </ButtonMini>

  <div class="mt-4">
    {#if !filteredSubjects.length}
      <div class="alert alert-info">No subjects available for the selected school.</div>
    {:else}
      {#each filteredSubjects as subject}
        <div class="card shadow-sm">
          <div class="card-body">
            <h3 class="card-title">
              {subject.displayName}
            </h3>
            <div class="compact-grid">
              {#if subject.ownedBySchoolId}
                <div class="row">
                  <span class="col-2">Eies av</span>
                  <span class="col-10">
                    {schools.find(s => s.id === subject.ownedBySchoolId)?.displayName}
                  </span>
                </div>
              {/if}
              <div class="row">
                <span class="col-2">Grupper</span>
                <span class="col-10">
                  {#if groupsBySubjectId[subject.id].length > 0}
                    {@render groupsInfo(groupsBySubjectId[subject.id])}
                  {:else}
                    <span class="fst-italic">ingen</span>
                  {/if}
                </span>
              </div>
              <div class="row">
                <span class="col-2">Grepkode</span>
                <span class="col-10 {subject.grepCode ? '' : 'fst-italic'}">
                  {subject.grepCode || 'ukjent'}
                </span>
              </div>
              <div class="row">
                <span class="col-2">Opplæringsfag</span>
                <span class="col-10 {subject.grepGroupCode ? '' : 'fst-italic'}">
                  {subject.grepGroupCode || 'ukjent'}
                </span>
              </div>
            </div>

            {#if subject.ownedBySchoolId}
              <ButtonMini
                options={{
                  title: 'Rediger',
                  iconName: 'edit',
                  skin: 'secondary',
                  variant: 'icon-left',
                  classes: 'my-2 me-2',
                  onClick: () => handleEditSubject(subject),
                }}
              >
                Rediger
              </ButtonMini>

              <ButtonMini
                options={{
                  title: 'Slett',
                  iconName: 'trash-can',
                  skin: 'secondary',
                  variant: 'icon-left',
                  classes: 'my-2',
                  onClick: () => handleDeleteSubject(subject.id),
                }}
              >
                Slett
              </ButtonMini>
            {/if}
          </div>
        </div>
      {/each}
    {/if}
  </div>
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
  .compact-grid {
    margin-bottom: 1rem;
  }
  .compact-grid .row {
    font-size: small;
  }
  .group-filter-input {
    border: 2px solid var(--bs-primary);
    border-radius: 0;
    height: 48px;
    margin-top: 0px;
    padding-left: 15px;
    margin-left: 10px;
  }
</style>
