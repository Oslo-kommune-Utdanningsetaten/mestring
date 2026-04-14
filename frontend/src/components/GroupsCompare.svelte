<script lang="ts">
  import { useTinyRouter } from 'svelte-tiny-router'
  import { dataStore } from '../stores/data'
  import { groupsList } from '../generated/sdk.gen'
  import type { GroupType } from '../generated/types.gen'
  import Link from './Link.svelte'

  const router = useTinyRouter()
  let groups = $derived<GroupType[]>([])
  let currentSchool = $derived($dataStore.currentSchool)

  const { groupIds } = $props<{
    groupIds: string[]
  }>()

  const fetchGroups = async () => {
    const results = await groupsList({
      query: { ids: groupIds.join(','), school: currentSchool.id },
    })
    groups = results.data || []
  }

  $effect(() => {
    fetchGroups()
  })
</script>

<section class="py-3">
  <h2>Sammenligner grupper</h2>

  {#if groups.length === 0}
    <div class="mt-3">🫤</div>
  {:else}
    <pre>
{JSON.stringify(groups, null, 2)}
    </pre>
    {#each groups as group}
      <div class="card shadow-sm p-3">
        <h3 class="mt-1 mb-3" title={group.feideId}>
          <Link to="/groups/{group.id}">
            {group.displayName}
          </Link>
        </h3>
      </div>
    {/each}
  {/if}
</section>

<style>
</style>
