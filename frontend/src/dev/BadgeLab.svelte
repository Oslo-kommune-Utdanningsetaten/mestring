<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-select.js'
  import type { ObservationType } from '../generated/types.gen'
  import type { MasteryData } from '../types/models'
  import { dataStore } from '../stores/data'
  import { useMasteryCalculations } from '../utils/masteryHelpers'
  import { inferMastery } from '../utils/functions'
  import MasteryLevelBadge from '../components/MasteryLevelBadge.svelte'
  import { MASTERY_BADGE_VARIANTS } from '../utils/constants'

  const millisecondsInDay = 24 * 60 * 60 * 1000
  const variants = [
    MASTERY_BADGE_VARIANTS.CIRCLE,
    MASTERY_BADGE_VARIANTS.TRIANGLE,
    MASTERY_BADGE_VARIANTS.SMILEY,
    MASTERY_BADGE_VARIANTS.BEEHIVE,
  ]

  let selectedSchemaId = $state($dataStore.masterySchemas[0]?.id || undefined)

  const masterySchema = $derived(
    $dataStore.masterySchemas.find(schema => schema.id === selectedSchemaId) ?? null
  )

  const calculations = $derived(useMasteryCalculations(masterySchema))

  // Turn an list of mastery values into an observation sequence,
  // spacing them one day apart so inferMastery can calculate a trend
  const observationsFromValues = (values: number[]): ObservationType[] => {
    const base = new Date('2025-01-01').getTime()
    return values.map(
      (value, i) =>
        ({
          masteryValue: value,
          createdAt: new Date(base + i * millisecondsInDay).toISOString(),
        }) as unknown as ObservationType
    )
  }

  // Build a short observation sequence rising from `start` to `end`.
  const makeObservations = (start: number, end: number, steps = 5): ObservationType[] =>
    observationsFromValues(
      Array.from({ length: steps }, (_, i) => Math.round(start + ((end - start) * i) / (steps - 1)))
    )

  // Rows added manually via the widget below - rendered first in table
  type LabRow = { values: number[]; masteryData: MasteryData | undefined }
  let customRows = $state<LabRow[]>([])

  let isAdding = $state(false)
  let observationInput = $state('')
  let inputError = $state('')

  const addCustomRow = () => {
    const values = observationInput
      .split(',')
      .map(part => part.trim())
      .filter(part => part.length > 0)
      .map(Number)

    if (values.length === 0 || values.some(Number.isNaN)) {
      inputError = 'Enter a comma-separated list of numbers, e.g. 1, 2, 2, 3'
      return
    }

    const observations = observationsFromValues(values)
    customRows = [{ values, masteryData: inferMastery(observations) ?? undefined }, ...customRows]
    observationInput = ''
    inputError = ''
    isAdding = false
  }

  // Each row is an observation sequence, from lowest value up to a differing end value (ranges useful for evaluating badge rendering)
  const rows = $derived.by(() => {
    const { minValue, maxValue } = calculations
    if (maxValue <= minValue) return []
    const endpoints: number[] = []
    for (let v = minValue; v <= maxValue; v++) endpoints.push(v)
    return endpoints.map(end => {
      const observations = makeObservations(minValue, end)
      return {
        values: observations.map(obs => obs.masteryValue),
        masteryData: inferMastery(observations) ?? undefined,
      }
    })
  })
</script>

<div class="container py-3">
  <h2 class="h4 mb-3">MasteryBadge Laboratory</h2>
  <div class="mb-3 pkt-inputwrapper">
    <pkt-select
      label="Mastery schema"
      name="masterySchema"
      value={selectedSchemaId}
      onchange={(e: Event) => {
        const target = e.target as HTMLSelectElement | null
        if (target?.value) selectedSchemaId = target.value
      }}
    >
      {#each $dataStore.masterySchemas as schema}
        <option value={schema.id}>{schema.title ?? schema.id} ({schema.id})</option>
      {/each}
    </pkt-select>
  </div>

  {#if !masterySchema}
    <div class="alert alert-warning">
      Mastery schema <code>{selectedSchemaId}</code>
      not found in the data store. Make sure you're logged in and a school with this schema is selected.
    </div>
  {:else}
    <p class="text-secondary">
      Schema <strong>{masterySchema.title}</strong>
      (
      <code>{masterySchema.id}</code>
      ) — range
      <code>{calculations.minValue}</code>
      –
      <code>{calculations.maxValue}</code>
      , deltaValue
      <code>{calculations.deltaValue}</code>
      . Trends come from
      <code>inferMastery</code>
      over an observation sequence rising from the bottom of the scale to each end value, so they reflect
      real linear-regression output.
    </p>

    <div class="my-3">
      {#if isAdding}
        <form
          class="d-flex align-items-start gap-2"
          onsubmit={e => {
            e.preventDefault()
            addCustomRow()
          }}
        >
          <div class="flex-grow-1">
            <input
              type="text"
              class="form-control form-control-sm"
              placeholder="Comma-separated observations, e.g. 1, 2, 2, 3"
              bind:value={observationInput}
              aria-label="Comma-separated observations"
            />
            {#if inputError}
              <small class="text-danger">{inputError}</small>
            {/if}
          </div>
          <button type="submit" class="btn btn-sm btn-primary">Add</button>
          <button
            type="button"
            class="btn btn-sm btn-outline-secondary"
            onclick={() => {
              isAdding = false
              observationInput = ''
              inputError = ''
            }}
          >
            Cancel
          </button>
        </form>
      {:else}
        <button
          type="button"
          class="btn btn-sm btn-outline-primary"
          title="Add a new row"
          onclick={() => (isAdding = true)}
        >
          + Add row
        </button>
      {/if}
    </div>

    <table class="table table-sm align-middle">
      <thead>
        <tr>
          <th>Observations</th>
          <th>Mastery</th>
          <th>Trend</th>
          {#each variants as variant}
            <th class="text-capitalize">{variant}</th>
          {/each}
        </tr>
      </thead>

      <tbody>
        {#each customRows as { values, masteryData }}
          <tr>
            <td><code>{values.join(', ')}</code></td>
            <td><code>{masteryData?.mastery ?? '–'}</code></td>
            <td><code>{masteryData?.trend ?? '–'}</code></td>
            {#each variants as variant}
              <td>
                <MasteryLevelBadge {variant} {masterySchema} {masteryData} />
              </td>
            {/each}
          </tr>
        {/each}
        {#each rows as { values, masteryData }}
          <tr>
            <td><code>{values.join(', ')}</code></td>
            <td><code>{masteryData?.mastery ?? '–'}</code></td>
            <td><code>{masteryData?.trend ?? '–'}</code></td>
            {#each variants as variant}
              <td>
                <MasteryLevelBadge {variant} {masterySchema} {masteryData} />
              </td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</div>
