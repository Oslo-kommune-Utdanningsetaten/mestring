<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-radiobutton.js'
  import { preferredSchoolYear } from '../stores/localStorageFunctions'
  import { currentUser, currentSchool } from '../stores/data'
  import { localStorage } from '../stores/localStorage'
  import { GROUP_VALIDITY_OPTIONS } from '../utils/constants'
  import { getAllSchoolYears, getCurrentSchoolYear } from '../utils/schoolYear'

  const allYears = $derived(
    $currentSchool ? getAllSchoolYears(new Date($currentSchool.createdAt)).reverse() : []
  )

  // Options for filtering by date validity
  const createdOptions = $derived.by(() => {
    if (!$currentSchool) return []

    return [
      ...allYears.map(year => ({
        value: year,
        label: year,
      })),
      allYears.length > 1 ? { value: 'all', label: 'Alle år' } : null,
    ].filter(Boolean) as { value: string; label: string }[]
  })

  // When school year is changed by user, also update the group validity (not the other way)
  const handleSelectSchoolYear = (schoolYear: string) => {
    localStorage('preferredSchoolYear').set(schoolYear)
    if (schoolYear === 'all') {
      // All years selected --> include all groups regardless of validity
      localStorage('preferredGroupValidity').set(GROUP_VALIDITY_OPTIONS.INCLUDE)
    } else if (schoolYear === getCurrentSchoolYear()) {
      // Current year selected --> only include valid groups
      localStorage('preferredGroupValidity').set(GROUP_VALIDITY_OPTIONS.ONLY)
    } else {
      // Past year selected --> only include invalid groups
      localStorage('preferredGroupValidity').set(GROUP_VALIDITY_OPTIONS.EXCLUDE)
    }
    window.location.reload()
  }
</script>

{#if $currentUser}
  <div class="radio-buttons" role="group">
    {#each createdOptions as option}
      <label class="radio-button mx-2">
        <input
          type="radio"
          name="preferredSchoolYear"
          value={option.value}
          checked={$preferredSchoolYear === option.value}
          onchange={() => handleSelectSchoolYear(option.value)}
        />
        <span class="name">{option.label}</span>
      </label>
    {/each}
  </div>
{:else}
  no user
{/if}

<style>
  .radio-buttons {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    font-size: 0.9rem;
  }

  .radio-button input {
    display: none;
  }

  .radio-button .name {
    display: flex;
    cursor: pointer;
    align-items: center;
    justify-content: center;
    border-radius: 3px;
    border: none;
    padding: 0.5rem 0.5rem;
    color: rgba(51, 65, 85, 1);
    transition: all 0.15s ease-in-out;
    background-color: #ddd;
  }

  .radio-button input:checked + .name {
    background-color: #fff;
    font-weight: 600;
    position: relative;
    border: 1px solid color-mix(in srgb, var(--effect-color) 50%);
    box-shadow: 0px 0px 10px color-mix(in srgb, black 30%);
    animation: select 0.3s ease;
  }

  /* Hover effect */
  .radio-button:hover .name {
    box-shadow: 0 0 0px 1px rgba(0, 0, 0, 0.06);
    background-color: rgba(255, 255, 255, 0.5);
  }

  @keyframes select {
    0% {
      transform: scale(0.95);
    }
    50% {
      transform: scale(1.05);
    }
    100% {
      transform: scale(1);
    }
  }
</style>
