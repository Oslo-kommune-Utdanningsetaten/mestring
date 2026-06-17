<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-select.js'
  import type { ObservationType } from '../generated/types.gen'
  import { dataStore } from '../stores/data'
  import { useMasteryCalculations } from '../utils/masteryHelpers'
  import { inferMastery } from '../utils/functions'
  import MasteryLevelBadge from '../components/MasteryLevelBadge.svelte'
  import { MASTERY_BADGE_VARIANTS } from '../utils/constants'

  const DEFAULT_SCHEMA_ID = 'x6JP0qgkSpiY'

  // Default to the previously hardcoded schema if present, otherwise the first available.
  let selectedSchemaId = $state(DEFAULT_SCHEMA_ID)

  // Pull the selected schema straight from the live data store.
  const masterySchema = $derived(
    $dataStore.masterySchemas.find(schema => schema.id === selectedSchemaId) ?? null
  )

  // Use the real calculation function so min/max/delta match production exactly.
  const calculations = $derived(useMasteryCalculations(masterySchema))

  const variants = [
    MASTERY_BADGE_VARIANTS.CIRCLE,
    MASTERY_BADGE_VARIANTS.TRIANGLE,
    MASTERY_BADGE_VARIANTS.SMILEY,
    MASTERY_BADGE_VARIANTS.BEEHIVE,
  ]

  // Build a short observation sequence rising from `start` to `end`.
  // Running these through inferMastery (linear regression) yields the same
  // kind of realistic, mostly-small trend values the app sees in production.
  const makeObservations = (start: number, end: number, steps = 5): ObservationType[] => {
    const base = new Date('2025-01-01').getTime()
    return Array.from({ length: steps }, (_, i) => {
      const value = Math.round(start + ((end - start) * i) / (steps - 1))
      return {
        masteryValue: value,
        createdAt: new Date(base + i * 86_400_000).toISOString(),
      } as unknown as ObservationType
    })
  }

  // Sweep across the real range: each row is an observation sequence rising from the
  // bottom of the scale up to a different end value -> realistic trends of varying strength.
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
  <h1 class="h4 mb-3">Badge Lab</h1>

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

    <table class="table table-sm align-middle">
      <thead>
        <tr>
          <th>observations</th>
          <th>mastery</th>
          <th>trend</th>
          {#each variants as variant}
            <th class="text-capitalize">{variant}</th>
          {/each}
        </tr>
      </thead>
      <tbody>
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
