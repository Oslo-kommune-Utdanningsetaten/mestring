<script lang="ts">
  import type { UserType, SubjectType, GroupType } from '../generated/types.gen'
  import StudentRow from './StudentRow.svelte'

  let {
    students,
    subjects,
    groups,
  }: {
    students: UserType[]
    subjects: SubjectType[]
    groups: GroupType[]
  } = $props()
</script>

<div class="students-grid" aria-label="Elevliste" style="--columns-count: {subjects.length}">
  <span class="item header header-row">Elev</span>
  {#each subjects as subject (subject.id)}
    <span class="item header header-row">
      <span class="column-header">
        {subject.shortName}
      </span>
    </span>
  {/each}
  {#each students as student (student.id)}
    <StudentRow {student} {subjects} {groups} />
  {/each}
</div>

<style>
  .students-grid {
    display: grid;
    grid-template-columns: minmax(180px, 2fr) repeat(var(--columns-count, 8), 1fr);
    align-items: start;
    gap: 0;
  }

  .students-grid :global(.item) {
    padding: 0.5rem;
    border-bottom: 1px solid var(--bs-border-color);
    min-height: 4rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .students-grid .item.header-row {
    background-color: var(--bs-light);
    font-weight: 800;
    max-height: 4rem;
  }

  .students-grid :global(.item.header:first-child),
  .students-grid :global(.item.student-name) {
    justify-content: flex-start;
  }

  .column-header {
    transform: rotate(-60deg);
    font-size: 0.8rem;
    padding: 0.1rem 0.1rem 0.1rem 0.3rem;
    max-width: 6rem;
    background-color: var(--pkt-color-surface-strong-light-green);
    border: 1px solid var(--pkt-color-grays-gray-100);
    overflow-wrap: break-word;
  }
</style>
