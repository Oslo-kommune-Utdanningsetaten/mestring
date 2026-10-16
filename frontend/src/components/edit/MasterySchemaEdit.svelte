<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import { JSONEditor, type Content, Mode } from 'svelte-jsoneditor'
  import type {
    MasterySchemaType,
    MasterySchemaCreateType,
    SchoolType,
  } from '../../generated/types.gen'
  import type { MasterySchemaConfig, MasterySchemaWithConfig } from '../../types/models'
  import { masterySchemasUpdate, masterySchemasCreate, schoolsList } from '../../generated/sdk.gen'
  import { useMasteryCalculations } from '../../utils/masteryHelpers'

  import ButtonMini from '../ButtonMini.svelte'
  import MasteryValueInput from '../MasteryValueInput.svelte'

  const { masterySchema, onDone } = $props<{
    masterySchema: Partial<MasterySchemaType>
    onDone: () => void
  }>()

  let localMasterySchema = $state<Partial<MasterySchemaWithConfig>>({ ...masterySchema })
  let schools = $state<SchoolType[]>([])

  let editorContent = $derived<Content>({ json: localMasterySchema.config })
  let calculations = $derived(useMasteryCalculations(localMasterySchema))
  let placeholderMasteryValue = $derived(calculations.defaultValue)

  const fetchSchools = async () => {
    try {
      const result = await schoolsList({})
      schools = result.data || []
    } catch (error) {
      console.error('Error fetching schools:', error)
      schools = []
    }
  }

  const handleSave = async () => {
    try {
      if ('json' in editorContent) {
        localMasterySchema.config = editorContent.json as MasterySchemaConfig
      } else if ('text' in editorContent) {
        localMasterySchema.config = JSON.parse(editorContent.text) as MasterySchemaConfig
      }
    } catch (error) {
      console.error('Invalid JSON in editor:', error)
      return
    }
    if (localMasterySchema.description === '') {
      localMasterySchema.description = null
    }
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
      console.error('Error saving MasterySchema:', error)
    }
  }

  $effect(() => {
    fetchSchools()
  })
</script>

<div class="p-4 mastery-schema-edit">
  <h3 class="pb-2">{localMasterySchema.id ? 'Redigerer mestringskjema' : 'Nytt mestringskjema'}</h3>
  <div class="form-group mb-3">
    <div class="d-flex gap-3">
      <div class="flex-fill">
        <label for="masterySchemaTitle" class="form-label">Tittel</label>
        <input
          id="masterySchemaTitle"
          type="text"
          class="form-control rounded-0 border-2 border-primary"
          bind:value={localMasterySchema.title}
          placeholder="Tittel"
        />
      </div>

      {#if schools.length > 1}
        <div style="flex: 0 0 40%;">
          <label for="schoolSelect" class="form-label">Lagre til skole</label>
          <select
            class="pkt-input w-100"
            id="schoolSelect"
            bind:value={localMasterySchema.schoolId}
          >
            {#each schools as school}
              <option value={school.id} selected={school.id === localMasterySchema?.id}>
                {school.displayName}
              </option>
            {/each}
          </select>
        </div>
      {/if}
    </div>
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

  <div class="my-4">
    <MasteryValueInput
      masterySchema={localMasterySchema as MasterySchemaType}
      bind:value={placeholderMasteryValue}
      title="Forhåndsvisning av input"
    />
  </div>

  <div style="height: 50vh;">
    <JSONEditor bind:content={editorContent} mode={Mode.text} />
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
