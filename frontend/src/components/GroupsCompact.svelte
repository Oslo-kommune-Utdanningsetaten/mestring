<script lang="ts">
  import { dataStore } from '../stores/data'
  import { urlStringFrom } from '../utils/functions'
  import { hasUserAccessToPath } from '../stores/access'
  import { USER_ROLES } from '../utils/constants'
  import { usersList } from '../generated/sdk.gen'
  import type { GroupType, UserType } from '../generated/types.gen'
  import GroupTag from './GroupTag.svelte'
  import UserTag from './UserTag.svelte'
  import SubjectTag from './SubjectTag.svelte'
  import Link from './Link.svelte'

  let currentSchool = $derived($dataStore.currentSchool)
  let groups = $derived<GroupType[]>($dataStore.currentUser.allGroups || [])
  let membersByGroupId = $state<Record<string, { teachers: UserType[]; students: UserType[] }>>({})

  const fetchAllmembersByGroupId = async () => {
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
        membersByGroupId = { ...membersByGroupId, [group.id]: { teachers, students } }
      } catch (error) {
        console.error(`Error fetching members for group ${group.id}:`, error)
        membersByGroupId = { ...membersByGroupId, [group.id]: { teachers: [], students: [] } }
      }
    })
  }

  $effect(() => {
    if (currentSchool) {
      fetchAllmembersByGroupId()
    }
  })
</script>

<section class="py-3">
  <h2>Mine grupper</h2>

  {#if groups.length === 0}
    <div class="mt-3">
      🫤 Du har visst ikke tilgang til noen grupper på {currentSchool?.displayName}.
    </div>
  {:else}
    <div class="card shadow-sm mt-4 groups-grid">
      {#each groups as group, i}
        <div class="group-row" class:border-top={i > 0}>
          <div class="group-name">
            <Link to="/groups/{group.id}" title={group.feideId}>
              {group.displayName}
            </Link>
            {#if group.subjectId}
              <SubjectTag subjectId={group.subjectId} />
            {/if}
          </div>

          <div>
            <GroupTag {group} isGroupTypeNameEnabled={true} />
          </div>

          {#if membersByGroupId && Object.hasOwn(membersByGroupId, group.id)}
            <div class="group-teachers d-flex flex-wrap gap-2">
              {#each membersByGroupId[group.id].teachers as teacher}
                <UserTag
                  user={teacher}
                  role={USER_ROLES.TEACHER}
                  allUsers={membersByGroupId[group.id].teachers}
                />
              {/each}
            </div>

            <div class="text-end text-nowrap">
              {#if currentSchool.isStudentListEnabled || $hasUserAccessToPath('/students')}
                <Link
                  to={urlStringFrom({ groupId: group.id }, { path: '/students', mode: 'replace' })}
                >
                  {membersByGroupId[group.id].students.length}
                  {membersByGroupId[group.id].students.length === 1 ? 'elev' : 'elever'}
                </Link>
              {:else}
                {membersByGroupId[group.id].students.length}
                {membersByGroupId[group.id].students.length === 1 ? 'elev' : 'elever'}
              {/if}
            </div>
          {:else}
            <div class="spinner-border spinner-border-sm" role="status">
              <span class="visually-hidden">Henter data...</span>
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</section>

<style>
  .groups-grid {
    display: grid;
    grid-template-columns: minmax(12rem, 20rem) 1fr auto 1fr;
    column-gap: 20px;
    padding: 0 0.75rem;
  }

  .group-row {
    grid-column: 1 / -1;
    display: grid;
    grid-template-columns: subgrid;
    align-items: center;
    padding: 0.5rem 0;
  }

  .group-teachers {
    justify-self: start;
  }

  .group-name {
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
  }
</style>
