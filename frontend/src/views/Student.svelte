<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-button.js'
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import { dataStore } from '../stores/data'
  import type { GroupReadable, UserReadable } from '../generated/types.gen'
  import { usersRetrieve, usersGroupsRetrieve } from '../generated/sdk.gen'
  import { urlStringFrom, calculateMasterysForStudent } from '../utils/functions'
  import GoalEdit from '../components/GoalEdit.svelte'
  import StudentSubjectGoals from '../components/StudentSubjectGoals.svelte'

  const { studentId } = $props<{ studentId: string }>()
  let student = $state<UserReadable | null>(null)
  let studentGroups = $state<GroupReadable[] | []>([])
  let goalsBySubjectId = $state<Record<string, any>>({})

  const fetchUser = async (userId: string) => {
    try {
      const result = await usersRetrieve({ path: { id: userId } })
      student = result.data!
      fetchGroupsForStudent(student.id)
    } catch (e) {
      console.error(`Could not load student with id ${userId}`, e)
    }
  }

  const fetchGroupsForStudent = async (studentId: string) => {
    try {
      const result = await usersGroupsRetrieve({
        path: { id: studentId },
        query: { roles: 'student' },
      })
      studentGroups = Array.isArray(result.data) ? result.data : []
    } catch (err) {
      console.error(`Could not load groups for ${studentId}`, err)
      studentGroups = []
    }
  }

  $effect(() => {
    if (studentId) {
      fetchUser(studentId)
      calculateMasterysForStudent(studentId).then(result => {
        goalsBySubjectId = result
      })
    }
  })
</script>

<section class="py-3">
  {#if student}
    <h2>Elev: {student.name}</h2>

    <!-- Groups -->
    <div class="card shadow-sm">
      <div class="card-header">Grupper</div>
      <div class="card-body">
        {#if studentGroups}
          <ul class="mb-0">
            {#each studentGroups as group}
              <li>
                <a
                  href={urlStringFrom(
                    { groupId: group.id },
                    {
                      path: '/students',
                      mode: 'replace',
                    }
                  )}
                >
                  {group.displayName}
                </a>
              </li>
            {/each}
          </ul>
        {:else}
          <div class="alert alert-danger">Ikke medlem av noen grupper</div>
        {/if}
      </div>
    </div>

    <!-- Goals and mastery -->
    <div class="card shadow-sm">
      <div class="card-header">Mål</div>

      {#if goalsBySubjectId && Object.keys(goalsBySubjectId).length > 0}
        <ul class="list-group list-group-flush">
          {#each Object.keys(goalsBySubjectId) as subjectId}
            <li class="list-group-item py-3">
              <StudentSubjectGoals {subjectId} {studentId} />
            </li>
          {/each}
        </ul>
      {:else}
        <div class="alert alert-info m-2">Ingen mål for denne eleven</div>
      {/if}
    </div>
  {:else}
    <div class="m-2">Fant ikke eleven</div>
  {/if}
</section>

<style>
</style>
