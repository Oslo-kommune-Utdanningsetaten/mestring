<script lang="ts">
  import type { UserType } from '../generated/types.gen'
  import type { UserRoleType } from '../types/models'
  import { USER_ROLES } from '../utils/constants'
  import { abbreviateName } from '../utils/functions'
  import Link from './Link.svelte'

  const {
    user,
    allUsers = [],
    role,
  } = $props<{
    user: UserType | null
    allUsers?: UserType[]
    role?: UserRoleType
  }>()

  const iconName = $derived<string>(role === USER_ROLES.TEACHER ? 'lecture' : 'person')
  const otherNames = $derived<string[]>(
    allUsers.filter((u: UserType) => u.id !== user?.id).map((u: UserType) => u.name) || []
  )
</script>

{#if user}
  <pkt-tag {iconName} skin="yellow">
    <span title={user.feideId}>
      {abbreviateName(user.name, otherNames)}
    </span>
  </pkt-tag>
{/if}

<style>
</style>
