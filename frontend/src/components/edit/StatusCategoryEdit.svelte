<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import { statusCategoriesUpdate, statusCategoriesCreate } from '../../generated/sdk.gen'
  import type { StatusCategoryType, StatusCategoryCreateType } from '../../generated/types.gen'

  import { STATUS_CATEGORY_TITLE_BY_NAME, NONE_FIELD_VALUE } from '../../utils/constants'
  import { localStorage } from '../../stores/localStorage'
  import { dataStore } from '../../stores/data'

  import ButtonMini from '../ButtonMini.svelte'

  const {
    statusCategory,
    onDone,
  }: {
    statusCategory: Partial<StatusCategoryType> | null
    onDone: () => void
  } = $props()
  // Date inputs only accept YYYY-MM-DD, but the backend returns full datetimes
  let localStatusCategory = $state<Partial<StatusCategoryType>>({
    ...statusCategory,
    openFrom: statusCategory?.openFrom?.split('T')[0],
    openTo: statusCategory?.openTo?.split('T')[0],
  })

  let validationErrors = $state<{ openFrom?: string; openTo?: string }>({})

  let masterySchemas = $derived($dataStore.masterySchemas.filter(schema => schema.isEnabled))
  let selectedMasterySchemaId = $derived(
    localStatusCategory.masterySchemaId || $dataStore.defaultMasterySchema.id
  )

  const handleSave = async () => {
    validationErrors = {}
    if (!localStatusCategory.openFrom) {
      validationErrors.openFrom = 'Fra-dato er påkrevd'
    }
    if (!localStatusCategory.openTo) {
      validationErrors.openTo = 'Til-dato er påkrevd'
    }
    if (localStatusCategory.openFrom && localStatusCategory.openTo) {
      const beginDate = new Date(localStatusCategory.openFrom)
      const endDate = new Date(localStatusCategory.openTo)
      if (beginDate > endDate) {
        validationErrors.openTo = 'Til-dato må være etter fra-dato'
      }
    }
    // Stop if validation fails
    if (Object.keys(validationErrors).length > 0) {
      return
    }

    try {
      if (localStatusCategory.id) {
        await statusCategoriesUpdate({
          path: { id: localStatusCategory.id },
          body: localStatusCategory as StatusCategoryType,
        })
      } else {
        await statusCategoriesCreate({
          body: localStatusCategory as StatusCategoryCreateType,
        })
      }
      onDone()
    } catch (error) {
      // TODO: Show an error message to the user
      console.error('Error saving StatusCategory:', error)
    }
  }

  const handleChangeMasterySchema = (masterySchemaId: string) => {
    if (masterySchemaId !== NONE_FIELD_VALUE) {
      localStatusCategory = { ...localStatusCategory, masterySchemaId }
      localStorage('preferredMasterySchemaId').set(masterySchemaId)
    }
  }
</script>

<div class="p-4 status-category-edit">
  <h3 class="pb-4">{localStatusCategory.id ? 'Redigerer statuskategori' : 'Ny statuskategori'}</h3>

  <!-- Name -->
  <div class="form-group mb-4">
    <label for="nameSelect" class="mb-1 field-label">Navn</label>
    <select class="pkt-input" id="nameSelect" bind:value={localStatusCategory.name}>
      {#each Object.keys(STATUS_CATEGORY_TITLE_BY_NAME) as key}
        <option value={key} selected={key === localStatusCategory.name}>
          {STATUS_CATEGORY_TITLE_BY_NAME[key]} [{key}]
        </option>
      {/each}
    </select>
  </div>

  <!-- Periode -->
  <div class="form-group mb-4">
    <span class="field-label">Periode statuskategorien er åpen for bruk</span>
    <div class="d-flex align-items-end gap-2 flex-wrap">
      <!-- Periode fra -->
      <div class="flex-fill" style="min-width: 140px">
        <label for="openFrom" class="form-label mb-1 text-muted">Fra</label>
        <input
          id="openFrom"
          type="date"
          class="form-control rounded-0 border-2 border-primary"
          class:is-invalid={validationErrors.openFrom}
          bind:value={localStatusCategory.openFrom}
          required
        />
        {#if validationErrors.openFrom}
          <div class="text-danger small mt-1">{validationErrors.openFrom}</div>
        {/if}
      </div>
      <span class="text-muted pb-2">–</span>

      <!-- Periode til -->
      <div class="flex-fill" style="min-width: 140px">
        <label for="openTo" class="form-label mb-1 text-muted">Til</label>
        <input
          id="openTo"
          type="date"
          class="form-control rounded-0 border-2 border-primary"
          class:is-invalid={validationErrors.openTo}
          bind:value={localStatusCategory.openTo}
          required
        />
        {#if validationErrors.openTo}
          <div class="text-danger small mt-1">{validationErrors.openTo}</div>
        {/if}
      </div>
    </div>
  </div>

  <!-- Mastery schema -->
  {#if masterySchemas.length}
    <div class="form-group mb-4">
      <label for="masterySchemaSelect" class="mb-1 field-label">Mestringsskjema</label>
      <select
        id="masterySchemaSelect"
        class="pkt-input"
        value={selectedMasterySchemaId}
        onchange={e => handleChangeMasterySchema((e.target as HTMLSelectElement).value)}
      >
        <option disabled value={NONE_FIELD_VALUE}>Velg mestringsskjema</option>
        {#each masterySchemas as masterySchema}
          <option disabled={!masterySchema.isEnabled} value={masterySchema.id}>
            {masterySchema.title}
          </option>
        {/each}
      </select>
    </div>
  {:else}
    <div class="alert alert-warning">
      Det finnes ingen mestringsskjemaer. Opprett et mestringsskjema før du oppretter en
      statuskategori.
    </div>
  {/if}

  <div class="form-group mb-4">
    <label for="masterySchemaSelect" class="mb-1 field-label">Enabled</label>
    <pkt-checkbox
      label={localStatusCategory.isEnabled ? 'Currently enabled' : 'Currently disabled'}
      labelPosition="right"
      isSwitch="true"
      aria-checked={localStatusCategory.isEnabled}
      checked={localStatusCategory.isEnabled}
      onchange={() => (localStatusCategory.isEnabled = !localStatusCategory.isEnabled)}
    ></pkt-checkbox>
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
  .status-category-edit {
    width: 100%;
    max-width: 100%;
  }

  input {
    height: 47px;
  }

  .field-label {
    display: block;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 0.5rem;
  }
</style>
