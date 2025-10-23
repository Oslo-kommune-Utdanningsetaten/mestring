<script lang="ts">
  import type { GroupType } from '../generated/types.gen'
  import { GROUP_TYPE_BASIS, GROUP_TYPE_TEACHING } from '../utils/constants'

  const { group, onclick, isTypeWarningEnabled } = $props<{
    group: GroupType | null
    isTypeWarningEnabled?: boolean
    onclick?: () => void
  }>()

  const label: string = $derived(
    group.type === GROUP_TYPE_BASIS ? 'Basisgruppe' : 'Undervisningsgruppe'
  )
  const skin: string = $derived(group.type === GROUP_TYPE_BASIS ? 'blue' : 'green')

  const isGroupTypeChanged = $derived.by(() => {
    // Inspect feideId to determine original group type
    const originalType =
      group.feideId.split(':')[3] === 'u' ? GROUP_TYPE_TEACHING : GROUP_TYPE_BASIS
    return originalType !== group.type
  })
</script>

{#if group}
  {#if onclick}
    <span class="button-container">
      <button
        type="button"
        class="p-0 m-0 border-0"
        title="Endre gruppetype"
        {onclick}
        aria-label={label}
      >
        <pkt-tag iconName="group" {skin}>
          <span>{label}</span>
          {#if isGroupTypeChanged && isTypeWarningEnabled}
            <span class="colored-icon">
              <pkt-icon
                name="alert-warning"
                class="pkt-icon--medium warning-icon"
                aria-label="advarsel"
              ></pkt-icon>
            </span>
          {/if}
        </pkt-tag>
      </button>
    </span>
  {:else}
    <pkt-tag iconName="group" {skin}>
      <span>{label}</span>
    </pkt-tag>
  {/if}
{/if}

<style>
  .button-container {
    display: inline-block;
    position: relative;
  }

  .warning-icon {
    position: absolute;
    top: 2px;
    right: -14px;
    z-index: 3;
    transform: rotate(5deg);
    filter: drop-shadow(0 1px 1px rgba(0, 0, 0, 0.12)) drop-shadow(0 2px 2px rgba(0, 0, 0, 0.12))
      drop-shadow(0 4px 4px rgba(0, 0, 0, 0.12)) drop-shadow(0 8px 8px rgba(0, 0, 0, 0.12));
  }

  .colored-icon pkt-icon {
    --fg-color: var(--pkt-color-brand-red-1000);
  }

  button {
    background: none;
    cursor: pointer;
  }

  button:hover {
    transform: scale(1.1);
    transition: transform 0.3s ease;
  }
</style>
