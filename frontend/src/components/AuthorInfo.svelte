<script lang="ts">
  import type { ObservationType, StatusType, UserType } from '../generated/types.gen'
  import { usersRetrieve } from '../generated/sdk.gen'
  import { formatDateTime, formatDateTimeWithToday, abbreviateName } from '../utils/functions'
  import { onMount } from 'svelte'

  const { item } = $props<{ item: ObservationType | StatusType }>()
  const { createdById, updatedById, createdAt, updatedAt } = item
  let creator = $state<(Partial<UserType> & { name: string }) | null>(null)
  let updator = $state<(Partial<UserType> & { name: string }) | null>(null)

  const hasBeenEdited: boolean = $derived(
    // is createdAt and updatedAt are within half second of each other
    Boolean(Math.abs(new Date(createdAt).getTime() - new Date(updatedAt).getTime()) > 500)
  )

  let titleData = $derived.by(() => {
    if (creator && updator) {
      let title = `Opprettet ${formatDateTime(createdAt)} av ${creator.name}`
      if (hasBeenEdited) {
        title += `\nSist oppdatert ${formatDateTime(updatedAt)} av ${updator.name}`
      }
      return title
    } else {
      return 'Laster brukerinfo...'
    }
  })

  const fetchUser = async (userId: string) => {
    if (!userId) return null
    const result = await usersRetrieve({ path: { id: userId } })
    return result.data || { name: 'ukjent' }
  }

  onMount(async () => {
    creator = await fetchUser(createdById)
    if (createdById === updatedById) updator = creator
    else updator = await fetchUser(updatedById)
  })
</script>

<span title={titleData}>
  {#if hasBeenEdited}
    {formatDateTimeWithToday(updatedAt)}, {updator?.name ? abbreviateName(updator.name) : 'ukjent'}*
  {:else}
    {formatDateTimeWithToday(createdAt)}, {creator?.name ? abbreviateName(creator.name) : 'ukjent'}
  {/if}
</span>

<style>
  span {
    font-family: inherit;
  }
</style>
