<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import '@oslokommune/punkt-elements/dist/pkt-checkbox.js'
  import type {
    UserType,
    NestedUserGroupType,
    NestedUserSchoolType,
    RoleType,
    SchoolType,
    GroupType,
  } from '../generated/types.gen'
  import {
    userGroupsList,
    userSchoolsList,
    userSchoolsDestroy,
    userSchoolsCreate,
  } from '../generated/sdk.gen'
  import { SCHOOL_ADMIN_ROLE, SCHOOL_INSPECTOR_ROLE, NONE_FIELD_VALUE } from '../utils/constants'
  import { dataStore } from '../stores/data'
  import GroupTag from './GroupTag.svelte'
  import { formatDate } from '../utils/functions'

  const { user, school } = $props<{ user: UserType; school: SchoolType }>()
  const adminRole = $derived<RoleType>(
    $dataStore.roles?.find(role => role.name === SCHOOL_ADMIN_ROLE)
  )
  const inspectorRole = $derived<RoleType>(
    $dataStore.roles?.find(role => role.name === SCHOOL_INSPECTOR_ROLE)
  )
  let userGroups = $state<NestedUserGroupType[]>([])
  let userSchools = $state<NestedUserSchoolType[]>([])
  let isLoadingData = $state<boolean>(false)
  let hasLoadedData = $state<boolean>(false)
  let isSchoolInspector = $derived(!!userSchools.find(us => us.role.id === inspectorRole?.id))
  let isSchoolAdmin = $derived(!!userSchools.find(us => us.role.id === adminRole?.id))
  const relevantSchoolRoles = [SCHOOL_INSPECTOR_ROLE, SCHOOL_ADMIN_ROLE]
  let selectedSchoolRole = $derived(
    isSchoolAdmin ? SCHOOL_ADMIN_ROLE : isSchoolInspector ? SCHOOL_INSPECTOR_ROLE : NONE_FIELD_VALUE
  )
  let teacherGroups = $derived(
    <GroupType[]>(userGroups.filter(ug => ug.role.name === 'teacher') || []).map(ug => ug.group)
  )
  let studentGroups = $derived(
    <GroupType[]>(userGroups.filter(ug => ug.role.name === 'student') || []).map(ug => ug.group)
  )

  let newestMembership: NestedUserGroupType | null = $derived(
    [...userGroups].sort(
      (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    )[0]
  )

  //let latestMembership: any = {}

  const fetchUserAffiliations = async () => {
    try {
      isLoadingData = true
      const groupsResult = await userGroupsList({ query: { user: user.id, school: school.id } })
      const schoolsResult = await userSchoolsList({ query: { user: user.id, school: school.id } })
      userGroups = (groupsResult.data || []).sort((a, b) => a.role.name.localeCompare(b.role.name))
      userSchools = schoolsResult.data || []
      hasLoadedData = true
    } catch (error) {
      console.error('Error fetching user data:', error)
      userGroups = []
      userSchools = []
    } finally {
      isLoadingData = false
    }
  }

  const handleRoleChange = async (roleName: string) => {
    if (!user.id || !school.id || !roleName) {
      console.error('Missing information', user, school, roleName)
      return
    }

    const confirmed = confirm(
      `Er du sikker på at du vil endre ${user.name} sin rolle til ${roleName}?`
    )

    if (!confirmed) return

    try {
      // Remove all existing roles
      await Promise.all(
        userSchools
          .filter(us => relevantSchoolRoles.includes(us.role.name))
          .map(async userSchool => {
            return await userSchoolsDestroy({
              path: {
                id: userSchool.id,
              },
            })
          })
      )
      // Add new role
      const roleToAssign = $dataStore.roles?.find(role => role.name === roleName)
      if (roleToAssign) {
        await userSchoolsCreate({
          body: { userId: user.id, schoolId: school.id, roleId: roleToAssign.id },
        })
      }
    } catch (error) {
      console.error('Error changing role:', error)
    } finally {
      fetchUserAffiliations()
    }
  }

  $effect(() => {
    fetchUserAffiliations()
  })
</script>

<div class="user-grid-row">
  <div>
    <div class="fw-semibold">{user.name}</div>
    <div class="text-muted small">{user.email || 'Ingen e-post'}</div>
  </div>
  <div class="text-muted small">{formatDate(user.createdAt)}</div>
  <div class="text-muted small">{formatDate(newestMembership?.createdAt)}</div>
  <div>
    {#if hasLoadedData}
      <div class="small">
        <div class="mb-1">
          <strong>Direkte til skolen:</strong>
          {userSchools.map(us => us.role.name).join(', ') || 'Ingen'}
        </div>
        <div class="d-flex flex-wrap gap-1 mb-1">
          <strong>Lærer:</strong>
          {#each teacherGroups as group (group.id)}
            <GroupTag
              {group}
              isGroupNameEnabled={true}
              href={group.isEnabled ? `/groups/${group.id}/` : undefined}
            />
          {/each}
        </div>
        <div class="d-flex flex-wrap gap-1">
          <strong>Elev:</strong>
          {#each studentGroups as group (group.id)}
            <GroupTag
              {group}
              isGroupNameEnabled={true}
              href={group.isEnabled ? `/groups/${group.id}/` : undefined}
            />
          {/each}
        </div>
      </div>
    {:else}
      <div class="spinner-border spinner-border-sm text-primary" role="status">
        <span class="visually-hidden">Laster...</span>
      </div>
    {/if}
  </div>
  <div>
    {#if userSchools.length > 0 || userGroups.length > 0}
      <div>
        <pkt-select
          name="userSchoolRole"
          value={selectedSchoolRole}
          onchange={(e: Event) => {
            const target = e.target as HTMLSelectElement | null
            const roleName = target?.value || NONE_FIELD_VALUE
            handleRoleChange(roleName)
          }}
        >
          <option value={NONE_FIELD_VALUE}>none</option>
          {#each relevantSchoolRoles as option}
            <option value={option}>
              {option}
            </option>
          {/each}
        </pkt-select>
      </div>
    {/if}
  </div>
</div>
