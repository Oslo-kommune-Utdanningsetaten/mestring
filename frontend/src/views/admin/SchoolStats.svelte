<script lang="ts">
  import { dataStore } from '../../stores/data'
  import type { GroupType } from '../../generated/types.gen'
  import GroupTag from '../../components/GroupTag.svelte'
  import Link from '../../components/Link.svelte'
  import ObservationsBarChart from '../../components/ObservationsBarChart.svelte'

  let currentSchool = $derived($dataStore.currentSchool)
  let groups = $derived<GroupType[]>($dataStore.currentUser.allGroups || [])

  const getSubjectName = (subjectId: string) => {
    const subject = $dataStore.subjects.find(subj => subj.id === subjectId)
    return subject ? subject.displayName : 'Ukjent fag'
  }

  $effect(() => {})
</script>

<section class="pt-3">
  <h2 class="mb-4">Observasjoner per uke</h2>
  <div class="border border-3 mb-4 p-3">
    <h3 class="mb-2">Hele skolen</h3>
    <!-- Observations for whole school -->
    <ObservationsBarChart schoolId={currentSchool.id} width={300} height={150} />
  </div>

  {#if groups.length > 1}
    {#each groups as group}
      <div class="border border-3 mb-4 p-3">
        <h3 class="mb-2" title={group.feideId}>
          <Link to="/groups/{group.id}">
            {group.displayName}
          </Link>
        </h3>
        <GroupTag classes="mb-1" {group} isGroupTypeNameEnabled={true} />

        {#if group.subjectId}
          <div class="text-muted">
            {getSubjectName(group.subjectId)}
          </div>
        {/if}

        <!-- students -->
        <div class="mt-2 mb-1">
          <!-- Observations for group -->
          <ObservationsBarChart groupId={group.id} width={300} height={150} />
        </div>
      </div>
    {/each}
  {/if}
</section>

<style>
</style>
