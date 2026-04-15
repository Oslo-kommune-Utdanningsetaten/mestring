<script lang="ts">
  import type { Mastery } from '../types/models'
  import type { GroupType, SubjectType } from '../generated/types.gen'
  import { dataStore } from '../stores/data'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import Link from './Link.svelte'
  import { MISSING_REASON_NO_OBSERVATIONS, MISSING_REASON_NO_GOALS } from '../utils/constants'

  let {
    group,
    subjects,
  }: {
    group: GroupType
    subjects: SubjectType[]
  } = $props()
</script>

<span class="item group-name">
  <Link to={`/groups/${group.id}`}>{group.displayName}</Link>
</span>
{#each subjects as subject}
  <span class="item">sup {subject.id}</span>
{/each}

<style>
</style>
