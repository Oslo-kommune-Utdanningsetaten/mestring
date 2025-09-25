<script lang="ts">
  import { dataStore } from '../stores/data'
  import { urlStringFrom } from '../utils/functions'
  import { TEACHER_ROLE, STUDENT_ROLE } from '../utils/constants'
  import { groupsList, usersList } from '../generated/sdk.gen'
  import type { GroupReadable, UserReadable } from '../generated/types.gen'

  let currentSchool = $derived($dataStore.currentSchool)
  let groups = $state<GroupReadable[]>([])
  let groupMembers = $state<Record<string, { teachers: UserReadable[]; students: UserReadable[] }>>(
    {}
  )

  const fetchGroups = async () => {
    try {
      const result = await groupsList({
        query: { school: currentSchool?.id, isEnabled: true },
      })
      groups = result.data || []
    } catch (error) {
      console.error('Error fetching groups:', error)
      groups = []
    }
  }

  const fetchAllGroupMembers = async () => {
    groups.forEach(async group => {
      try {
        const teachersResult = await usersList({
          query: { groups: group.id, school: currentSchool.id, roles: TEACHER_ROLE },
        })
        const studentsResult = await usersList({
          query: { groups: group.id, school: currentSchool.id, roles: STUDENT_ROLE },
        })
        const teachers = teachersResult.data || []
        const students = studentsResult.data || []
        groupMembers = { ...groupMembers, [group.id]: { teachers, students } }
      } catch (error) {
        console.error(`Error fetching members for group ${group.id}:`, error)
        groupMembers = { ...groupMembers, [group.id]: { teachers: [], students: [] } }
      }
    })
  }

  $effect(() => {
    if (currentSchool) {
      fetchGroups().then(() => {
        fetchAllGroupMembers()
      })
    }
  })
</script>

<section class="py-3">
  <h2>Mine grupper</h2>
  <section class="py-2">
    {#if groups.length === 0}
      <div class="alert alert-info">Du har visst ikke tilgang til noen grupper</div>
    {:else}
      <div class="card shadow-sm">
        <!-- Header row -->
        <div class="group-card-header row fw-bold bg-light border-bottom p-3 mx-0">
          <div class="col-3">Gruppe</div>
          <div class="col-3">Elever</div>
          <div class="col-6">Lærere</div>
        </div>

        <!-- Student rows -->
        {#each groups as group}
          <div class="row align-items-center border-bottom p-3 mx-0">
            <div class="col-3">
              <a href="/groups/{group.id}">
                {group.displayName}
              </a>
            </div>
            <div class="col-3">
              {#if groupMembers && Object.hasOwn(groupMembers, group.id)}
                <a
                  href={urlStringFrom(
                    { groupId: group.id },
                    {
                      path: '/students',
                      mode: 'replace',
                    }
                  )}
                >
                  {groupMembers[group.id].students.length}
                  {groupMembers[group.id].students.length === 1 ? 'elev' : 'elever'}
                </a>
              {:else}
                <div class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Henter data...</span>
                </div>
              {/if}
            </div>
            <div class="col-6">
              {#if groupMembers && Object.hasOwn(groupMembers, group.id)}
                {groupMembers[group.id].teachers.map(m => m.name).join(', ')}
              {:else}
                <div class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Henter data...</span>
                </div>
              {/if}
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </section>
</section>

<style>
</style>
