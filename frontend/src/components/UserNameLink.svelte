<script lang="ts">
  import Link from './Link.svelte'
  import type { UserType } from '../generated/types.gen'

  let {
    user,
  }: {
    user: UserType
  } = $props()
  const firstName = $derived(user.name.split(' ')[0])
  const lastNames = $derived(user.name.split(' ').slice(1).join(' '))
</script>

<Link to={`/students/${user.id}`}>
  <span class="name-wrapper" title={user.name}>
    <div class="first-name">
      {firstName}
    </div>
    <div class="last-names">
      {lastNames}
    </div>
  </span>
</Link>

<style>
  .name-wrapper {
    flex: 1;
    display: grid;
    overflow: hidden;
    min-width: 2.5rem;
  }

  .first-name {
    margin-top: 0px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .last-names {
    font-size: 0.8rem;
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>
