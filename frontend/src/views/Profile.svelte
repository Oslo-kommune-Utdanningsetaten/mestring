<script lang="ts">
  import { usersRetrieve } from '../generated/sdk.gen'
  import { fetchUserData } from '../utils/functions'
  import { USER_ROLES, MASTERY_BADGE_VARIANTS, GROUP_VALIDITY_OPTIONS } from '../utils/constants'
  import { dataStore, setCurrentSchool, currentUser } from '../stores/data'
  import type { GroupType, SchoolType } from '../generated/types.gen'
  import { localStorage } from '../stores/localStorage'
  import { hasUserAccessToPath } from '../stores/access'
  import type { UserRoleType, UserDecorated } from '../types/models'
  import '@oslokommune/punkt-elements/dist/pkt-radiobutton.js'
  import GroupTag from '../components/GroupTag.svelte'
  import Link from '../components/Link.svelte'

  const { userId } = $props<{ userId?: string }>()
  const isProfileMode = $derived($currentUser.id && !userId)

  const isMasteryBarChartVisible = localStorage<boolean>('isMasteryBarChartVisible')
  const isSubjectPolarChartVisible = localStorage<boolean>('isSubjectPolarChartVisible')
  const preferredMasteryBadgeVariant = localStorage<MASTERY_BADGE_VARIANTS>(
    'preferredMasteryBadgeVariant'
  )
  const preferredGroupValidity = localStorage<GROUP_VALIDITY_OPTIONS>('preferredGroupValidity')

  // Fall back to the default when nothing is stored yet
  const selectedBadgeVariant = $derived(
    $preferredMasteryBadgeVariant || MASTERY_BADGE_VARIANTS.BEEHIVE
  )
  const selectedGroupValidity = $derived($preferredGroupValidity || GROUP_VALIDITY_OPTIONS.ONLY)

  // Options for mastery badge variant selection
  const badgeOptions = [
    { value: MASTERY_BADGE_VARIANTS.BEEHIVE, label: 'Bikube' },
    { value: MASTERY_BADGE_VARIANTS.CIRCLE, label: 'Sirkel' },
    { value: MASTERY_BADGE_VARIANTS.TRIANGLE, label: 'Trekant' },
    { value: MASTERY_BADGE_VARIANTS.SMILEY, label: 'Smiley' },
  ] as const

  // Options for filtering by groups by date validity
  const groupValidityOptions = [
    { value: GROUP_VALIDITY_OPTIONS.INCLUDE, label: 'Alt' },
    { value: GROUP_VALIDITY_OPTIONS.ONLY, label: 'Kun dette skoleåret' },
    { value: GROUP_VALIDITY_OPTIONS.EXCLUDE, label: 'Ikke i dette skoleåret' },
  ] as const

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

  const handleToggleMasteryBarChart = () =>
    isMasteryBarChartVisible.set(!isMasteryBarChartVisible.get())

  const handleToggleSubjectPolarChart = () =>
    isSubjectPolarChartVisible.set(!isSubjectPolarChartVisible.get())

  const handleSelectBadgeVariant = (variant: MASTERY_BADGE_VARIANTS) =>
    localStorage('preferredMasteryBadgeVariant').set(variant)

  const handleSelectGroupValidity = (validity: GROUP_VALIDITY_OPTIONS) =>
    localStorage('preferredGroupValidity').set(validity)

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
            <strong>Roller ved {$dataStore.currentSchool?.displayName.split(' ')[0]}</strong>
            <div class="text-muted">{userRoles.join(', ')}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Settings -->
    {#if isProfileMode}
      <div class="card mb-3">
        <div class="card-header">
          <h3>Innstillinger</h3>
        </div>
        <div class="card-body">
          <div class="mb-4">
            <strong>Mini stolpediagram</strong>
            <pkt-checkbox
              label={$isMasteryBarChartVisible ? 'Vises' : 'Skjules'}
              labelPosition="right"
              isSwitch="true"
              aria-checked={$isMasteryBarChartVisible}
              checked={$isMasteryBarChartVisible}
              onchange={() => handleToggleMasteryBarChart()}
            ></pkt-checkbox>
          </div>

          <div class="mb-4">
            <strong>Radial-diagram pr. elev og fag</strong>
            <pkt-checkbox
              label={$isSubjectPolarChartVisible ? 'Vises' : 'Skjules'}
              labelPosition="right"
              isSwitch="true"
              aria-checked={$isSubjectPolarChartVisible}
              checked={$isSubjectPolarChartVisible}
              onchange={() => handleToggleSubjectPolarChart()}
            ></pkt-checkbox>
          </div>

          <div class="mb-4">
            <strong>Mestringsmerke</strong>
            {#if $hasUserAccessToPath('/dev/badge-lab')}
              <span class="text-muted">
                - [<Link to="/dev/badge-lab">kan testes her</Link>]
              </span>
            {/if}
            <fieldset class="d-flex flex-wrap gap-4 mt-2">
              <legend class="visually-hidden">Velg type mestringsmerke</legend>
              {#each badgeOptions as option}
                <pkt-radiobutton
                  name="preferredMasteryBadgeVariant"
                  value={option.value}
                  label={option.label}
                  checked={selectedBadgeVariant === option.value}
                  onchange={() => handleSelectBadgeVariant(option.value)}
                ></pkt-radiobutton>
              {/each}
            </fieldset>
          </div>

          <div class="mb-2">
            <strong>Synlige data</strong>
            <fieldset class="d-flex flex-wrap gap-4 mt-2">
              <legend class="visually-hidden">Velg type mestringsmerke</legend>
              {#each groupValidityOptions as option}
                <pkt-radiobutton
                  name="preferredMasteryBadgeVariant"
                  value={option.value}
                  label={option.label}
                  checked={selectedGroupValidity === option.value}
                  onchange={() => handleSelectGroupValidity(option.value)}
                ></pkt-radiobutton>
              {/each}
            </fieldset>
          </div>
        </div>
      </div>
    {/if}

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
