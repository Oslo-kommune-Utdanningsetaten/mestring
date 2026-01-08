<script lang="ts">
  import type { StatusType, SubjectType, UserType } from '../generated/types.gen'
  import { statusCreate, statusUpdate } from '../generated/sdk.gen'
  import type { MasterySchemaWithConfig } from '../types/models'
  import { useMasteryCalculations } from '../utils/masteryHelpers'
  import { dataStore } from '../stores/data'
  import ButtonMini from './ButtonMini.svelte'
  import ValueInputVertical from './ValueInputVertical.svelte'
  import ValueInputHorizontal from './ValueInputHorizontal.svelte'

  const { student, status, subject, onDone } = $props<{
    student: UserType | null
    status: StatusType | {} | null
    subject: SubjectType | null
    onDone: () => void
  }>()

  const masterySchema: MasterySchemaWithConfig = $derived($dataStore.defaultMasterySchema)
  const calculations = $derived(useMasteryCalculations(masterySchema))

  let localStatus = $state<Partial<StatusType> & { masteryValue: number }>({
    masteryValue: calculations.defaultValue,
  })

  // Update localStatus when status prop changes
  $effect(() => {
    localStatus = {
      ...status,
    }
  })

  const renderDirection = (): 'horizontal' | 'vertical' | 'unknown' => {
    return masterySchema?.config?.renderDirection || 'unknown'
  }

  const handleSave = async () => {
    localStatus.studentId = student?.id
    localStatus.subjectId = subject?.id
    localStatus.schoolId = $dataStore.currentSchool?.id
    try {
      if (localStatus.id) {
        const result = await statusUpdate({
          path: { id: localStatus.id },
          body: localStatus as any,
        })
      } else {
        const result = await statusCreate({
          body: localStatus as any,
        })
      }
      onDone()
    } catch (error) {
      console.error('Error saving status:', error)
    }
  }
</script>

<div class="status-edit p-4">
  {#if localStatus}
    <h3 class="pb-2">
      {localStatus.id ? 'Redigerer' : 'Ny'} status
    </h3>

    {#if masterySchema?.config?.isMasteryValueInputEnabled}
      <div class="mb-4">
        {#if renderDirection() === 'vertical'}
          <ValueInputVertical
            {masterySchema}
            bind:masteryValue={localStatus.masteryValue}
            label="Hvor ofte mestrer {student?.name} {subject?.shortName || 'dette faget'}?"
          />
        {:else}
          <ValueInputHorizontal
            {masterySchema}
            bind:masteryValue={localStatus.masteryValue}
            label="Hvor ofte mestrer {student?.name} {subject?.shortName || 'dette faget'}?"
          />
        {/if}
      </div>
    {/if}

    {#if masterySchema?.config?.isMasteryDescriptionInputEnabled}
      <div class="form-group my-4">
        <label for="description" class="form-label">Beskrivelse/tilbakemelding</label>
        <textarea
          id="description"
          class="form-control rounded-0 border-2 border-primary"
          bind:value={localStatus.masteryDescription}
          placeholder="Kort beskrivelse av elevens mestringsnivå"
          rows="4"
        ></textarea>
      </div>
    {/if}

    {#if masterySchema?.config?.isFeedforwardInputEnabled}
      <div class="form-group mb-3">
        <label for="feedforward" class="form-label">Fremovermelding</label>
        <textarea
          id="feedforward"
          class="form-control rounded-0 border-2 border-primary"
          bind:value={localStatus.feedforward}
          placeholder="Konkret, hva kan eleven gjøre for å forbedre seg?"
          rows="4"
        ></textarea>
      </div>
    {/if}

    <div class="d-flex gap-2 justify-content-start mt-4">
      <ButtonMini
        options={{
          title: 'Lagre',
          iconName: 'check',
          skin: 'primary',
          variant: 'label-only',
          classes: 'm-2',
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
  {:else}
    No status...
  {/if}
</div>

<style>
  .status-edit {
    width: 100%;
    max-width: 100%;
  }
</style>
