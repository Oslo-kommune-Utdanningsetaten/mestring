<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-radiobutton.js'
  import type { SchoolType } from '../generated/types.gen'

  import { currentUser, currentSchool } from '../stores/data'
  import { localStorage } from '../stores/localStorage'

  const handleSelectSchool = (school: SchoolType) => {
    // set localStorage and reload, which in turn will trigger dataStore to update with school-specific data
    localStorage<SchoolType>('currentSchool').set(school)
    window.location.reload()
  }
</script>

<div class="radio-buttons" role="group">
  {#each $currentUser?.schools as school}
    <label class="radio-button mx-2">
      <input
        type="radio"
        name="currentSchool"
        value={school.id}
        checked={$currentSchool.id === school.id}
        onchange={() => handleSelectSchool(school)}
      />
      <span class="name">{school.displayName}</span>
    </label>
  {/each}
</div>

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
