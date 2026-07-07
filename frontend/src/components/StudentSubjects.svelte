<script lang="ts">
  import type { UserType, GroupType, SubjectType } from '../generated/types.gen'
  import { dataStore } from '../stores/data'
  import { groupsList } from '../generated/sdk.gen'
  import StudentSubject from './StudentSubject.svelte'

  const { student } = $props<{
    student: UserType
  }>()

  let { currentSchool, subjects } = $derived($dataStore)
  let groups = $state<GroupType[]>([])
  let studentSubjects = $state<SubjectType[]>([])
  let isLoading = $state(false)

  const fetchData = async () => {
    isLoading = true
    try {
      const groupsResult = await groupsList({
        query: { school: currentSchool.id, user: student.id },
      })
      groups = (groupsResult.data || []).filter(group => group.type === 'teaching')
      studentSubjects = subjects.filter(subject =>
        groups.some(group => group.subjectId === subject.id)
      )
    } catch (error) {
      console.error(`Could not load subjects for ${student.id}`, error)
      groups = []
      return
    } finally {
      isLoading = false
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
  {#if isLoading}
    <div class="spinner-border spinner-border-sm" role="status">
      <span class="visually-hidden">Henter data...</span>
    </div>
  {:else if groups.length < 1}
    <div class="mt-3">🫤 Ingen fag, gitt.</div>
  {:else}
    <div class="card shadow-sm mt-4 list-group">
      {#each groups as group (group.id)}
        {@const subject = studentSubjects.find(s => s.id === group.subjectId)}
        {#if subject}
          <div class="list-group-item">
            <StudentSubject {student} {subject} />
          </div>
        {/if}
      {/each}
    </div>
  {/if}
</section>

<style>
</style>
