<script lang="ts">
  import { fly } from 'svelte/transition'
  import { alerts, removeAlert } from '../stores/alerts'
  import { formatDateDistance } from '../utils/functions'
</script>

<div class="alert-bar-container">
  {#each $alerts as alert (alert.id)}
    <div
      class="bg-{alert.type} d-flex gap-3 alert-bar"
      role="alert"
      in:fly={{ y: 100, duration: 650 }}
      out:fly={{ y: -100, duration: 650 }}
    >
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

<style>
  .alert-bar-container {
    width: 100%;
    overflow: hidden;
  }

  .alert-bar {
    border-radius: 0;
    margin-bottom: 0;
    padding: 0.5rem 4rem;
  }

  .timestamp {
    opacity: 0.9;
  }
</style>
