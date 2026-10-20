<script lang="ts">
  import ColorPicker from 'svelte-awesome-color-picker'
  import type { GoalType, UserType } from '../generated/types.gen'
  import type { MasterySchemaConfig, MasterySchemaWithConfig } from '../types/models'
  import { VALUE_INPUT_VARIANT, VALUE_INPUT_VARIANTS } from '../utils/constants'

  import ObservationEdit from '../components/edit/ObservationEdit.svelte'

  type Rgb = { r: number; g: number; b: number; a: number }

  const parseRgbString = (color: string): Rgb => {
    const match = color.match(/rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/)
    if (!match) return { r: 0, g: 0, b: 0, a: 1 }
    return { r: Number(match[1]), g: Number(match[2]), b: Number(match[3]), a: 1 }
  }

  const toRgbString = (rgb: Rgb): string => `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`

  let config = $state<MasterySchemaConfig>({
    levels: [
      { title: 'Gjengi', color: 'rgb(235, 101, 97)', minValue: 1, maxValue: 33 },
      { title: 'Forklare', color: 'rgb(255, 204, 0)', minValue: 34, maxValue: 66 },
      { title: 'Se sammenhenger', color: 'rgb(23, 231, 21)', minValue: 67, maxValue: 100 },
    ],
    inputIncrement: 1,
    flatTrendThreshold: 6,
    valueInput: VALUE_INPUT_VARIANT.SLIDER_HORIZONTAL_STAIRS,
    isIncrementIndicatorEnabled: true,
    isMasteryValueVisible: true,
    isMasteryValueInputEnabled: true,
    isMasteryDescriptionInputEnabled: true,
    isFeedforwardInputEnabled: true,
  })

  const configJson = $derived(JSON.stringify(config, null, 2))

  const masterySchema = $derived<MasterySchemaWithConfig>({
    id: 'lab-schema',
    title: 'Lab-skjema',
    config,
  } as MasterySchemaWithConfig)

  const aStudent = { id: 'some-student', name: 'Frank Larsen' } as UserType
  const aGoal = { id: 'some-goal', title: 'et lab-mål' } as GoalType

  const booleanFlags: { key: keyof MasterySchemaConfig; label: string }[] = [
    { key: 'isMasteryValueInputEnabled', label: 'Mestringsverdi input' },
    { key: 'isMasteryValueVisible', label: 'Mestringsverdi synlig' },
    { key: 'isIncrementIndicatorEnabled', label: 'Verdi-indikator' },
    { key: 'isMasteryDescriptionInputEnabled', label: 'Tilbakemelding' },
    { key: 'isFeedforwardInputEnabled', label: 'Fremovermelding' },
  ]

  const addLevel = () => {
    const lastLevel = config.levels[config.levels.length - 1]
    const minValue = lastLevel ? lastLevel.maxValue + 1 : 1
    config.levels.push({
      title: 'Nivå ' + (config.levels.length + 1),
      color: 'rgb(100, 100, 100)',
      minValue,
      maxValue: minValue + 10,
    })
  }

  const removeLevel = (index: number) => {
    config.levels.splice(index, 1)
  }

  const handleCopyJson = async () => {
    try {
      await navigator.clipboard.writeText(configJson)
    } catch (error) {
      console.error('Kunne ikke kopiere JSON:', error)
    }
  }
</script>

<div class="container-fluid py-3">
  <h2 class="mb-3">MasterySchema Laboratory</h2>

  <div class="d-flex gap-4 align-items-start">
    <div class="lab-config">
      <h3 class="my-4">Konfigurasjon</h3>

      <div class="form-group mb-3">
        <div class="form-label fw-bold">
          Nivåer <button type="button" class="btn btn-outline-primary btn-sm" onclick={addLevel}>
            Legg til nivå
          </button>
        </div>
        {#each config.levels as level, index}
          <div class="d-flex gap-2 align-items-center mb-2">
            <ColorPicker
              bind:rgb={() => parseRgbString(level.color), rgb => (level.color = toRgbString(rgb))}
              position="responsive"
              label=""
            />
            <input
              type="text"
              class="form-control rounded-0 border-2 border-primary"
              bind:value={level.title}
              placeholder="Tittel"
              aria-label="Nivåtittel"
            />
            <input
              type="number"
              class="form-control rounded-0 border-2 border-primary lab-number"
              bind:value={level.minValue}
              aria-label="Min verdi"
            />
            <input
              type="number"
              class="form-control rounded-0 border-2 border-primary lab-number"
              bind:value={level.maxValue}
              aria-label="Maks verdi"
            />
            <button
              type="button"
              class="btn btn-outline-danger btn-sm"
              onclick={() => removeLevel(index)}
              aria-label="Fjern nivå"
            >
              ✕
            </button>
          </div>
        {/each}
      </div>

      <div class="form-group mb-3">
        <label for="labValueInput" class="form-label fw-bold">Input-variant</label>
        <select id="labValueInput" class="pkt-input w-100" bind:value={config.valueInput}>
          {#each VALUE_INPUT_VARIANTS as variant}
            <option value={variant}>{variant}</option>
          {/each}
        </select>
      </div>

      <div class="d-flex gap-3 mb-3">
        <div class="flex-fill">
          <label for="labInputIncrement" class="form-label fw-bold">Stegverdi</label>
          <input
            id="labInputIncrement"
            type="number"
            class="form-control rounded-0 border-2 border-primary"
            bind:value={config.inputIncrement}
          />
        </div>
        <div class="flex-fill">
          <label for="labFlatTrendThreshold" class="form-label fw-bold">Flat trend terskel</label>
          <input
            id="labFlatTrendThreshold"
            type="number"
            class="form-control rounded-0 border-2 border-primary"
            bind:value={config.flatTrendThreshold}
          />
        </div>
      </div>

      <div class="form-group mb-3">
        <div class="form-label fw-bold">Tilgjengelige elementer</div>
        {#each booleanFlags as flag}
          <div class="form-check">
            <input
              id="lab-flag-{flag.key}"
              type="checkbox"
              class="form-check-input"
              bind:checked={config[flag.key] as boolean}
            />
            <label for="lab-flag-{flag.key}" class="form-check-label">{flag.label}</label>
          </div>
        {/each}
      </div>
    </div>

    <div class="lab-preview">
      {#key configJson}
        <ObservationEdit
          student={aStudent}
          goal={aGoal}
          observation={null}
          {masterySchema}
          isPersistenceControlEnabled={false}
          onDone={() => {}}
        />
      {/key}
    </div>
  </div>

  <div class="mt-4">
    <div class="d-flex align-items-center gap-3">
      <h3 class="mb-0">JSON config</h3>
      <button type="button" class="btn btn-outline-primary btn-sm" onclick={handleCopyJson}>
        Kopier
      </button>
    </div>
    <pre class="lab-json mt-2">{configJson}</pre>
  </div>
</div>

<style>
  /* 2:3 flex ratio = 40/60 split of the space remaining after gap */
  .lab-config {
    flex: 2;
    min-width: 0;
  }

  .lab-preview {
    flex: 3;
    min-width: 0;
    border: 2px dashed orange;
  }

  .lab-number {
    max-width: 5.5rem;
  }

  .level-swatch {
    flex: 0 0 1.5rem;
    height: 1.5rem;
    border: 1px solid #999;
  }

  .lab-json {
    background-color: #f6f8fa;
    border: 1px solid #ddd;
    padding: 1rem;
    max-height: 20rem;
    overflow: auto;
    font-size: 0.85rem;
  }
</style>
