<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-button.js'
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import MasterySchemaEdit from './MasterySchemaEdit.svelte'
  import { masterySchemasList, masterySchemasDestroy } from '../generated/sdk.gen'
  import type { MasterySchemaReadable } from '../generated/types.gen'

  let masterySchemas = $state<MasterySchemaReadable[]>([])
  let masterySchemaWip: Partial<MasterySchemaReadable> | null =
    $state<Partial<MasterySchemaReadable> | null>(null)

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

  const handleEditMasterySchema = (schema: MasterySchemaReadable | null) => {
    masterySchemaWip = schema ? { ...schema } : {}
  }

  async function handleDeleteMasterySchema(masterySchemaId: string) {
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

  <div class="mt-4">
    {#if masterySchemas.length > 0}
      {#each masterySchemas as masterySchema}
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">{masterySchema.title}</h5>
            <p class="card-text">
              {masterySchema.description || 'Ingen beskrivelse'}
            </p>
            <pre>{JSON.stringify(masterySchema.schema, null, 2)}</pre>
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
  }
</style>
