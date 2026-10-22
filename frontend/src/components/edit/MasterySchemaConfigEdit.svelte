<script lang="ts">
  import ColorPicker from 'svelte-awesome-color-picker'
  import type { GoalType, UserType } from '../../generated/types.gen'
  import type { MasterySchemaConfig, MasterySchemaWithConfig } from '../../types/models'
  import { VALUE_INPUT_VARIANTS } from '../../utils/constants'

  import ObservationEdit from './ObservationEdit.svelte'

  const { masterySchema } = $props<{
    masterySchema: Partial<MasterySchemaWithConfig>
  }>()

  type Rgb = { r: number; g: number; b: number; a: number }

  const parseRgbString = (color: string): Rgb => {
    const rgbMatch = color.match(/rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/)
    if (rgbMatch) {
      return { r: Number(rgbMatch[1]), g: Number(rgbMatch[2]), b: Number(rgbMatch[3]), a: 1 }
    }
    const hexMatch = color.match(/^#([0-9a-fA-F]{6})$/)
    if (hexMatch) {
      const hex = hexMatch[1]
      return {
        r: parseInt(hex.slice(0, 2), 16),
        g: parseInt(hex.slice(2, 4), 16),
        b: parseInt(hex.slice(4, 6), 16),
        a: 1,
      }
    }
    return { r: 0, g: 0, b: 0, a: 1 }
  }

  const toRgbString = (rgb: Rgb): string => `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`

  const aStudent = { id: 'some-student', name: 'Frank Larsen' } as UserType
  const aGoal = { id: 'some-goal', title: 'Et mål' } as GoalType

  const booleanFlags: { key: keyof MasterySchemaConfig; label: string }[] = [
    { key: 'isMasteryValueInputEnabled', label: 'Mestringsverdi input' },
    { key: 'isMasteryValueVisible', label: 'Mestringsverdi synlig' },
    { key: 'isIncrementIndicatorEnabled', label: 'Verdi-indikator' },
    { key: 'isMasteryDescriptionInputEnabled', label: 'Tilbakemelding' },
    { key: 'isFeedforwardInputEnabled', label: 'Fremovermelding' },
  ]

  // svelte-ignore state_referenced_locally
  let config = $state<MasterySchemaConfig>({ ...masterySchema.config })

  $effect(() => {
    masterySchema.config = $state.snapshot(config)
  })

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
</script>

<div class="d-flex gap-4 align-items-start">
  <div class="config">
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
            class="form-control rounded-0 border-2 border-primary number-input"
            bind:value={level.minValue}
            aria-label="Min verdi"
          />
          <input
            type="number"
            class="form-control rounded-0 border-2 border-primary number-input"
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

  <div class="preview">
    <ObservationEdit
      student={aStudent}
      goal={aGoal}
      observation={null}
      {masterySchema}
      isPersistenceControlEnabled={false}
      onDone={() => {}}
    />
  </div>
</div>

<style>
  /* 2:3 flex ratio = 40/60 split of the space remaining after gap */
  .config {
    flex: 2;
    min-width: 0;
  }

  .preview {
    flex: 3;
    min-width: 0;
    border: 2px dashed orange;
  }

  .number-input {
    max-width: 5rem;
  }
</style>
