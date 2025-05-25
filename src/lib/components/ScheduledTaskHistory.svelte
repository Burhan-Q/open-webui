<script>
  import { onMount } from 'svelte';
  import { getScheduledTaskExecutions } from '$lib/apis';
  import { format } from 'date-fns';

  export let taskId;

  let executions = [];
  let loading = true;
  let error = null;

  onMount(async () => {
    try {
      executions = await getScheduledTaskExecutions(taskId);
    } catch (err) {
      error = err;
    } finally {
      loading = false;
    }
  });
</script>

{#if loading}
  <p>Loading...</p>
{:else if error}
  <p>Error loading execution history: {error.message}</p>
{:else}
  <table>
    <thead>
      <tr>
        <th>Execution Time</th>
        <th>Status</th>
        <th>Output</th>
        <th>Error Message</th>
      </tr>
    </thead>
    <tbody>
      {#each executions as execution}
        <tr>
          <td>{format(new Date(execution.run_at * 1000), 'yyyy-MM-dd HH:mm:ss')}</td>
          <td>{execution.status}</td>
          <td>{execution.response}</td>
          <td>{execution.error_message}</td>
        </tr>
      {/each}
    </tbody>
  </table>
{/if}
