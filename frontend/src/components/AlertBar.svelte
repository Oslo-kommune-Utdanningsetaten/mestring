<script lang="ts">
  import { fly } from 'svelte/transition'
  import { alerts, removeAlert, removeAllAlerts } from '../stores/alerts'
  import { formatDateTimeWithToday } from '../utils/functions'
</script>

<div class="alert-bar-container">
  {#each $alerts as alert, index (alert.id)}
    <div
      class="bg-{alert.type} d-flex gap-3 alert-bar align-bottom"
      role="alert"
      in:fly={{ y: 100, duration: 650 }}
      out:fly={{ y: -100, duration: 650 }}
    >
      <span class="timestamp">{formatDateTimeWithToday(alert?.timestamp)}</span>
      <span>👉 {alert.message}</span>
      <span class="ms-auto">
        {#if $alerts.length > 1 && index === 0}
          <button
            type="button"
            class="btn btn-sm btn-outline-secondary remove-all-btn"
            onclick={() => removeAllAlerts()}
          >
            Fjern alle meldinger
          </button>
        {/if}

        <button
          type="button"
          class="btn-close ms-1"
          title="Fjern melding"
          onclick={() => removeAlert(alert?.id)}
        ></button>
      </span>
    </div>
  {/each}
</div>

<style>
  .alert-bar-container {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1050;
    pointer-events: none;
  }

  .alert-bar {
    padding: 0.5rem 4rem;
    pointer-events: auto;
  }

  .timestamp {
    opacity: 0.9;
  }

  .remove-all-btn {
    pointer-events: auto;
  }
</style>
