<script lang="ts">
  import { dataStore } from '../stores/data'
  import { goalsCreate, goalsUpdate, masterySchemasList } from '../generated/sdk.gen'
  import type { GoalWritable, UserReadable, MasterySchemaReadable } from '../generated/types.gen'

  const { student, goal, onDone } = $props<{
    student: UserReadable | null
    goal: GoalWritable | null
    onDone: () => void
  }>()
  let localGoal = $state<Record<string, any>>({ ...goal })
  let masterySchemas = $state<MasterySchemaReadable[]>([])

  const fetchMasterySchemas = async () => {
    try {
      const result = await masterySchemasList()
      masterySchemas = result.data || []
    } catch (error) {
      console.error('Error fetching mastery schemas:', error)
      masterySchemas = []
    }
  }

  const handleSave = async () => {
    localGoal.studentId = student?.id
    try {
      if (goal.id) {
        await goalsUpdate({
          path: { id: localGoal.id },
          body: localGoal,
        })
      } else {
        await goalsCreate({
          body: localGoal,
        })
      }
      onDone()
    } catch (error) {
      // TODO: Show an error message to the user
      console.error('Error saving goal:', error)
    }
  }
  // Fetch mastery schemas when component mounts
  $effect(() => {
    fetchMasterySchemas()
    localGoal = { masterySchemaId: '', subjectId: '', ...goal }
  })
</script>

<div class="p-4">
  <h3 class="pb-2">{localGoal.id ? 'Redigerer mål for' : 'Nytt mål for'} {student?.name}</h3>
  <div class="form-group mb-3">
    <div class="pkt-inputwrapper">
      <label for="goalSubject" class="form-label">Fag</label>
      <select class="pkt-input" bind:value={localGoal.subjectId}>
        <option value="">Velg fag</option>
        {#each $dataStore.subjects as subject}
          <option value={subject.id}>{subject.displayName}</option>
        {/each}
      </select>
    </div>
  </div>

  <div class="form-group mb-3">
    <div class="pkt-inputwrapper">
      <label for="goalSubject" class="form-label">Skjema</label>
      <select class="pkt-input" bind:value={localGoal.masterySchemaId}>
        <option value="" disabled>Velg mestringsskjema</option>
        {#each masterySchemas as masterySchema}
          <option value={masterySchema.id}>{masterySchema.title}</option>
        {/each}
      </select>
    </div>
  </div>

  <div class="form-group mb-3">
    <label for="goalTitle" class="form-label">Tittel</label>
    <input
      id="goalTitle"
      type="text"
      class="form-control rounded-0 border-2 border-primary input-field"
      bind:value={localGoal.title}
      placeholder="Tittel på målet"
    />
  </div>

  <div class="form-group mb-3">
    <label for="goalSortOrder" class="form-label">Rekkefølge</label>
    <input
      id="goalSortOrder"
      type="integer"
      class="form-control rounded-0 border-2 border-primary input-field"
      bind:value={localGoal.sortOrder}
      placeholder="Rekkefølge (tall)"
    />
  </div>

  <div class="d-flex gap-2 justify-content-start mt-4">
    <pkt-button
      size="medium"
      skin="primary"
      type="button"
      variant="label-only"
      class="m-2"
      role="button"
      onclick={() => handleSave()}
      onkeydown={(e: any) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          handleSave()
        }
      }}
      tabindex="0"
      disabled={localGoal.masterySchemaId === '' ||
        localGoal.subjectId === '' ||
        !localGoal.title?.trim()}
    >
      Lagre
    </pkt-button>

    <pkt-button
      size="medium"
      skin="secondary"
      type="button"
      variant="label-only"
      class="m-2"
      onclick={() => onDone()}
      onkeydown={(e: any) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onDone()
        }
      }}
      role="button"
      tabindex="0"
    >
      Avbryt
    </pkt-button>
  </div>
</div>

<style>
  label {
    font-weight: 800;
  }

  .input-field {
    height: 48px;
  }
  input,
  select {
    width: 100% !important;
  }
</style>
