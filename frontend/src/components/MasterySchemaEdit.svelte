<script lang="ts">
  import ButtonMini from './ButtonMini.svelte'
  import MasteryValueInput from './MasteryValueInput.svelte'
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import { JSONEditor } from 'svelte-jsoneditor'
  import { masterySchemasUpdate, masterySchemasCreate } from '../generated/sdk.gen'
  import type { MasterySchemaType, MasterySchemaCreateType } from '../generated/types.gen'
  import type { MasterySchemaConfig } from '../types/models'
  import { useMasteryCalculations } from '../utils/masteryHelpers'

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
    valueInput: 'sliderHorizontal',
    inputIncrement: 1,
    flatTrendThreshold: 5,
    isValueIndicatorEnabled: true,
    isFeedforwardInputEnabled: true,
    isIncrementIndicatorEnabled: true,
    isMasteryValueInputEnabled: true,
    isMasteryDescriptionInputEnabled: true,
  }

  const { masterySchema, onDone } = $props<{
    masterySchema: Partial<MasterySchemaType> | null
    onDone: () => void
  }>()
  let localMasterySchema = $derived<Partial<MasterySchemaType>>({ ...masterySchema })
  let localJson = $derived<Partial<MasterySchemaConfig>>(
    localMasterySchema?.config || defaultConfig
  )
  let calculations = $derived(useMasteryCalculations(masterySchema))
  let placeholderMasteryValue = $derived(calculations.defaultValue)

  const handleJsonChange = (updatedContent: any) => {
    if (updatedContent.json) {
      localJson = updatedContent.json
      localMasterySchema.config = localJson
    } else if (updatedContent.text) {
      localJson = JSON.parse(updatedContent.text)
      localMasterySchema.config = localJson
    }
  }

  const handleSave = async () => {
    localMasterySchema.config = localJson
    try {
      if (localMasterySchema.id) {
        await masterySchemasUpdate({
          path: { id: localMasterySchema.id },
          body: localMasterySchema as MasterySchemaType,
        })
      } else {
        await masterySchemasCreate({
          body: localMasterySchema as MasterySchemaCreateType,
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

  <div>
    <MasteryValueInput
      masterySchema={localMasterySchema as MasterySchemaType}
      bind:value={placeholderMasteryValue}
      title="Forhåndsvisning av input"
    />
  </div>

  <div style="height: 40vh;">
    <JSONEditor content={{ json: localJson }} onChange={handleJsonChange} />
  </div>

  <div class="d-flex gap-2 justify-content-start">
    <ButtonMini
      options={{
        title: 'Lagre',
        iconName: 'check',
        skin: 'primary',
        variant: 'label-only',
        classes: 'mt-3',
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
        classes: 'mt-3 ms-3',
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
</style>
