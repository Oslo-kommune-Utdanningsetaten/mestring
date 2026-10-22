<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import type { MasterySchemaType } from '../../generated/types.gen'
  import type { MasterySchemaWithConfig } from '../../types/models'
  import {
    masterySchemasDestroy,
    masterySchemasList,
    masterySchemasPartialUpdate,
  } from '../../generated/sdk.gen'
  import { VALUE_INPUT_VARIANT } from '../../utils/constants'
  import { currentSchool } from '../../stores/data'
  import { useMasteryCalculations, areSchemaValuesConsistent } from '../../utils/masteryHelpers'

  import ButtonMini from '../../components/ButtonMini.svelte'
  import MasterySchemaLevel from '../../components/MasterySchemaLevel.svelte'
  import Offcanvas from '../../components/Offcanvas.svelte'
  import MasterySchemaEdit from '../../components/edit/MasterySchemaEdit.svelte'

  let masterySchemaWip = $state<Partial<MasterySchemaWithConfig> | null>(null)
  let isJsonVisible = $state<boolean>(false)
  let isEditorOpen = $state<boolean>(false)
  let masterySchemas = $state<MasterySchemaWithConfig[]>([])

  const areSchemasConsistent = $derived(areSchemaValuesConsistent(masterySchemas))

  const defaultConfig = {
    levels: [
      { title: 'Gjengi', color: 'rgb(235, 101, 97)', minValue: 1, maxValue: 33 },
      { title: 'Forklare', color: 'rgb(255, 204, 0)', minValue: 34, maxValue: 66 },
      { title: 'Se sammenhenger', color: 'rgb(23, 231, 21)', minValue: 67, maxValue: 100 },
    ],
    inputIncrement: 1,
    flatTrendThreshold: 6,
    valueInput: VALUE_INPUT_VARIANT.SLIDER_HORIZONTAL_STAIRS,
    isIncrementIndicatorEnabled: true,
    isMasteryValueVisible: false,
    isMasteryValueInputEnabled: true,
    isMasteryDescriptionInputEnabled: true,
    isFeedforwardInputEnabled: true,
  }

  const fetchMasterySchemas = async () => {
    const result = await masterySchemasList({ query: { school: $currentSchool.id } })
    masterySchemas = result.data || []
  }

  const handleDone = () => {
    isEditorOpen = false
    fetchMasterySchemas()
  }

  const handleNewMasterySchema = () => {
    masterySchemaWip = { schoolId: $currentSchool.id, config: defaultConfig }
    isEditorOpen = true
  }

  const handleEditMasterySchema = (masterySchema: MasterySchemaType | null) => {
    masterySchemaWip = { ...masterySchema }
    isEditorOpen = true
  }

  const handleCopyMasterySchema = (masterySchema: MasterySchemaType | null) => {
    masterySchemaWip = { ...masterySchema }
    delete masterySchemaWip.id
    masterySchemaWip.title = 'KOPI: ' + masterySchemaWip.title
    isEditorOpen = true
  }

  const handleDeleteMasterySchema = async (masterySchemaId: string) => {
    try {
      await masterySchemasDestroy({
        path: { id: masterySchemaId },
      })
    } catch (error) {
      console.error('Error deleting schema:', error)
    } finally {
      await fetchMasterySchemas()
    }
  }

  // Toggle whether group title is displayed in goal edit
  const toggleIsDefault = async (masterySchema: MasterySchemaType) => {
    try {
      const current = masterySchema.isDefault ?? false
      const result = await masterySchemasPartialUpdate({
        path: { id: masterySchema.id },
        body: { isDefault: !current },
      })
      const otherSchemasForSchool = masterySchemas.filter(
        schema => schema.schoolId === $currentSchool?.id && schema.id !== masterySchema.id
      )
      // If setting this schema to default, unset others
      if (result.data?.isDefault) {
        for (const schema of otherSchemasForSchool) {
          await masterySchemasPartialUpdate({
            path: { id: schema.id },
            body: { isDefault: false },
          })
        }
      }
    } catch (error) {
      console.error('Error updating isGoalTitleEnabled:', error)
    } finally {
      // sleep a bit to allow backend to process changes
      await new Promise(resolve => setTimeout(resolve, 0.6))
      await fetchMasterySchemas()
    }
  }

  const toggleIsEnabled = async (masterySchema: MasterySchemaType) => {
    try {
      const current = masterySchema.isEnabled ?? false
      await masterySchemasPartialUpdate({
        path: { id: masterySchema.id },
        body: { isEnabled: !current },
      })
    } catch (error) {
      console.error('Error updating isEnabled:', error)
    } finally {
      await fetchMasterySchemas()
    }
  }

  const getMasteryLevelsSummary = (masterySchema: MasterySchemaWithConfig) => {
    const calculations = useMasteryCalculations(masterySchema)
    return calculations.minValue + ' - ' + calculations.maxValue
  }

  $effect(() => {
    if ($currentSchool?.id) {
      fetchMasterySchemas()
    }
  })
</script>

<section class="py-4">
  <h2 class="mb-4">Mestringsskjemaer</h2>

  {#if $currentSchool}
    {#if masterySchemas.length > 0 && !areSchemasConsistent}
      <div class="alert alert-warning my-3">
        Mestringsskjemaene for denne skolen har ulik range. Dette kan føre til inkonsistente
        visninger og problemer med datakvalitet. Vurder å justere range i skjemaene slik at de er
        like.
      </div>
    {/if}
    {#if masterySchemas.length > 0 && !masterySchemas.some(schema => schema.isEnabled)}
      <div class="alert alert-warning mt-3">
        Ingen av mestringsskjemaene for denne skolen er satt til enabled.
      </div>
    {/if}
    {#if masterySchemas.length > 0 && !masterySchemas.some(schema => schema.isDefault)}
      <div class="alert alert-warning mt-3">
        Ingen av mestringsskjemaene for denne skolen er satt til default.
      </div>
    {/if}

    <ButtonMini
      options={{
        title: 'Nytt mestringsskjema',
        iconName: 'plus-sign',
        skin: 'primary',
        variant: 'label-only',
        classes: '',
        onClick: () => handleNewMasterySchema(),
      }}
    >
      Nytt mestringsskjema
    </ButtonMini>

    {#if masterySchemas.length > 0}
      {#each masterySchemas as masterySchema}
        <div class="card shadow-sm">
          <div class="card-body">
            <h3 class="card-title">
              {masterySchema.title}
            </h3>
            <div>
              {masterySchema.description || 'Ingen beskrivelse'}
            </div>
            <div class="text-muted my-3">
              <div>
                Range: {getMasteryLevelsSummary(masterySchema)}
              </div>
              <div>
                Input: {masterySchema.config.valueInput}
              </div>
              <div>
                ID: {masterySchema.id}
              </div>
            </div>

            <div class="mb-2">
              <pkt-checkbox
                label={masterySchema.isDefault ? 'Default schema for school' : 'Not default'}
                labelPosition="right"
                isSwitch="true"
                aria-checked={masterySchema.isDefault}
                checked={masterySchema.isDefault}
                onchange={() => toggleIsDefault(masterySchema)}
              ></pkt-checkbox>
            </div>

            <div class="mb-4">
              <pkt-checkbox
                label={masterySchema.isEnabled ? 'Currently enabled' : 'Currently disabled'}
                labelPosition="right"
                isSwitch="true"
                aria-checked={masterySchema.isEnabled}
                checked={masterySchema.isEnabled}
                onchange={() => toggleIsEnabled(masterySchema)}
              ></pkt-checkbox>
            </div>

            <div class="mb-4 d-flex gap-2">
              {#each masterySchema?.config?.levels || [] as level}
                <div class="d-flex flex-column align-items-center">
                  <MasterySchemaLevel masteryValue={level.minValue} {masterySchema} />
                  <span class="small text-muted py-1 bg-light w-100 text-center">
                    {level.minValue}&nbsp;➡&nbsp;{level.maxValue}
                  </span>
                </div>
              {/each}
            </div>

            {#if isJsonVisible}
              <div class="json-viewer">
                <pre>{JSON.stringify(masterySchema, null, 2)}</pre>
              </div>
            {/if}

            <ButtonMini
              options={{
                title: 'Rediger',
                iconName: 'edit',
                skin: 'secondary',
                variant: 'icon-left',
                classes: 'my-2 me-2',
                onClick: () => handleEditMasterySchema(masterySchema),
              }}
            >
              Rediger
            </ButtonMini>

            <ButtonMini
              options={{
                title: 'Kopier',
                iconName: 'copy',
                skin: 'secondary',
                variant: 'icon-left',
                classes: 'my-2 me-2',
                onClick: () => handleCopyMasterySchema(masterySchema),
              }}
            >
              Kopier
            </ButtonMini>

            <ButtonMini
              options={{
                title: 'Slett',
                iconName: 'trash-can',
                skin: 'secondary',
                variant: 'icon-left',
                classes: 'my-2',
                onClick: () => handleDeleteMasterySchema(masterySchema.id),
                delayActionFor: 4,
              }}
            >
              Slett
            </ButtonMini>
          </div>
        </div>
      {/each}
    {:else}
      <div class="alert alert-info">Ingen mestringsskjemaer for denne skolen</div>
    {/if}
  {:else}
    <div class="alert alert-info">Velg en skole</div>
  {/if}
</section>

<!-- Offcanvas for creating/editing mastery schemas -->
<Offcanvas
  bind:isOpen={isEditorOpen}
  width="90vw"
  ariaLabel="Rediger mestringsskjema"
  onClosed={() => {
    masterySchemaWip = null
    fetchMasterySchemas()
  }}
>
  {#if masterySchemaWip}
    <MasterySchemaEdit masterySchema={masterySchemaWip} onDone={handleDone} />
  {/if}
</Offcanvas>

<style>
  pre {
    white-space: pre-wrap;
  }
  .filters-container {
    display: flex;
    gap: 1rem;
    align-items: flex-end;
  }

  .filter-item {
    display: flex;
    flex-direction: column;
    flex: 1 1 20rem;
    min-width: 3rem;
    max-width: 25rem;
  }
</style>
