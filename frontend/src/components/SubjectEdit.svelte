<script lang="ts">
  import { subjectsCreate, subjectsUpdate } from '../generated/sdk.gen'
  import type { SubjectReadable, SchoolReadable } from '../generated/types.gen'
  import ButtonMini from './ButtonMini.svelte'

  const { subject, school, onDone } = $props<{
    subject: SubjectReadable | null
    school: SchoolReadable | null
    onDone: () => void
  }>()
  let displayName = $state<string | null>(null)
  let shortName = $state<string | null>(null)
  let isFormValid = $derived(!!displayName?.trim() && !!shortName?.trim())

  const handleSave = async () => {
    try {
      if (subject?.id) {
        await subjectsUpdate({
          path: { id: subject.id },
          body: { ...subject, displayName, shortName },
        })
      } else {
        if (displayName === null || shortName === null || school === null) {
          console.error('Missing required fields to create subject')
          return
        }
        await subjectsCreate({
          body: { displayName, shortName, ownedBySchoolId: school.id },
        })
      }
      onDone()
    } catch (error) {
      console.error('Error saving subject:', error)
    }
  }

  $effect(() => {
    if (subject) {
      displayName = subject.displayName ?? null
      shortName = subject.shortName ?? null
    }
  })
</script>

<div class="p-4">
  <h3 class="pb-2">{subject?.id ? 'Redigerer' : 'Nytt'} mål for {school?.displayName}</h3>
  <hr />

  <div class="form-group mb-3">
    <label for="subjectName" class="form-label">Navn</label>
    <input
      id="subjectName"
      type="text"
      class="form-control rounded-0 border-2 border-primary input-field"
      name="displayName"
      bind:value={displayName}
      placeholder="Engelsk 3. årstrinn"
    />

    <label for="subjectShortName" class="form-label">Kortnavn</label>
    <input
      id="subjectShortName"
      type="text"
      class="form-control rounded-0 border-2 border-primary input-field"
      name="shortName"
      bind:value={shortName}
      placeholder="Engelsk"
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
  label {
    font-weight: 800;
  }

  .input-field {
    height: 48px;
  }

  input {
    width: 100% !important;
  }
</style>
