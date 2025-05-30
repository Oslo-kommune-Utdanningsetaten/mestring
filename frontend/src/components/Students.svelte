<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-select.js'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { dataStore } from '../stores/data'
  import { urlStringFrom } from '../utils/functions'
  import StudentRow from './StudentRow.svelte'

  import { groupsList, groupsMembersRetrieve, usersGroupsRetrieve } from '../api/sdk.gen'
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
  let students = $state<BasicUserReadable[]>([])
  let groupsByStudentId = $state({})

  async function fetchGroups() {
    try {
      const result = await groupsList({
        query: {
          school: currentSchool?.id,
        },
      })
      allGroups = result.data || []
    } catch (error) {
      console.error('Error fetching groups:', error)
      allGroups = []
    }
  }

  async function fetchGroupMembers(groupId: string) {
    try {
      const result = await groupsMembersRetrieve({
        path: {
          id: groupId,
        },
      })
      const members: any = result.data || []
      console.log(`Fetched members for group ${groupId}:`, members)
      students =
        members
          .filter((member: NestedGroupUserReadable) => member.role.name === 'student')
          .map((member: NestedGroupUserReadable) => member.user) || []
      students.forEach((student: BasicUserReadable) => {
        fetchGroupsForStudent(student.id)
      })
    } catch (error) {
      console.error(`Error fetching members for group ${groupId}:`, error)
      students = []
    }
  }

  async function fetchGroupsForStudent(studentId: string) {
    try {
      const result = await usersGroupsRetrieve({
        path: { id: studentId },
        // only return the groups where this user is a student
        query: { roles: 'student' },
      })
      const studentGroups: GroupReadable[] = result.data || []
      groupsByStudentId = {
        ...groupsByStudentId,
        [studentId]: studentGroups,
      }
    } catch (err) {
      console.error(`Could not load groups for ${studentId}`, err)
      groupsByStudentId = {
        ...groupsByStudentId,
        [studentId]: [],
      }
    }
  }

  function handleGroupSelect(groupId: string): void {
    if (groupId && groupId !== '0') {
      window.location.href = urlStringFrom({ groupId }, { mode: 'merge' })
    } else {
      window.location.href = urlStringFrom({}, { mode: 'replace' })
    }
  }

  $effect(() => {
    if (currentSchool) {
      fetchGroups().then(() => {
        if (selectedGroupId) {
          selectedGroup = allGroups.find(group => group.id === selectedGroupId) || null
          fetchGroupMembers(selectedGroupId)
        }
      })
    }
  })
</script>

<section class="py-3">
  <h2 class="pb-2">Elever</h2>

  <!-- Filter groups -->
  <div class="d-flex align-items-center gap-2">
    <div class="pkt-inputwrapper">
      <select
        class="pkt-input"
        id="groupSelect"
        onchange={(e: Event) => handleGroupSelect((e.target as HTMLSelectElement).value)}
      >
        <option value="0" selected={!selectedGroupId}>Velg gruppe</option>
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
    <pre>{JSON.stringify(groupsByStudentId, null, 2)}</pre>
    <div class="card shadow-sm">
      <!-- Header row -->
      <div class="student-grid-row fw-bold header">
        <div>Navn</div>
        <div>Klasse</div>
        <div>
          Fag
          <div class="group-grid-columns">
            <span>as</span>
            <span>as</span>
            <span>as</span>
            <span>as</span>
          </div>
        </div>
      </div>

      <!-- Student rows -->
      {#each students as student}
        <StudentRow {student} />
      {/each}
    </div>
  {/if}
</section>

<style>
</style>
