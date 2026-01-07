<script lang="ts">
  import { goalsCreate, goalsUpdate } from '../generated/sdk.gen'
  import type {
    GoalType,
    GroupType,
    UserType,
    SubjectType,
    GoalCreateType,
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
    student?: UserType | null
    subject?: SubjectType | null
    group?: GroupType | null
    goal?: GoalType | null
    isGoalPersonal: boolean
    onDone?: () => void | Promise<void>
  }>()

  let localGoal = $state<Partial<GoalType>>({})
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
    const goalType = isGoalPersonal ? 'individuelt ' : 'gruppe'
    const target = isGoalPersonal ? student?.name : group?.displayName
    return `${action} ${goalType}mål for ${target}`
  }

  const handleChangeMasterySchema = (masterySchemaId: string) => {
    if (masterySchemaId !== NONE_FIELD_VALUE) {
      localGoal = { ...localGoal, masterySchemaId }
      setLocalStorageItem('preferredMasterySchemaId', masterySchemaId)
    }
  }

  const handleChangeSubject = (subjectId: string) => {
    if (subjectId !== NONE_FIELD_VALUE) {
      localGoal = {
        ...goal,
        subjectId,
      }
      setLocalStorageItem('preferredSubjectId', subjectId)
    }
  }

  const handleSave = async () => {
    try {
      if (localGoal.id) {
        await goalsUpdate({
          path: { id: localGoal.id },
          body: localGoal as GoalType,
        })
      } else {
        await goalsCreate({
          body: localGoal as GoalCreateType,
        })
      }
      if (onDone) {
        await onDone()
      }
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
      {#if isGoalPersonal}
        <pkt-select
          label="Fag"
          name="goalSubject"
          fullwidth={true}
          value={localGoal.subjectId || NONE_FIELD_VALUE}
          hasError={!localGoal.subjectId || localGoal.subjectId === NONE_FIELD_VALUE}
          requiredText="Velg et fag"
          disabled={!localGoal.isRelevant}
          onchange={(e: Event) => {
            const target = e.target as HTMLSelectElement | null
            const subjectId = target?.value || NONE_FIELD_VALUE
            handleChangeSubject(subjectId)
          }}
        >
          <option disabled value={NONE_FIELD_VALUE}>Velg fag</option>
          {#each $dataStore.subjects as aSubject}
            <option value={aSubject.id}>
              {aSubject.displayName}
            </option>
          {/each}
        </pkt-select>
      {:else}
        <div class="fs-5 mb-1 {!subjectViaGroup ? 'alert alert-warning' : ''}">
          {subjectViaGroup
            ? 'Fag: ' + subjectViaGroup.displayName
            : 'Denne gruppen er ikke tilknyttet et fag'}
        </div>
      {/if}
    </div>
  </div>
  <div class="form-group mb-3">
    <div class="pkt-inputwrapper">
      <pkt-select
        label="Mestringsskjema"
        name="goalMasterySchema"
        fullwidth={true}
        value={localGoal.masterySchemaId || NONE_FIELD_VALUE}
        hasError={!localGoal.masterySchemaId || localGoal.masterySchemaId === NONE_FIELD_VALUE}
        requiredText="Velg et mestringsskjema"
        disabled={!localGoal.isRelevant}
        onchange={(e: Event) => {
          const target = e.target as HTMLSelectElement | null
          const msid = target?.value || NONE_FIELD_VALUE
          handleChangeMasterySchema(msid)
        }}
      >
        <option disabled value={NONE_FIELD_VALUE}>Velg mestringsskjema</option>
        {#each masterySchemas as masterySchema}
          <option disabled={!masterySchema.isDefault} value={masterySchema.id}>
            {masterySchema.title}
          </option>
        {/each}
      </pkt-select>
    </div>
  </div>

  <div class="form-group mb-3">
    <label for="goalSortOrder" class="form-label">Rekkefølge</label>
    <input
      id="goalSortOrder"
      type="integer"
      class="form-control rounded-0 border-2 border-primary input-field"
      bind:value={localGoal.sortOrder}
      disabled={!localGoal.isRelevant}
      placeholder="Rekkefølge (tall)"
    />
  </div>

  {#if $dataStore.currentSchool.isGoalTitleEnabled}
    <div class="form-group mb-3">
      <label for="goalTitle" class="form-label">Tittel</label>
      <input
        id="goalTitle"
        type="text"
        class="form-control rounded-0 border-2 border-primary input-field"
        bind:value={localGoal.title}
        disabled={!localGoal.isRelevant}
        placeholder="Tittel på målet"
      />
    </div>
  {/if}

  <div>
    <pkt-checkbox
      class="mb-1"
      label={localGoal.isRelevant ? 'Målet er i bruk' : 'Målet er ikke lenger relevant'}
      labelPosition="right"
      isSwitch="true"
      aria-checked={localGoal.isRelevant ? 'true' : 'false'}
      checked={localGoal.isRelevant}
      onchange={() => (localGoal = { ...localGoal, isRelevant: !localGoal.isRelevant })}
    ></pkt-checkbox>
  </div>

  <div class="d-flex gap-3 justify-content-start mt-5">
    <ButtonMini
      options={{
        title: 'Lagre',
        iconName: 'check',
        skin: 'primary',
        variant: 'label-only',
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
