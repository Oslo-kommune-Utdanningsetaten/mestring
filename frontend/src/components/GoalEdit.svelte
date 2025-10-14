<script lang="ts">
  import { goalsCreate, goalsUpdate } from '../generated/sdk.gen'
  import type {
    GoalWritable,
    GroupReadable,
    UserReadable,
    SubjectReadable,
    GoalReadable,
  } from '../generated/types.gen'
  import { dataStore } from '../stores/data'
  import { setLocalStorageItem } from '../stores/localStorage'
  import ButtonMini from './ButtonMini.svelte'
  import { NONE_FIELD_VALUE } from '../utils/constants'

  // This component is used for both personal and group goals!
  // If group is passed, student AND subject should be null
  // If student is passed, group should be null

  const {
    student = null,
    subject = null,
    group = null,
    goal = null,
    onDone,
    isGoalPersonal,
  } = $props<{
    student?: UserReadable | null
    subject?: SubjectReadable | null
    group?: GroupReadable | null
    goal?: GoalWritable | null
    isGoalPersonal: boolean
    onDone: () => void
  }>()
  let localGoal = $state<Partial<GoalReadable>>({})
  let subjectViaGroup = $derived(
    group ? $dataStore.subjects.find(s => s.id === group?.subjectId) : null
  )
  let masterySchemas = $derived($dataStore.masterySchemas)

  // What determines if we can edit the goal?
  let isFormValid = $derived(
    !!localGoal.masterySchemaId && (isGoalPersonal ? !!localGoal.subjectId : !!subjectViaGroup)
  )

  const getTitle = () => {
    const action = localGoal.id ? 'Redigerer' : 'Nytt'
    const goalType = isGoalPersonal ? 'personlig ' : 'gruppe'
    const target = isGoalPersonal ? student?.name : group?.displayName
    return `${action} ${goalType}mål for ${target}`
  }

  const handleUpdatePreferredMasterySchema = () => {
    if (localGoal.masterySchemaId) {
      setLocalStorageItem('preferredMasterySchemaId', localGoal.masterySchemaId)
    }
  }

  const handleChangeSubject = (subjectId: string | null) => {
    localGoal = {
      ...goal,
      subjectId,
    }
  }

  const handleSave = async () => {
    try {
      if (localGoal.id) {
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
      console.error('Error saving goal:', error)
    }
  }

  // Update localGoal when goal prop changes
  $effect(() => {
    localGoal = {
      ...goal,
    }
  })
</script>

<div class="goal-edit p-4">
  <h3 class="pb-2">{getTitle()}</h3>
  <hr />
  <div class="form-group mb-3">
    <div class="pkt-inputwrapper">
      <label for="goalSubject" class="form-label">Fag</label>
      {#if isGoalPersonal}
        <select
          class="pkt-input"
          onchange={(e: Event) => {
            const target = e.target as HTMLSelectElement | null
            const subjectId = target?.value || null
            handleChangeSubject(subjectId)
          }}
        >
          <option value={NONE_FIELD_VALUE} selected={!localGoal.subjectId}>Velg fag</option>
          {#each $dataStore.subjects as aSubject}
            <option value={aSubject.id} selected={localGoal.subjectId === aSubject.id}>
              {aSubject.displayName}
            </option>
          {/each}
        </select>
      {:else}
        <div
          class="border border-2 rounded-0 border-primary fs-5 p-2 {!subjectViaGroup
            ? 'alert alert-warning'
            : ''}"
        >
          {subjectViaGroup
            ? subjectViaGroup.displayName
            : 'Denne gruppen er ikke tilknyttet et fag'}
        </div>
      {/if}
    </div>
  </div>

  <div class="form-group mb-3">
    <div class="pkt-inputwrapper">
      <label for="goalSubject" class="form-label">Mestringsskjema</label>
      <select
        class="pkt-input"
        bind:value={localGoal.masterySchemaId}
        onchange={handleUpdatePreferredMasterySchema}
      >
        <option value="" disabled>Velg mestringsskjema</option>
        {#each masterySchemas as masterySchema}
          <option value={masterySchema.id}>{masterySchema.title}</option>
        {/each}
      </select>
    </div>
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

  <div class="d-flex gap-2 justify-content-start mt-4">
    <ButtonMini
      options={{
        title: 'Lagre',
        iconName: 'check',
        skin: 'primary',
        variant: 'label-only',
        classes: 'm-2',
        disabled: !isFormValid,
        onClick: () => handleSave(),
      }}
    >
      Lagre
    </ButtonMini>

    <ButtonMini
      options={{
        title: 'Avbryt',
        iconName: 'close',
        skin: 'secondary',
        variant: 'label-only',
        classes: 'm-2',
        onClick: () => onDone(),
      }}
    >
      Avbryt
    </ButtonMini>
  </div>
</div>

<style>
  .goal-edit {
    width: 100%;
    max-width: 100%;
  }

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
