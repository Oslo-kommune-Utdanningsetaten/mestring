<script lang="ts">
  import type { UserType } from '../generated/types.gen'
  import type { UserRoleType } from '../types/models'
  import { usersRetrieve } from '../generated/sdk.gen'
  import { USER_ROLES } from '../utils/constants'
  import { abbreviateName } from '../utils/functions'
  import Link from './Link.svelte'

  const {
    user,
    userId,
    allUsers = [],
    role,
    href,
  } = $props<{
    user?: UserType | null | undefined
    userId?: string | undefined
    allUsers?: UserType[]
    role?: UserRoleType
    href?: string
  }>()

  const iconName = $derived<string>(
    role === USER_ROLES.TEACHER ? 'lecture' : role === USER_ROLES.STUDENT ? 'education' : 'person'
  )
  const otherNames = $derived<string[]>(
    allUsers.filter((u: UserType) => u.id !== user?.id).map((u: UserType) => u.name) || []
  )

  let userToDisplay: UserType | null = $derived(user || null)

  $effect(() => {
    if (user) {
      userToDisplay = user
    } else if (userId) {
      usersRetrieve({ path: { id: userId } }).then(result => {
        userToDisplay = result.data || null
      })
    } else {
      userToDisplay = null
      console.warn('UserTag: No user or userId provided')
    }
  })
</script>

{#if userToDisplay}
  <pkt-tag {iconName} skin="yellow">
    {#if href}
      <Link to={href}>
        {abbreviateName(userToDisplay.name, otherNames)}
      </Link>
    {:else}
      <span title={userToDisplay.feideId}>
        {abbreviateName(userToDisplay.name, otherNames)}
      </span>
    {/if}
  </pkt-tag>
{/if}

<style>
</style>
