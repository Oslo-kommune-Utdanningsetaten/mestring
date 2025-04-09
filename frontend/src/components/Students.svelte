<script lang="ts">
  import StudentRow from './StudentRow.svelte'
  import { useTinyRouter } from 'svelte-tiny-router'
  import { dataStore } from '../stores/data'

  import type { Student as StudentType, Group as GroupType } from '../types/models'
  import { urlStringFrom } from '../utils/functions'
  const router = useTinyRouter()

  const students = $derived($dataStore.students)
  const teachingGroups = $derived($dataStore.groups.filter(s => s.type === 'teaching'))
  const basisGroups = $derived($dataStore.groups.filter(s => s.type === 'basis'))
  const activeTeachingGroupId = $derived(router.getQueryParam('teachingGroupId'))
  const activeTeachingGroup = $derived(teachingGroups.find(tg => tg.id === activeTeachingGroupId))
  const activeBasisGroupId = $derived(router.getQueryParam('basisGroupId'))
  const activeBasisGroup = $derived(basisGroups.find(bg => bg.id === activeBasisGroupId))

  // Filter students by group and subject
  const filteredStudents = $derived(
    students
      .filter((student: StudentType) => {
        return activeTeachingGroupId ? student.groupIds.includes(activeTeachingGroupId) : true
      })
      .filter((student: StudentType) => {
        return activeBasisGroupId ? student.groupIds.includes(activeBasisGroupId) : true
      })
  )

  // a derived map of groups by id, i.e. the superset of all student groups, by group id
  const groupsById = $derived(
    filteredStudents
      .map((student: StudentType) => student.groupIds)
      .flat()
      .reduce((acc: { [key: string]: GroupType | undefined }, groupId: string) => {
        acc[groupId] = $dataStore.groups.find(g => g.id === groupId)
        return acc
      }, {})
  )
</script>

<section class="py-3">
  <h2>Elever</h2>

  <!-- Filter basis groups -->
  <div class="d-flex align-items-center gap-2">
    <div class="dropdown">
      <button
        class="btn btn-outline-secondary dropdown-toggle link-button"
        type="button"
        data-bs-toggle="dropdown"
        aria-expanded="false"
      >
        {activeBasisGroup?.name || 'Velg gruppe'}
      </button>
      <ul class="dropdown-menu">
        <li>
          <a
            class="dropdown-item dropdown-link"
            href={urlStringFrom({ basisGroupId: null }, { mode: 'merge' })}
          >
            Alle grupper
          </a>
        </li>
        {#each basisGroups as group}
          <li>
            <a
              class="dropdown-item dropdown-link"
              href={urlStringFrom({ basisGroupId: group.id }, { mode: 'merge' })}
            >
              {group.name}
            </a>
          </li>
        {/each}
      </ul>
    </div>
    <!-- Filter teaching groups -->
    <div class="dropdown">
      <button
        class="btn btn-outline-secondary dropdown-toggle link-button"
        type="button"
        data-bs-toggle="dropdown"
        aria-expanded="false"
      >
        {activeTeachingGroup
          ? activeTeachingGroup.name + ' | ' + activeTeachingGroup.grade
          : 'Velg fag'}
      </button>
      <ul class="dropdown-menu">
        <li>
          <a
            class="dropdown-item dropdown-link"
            href={urlStringFrom({ teachingGroupId: null }, { mode: 'merge' })}
          >
            Alle fag
          </a>
        </li>
        {#each teachingGroups as subject}
          <li>
            <a
              class="dropdown-item dropdown-link"
              href={urlStringFrom({ teachingGroupId: subject.id }, { mode: 'merge' })}
            >
              {subject.name} | {subject.grade}
            </a>
          </li>
        {/each}
      </ul>
    </div>
    <a class="link-button" href={urlStringFrom({}, { mode: 'replace' })}>Nullstill</a>
  </div>
</section>

<section class="py-3">
  {#if filteredStudents.length === 0}
    <div class="alert alert-info">Ingen elever matcher det filteret</div>
  {:else}
    <div class="card shadow-sm">
      <!-- Header row -->
      <div class="student-grid-row fw-bold header">
        <div>Navn</div>
        <div>Klasse</div>
        <div>
          <span>Mål</span>
          <div class="group-grid-columns">
            {#each Object.values(groupsById) as group}
              <span class="group-grid-column">
                {group?.id.includes('-') ? group.name : 'Sosialt'}
              </span>
            {/each}
          </div>
        </div>
        <div>&nbsp;</div>
      </div>

      <!-- Student rows -->
      {#each filteredStudents as student}
        <StudentRow {student} groupIds={Object.keys(groupsById)} />
      {/each}
    </div>
  {/if}
</section>

<style>
  .dropdown-link {
    font-size: 1em !important;
  }

  .dropdown-link:hover {
    text-decoration: none;
  }
</style>
