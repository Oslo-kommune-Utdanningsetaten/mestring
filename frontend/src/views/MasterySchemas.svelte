<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-button.js'
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import MasterySchemaEdit from '../components/MasterySchemaEdit.svelte'
  import { masterySchemasDestroy, masterySchemasList } from '../generated/sdk.gen'
  import type { MasterySchemaReadable } from '../generated/types.gen'
  import type { MasterySchemaWithConfig } from '../types/models'

  let masterySchemas = $state<MasterySchemaWithConfig[]>([])
  let masterySchemaWip: Partial<MasterySchemaReadable> | null =
    $state<Partial<MasterySchemaReadable> | null>(null)

  let isJsonVisible = $state<boolean>(false)

  const fetchMasterySchemas = async () => {
    try {
      const result = await masterySchemasList()
      masterySchemas = result.data || []
    } catch (error) {
      console.error('Error fetching groups:', error)
      masterySchemas = []
    }
  }

  const handleDone = () => {
    masterySchemaWip = null
    fetchMasterySchemas()
  }

  const handleEditMasterySchema = (masterySchema: MasterySchemaReadable | null) => {
    masterySchemaWip = masterySchema ? { ...masterySchema } : {}
  }

  const handleDeleteMasterySchema = async (masterySchemaId: string) => {
    try {
      await masterySchemasDestroy({ path: { id: masterySchemaId } })
      await fetchMasterySchemas()
    } catch (error) {
      console.error('Error deleting schema:', error)
    }
  }

  $effect(() => {
    fetchMasterySchemas()
  })
</script>

<section class="py-4">
  <h1 class="mb-4">Mastery Schemas</h1>
  <pkt-button
    size="small"
    skin="primary"
    type="button"
    variant="label-only"
    onclick={() => handleEditMasterySchema(null)}
    onkeydown={(e: any) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault()
        handleEditMasterySchema(null)
      }
    }}
    role="button"
    tabindex="0"
  >
    Nytt mestringsskjema
  </pkt-button>

  <div class="pkt-input-check mt-3">
    <div class="pkt-input-check__input">
      <input
        class="pkt-input-check__input-checkbox"
        type="checkbox"
        role="switch"
        id="groupTypeSwitch"
        bind:checked={isJsonVisible}
      />
      <label class="pkt-input-check__input-label" for="groupTypeSwitch">Vis JSON config</label>
    </div>
  </div>

  <div class="mt-4">
    {#if masterySchemas.length > 0}
      {#each masterySchemas as masterySchema}
        <div class="card shadow-sm">
          <div class="card-body">
            <h5 class="card-title">{masterySchema.title}</h5>
            <p class="card-text">
              {masterySchema.description || 'Ingen beskrivelse'}
            </p>

            <div class="mb-4">
              {#each masterySchema?.config?.levels as level}
                <span class="p-2" style="background-color: {level.color || 'white'};">
                  {level.title}
                </span>
              {/each}
            </div>

            {#if isJsonVisible}
              <div class="json-viewer">
                <pre>{JSON.stringify(masterySchema, null, 2)}</pre>
              </div>
            {/if}

            <pkt-button
              size="small"
              skin="secondary"
              variant="icon-left"
              iconName="edit"
              class="my-2 me-2"
              onclick={() => handleEditMasterySchema(masterySchema)}
              onkeydown={(e: any) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  handleEditMasterySchema(masterySchema)
                }
              }}
              role="button"
              tabindex="0"
            >
              Rediger
            </pkt-button>

            <pkt-button
              size="small"
              skin="secondary"
              variant="icon-left"
              iconName="trash-can"
              class="my-2"
              onclick={() => handleDeleteMasterySchema(masterySchema.id)}
              onkeydown={(e: any) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  handleDeleteMasterySchema(masterySchema.id)
                }
              }}
              role="button"
              tabindex="0"
            >
              Slett
            </pkt-button>
          </div>
        </div>
      {/each}
    {:else}
      <div class="alert alert-info">No mastery schemas available.</div>
    {/if}
  </div>
</section>

<!-- offcanvas for creating/editing goals -->
<div class="custom-offcanvas shadow-sm" class:visible={!!masterySchemaWip}>
  <MasterySchemaEdit masterySchema={masterySchemaWip} onDone={handleDone} />
</div>

<style>
  .custom-offcanvas {
    right: -70vw;
    width: 70vw;
    overflow-y: auto;
  }
</style>
