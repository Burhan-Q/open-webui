<script lang="ts">
  import { onMount } from 'svelte';
  import { getScheduledTask, updateScheduledTask, deleteScheduledTask, runScheduledTask } from '$lib/apis';
  import ScheduledTaskEditor from '$lib/components/ScheduledTaskEditor.svelte';
  import ScheduledTaskHistory from '$lib/components/ScheduledTaskHistory.svelte';
  import { user } from '$lib/stores';
  import { goto } from '$app/navigation';

  export let params;

  let task = null;
  let showEditor = false;
  let showHistory = false;
  let currentUser;

  $: user.subscribe((value) => {
    currentUser = value;
  });

  onMount(async () => {
    if (currentUser) {
      task = await getScheduledTask(currentUser.token, params.id);
    }
  });

  const openEditor = () => {
    showEditor = true;
  };

  const closeEditor = () => {
    showEditor = false;
  };

  const saveTask = async (updatedTask) => {
    await updateScheduledTask(currentUser.token, task.id, updatedTask);
    task = updatedTask;
    closeEditor();
  };

  const deleteTask = async () => {
    await deleteScheduledTask(currentUser.token, task.id);
    goto('/scheduled-tasks');
  };

  const runTask = async () => {
    await runScheduledTask(currentUser.token, task.id);
    showHistory = true;
  };
</script>

<main>
  {#if task}
    <h1>{task.name}</h1>
    <button on:click={openEditor}>Edit Task</button>
    <button on:click={deleteTask}>Delete Task</button>
    <button on:click={runTask}>Run Task</button>
    {#if showEditor}
      <ScheduledTaskEditor
        {task}
        on:save={(event) => saveTask(event.detail)}
        on:cancel={closeEditor}
      />
    {/if}
    {#if showHistory}
      <ScheduledTaskHistory taskId={task.id} />
    {/if}
  {:else}
    <p>Loading...</p>
  {/if}
</main>
