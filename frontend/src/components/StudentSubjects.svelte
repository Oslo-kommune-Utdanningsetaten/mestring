<script lang="ts">
  import type { UserType, GroupType, SubjectType } from '../generated/types.gen'
  import { groupsList } from '../generated/sdk.gen'
  import { dataStore } from '../stores/data'
  import {
    getPreferredCreatedParams,
    getPreferredGroupValidity,
  } from '../stores/localStorageFunctions'
  import StudentSubject from './StudentSubject.svelte'

  const { student } = $props<{
    student: UserType
  }>()

  let groups = $state<GroupType[]>([])
  let isLoading = $state(false)
  let { currentSchool, subjects } = $derived($dataStore)
  let studentSubjects = $derived<SubjectType[]>(
    subjects.filter(subject => groups.some(group => group.subjectId === subject.id))
  )

  const fetchData = async () => {
    isLoading = true
    try {
      const groupsResult = await groupsList({
        query: {
          school: currentSchool.id,
          user: student.id,
          valid: getPreferredGroupValidity(),
          ...getPreferredCreatedParams(),
        },
      })
      groups = (groupsResult.data || []).filter(group => group.type === 'teaching')
    } catch (error) {
      console.error(`Failed to load groups for ${student.id}`, error)
      groups = []
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
  <h2>Mine faglige mål</h2>
  {#if isLoading}
    <div class="spinner-border spinner-border-sm" role="status">
      <span class="visually-hidden">Henter data...</span>
    </div>
  {:else if studentSubjects.length < 1}
    <div class="mt-3">🫤 Ingen fag, gitt.</div>
  {:else}
    <div class="card shadow-sm mt-4 list-group">
      {#each studentSubjects as subject (subject.id)}
        {@const group = groups.find(g => g.subjectId === subject.id)}
        {#if group}
          <div class="list-group-item">
            <StudentSubject {student} {subject} {group} />
          </div>
        {/if}
      {/each}
    </div>
  {/if}
</section>

<style>
</style>
