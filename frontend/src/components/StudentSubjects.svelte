<script lang="ts">
  import type { ObservationType, GroupType, SubjectType } from '../generated/types.gen'
  import { dataStore } from '../stores/data'
  import { groupsList } from '../generated/sdk.gen'
  import StudentSubjectChart from './StudentSubjectChart.svelte'

  let { currentSchool, currentUser, subjects } = $derived($dataStore)
  let observations = $state<ObservationType[]>([])
  let groups = $state<GroupType[]>([])
  let studentSubjects = $derived(
    subjects.filter(subject => groups.some(group => group.subjectId === subject.id))
  )

  const fetchData = async () => {
    try {
      const groupsResult = await groupsList({
        query: { school: currentSchool.id, user: currentUser.id },
      })
      groups = (groupsResult.data || []).filter(group => group.type === 'teaching')
    } catch (error) {
      console.error(`Could not load subjects for ${currentUser.id}`, error)
      groups = []
    }
  }

  $effect(() => {
    if (currentSchool) {
      fetchData()
    }
  })
</script>

<section class="py-4">
  <h2>Mine fag</h2>

  {#if groups.length < 1}
    <div class="mt-3">🫤 Ingen fag, gitt.</div>
  {:else}
    <div class="card shadow-sm mt-4">
      <ul class="list-group list-group-flush">
        {#each groups as group (group.id)}
          {@const subject = studentSubjects.find(s => s.id === group.subjectId)}
          <li class="list-group-item">
            <h3 class="my-3">
              {subject.shortName || subject.displayName || subject.grepCode}
            </h3>
            <hr class="border border-3 opacity-50" />
            <div class="py-3">
              <StudentSubjectChart student={currentUser} {subject} />
            </div>
          </li>
        {/each}
      </ul>
    </div>
  {/if}
</section>

<style>
</style>
