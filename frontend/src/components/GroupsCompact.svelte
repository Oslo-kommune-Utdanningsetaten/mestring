<script lang="ts">
  import type { GroupType, UserType } from '../generated/types.gen'
  import { usersList } from '../generated/sdk.gen'
  import { currentSchool, currentUser } from '../stores/data'
  import { urlStringFrom } from '../utils/functions'
  import { hasUserAccessToPath } from '../stores/access'
  import { USER_ROLES } from '../utils/constants'

  import GroupTag from './GroupTag.svelte'
  import UserTag from './UserTag.svelte'
  import SubjectTag from './SubjectTag.svelte'
  import Link from './Link.svelte'

  let groups = $derived<GroupType[]>($currentUser.allGroups || [])
  let membersByGroupId = $state<Record<string, { teachers: UserType[]; students: UserType[] }>>({})

  const fetchAllmembersByGroupId = async () => {
    await Promise.all(
      groups.map(async group => {
        try {
          const [teachersResult, studentsResult] = await Promise.all([
            usersList({
              query: {
                groups: group.id,
                school: $currentSchool.id,
                roles: USER_ROLES.TEACHER,
              },
            }),
            usersList({
              query: {
                groups: group.id,
                school: $currentSchool.id,
                roles: USER_ROLES.STUDENT,
              },
            }),
          ])

          const teachers = teachersResult.data || []
          const students = studentsResult.data || []
          membersByGroupId = { ...membersByGroupId, [group.id]: { teachers, students } }
        } catch (error) {
          console.error(`Error fetching members for group ${group.id}:`, error)
          membersByGroupId = {
            ...membersByGroupId,
            [group.id]: { teachers: [], students: [] },
          }
        }
      })
    )
  }

  $effect(() => {
    if ($currentSchool) {
      fetchAllmembersByGroupId()
    }
  })
</script>

<section class="py-3">
  <h2>Mine grupper</h2>

  {#if groups.length === 0}
    <div class="mt-3">
      🫤 Du har visst ikke tilgang til noen grupper på {$currentSchool?.displayName}.
    </div>
  {:else}
    <div class="card shadow-sm mt-4 groups-grid">
      {#each groups as group, i}
        <div class="group-row" class:border-top={i > 0}>
          <div class="group-name">
            <GroupTag
              href="/groups/{group.id}"
              {group}
              isGroupTypeNameEnabled={true}
              isGroupNameEnabled={true}
            />
          </div>

          <div class="subject-name">
            {#if group.subjectId}
              <SubjectTag subjectId={group.subjectId} />
            {/if}
          </div>

          {#if membersByGroupId && Object.hasOwn(membersByGroupId, group.id)}
            <div class="group-teachers d-flex flex-wrap gap-2">
              {#each membersByGroupId[group.id].teachers as teacher}
                <UserTag
                  user={teacher}
                  role={USER_ROLES.TEACHER}
                  allUsers={membersByGroupId[group.id].teachers}
                  href="/users/{teacher.id}"
                />
              {/each}
            </div>

            <div class="text-end text-nowrap">
              {#if $hasUserAccessToPath('/students')}
                <Link
                  to={urlStringFrom({ group: group.id }, { path: '/students', mode: 'replace' })}
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
    grid-template-columns: auto auto auto auto;
    column-gap: 15px;
  }

  .group-row {
    grid-column: 1 / -1;
    display: grid;
    grid-template-columns: subgrid;
    align-items: center;
    padding: 1rem;
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
