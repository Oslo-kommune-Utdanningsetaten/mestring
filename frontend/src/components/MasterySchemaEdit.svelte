<script lang="ts">
  import ButtonMini from './ButtonMini.svelte'
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import { JSONEditor } from 'svelte-jsoneditor'
  import { masterySchemasUpdate, masterySchemasCreate } from '../generated/sdk.gen'
  import type { MasterySchemaType } from '../generated/types.gen'
  import type { MasterySchemaConfig } from '../types/models'

  const defaultConfig = {
    levels: [
      {
        title: 'Gjengi',
        minValue: 0,
        maxValue: 33,
        color: '#ff8274',
      },
      {
        title: 'Forklare',
        minValue: 34,
        maxValue: 66,
        color: '#f9c66b',
      },
      {
        title: 'Se sammenhenger',
        minValue: 67,
        maxValue: 100,
        color: '#38a87f',
      },
    ],
    renderDirection: 'horizontal',
    increment: 1,
  }

  const { masterySchema, onDone } = $props<{
    masterySchema: Partial<MasterySchemaType> | null
    onDone: () => void
  }>()
  let localMasterySchema = $state<Partial<MasterySchemaType>>({ ...masterySchema })
  let localJson = $derived<Partial<MasterySchemaConfig>>(
    localMasterySchema?.config || defaultConfig
  )

  const handleJsonChange = (updatedContent: any) => {
    if (updatedContent.json) {
      localJson = updatedContent.json
    } else if (updatedContent.text) {
      localJson = JSON.parse(updatedContent.text)
    }
  }

  const handleSave = async () => {
    localMasterySchema.config = localJson
    try {
      if (localMasterySchema.id) {
        await masterySchemasUpdate({
          path: { id: localMasterySchema.id },
          body: localMasterySchema,
        })
      } else {
        await masterySchemasCreate({
          body: localMasterySchema,
        })
      }
      onDone()
    } catch (error) {
      // TODO: Show an error message to the user
      console.error('Error saving MasterySchema:', error)
    }
  }

  $effect(() => {
    localMasterySchema = { ...masterySchema }
  })
</script>

<div class="p-4 mastery-schema-edit">
  <h3 class="pb-2">{localMasterySchema.id ? 'Redigerer mestringskjema' : 'Nytt mestringskjema'}</h3>
  <div class="form-group mb-3">
    <label for="masterySchemaTitle" class="form-label">Tittel</label>
    <input
      id="masterySchemaTitle"
      type="text"
      class="form-control rounded-0 border-2 border-primary"
      bind:value={localMasterySchema.title}
      placeholder="Tittel"
    />
  </div>

  <div class="form-group mb-3">
    <label for="masterySchemaDescription" class="form-label">Beskrivelse</label>
    <input
      id="masterySchemaDescription"
      type="text"
      class="form-control rounded-0 border-2 border-primary"
      bind:value={localMasterySchema.description}
      placeholder="Beskrivelse"
    />
  </div>

  <JSONEditor content={{ json: localJson }} onChange={handleJsonChange} />

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
</div>

<style>
  .mastery-schema-edit {
    width: 100%;
    max-width: 100%;
  }

  input {
    height: 47px;
  }

  input,
  select {
    width: 100% !important;
  }
</style>
