<script lang="ts">
  const { tags = [] }: { tags: string[] } = $props()
</script>

{#if tags.length}
  <ul class="tags-list">
    {#each tags as tag}
      <li class="tag">{tag}</li>
    {/each}
  </ul>
{/if}

<style>
  .tags-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .tag {
    border: 2px solid var(--bs-gray);
    border-radius: 3px;
    background: var(--bs-light);
    color: var(--bs-primary);
    padding: 0.2rem 0.6rem;
    font-weight: 600;
  }
</style>
