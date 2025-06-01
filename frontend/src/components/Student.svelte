<script lang="ts">
  import { dataStore } from '../stores/data'
  import {
    type GroupReadable,
    type UserReadable,
    type NestedGroupUserReadable,
    type BasicUserReadable,
  } from '../api/types.gen'
  import { usersRetrieve, usersGroupsRetrieve } from '../api/sdk.gen'
  import { urlStringFrom } from '../utils/functions'

  const { studentId } = $props<{ studentId: string }>()
  let student = $state<UserReadable | null>(null)
  let studentGroups = $state<GroupReadable[] | []>([])

  async function fetchUser(userId: string) {
    try {
      const result = await usersRetrieve({ path: { id: userId } })
      student = result.data!
      fetchGroupsForStudent(student.id)
    } catch (e) {
      console.error(`Could not load student with id ${userId}`, e)
    }
  }

  async function fetchGroupsForStudent(studentId: string) {
    try {
      const result = await usersGroupsRetrieve({
        path: { id: studentId },
        // only return the groups where this user is a student
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
    }
  })
</script>

<section class="py-3">
  {#if student}
    <h2>{student.name}</h2>
    <h3>Grupper</h3>
    {#if studentGroups}
      <ul class="student-info">
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
      <h3>Mål</h3>
    {/if}
  {:else}
    <div class="alert alert-danger">Fant ikke eleven</div>
  {/if}
</section>
