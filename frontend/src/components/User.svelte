<script lang="ts">
  import ButtonMini from './ButtonMini.svelte'
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import '@oslokommune/punkt-elements/dist/pkt-checkbox.js'

  import type {
    UserReadable,
    NestedUserGroupReadable,
    NestedUserSchoolReadable,
    RoleReadable,
    SchoolReadable,
  } from '../generated/types.gen'
  import {
    userGroupsList,
    userSchoolsList,
    userSchoolsDestroy,
    userSchoolsCreate,
  } from '../generated/sdk.gen'
  import { SCHOOL_ADMIN_ROLE } from '../utils/constants'
  import { dataStore } from '../stores/data'

  const { user, school } = $props<{ user: UserReadable; school: SchoolReadable }>()
  const adminRole = $derived<RoleReadable>(
    $dataStore.roles?.find(role => role.name === SCHOOL_ADMIN_ROLE)
  )
  let userGroups = $state<NestedUserGroupReadable[]>([])
  let userSchools = $state<NestedUserSchoolReadable[]>([])
  let isLoadingData = $state<boolean>(false)
  let hasLoadedData = $state<boolean>(false)
  let isSchoolAdmin = $derived(!!userSchools.find(us => us.role.id === adminRole?.id))

  const fetchUserAffiliations = async () => {
    try {
      isLoadingData = true
      const groupsResult = await userGroupsList({ query: { user: user.id, school: school.id } })
      const schoolsResult = await userSchoolsList({ query: { user: user.id, school: school.id } })
      userGroups = groupsResult.data || []
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

  const handleToggleSchoolAdminStatus = async () => {
    if (!user.id || !school.id || !adminRole.id) {
      console.error('Missing user, school, or admin role information', user, school, adminRole)
      return
    }
    try {
      if (isSchoolAdmin) {
        // Remove admin role
        const userGroupAdmin = userSchools.find(us => us.role.name === SCHOOL_ADMIN_ROLE)
        if (userGroupAdmin) {
          await userSchoolsDestroy({
            path: {
              id: userGroupAdmin.id,
            },
          })
        }
      } else {
        // Add admin role
        await userSchoolsCreate({
          body: { userId: user.id, schoolId: school.id, roleId: adminRole.id },
        })
      }
    } catch (error) {
      console.error('Error toggling school admin status:', error)
    } finally {
      fetchUserAffiliations()
    }
  }
</script>

<div class="row p-2 border-bottom mx-0">
  <div class="col-4">
    <div class="fw-semibold">{user.name}</div>
    <div class="text-muted small">{user.email || 'Ingen e-post'}</div>
  </div>
  <div class="col-6">
    {#if hasLoadedData}
      <div class="small">
        <div>
          <strong>Direkte til skolen:</strong>
          {userSchools.map(us => us.role.name).join(', ') || 'Ingen'}
        </div>
        <div>
          <strong>Grupper på skolen:</strong>
          {userGroups.map(ug => ug.group.displayName).join(', ') || 'Ingen'}
        </div>
      </div>
    {/if}
  </div>
  <div class="col-2">
    {#if userSchools.length > 0 || userGroups.length > 0}
      <pkt-checkbox
        label="Admin"
        labelPosition="left"
        isSwitch="true"
        aria-checked={isSchoolAdmin}
        checked={isSchoolAdmin}
        onchange={() => handleToggleSchoolAdminStatus()}
      ></pkt-checkbox>
    {:else}
      <div class="pkt-input-check">
        <ButtonMini
          options={{
            title: 'Hent tilknytninger',
            iconName: 'process-back',
            skin: 'secondary',
            variant: 'icon-only',
            classes: '',
            onClick: () => fetchUserAffiliations(),
          }}
        >
          Hent tilknytninger
        </ButtonMini>
      </div>
    {/if}
  </div>
</div>
