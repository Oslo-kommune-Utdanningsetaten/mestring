<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import { statusCategoriesUpdate, statusCategoriesCreate } from '../generated/sdk.gen'
  import type { StatusCategoryType, StatusCategoryCreateType } from '../generated/types.gen'
  import { STATUS_CATEGORY_NAMES, NONE_FIELD_VALUE } from '../utils/constants'
  import { localStorage } from '../stores/localStorage'
  import { dataStore } from '../stores/data'
  import ButtonMini from './ButtonMini.svelte'

  const { statusCategory, onDone } = $props<{
    statusCategory: Partial<StatusCategoryType> | null
    onDone: () => void
  }>()
  let masterySchemas = $derived($dataStore.masterySchemas.filter(schema => schema.isEnabled))
  let localStatusCategory = $derived<Partial<StatusCategoryType>>({ ...statusCategory })
  let selectedMasterySchemaId = $derived(
    localStatusCategory.masterySchemaId || $dataStore.defaultMasterySchema.id
  )

  const handleSave = async () => {
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
      localStorage<string>('preferredMasterySchemaId').set(masterySchemaId)
    }
  }
</script>

<div class="p-4 status-category-edit">
  <h3 class="pb-2">{localStatusCategory.id ? 'Redigerer statuskategori' : 'Ny statuskategori'}</h3>
  <div class="form-group mb-3">
    <label for="stausCategoryTitle" class="form-label">Tittel</label>
    <input
      id="stausCategoryTitle"
      type="text"
      class="form-control rounded-0 border-2 border-primary"
      bind:value={localStatusCategory.title}
      placeholder="Tittel"
    />
  </div>

  <div class="form-group mb-3">
    <label for="nameSelect" class="mb-1">Velg kategori-navn</label>
    <select class="pkt-input" id="nameSelect" bind:value={localStatusCategory.name}>
      {#each Object.keys(STATUS_CATEGORY_NAMES) as key}
        <option value={key} selected={key === localStatusCategory.name}>
          {key}
          ({STATUS_CATEGORY_NAMES[key]})
        </option>
      {/each}
    </select>
  </div>

  <!-- Mastery schema -->
  {#if masterySchemas.length > 1}
    <div class="form-group mb-3">
      <div>
        <pkt-select
          label="Mestringsskjema"
          name="goalMasterySchema"
          fullwidth={true}
          value={localStatusCategory.masterySchemaId || NONE_FIELD_VALUE}
          hasError={!localStatusCategory.masterySchemaId ||
            localStatusCategory.masterySchemaId === NONE_FIELD_VALUE}
          requiredText="Velg et mestringsskjema"
          disabled={!localStatusCategory.isEnabled}
          onchange={(e: Event) => {
            const target = e.target as HTMLSelectElement | null
            const msid = target?.value || NONE_FIELD_VALUE
            handleChangeMasterySchema(msid)
          }}
        >
          <option disabled value={NONE_FIELD_VALUE}>Velg mestringsskjema</option>
          {#each masterySchemas as masterySchema}
            <option
              disabled={!masterySchema.isEnabled}
              value={masterySchema.id}
              selected={masterySchema.id === selectedMasterySchemaId}
            >
              {masterySchema.title}
            </option>
          {/each}
        </pkt-select>
      </div>
    </div>
  {/if}

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
</style>
