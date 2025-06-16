<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-button.js'
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import { JSONEditor } from 'svelte-jsoneditor'
  import { masterySchemasUpdate, masterySchemasCreate } from '../generated/sdk.gen'
  import type { MasterySchemaReadable } from '../generated/types.gen'

  const defaultSchema = {
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
    masterySchema: Partial<MasterySchemaReadable>
    onDone: () => void
  }>()
  let localMasterySchema = $state<Partial<MasterySchemaReadable>>({ ...masterySchema })
  let localJson = $derived<any>(localMasterySchema?.schema || defaultSchema)

  const handleJsonChange = (updatedContent: any) => {
    if (updatedContent.json) {
      localJson = updatedContent.json
    } else if (updatedContent.text) {
      localJson = JSON.parse(updatedContent.text)
    }
  }

  async function handleSave() {
    localMasterySchema.schema = JSON.stringify(localJson)
    try {
      if (localMasterySchema.id) {
        const result = await masterySchemasUpdate({
          path: { id: localMasterySchema.id },
          body: localMasterySchema,
        })
      } else {
        const result = await masterySchemasCreate({
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

<div class="p-4">
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
      disabled={!localMasterySchema.title?.trim()}
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
