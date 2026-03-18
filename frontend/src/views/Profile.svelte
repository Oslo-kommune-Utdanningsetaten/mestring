<script lang="ts">
  import { usersRetrieve } from '../generated/sdk.gen'
  import { fetchUserData } from '../utils/functions'
  import { USER_ROLES } from '../utils/constants'
  import { dataStore, setCurrentSchool, currentUser } from '../stores/data'
  import type { GroupType, SchoolType, UserType, UserSchoolType } from '../generated/types.gen'
  import GroupTag from '../components/GroupTag.svelte'
  import type { UserRoleType, UserDecorated } from '../types/models'

  const { userId } = $props<{ userId?: string }>()
  const isProfileMode = $derived($currentUser.id && !userId)

  // For admin viewing another user's profile
  let otherUser = $state<UserDecorated | undefined>(undefined)
  let otherUserRoles = $state<UserRoleType[]>([])
  let otherTeacherGroups = $state<GroupType[]>([])
  let otherStudentGroups = $state<GroupType[]>([])

  // Derived values that work in both modes
  const user = $derived(isProfileMode ? $currentUser : otherUser)
  const userRoles = $derived(isProfileMode ? $currentUser?.roles || [] : otherUserRoles)
  const teacherGroups = $derived(
    isProfileMode ? $currentUser?.teacherGroups || [] : otherTeacherGroups
  )
  const studentGroups = $derived(
    isProfileMode ? $currentUser?.studentGroups || [] : otherStudentGroups
  )
  const allGroups = $derived(
    isProfileMode ? $currentUser?.allGroups || [] : [...otherTeacherGroups, ...otherStudentGroups]
  )
  const schools = $derived<SchoolType[]>(isProfileMode ? $currentUser?.schools || [] : [])

  const groupsCount = $derived(allGroups.length)

  const otherGroups = $derived.by(() => {
    if (!allGroups || !teacherGroups || !studentGroups) return []
    return allGroups
      .filter((g: GroupType) => !teacherGroups.map((tg: GroupType) => tg.id).includes(g.id))
      .filter((g: GroupType) => !studentGroups.map((sg: GroupType) => sg.id).includes(g.id))
  })

  const loadUserData = async (userId: string) => {
    const [userResult, userData] = await Promise.all([
      usersRetrieve({ path: { id: userId } }),
      fetchUserData(userId, $dataStore.currentSchool?.id),
    ])
    otherUser = userResult.data
    if (!otherUser) {
      console.error(`User with id ${userId} not found`)
      return
    }
    otherTeacherGroups = userData.teacherGroups
    otherStudentGroups = userData.studentGroups
    const userSchools = userData.userSchools

    const isSchoolAdmin = !!userSchools.some(
      userSchool =>
        userSchool.role.name === USER_ROLES.ADMIN &&
        userSchool.school.id === $dataStore.currentSchool?.id
    )
    const isSchoolInspector = !!userSchools.some(
      userSchool =>
        userSchool.role.name === USER_ROLES.INSPECTOR &&
        userSchool.school.id === $dataStore.currentSchool?.id
    )
    otherUserRoles = [
      otherStudentGroups.length > 0 ? USER_ROLES.STUDENT : null,
      otherTeacherGroups.length > 0 ? USER_ROLES.TEACHER : null,
      isSchoolAdmin ? USER_ROLES.ADMIN : null,
      isSchoolInspector ? USER_ROLES.INSPECTOR : null,
      otherUser.isSuperadmin ? USER_ROLES.SUPERADMIN : null,
    ].filter(Boolean) as UserRoleType[]
  }

  const handleSelectSchool = (school: SchoolType) => {
    setCurrentSchool(school)
  }

  $effect(() => {
    // Only load data when viewing another user's profile (admin mode)
    if (!isProfileMode && userId) {
      loadUserData(userId)
    }
  })
</script>

{#if user}
  <section class="container my-4">
    {#if isProfileMode}
      <h2 class="mb-4">Min side</h2>
    {/if}

    <!-- User Information -->
    <div class="card mb-3">
      <div class="card-header">
        <h3>Brukerinformasjon</h3>
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-3 mb-2">
            <strong>Navn</strong>
            <div class="text-muted">{user.name}</div>
          </div>
          <div class="col-md-3 mb-2">
            <strong>E-post</strong>
            <div class="text-muted">{user.email}</div>
          </div>
          <div class="col-md-3 mb-2">
            <strong>Intern ID</strong>
            <div class="text-muted">{user.id}</div>
          </div>
          <div class="col-md-3 mb-2">
            <strong>Roller</strong>
            <div class="text-muted">{userRoles.join(', ')}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- School selection -->
    {#if isProfileMode}
      <div class="card">
        <div class="card-header">
          <h3>Aktiv skole</h3>
        </div>
        <div class="card-body">
          {#if schools.length > 0}
            <div class="row g-2">
              {#each schools as school}
                <div class="col-md-6">
                  <button
                    class="btn w-100 {$dataStore.currentSchool?.id === school.id
                      ? 'btn-primary'
                      : 'btn-outline-secondary'}"
                    onclick={() => handleSelectSchool(school)}
                  >
                    {school.displayName}
                  </button>
                </div>
              {/each}
            </div>
          {:else}
            <span class="text-muted">
              Du er visst ikke tilknyttet noen skoler som bruker denne tjenesten
            </span>
          {/if}
        </div>
      </div>
    {/if}

    <!-- Group access -->
    <div class="card mb-3">
      <div class="card-header d-flex">
        <h3 class="mb-0">Tilgang til grupper ({groupsCount})</h3>
      </div>
      <div class="card-body">
        <!-- Teacher groups -->
        <h4 class="mt-1 mb-2">Som lærer</h4>
        {#if teacherGroups?.length > 0}
          <div class="d-flex flex-wrap gap-2">
            {#each teacherGroups as group}
              <GroupTag {group} isGroupNameEnabled={true} href={`/groups/${group.id}/`} />
            {/each}
          </div>
        {:else}
          <span class="text-muted">Ikke medlem av noen grupper som lærer</span>
        {/if}

        <!-- Student groups -->
        <h4 class="mt-4 mb-2">Som elev</h4>
        {#if studentGroups?.length > 0}
          <div class="d-flex flex-wrap gap-2">
            {#each studentGroups as group}
              <GroupTag {group} isGroupNameEnabled={true} href={`/groups/${group.id}/`} />
            {/each}
          </div>
        {:else}
          <span class="text-muted">Ikke medlem av noen grupper som elev</span>
        {/if}

        <!-- Other groups -->
        <h4 class="mt-4 mb-2">Øvirge tilganger</h4>
        {#if otherGroups?.length > 0}
          <div class="d-flex flex-wrap gap-2">
            {#each otherGroups as group}
              <GroupTag {group} isGroupNameEnabled={true} href={`/groups/${group.id}/`} />
            {/each}
          </div>
        {:else}
          <span class="text-muted">Ingen øvrige tilganger</span>
        {/if}
      </div>
    </div>
  </section>
{:else}
  no user
{/if}

<style>
  button {
    border-radius: 0px;
  }
</style>
