<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-radiobutton.js'
  import { usersRetrieve } from '../generated/sdk.gen'
  import type { GroupType, SchoolType } from '../generated/types.gen'
  import type { UserRoleType, UserDecorated } from '../types/models'
  import {
    getPreferredGroupValidity,
    getPreferredMasteryBadgeVariant,
    preferredSchoolYear,
  } from '../stores/localStorageFunctions'
  import { dataStore, currentUser, currentSchool } from '../stores/data'
  import { localStorage } from '../stores/localStorage'
  import { hasUserAccessToPath } from '../stores/access'
  import { USER_ROLES, MASTERY_BADGE_VARIANTS, GROUP_VALIDITY_OPTIONS } from '../utils/constants'
  import { fetchUserData } from '../utils/functions'
  import { getAllSchoolYears, getCurrentSchoolYear } from '../utils/schoolYear'

  import GroupTag from '../components/GroupTag.svelte'
  import Link from '../components/Link.svelte'
  import SchoolSelector from '../components/SchoolSelector.svelte'

  const { userId } = $props<{ userId?: string }>()
  const isProfileMode = $derived($currentUser.id && !userId)

  const isMasteryBarChartVisible = localStorage<boolean>('isMasteryBarChartVisible')
  const isSubjectPolarChartVisible = localStorage<boolean>('isSubjectPolarChartVisible')
  let selectedGroupValidity = $state<GROUP_VALIDITY_OPTIONS>(getPreferredGroupValidity())

  // Options for mastery badge variant selection
  const badgeOptions = [
    { value: MASTERY_BADGE_VARIANTS.BEEHIVE, label: 'Bikube' },
    { value: MASTERY_BADGE_VARIANTS.CIRCLE, label: 'Sirkel' },
    { value: MASTERY_BADGE_VARIANTS.TRIANGLE, label: 'Trekant' },
    { value: MASTERY_BADGE_VARIANTS.SMILEY, label: 'Smiley' },
  ] as const

  // Options for filtering by groups by date validity
  const groupValidityOptions = [
    { value: GROUP_VALIDITY_OPTIONS.INCLUDE, label: 'Alle grupper' },
    { value: GROUP_VALIDITY_OPTIONS.ONLY, label: 'Kun gyldige grupper' },
    { value: GROUP_VALIDITY_OPTIONS.EXCLUDE, label: 'Kun ugyldige grupper' },
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

  // Options for filtering by date validity
  const createdOptions = $derived.by(() => {
    if (!$currentSchool) return []

    const allYears = getAllSchoolYears(new Date($currentSchool.createdAt)).reverse()
    return [
      ...allYears.map(year => ({
        value: year,
        label: year,
      })),
      allYears.length > 1 ? { value: 'all', label: 'Alle år' } : null,
    ].filter(Boolean) as { value: string; label: string }[]
  })

  // Derived values for filtering groups by validity
  const validTeacherGroups = $derived(teacherGroups.filter((g: GroupType) => g.isValid))
  const invalidTeacherGroups = $derived(teacherGroups.filter((g: GroupType) => !g.isValid))
  const validStudentGroups = $derived(studentGroups.filter((g: GroupType) => g.isValid))
  const invalidStudentGroups = $derived(studentGroups.filter((g: GroupType) => !g.isValid))

  const allGroups = $derived(
    isProfileMode ? $currentUser?.allGroups || [] : [...otherTeacherGroups, ...otherStudentGroups]
  )
  const schools = $derived<SchoolType[]>(isProfileMode ? $currentUser?.schools || [] : [])

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
    // set localStorage and reload, which in turn will trigger dataStore to update with school-specific data
    localStorage<SchoolType>('currentSchool').set(school)
    window.location.reload()
  }

  const handleToggleMasteryBarChart = () =>
    isMasteryBarChartVisible.set(!isMasteryBarChartVisible.get())

  const handleToggleSubjectPolarChart = () =>
    isSubjectPolarChartVisible.set(!isSubjectPolarChartVisible.get())

  const handleSelectBadgeVariant = (variant: MASTERY_BADGE_VARIANTS) =>
    localStorage('preferredMasteryBadgeVariant').set(variant)

  const handleSelectGroupValidity = (validity: GROUP_VALIDITY_OPTIONS) => {
    localStorage('preferredGroupValidity').set(validity)
    selectedGroupValidity = getPreferredGroupValidity()
  }

  // When school year is changed by user, also update the group validity (not the other way)
  const handleSelectSchoolYear = (schoolYear: string) => {
    localStorage('preferredSchoolYear').set(schoolYear)
    if (schoolYear === 'all') {
      // All years selected --> include all groups regardless of validity
      localStorage('preferredGroupValidity').set(GROUP_VALIDITY_OPTIONS.INCLUDE)
    } else if (schoolYear === getCurrentSchoolYear()) {
      // Current year selected --> only include valid groups
      localStorage('preferredGroupValidity').set(GROUP_VALIDITY_OPTIONS.ONLY)
    } else {
      // Past year selected --> only include invalid groups
      localStorage('preferredGroupValidity').set(GROUP_VALIDITY_OPTIONS.EXCLUDE)
    }
    // Update local state
    selectedGroupValidity = getPreferredGroupValidity()
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
                  checked={getPreferredMasteryBadgeVariant() === option.value}
                  onchange={() => handleSelectBadgeVariant(option.value)}
                ></pkt-radiobutton>
              {/each}
            </fieldset>
          </div>

          <div class="mb-2">
            <strong>Gruppers gyldighet (på dato fra Feide)</strong>
            <fieldset class="d-flex flex-wrap gap-4 mt-2">
              <legend class="visually-hidden">Velg hvilke grupper som vises</legend>
              {#each groupValidityOptions as option}
                {#key selectedGroupValidity + option.value}
                  <pkt-radiobutton
                    name="preferredGroupValidity"
                    value={option.value}
                    label={option.label}
                    checked={selectedGroupValidity === option.value}
                    onchange={() => handleSelectGroupValidity(option.value)}
                    disabled={!$currentUser?.isSuperadmin}
                    id={'preferredGroupValidity-' + option.value}
                  ></pkt-radiobutton>
                {/key}
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
          <SchoolSelector />
        </div>
      </div>
    {/if}

    <!-- Group access -->
    <div class="card mb-3">
      <div class="card-header d-flex">
        <h3 class="mb-0">Tilgang til grupper</h3>
      </div>

      <div class="card-body">
        <!-- Teacher groups -->
        <h4 class="mt-1 mb-2">Som lærer</h4>
        {#if teacherGroups?.length > 0}
          {#if validTeacherGroups?.length > 0}
            <h5 class="mt-3 mb-2">Dette skoleåret ({getCurrentSchoolYear()})</h5>
            <div class="d-flex flex-wrap gap-2">
              {#each validTeacherGroups as group}
                <GroupTag {group} isGroupNameEnabled={true} href={`/groups/${group.id}/`} />
              {/each}
            </div>
          {/if}
          {#if invalidTeacherGroups?.length > 0}
            <h5 class="mt-3 mb-2">Tidligere år</h5>
            <div class="d-flex flex-wrap gap-2">
              {#each invalidTeacherGroups as group}
                <GroupTag {group} isGroupNameEnabled={true} href={`/groups/${group.id}/`} />
              {/each}
            </div>
          {/if}
        {:else}
          <span class="text-muted">Ikke medlem av noen grupper som lærer</span>
        {/if}

        <!-- Student groups -->
        <h4 class="mt-4 mb-2">Som elev</h4>
        {#if studentGroups?.length > 0}
          {#if validStudentGroups?.length > 0}
            <h5 class="mt-3 mb-2">Dette skoleåret ({getCurrentSchoolYear()})</h5>
            <div class="d-flex flex-wrap gap-2">
              {#each validStudentGroups as group}
                <GroupTag {group} isGroupNameEnabled={true} href={`/groups/${group.id}/`} />
              {/each}
            </div>
          {/if}
          {#if invalidStudentGroups?.length > 0}
            <h5 class="mt-3 mb-2">Tidligere år</h5>
            <div class="d-flex flex-wrap gap-2">
              {#each invalidStudentGroups as group}
                <GroupTag {group} isGroupNameEnabled={true} href={`/groups/${group.id}/`} />
              {/each}
            </div>
          {/if}
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
</style>
