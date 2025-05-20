<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-select.js'
  import { onMount } from 'svelte'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { dataStore } from '../stores/data'
  import { urlStringFrom } from '../utils/functions'
  import StudentRow from './StudentRow.svelte'

  import { groupsList, groupsMembersRetrieve } from '../api/sdk.gen'
  import {
    type GroupReadable,
    type NestedGroupUserReadable,
    type BasicUserReadable,
  } from '../api/types.gen'

  const router = useTinyRouter()
  const currentSchool = $derived($dataStore.currentSchool)

  let selectedGroupId = $derived(router.getQueryParam('groupId'))
  let selectedGroup = $state<GroupReadable | null>(null)
  let allGroups = $state<GroupReadable[]>([])
  let teachingGroups = $state<GroupReadable[]>([])
  let basisGroups = $state<GroupReadable[]>([])

  async function fetchGroups() {
    try {
      const result = await groupsList({
        query: {
          school: currentSchool?.id,
        },
      })
      allGroups = result.data || []
      teachingGroups = allGroups.filter(group => group.type === 'undervisning')
      basisGroups = allGroups.filter(group => group.type === 'basis')
    } catch (error) {
      console.error('Error fetching groups:', error)
      allGroups = []
      teachingGroups = []
      basisGroups = []
    }
  }

  async function fetchGroupMembers(groupId: string): Promise<{
    teachers: BasicUserReadable[]
    students: BasicUserReadable[]
  }> {
    console.log('Fetching members:', groupId)

    try {
      const result = await groupsMembersRetrieve({
        path: {
          id: groupId,
        },
      })
      const members: any = result.data || []

      const teachers: BasicUserReadable[] =
        members
          .filter((member: NestedGroupUserReadable) => member.role.name === 'teacher')
          .map((member: NestedGroupUserReadable) => member.user) || []
      const students: BasicUserReadable[] =
        members
          .filter((member: NestedGroupUserReadable) => member.role.name === 'student')
          .map((member: NestedGroupUserReadable) => member.user) || []

      return { teachers, students }
    } catch (error) {
      console.error(`Error fetching members for group ${groupId}:`, error)
      return { teachers: [], students: [] }
    }
  }

  async function handleGroupSelect(groupId: string): Promise<void> {
    if (!groupId) {
      // clear selection and URL
      selectedGroup = null
      history.replaceState(null, '', urlStringFrom({}, { mode: 'replace' }))
      return
    }

    history.replaceState(null, '', urlStringFrom({ groupId }, { mode: 'merge' }))

    // 2) fetch & show the new group
    const { students, teachers } = await fetchGroupMembers(groupId)
    selectedGroup = {
      ...selectedGroup,
      students,
      teachers,
      displayName: allGroups.find(g => g.id === groupId)?.displayName || '',
    }
  }

  onMount(async () => {
    await fetchGroups()
    console.log('Selected groupId:', selectedGroupId)
    if (selectedGroupId) {
      handleGroupSelect(selectedGroupId)
    }
  })
</script>

<section class="py-3">
  <h2>Elever</h2>

  <!-- Filter groups -->
  <div class="d-flex align-items-center gap-2">
    <div class="pkt-inputwrapper">
      <label class="pkt-inputwrapper__label" for="exampleSelect1">
        <span>Velg gruppe</span>
      </label>
      <select
        class="pkt-input"
        id="exampleSelect1"
        onchange={() => handleGroupSelect(event.target.value)}
      >
        <option value="0" selected={!selectedGroupId}>Alle</option>
        {#each allGroups as group}
          <option value={group.id} selected={group.id === selectedGroupId}>
            {group.displayName}
          </option>
        {/each}
      </select>
    </div>

    <a class="link-button" href={urlStringFrom({}, { mode: 'replace' })}>Nullstill</a>
  </div>
</section>

<section class="py-3">
  {#if !selectedGroup}
    <div class="alert alert-info">Ingen gruppe valgt</div>
  {:else}
    <div class="card shadow-sm">
      <!-- Header row -->
      <div class="student-grid-row fw-bold header">
        <div>Navn</div>
        <div>Klasse</div>
        <div>
          <span>Mål</span>
          <div class="group-grid-columns">5 :)</div>
        </div>
        <div>&nbsp;</div>
      </div>

      <!-- Student rows -->
      {#each selectedGroup.students as student}
        <StudentRow {student} />
      {/each}
    </div>
  {/if}
</section>

<style>
  .dropdown-link {
    font-size: 1em !important;
  }

  .dropdown-link:hover {
    text-decoration: none;
  }

  .selected {
    font-weight: bold;
  }
</style>
