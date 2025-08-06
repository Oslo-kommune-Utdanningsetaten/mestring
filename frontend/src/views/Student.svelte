<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-button.js'
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import { onMount } from 'svelte'

  import type { GroupReadable, UserReadable, SubjectReadable } from '../generated/types.gen'
  import { usersRetrieve, usersGroupsRetrieve } from '../generated/sdk.gen'
  import { urlStringFrom, subjectIdsViaGroupOrGoal } from '../utils/functions'
  import StudentSubjectGoals from '../components/StudentSubjectGoals.svelte'
  import { dataStore } from '../stores/data'

  const { studentId } = $props<{ studentId: string }>()
  let student = $state<UserReadable | null>(null)
  let groups = $state<GroupReadable[] | []>([])
  let subjects = $state<SubjectReadable[]>([])

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
      groups = Array.isArray(result.data) ? result.data : []
    } catch (err) {
      console.error(`Could not load groups for ${studentId}`, err)
      groups = []
    }
  }

  const fetchSubjects = async (studentId: string) => {
    try {
      const subjectIds = await subjectIdsViaGroupOrGoal(studentId)
      if (subjectIds.length > 0) {
        subjects = $dataStore.subjects.filter((subject: SubjectReadable) =>
          subjectIds.includes(subject.id)
        )
      }
    } catch (err) {
      console.error(`Could not load subjects for ${studentId}`, err)
      subjects = []
    }
  }

  onMount(() => {
    if (studentId) {
      fetchUser(studentId)
      fetchSubjects(studentId)
    }
  })
</script>

<section class="py-3">
  {#if student}
    <h1>Elev: {student.name}</h1>

    <!-- Groups -->
    <div class="card shadow-sm">
      <h2 class="card-header">Grupper</h2>
      <div class="card-body">
        {#if groups}
          <ul class="mb-0">
            {#each groups as group}
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
      <h2 class="card-header">Mål</h2>

      {#if subjects.length > 0}
        <ul class="list-group list-group-flush">
          {#each subjects as subject (subject.id)}
            <li class="list-group-item py-3">
              <StudentSubjectGoals subjectId={subject.id} {studentId} />
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
