<script lang="ts">
  import ButtonMini from './ButtonMini.svelte'
  import StudentSVG from '../assets/education.svg.svelte'

  interface DeletedGroup {
    id: string
    displayName: string
    feideId: string
  }

  interface DeletedUser {
    id: string
    name: string
    feideId: string
  }

  interface DeletedUserGroup {
    id: string
    user_Name: string
    user_FeideId: string
    group_DisplayName: string
    role_Name: string
    deletedAt: string
  }

  interface DeletedGoal {
    id: string
    title: string
    student_Name?: string
    subject_Name?: string
    group_DisplayName?: string
  }

  interface DeletedObservation {
    id: string
    student_Name: string
    observer_Name: string
    goal_Title: string
  }

  interface CleanerbotChanges {
    group: { 'soft-deleted': DeletedGroup[]; 'hard-deleted': DeletedGroup[] }
    user: { 'soft-deleted': DeletedUser[]; 'hard-deleted': DeletedUser[] }
    userGroup: { 'soft-deleted': DeletedUserGroup[]; 'hard-deleted': DeletedUserGroup[] }
    goal: { 'soft-deleted': DeletedGoal[]; 'hard-deleted': DeletedGoal[] }
    observation: { 'soft-deleted': DeletedObservation[]; 'hard-deleted': DeletedObservation[] }
  }

  interface CleanerbotData {
    orgNumber: string
    changes: CleanerbotChanges
    errors: string[]
  }

  const { data, onDone } = $props<{
    data: CleanerbotData
    onDone: () => void
  }>()

  const hasChanges = $derived.by(() => {
    const changes = data.changes
    return (
      changes.group['soft-deleted'].length > 0 ||
      changes.group['hard-deleted'].length > 0 ||
      changes.user['soft-deleted'].length > 0 ||
      changes.user['hard-deleted'].length > 0 ||
      changes.userGroup['soft-deleted'].length > 0 ||
      changes.userGroup['hard-deleted'].length > 0 ||
      changes.goal['soft-deleted'].length > 0 ||
      changes.goal['hard-deleted'].length > 0 ||
      changes.observation['soft-deleted'].length > 0 ||
      changes.observation['hard-deleted'].length > 0 ||
      data.errors.length > 0
    )
  })
</script>

<section class="m-3">
  <h2 class="my-3">Cleaner Bot Dry Run Results</h2>
  <p class="text-muted">Org: {data.orgNumber}</p>

  {#if !hasChanges}
    <div class="alert alert-success">No changes would be made. All data is clean!</div>
  {/if}

  <!-- Groups -->
  {#if data.changes.group['soft-deleted'].length > 0 || data.changes.group['hard-deleted'].length > 0}
    <h3 class="mt-4">Groups</h3>
    <table class="table table-sm table-hover align-middle mb-4">
      <thead class="table-light">
        <tr>
          <th>Display Name</th>
          <th>Feide ID</th>
        </tr>
      </thead>
      <tbody>
        {#each data.changes.group['soft-deleted'] as group}
          <tr class="table-warning">
            <td>{group.displayName}</td>
            <td>{group.feideId}</td>
            <td><span class="badge bg-warning">Soft Delete</span></td>
          </tr>
        {/each}
        {#each data.changes.group['hard-deleted'] as group}
          <tr class="table-danger">
            <td>{group.displayName}</td>
            <td>{group.feideId}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}

  <!-- Users -->
  {#if data.changes.user['soft-deleted'].length > 0 || data.changes.user['hard-deleted'].length > 0}
    <h3 class="mt-4">Users</h3>
    <table class="table table-sm table-hover align-middle mb-4">
      <thead class="table-light">
        <tr>
          <th>Name</th>
          <th>Feide ID</th>
        </tr>
      </thead>
      <tbody>
        {#each data.changes.user['soft-deleted'] as user}
          <tr class="table-warning">
            <td>{user.name}</td>
            <td>{user.feideId}</td>
          </tr>
        {/each}
        {#each data.changes.user['hard-deleted'] as user}
          <tr class="table-danger">
            <td>{user.name}</td>
            <td>{user.feideId}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}

  <!-- UserGroups (Memberships) -->
  {#if data.changes.userGroup['soft-deleted'].length > 0 || data.changes.userGroup['hard-deleted'].length > 0}
    <h3 class="mt-4">Memberships</h3>
    <table class="table table-sm table-hover align-middle mb-4">
      <thead class="table-light">
        <tr>
          <th>User</th>
          <th>Role</th>
          <th>Group</th>
        </tr>
      </thead>
      <tbody>
        {#each data.changes.userGroup['soft-deleted'] as membership}
          <tr class="table-warning">
            <td>{membership.user_Name}</td>
            <td>
              {membership.role_Name}
            </td>
            <td>{membership.group_DisplayName}</td>
          </tr>
        {/each}
        {#each data.changes.userGroup['hard-deleted'] as membership}
          <tr class="table-danger">
            <td>{membership.user_Name}</td>
            <td>
              {membership.role_Name}
            </td>
            <td>{membership.group_DisplayName}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}

  <!-- Goals -->
  {#if data.changes.goal['soft-deleted'].length > 0 || data.changes.goal['hard-deleted'].length > 0}
    <h3 class="mt-4">Goals</h3>
    <table class="table table-sm table-hover align-middle mb-4">
      <thead class="table-light">
        <tr>
          <th>Title</th>
          <th>Context</th>
        </tr>
      </thead>
      <tbody>
        {#each data.changes.goal['soft-deleted'] as goal}
          <tr class="table-warning">
            <td>{goal.title}</td>
            <td>
              {#if goal.student_Name && goal.subject_Name}
                {goal.student_Name} - {goal.subject_Name}
              {:else if goal.group_DisplayName}
                Group: {goal.group_DisplayName}
              {:else}
                -
              {/if}
            </td>
          </tr>
        {/each}
        {#each data.changes.goal['hard-deleted'] as goal}
          <tr class="table-danger">
            <td>{goal.title}</td>
            <td>
              {#if goal.student_Name && goal.subject_Name}
                {goal.student_Name} - {goal.subject_Name}
              {:else if goal.group_DisplayName}
                Group: {goal.group_DisplayName}
              {:else}
                -
              {/if}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}

  <!-- Observations -->
  {#if data.changes.observation['soft-deleted'].length > 0 || data.changes.observation['hard-deleted'].length > 0}
    <h3 class="mt-4">Observations</h3>
    <table class="table table-sm table-hover align-middle mb-4">
      <thead class="table-light">
        <tr>
          <th>Student</th>
          <th>Observer</th>
          <th>Goal</th>
        </tr>
      </thead>
      <tbody>
        {#each data.changes.observation['soft-deleted'] as observation}
          <tr class="table-warning">
            <td>{observation.student_Name}</td>
            <td>{observation.observer_Name}</td>
            <td>{observation.goal_Title}</td>
          </tr>
        {/each}
        {#each data.changes.observation['hard-deleted'] as observation}
          <tr class="table-danger">
            <td>{observation.student_Name}</td>
            <td>{observation.observer_Name}</td>
            <td>{observation.goal_Title}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}

  <!-- Errors -->
  {#if data.errors.length > 0}
    <h3 class="mt-4">Errors</h3>
    <div class="alert alert-danger">
      <ul class="mb-0">
        {#each data.errors as error}
          <li>{error}</li>
        {/each}
      </ul>
    </div>
  {/if}

  <ButtonMini
    options={{
      title: 'Lukk',
      skin: 'secondary',
      variant: 'label-only',
      onClick: () => onDone(),
    }}
  >
    Close
  </ButtonMini>
</section>
