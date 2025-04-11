<script lang="ts">
  import { dataStore } from '../stores/data'
  import type { Goal as GoalType } from '../types/models'

  const { studentGoal, index } = $props<{
    studentGoal: GoalType
    index: number
  }>()

  const isAnonymous = true

  function getGroupDescription(goal: GoalType) {
    const group = $dataStore.groups.find(g => g.id === goal.groupId)
    if (!group) return null
    return group.type === 'basis' ? 'Sosialt' : group.name
  }
</script>

{#if isAnonymous}
  <span class="fw-medium indented">
    {index + 1}
    <span class="text-muted small">[{getGroupDescription(studentGoal)}]</span>
  </span>
{:else}
  <span class="fw-medium indented" title={studentGoal.description}>
    {studentGoal.title}
    <span class="text-muted small">[{getGroupDescription(studentGoal)}]</span>
  </span>
{/if}

<style>
</style>
