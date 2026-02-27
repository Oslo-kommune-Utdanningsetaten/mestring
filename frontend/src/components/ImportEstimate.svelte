<script lang="ts">
  import { getAnchorPath } from 'svelte-jsoneditor'

  const { data } = $props<{
    data: Record<string, unknown>
  }>()

  let dataType = $derived.by(() => {
    if (data.hasOwnProperty('newGroups')) return 'groups'
    if (data.hasOwnProperty('newUsers')) return 'users'
    if (data.hasOwnProperty('newMemberships')) return 'memberships'
    return 'unknown'
  })
</script>

<section class="m-3">
  {#if dataType === 'groups'}
    <h2 class="my-3">Nye grupper ({data.newGroupCount})</h2>
    <table class="table table-sm table-hover table-striped table-success align-middle mb-0">
      <thead class="table-light">
        <tr>
          <th>Navn</th>
          <th>FeideID</th>
        </tr>
      </thead>
      <tbody>
        {#each data.newGroups as group}
          <tr>
            <td>{group.displayName}</td>
            <td>{group.id}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  {:else if dataType === 'users'}
    <h2 class="my-3">Nye brukere ({data.newUserCount})</h2>
    <table class="table table-sm table-hover table-striped table-success align-middle mb-0">
      <thead class="table-light">
        <tr>
          <th>Navn</th>
          <th>FeideID</th>
        </tr>
      </thead>
      <tbody>
        {#each data.newUsers as user}
          <tr>
            <td>{user.name}</td>
            <td>{user.feideId}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  {:else if dataType === 'memberships'}
    <h2 class="my-3">Nye medlemskap ({data.newMembershipCount})</h2>
    <table class="table table-sm table-hover table-striped align-middle mb-0">
      <thead class="table-light">
        <tr>
          <th>Bruker</th>
          <th>Rolle</th>
          <th>Gruppe</th>
        </tr>
      </thead>
      <tbody>
        {#each data.newMemberships as membership}
          <tr class:table-warning={membership.role === 'teacher'}>
            <td>{membership.userName}</td>
            <td>{membership.role}</td>
            <td>{membership.groupName}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</section>
