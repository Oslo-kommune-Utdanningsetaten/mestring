<script lang="ts">
  import { useTinyRouter } from 'svelte-tiny-router'
  import { dataStore } from '../stores/data'
  import { urlStringFrom } from '../utils/functions'
  import { hasUserAccessToPath } from '../stores/access'
  import { USER_ROLES } from '../utils/constants'
  import { usersList } from '../generated/sdk.gen'
  import type { GroupType, UserType } from '../generated/types.gen'
  import GroupTag from '../components/GroupTag.svelte'
  import UserTag from '../components/UserTag.svelte'
  import Link from '../components/Link.svelte'
  import GroupsCompare from '../components/GroupsCompare.svelte'
  import GroupsWithSubjects from '../components/GroupsWithSubjects.svelte'

  let currentSchool = $derived($dataStore.currentSchool)
  let groups = $derived<GroupType[]>($dataStore.currentUser.allGroups || [])
  let groupMembers = $state<Record<string, { teachers: UserType[]; students: UserType[] }>>({})

  const router = useTinyRouter()
  const groupIds = $derived(router.getQueryParam('groups')?.split(',') || [])

  const fetchAllGroupMembers = async () => {
    groups.forEach(async group => {
      try {
        const teachersResult = await usersList({
          query: { groups: group.id, school: currentSchool.id, roles: USER_ROLES.TEACHER },
        })
        const studentsResult = await usersList({
          query: { groups: group.id, school: currentSchool.id, roles: USER_ROLES.STUDENT },
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

  const getSubjectName = (subjectId: string) => {
    const subject = $dataStore.subjects.find(subj => subj.id === subjectId)
    return subject ? subject.displayName : 'Ukjent fag'
  }

  $effect(() => {
    if (currentSchool) {
      fetchAllGroupMembers()
    }
  })
</script>

{#if groupIds.length}
  <GroupsWithSubjects {groupIds} />
{:else}
  <section class="py-3">
    <h2>Mine grupper</h2>

    {#if groups.length === 0}
      <div class="mt-3">
        🫤 Du har visst ikke tilgang til noen grupper på {currentSchool?.displayName}.
      </div>
    {:else}
      {#each groups as group}
        <div class="card shadow-sm p-3">
          <h3 class="mt-1 mb-3" title={group.feideId}>
            <Link to="/groups/{group.id}">
              {group.displayName}
            </Link>
          </h3>

          <div class="d-flex align-items-center gap-2">
            <GroupTag {group} isGroupTypeNameEnabled={true} />

            <!-- teachers -->
            {#if groupMembers && Object.hasOwn(groupMembers, group.id)}
              {#each groupMembers[group.id].teachers as teacher}
                <UserTag
                  user={teacher}
                  role={USER_ROLES.TEACHER}
                  allUsers={groupMembers[group.id].teachers}
                />
              {/each}
            {/if}
          </div>

          {#if group.subjectId}
            <div class="mt-3">
              {getSubjectName(group.subjectId)}
            </div>
          {/if}

          <!-- students -->
          <div class="mt-3 mb-1">
            {#if groupMembers && Object.hasOwn(groupMembers, group.id)}
              {#if currentSchool.isStudentListEnabled || $hasUserAccessToPath('/students')}
                <Link
                  to={urlStringFrom(
                    { groupId: group.id },
                    {
                      path: '/students',
                      mode: 'replace',
                    }
                  )}
                >
                  {groupMembers[group.id].students.length}
                  {groupMembers[group.id].students.length === 1 ? 'elev' : 'elever'}
                </Link>
              {:else}
                {groupMembers[group.id].students.length}
                {groupMembers[group.id].students.length === 1 ? 'elev' : 'elever'}
              {/if}
            {:else}
              <div class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Henter data...</span>
              </div>
            {/if}
          </div>
        </div>
      {/each}
    {/if}
  </section>
{/if}

<style>
</style>
