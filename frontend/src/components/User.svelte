<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-button.js'
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import type {
    UserReadable,
    NestedUserGroupReadable,
    NestedUserSchoolReadable,
  } from '../generated/types.gen'
  import { userGroupsList, userSchoolsList } from '../generated/sdk.gen'

  const { user, schoolId } = $props<{ user: UserReadable; schoolId: string | null }>()

  let userGroups = $state<NestedUserGroupReadable[]>([])
  let userSchools = $state<NestedUserSchoolReadable[]>([])
  let isLoadingData = $state<boolean>(false)
  let hasLoadedData = $state<boolean>(false)

  const fetchAffiliations = async () => {
    try {
      isLoadingData = true
      const groupsResult = await userGroupsList({ query: { user: user.id, school: schoolId } })
      const schoolsResult = await userSchoolsList({ query: { user: user.id, school: schoolId } })
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
</script>

<div class="row p-2 border-bottom">
  <div class="col-4">
    <div class="fw-semibold">{user.name}</div>
    <div class="text-muted small">{user.email || 'Ingen e-post'}</div>
  </div>
  <div class="col-4 ps-2">
    <pkt-button
      size="small"
      skin="secondary"
      type="button"
      variant="label-only"
      title="Hent tilknytninger"
      disabled={isLoadingData}
      onclick={fetchAffiliations}
      onkeydown={(e: any) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          fetchAffiliations()
        }
      }}
      role="button"
      tabindex="0"
    >
      Hent tilknytninger
    </pkt-button>
  </div>
  <div class="col-4">
    {#if hasLoadedData}
      <div class="small">
        <div>
          <strong>Grupper:</strong>
          {userGroups.map(ug => ug.group.displayName).join(', ') || 'Ingen'}
        </div>
        <div>
          <strong>Skoler:</strong>
          {userSchools.map(us => us.role.name).join(', ') || 'Ingen'}
        </div>
      </div>
    {/if}
  </div>
</div>
