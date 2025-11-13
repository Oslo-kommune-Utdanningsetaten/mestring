<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-alert.js'

  import { alerts, removeAlert, addAlert } from '../stores/alerts'
  import { formatDateDistance } from '../utils/functions'
  const alertTypes = ['success', 'info', 'warning', 'danger']
</script>

{#if $alerts.length > 0}
  <div class="alert-bar-container">
    {#each $alerts as alert (alert.id)}
      <div class="alert alert-{alert.type} d-flex gap-3 ps-4" role="alert">
        <span class="timestamp">{formatDateDistance(alert?.timestamp)}</span>
        <span>{alert.message}</span>
        <button
          type="button"
          class="btn-close ms-auto"
          aria-label="Close"
          on:click={() => removeAlert(alert?.id)}
        ></button>
      </div>
    {/each}
  </div>
{/if}

<style>
  .alert-bar-container {
    width: 100%;
  }

  .alert {
    border-radius: 0;
    margin-bottom: 0;
  }

  .timestamp {
    font-family: 'Courier New', Courier, monospace;
    opacity: 0.7;
  }
</style>
