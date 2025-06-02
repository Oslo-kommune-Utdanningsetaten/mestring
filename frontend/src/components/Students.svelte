<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-select.js'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { dataStore } from '../stores/data'
  import { urlStringFrom } from '../utils/functions'
  import StudentRow from './StudentRow.svelte'

  import { groupsList, groupsMembersRetrieve, usersGoalsRetrieve } from '../api/sdk.gen'
  import {
    type GroupReadable,
    type GoalReadable,
    type NestedGroupUserReadable,
    type BasicUserReadable,
  } from '../api/types.gen'

  const router = useTinyRouter()
  const currentSchool = $state($dataStore.currentSchool)
  const subjects = $state($dataStore.subjects)

  let selectedGroupId = $derived(router.getQueryParam('groupId'))
  let selectedGroup = $state<GroupReadable | null>(null)
  let allGroups = $state<GroupReadable[]>([])
  let students = $state<BasicUserReadable[]>([])
  let groupsByStudentId = $state({})

  async function fetchAllGroups() {
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

  async function fetchMembersOfSelectedGroup(groupId: string) {
    try {
      const result = await groupsMembersRetrieve({
        path: {
          id: groupId,
        },
      })
      const members: any = result.data || []
      students =
        members
          .filter((member: NestedGroupUserReadable) => member.role.name === 'student')
          .map((member: NestedGroupUserReadable) => member.user) || []
    } catch (error) {
      console.error(`Error fetching members for group ${groupId}:`, error)
      students = []
    }
  }

  async function getUniqueSubjectsForStudents(students: BasicUserReadable[]): Promise<string[]> {
    const goalsArrays = await Promise.all(
      students.map(async (student): Promise<GoalReadable[]> => {
        const result = await usersGoalsRetrieve({
          path: {
            id: student.id,
          },
        })
        return Array.isArray(result.data) ? result.data : []
      })
    )
    const uniqueSubjects = new Set<string>()
    goalsArrays.forEach(goals => {
      if (goals) {
        goals.forEach(goal => {
          const subject = $dataStore.subjects.find(s => s.id === goal.subjectId)
          if (subject) {
            uniqueSubjects.add(subject.displayName)
          }
        })
      }
    })
    return Array.from(uniqueSubjects)
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
      fetchAllGroups().then(() => {
        if (selectedGroupId) {
          selectedGroup = allGroups.find(group => group.id === selectedGroupId) || null
          fetchMembersOfSelectedGroup(selectedGroupId).then(() => {
            groupsByStudentId = {}
            getUniqueSubjectsForStudents(students).then(uniqueSubjects => {
              // TODO: pick up here, this is where we can use uniqueSubjects
              console.log('Unique subjects:', uniqueSubjects)
            })
          })
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
        <div class="group-grid-columns">
          <span>as</span>
          <span>as</span>
          <span>as</span>
          <span>as</span>
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
