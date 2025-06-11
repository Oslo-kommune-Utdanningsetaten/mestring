<script lang="ts">
  import { dataStore } from '../stores/data'
  import { goalsCreate, goalsUpdate } from '../generated/sdk.gen'
  import type { GoalWritable, UserReadable } from '../generated/types.gen'

  const { student, goal, onDone } = $props<{
    student: UserReadable | null
    goal: GoalWritable | null
    onDone: () => void
  }>()
  let localGoal = $state<Record<string, any>>({ ...goal })

  async function handleSave() {
    localGoal.studentId = student?.id
    try {
      if (goal.id) {
        // Update existing goal
        const result = await goalsUpdate({
          path: { id: localGoal.id },
          body: localGoal,
        })
        console.log('Goal updated:', result.data)
      } else {
        // Create new goal
        const result = await goalsCreate({
          body: localGoal,
        })
        console.log('Goal created:', result.data)
      }
      // Report to parent component
      onDone()
    } catch (error) {
      // TODO: Show an error message to the user
      console.error('Error saving goal:', error)
    }
  }
</script>

<div class="p-4">
  <h3 class="pb-2">{localGoal.id ? 'Redigerer mål for' : 'Nytt mål for'} {student?.name}</h3>

  <div class="form-group mb-3">
    <div class="pkt-inputwrapper">
      <label for="goalSubject" class="form-label">Fag</label>
      <select class="pkt-input" bind:value={localGoal.subject_id}>
        <option value="">Velg fag</option>
        {#each $dataStore.subjects as subject}
          <option value={subject.id}>{subject.displayName}</option>
        {/each}
      </select>
    </div>
  </div>

  <div class="form-group mb-3">
    <label for="goalTitle" class="form-label">Tittel</label>
    <input
      id="goalTitle"
      type="text"
      class="form-control rounded-0 border-2 border-primary"
      bind:value={localGoal.title}
      placeholder="Tittel på målet"
    />
  </div>

  <div class="d-flex gap-2 justify-content-start mt-4">
    <pkt-button
      size="medium"
      skin="primary"
      type="button"
      variant="label-only"
      class="m-2"
      onclick={() => handleSave()}
      onkeydown={(e: any) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          handleSave()
        }
      }}
      role="button"
      tabindex="0"
      disabled={!localGoal.title?.trim() || !localGoal.subject_id}
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
  input {
    height: 47px;
  }
  input,
  select {
    width: 100% !important;
  }
</style>
