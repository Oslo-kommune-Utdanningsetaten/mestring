<script lang="ts">
  import { dataStore } from '../stores/data'
  import { urlStringFrom } from '../utils/functions'
  import { groupsList, groupsMembersRetrieve } from '../generated/sdk.gen'
  import type { GroupReadable, NestedGroupUserReadable } from '../generated/types.gen'

  const currentSchool = $derived($dataStore.currentSchool)
  const currentUser = $derived($dataStore.currentUser)
  let groups = $state<GroupReadable[]>([])
  let isAllGroupsTypesEnabled = $state<boolean>(false)
  let groupMembers = $state<
    Record<string, { teachers: NestedGroupUserReadable[]; students: NestedGroupUserReadable[] }>
  >({})

  const fetchGroups = async () => {
    const options = isAllGroupsTypesEnabled
      ? { school: currentSchool?.id }
      : { school: currentSchool?.id, type: 'basis' }
    try {
      const result = await groupsList({
        query: options,
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
        const result = await groupsMembersRetrieve({
          path: {
            id: group.id,
          },
        })
        const members: any = result.data || []
        const teachers =
          members.filter((member: NestedGroupUserReadable) => member.role.name === 'teacher') || []
        const students =
          members.filter((member: NestedGroupUserReadable) => member.role.name === 'student') || []
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
  <h2 class="mb-4">Mine grupper</h2>
  <p class="d-flex align-items-center gap-2">
    Dette er <span class="fw-bold">
      {#if isAllGroupsTypesEnabled}
        alle gruppene
      {:else}
        basisgruppene
      {/if}
    </span>
    du har tilgang til.
  </p>
  <div class="pkt-input-check">
    <div class="pkt-input-check__input">
      <input
        class="pkt-input-check__input-checkbox"
        type="checkbox"
        role="switch"
        id="groupTypeSwitch"
        bind:checked={isAllGroupsTypesEnabled}
      />
      <label class="pkt-input-check__input-label" for="groupTypeSwitch">Vis alle grupper</label>
    </div>
  </div>

  <section class="py-3">
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
                {groupMembers[group.id].teachers.map(m => m.user.name).join(', ')}
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
