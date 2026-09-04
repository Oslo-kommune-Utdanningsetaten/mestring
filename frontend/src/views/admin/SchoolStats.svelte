<script lang="ts">
  import type { GroupType } from '../../generated/types.gen'
  import { dataStore } from '../../stores/data'
  import { getSubjectName } from '../../utils/functions'
  import { preferredSchoolYear } from '../../stores/localStorageFunctions'
  import { calculateSchoolYearMilestones, getCurrentSchoolYear } from '../../utils/schoolYear'

  import GroupTag from '../../components/GroupTag.svelte'
  import ObservationsBarChart from '../../components/ObservationsBarChart.svelte'

  const currentSchoolYear = getCurrentSchoolYear()
  let currentSchool = $derived($dataStore.currentSchool)
  let groups = $derived<GroupType[]>($dataStore.currentUser.allGroups || [])

  const now = new Date()
  const { startAt, midyearAt, endAt } = calculateSchoolYearMilestones(
    new Date(`${$preferredSchoolYear.split('-')[0] + '-10-01'}`) // Any date in the preferred school year
  )
  const fromDate: string = $derived.by(() => {
    if ($preferredSchoolYear === currentSchoolYear) {
      return now.getMonth() < 7 ? midyearAt : startAt
    }
    return startAt
  })
  const toDate: string = $derived.by(() => {
    if ($preferredSchoolYear === currentSchoolYear) {
      return now.getMonth() < 7 ? endAt : midyearAt
    }
    return endAt
  })
</script>

{#if currentSchool}
  <section class="pt-3">
    <h2 class="mb-4">Observasjoner opprettet per uke</h2>
    <p class="text-muted">{fromDate} ➡ {toDate}</p>
    <div class="border border-3 mb-4 p-3">
      <h3 class="mb-2">Hele skolen</h3>
      <!-- Observations for whole school -->
      <ObservationsBarChart
        schoolId={currentSchool.id}
        width={500}
        height={150}
        {fromDate}
        {toDate}
      />
    </div>

    {#if groups.length > 1}
      {#each groups as group}
        <div class="border border-3 mb-4 p-3">
          <GroupTag
            classes="mb-3 mt-2"
            {group}
            isGroupTypeNameEnabled={true}
            isGroupNameEnabled={true}
            href={`/groups/${group.id}`}
          />

          <!-- students -->
          <div class="mt-2 mb-1">
            <!-- Observations for group -->
            <ObservationsBarChart groupId={group.id} width={500} height={150} {fromDate} {toDate} />
          </div>
        </div>
      {/each}
    {/if}
  </section>
{/if}

<style>
</style>
