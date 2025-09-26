<script lang="ts">
  import { subjectsCreate, subjectsUpdate } from '../generated/sdk.gen'
  import type { SubjectReadable, SchoolReadable } from '../generated/types.gen'
  import ButtonMini from './ButtonMini.svelte'

  const {
    subject = null,
    school = null,
    onDone,
  } = $props<{
    subject: SubjectReadable | null
    school: SchoolReadable | null
    onDone: () => void
  }>()
  let localSubject = $derived<Partial<SubjectReadable>>({ ...subject })

  // What determines if we can edit the subject?
  let isFormValid = $derived(
    !!localSubject.displayName && !!localSubject.shortName && !!localSubject.ownedBySchoolId
  )

  const handleSave = async () => {
    try {
      if (localSubject.id) {
        await subjectsUpdate({
          path: { id: localSubject.id },
          body: localSubject,
        })
      } else {
        await subjectsCreate({
          body: localSubject,
        })
      }
      onDone()
    } catch (error) {
      console.error('Error saving subject:', error)
    }
  }

  $effect(() => {
    localSubject = {
      ...subject,
    }
  })
</script>

<div class="p-4">
  <h3 class="pb-2">{localSubject.id ? 'Redigerer' : 'Nytt'} mål for {school?.displayName}</h3>
  <hr />

  <pre>
    {JSON.stringify(localSubject, null, 2)}
    {JSON.stringify(school, null, 2)}
  </pre>

  <div class="form-group mb-3">
    <label for="subjectName" class="form-label">Navn</label>
    <input
      id="subjectName"
      type="text"
      class="form-control rounded-0 border-2 border-primary input-field"
      bind:value={localSubject.displayName}
      placeholder="Engelsk 3. årstrinn"
    />

    <label for="subjectShortName" class="form-label">Kortnavn</label>
    <input
      id="subjectShortName"
      type="text"
      class="form-control rounded-0 border-2 border-primary input-field"
      bind:value={localSubject.shortName}
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
        disabled: !isFormValid,
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
