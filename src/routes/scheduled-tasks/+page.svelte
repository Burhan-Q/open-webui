<script lang="ts">
  import { onMount } from 'svelte';
  import { getScheduledTasks, createScheduledTask } from '$lib/apis';
  import ScheduledTaskEditor from '$lib/components/ScheduledTaskEditor.svelte';
  import ScheduledTasksList from '$lib/components/ScheduledTasksList.svelte';
  import { user } from '$lib/stores';
  import { goto } from '$app/navigation';

  let tasks = [];
  let showEditor = false;
  let selectedTask = null;
  let currentUser;

  $: user.subscribe((value) => {
    currentUser = value;
  });

  onMount(async () => {
    if (currentUser) {
      tasks = await getScheduledTasks(currentUser.token);
    }
  });

  const openEditor = (task = null) => {
    selectedTask = task;
    showEditor = true;
  };

  const closeEditor = () => {
    selectedTask = null;
    showEditor = false;
  };

  const saveTask = async (task) => {
    if (task.id) {
      // Update existing task
      await updateScheduledTask(currentUser.token, task.id, task);
    } else {
      // Create new task
      const newTask = await createScheduledTask(currentUser.token, task);
      tasks = [...tasks, newTask];
    }
    closeEditor();
  };

  const deleteTask = async (taskId) => {
    await deleteScheduledTask(currentUser.token, taskId);
    tasks = tasks.filter((task) => task.id !== taskId);
  };

  const runTask = async (taskId) => {
    await runScheduledTask(currentUser.token, taskId);
    goto(`/scheduled-tasks/${taskId}`);
  };
</script>

<main>
  <h1>Scheduled Tasks</h1>
  <button on:click={() => openEditor()}>Create Task</button>
  <ScheduledTasksList
    {tasks}
    on:edit={(event) => openEditor(event.detail)}
    on:delete={(event) => deleteTask(event.detail.id)}
    on:run={(event) => runTask(event.detail.id)}
  />
  {#if showEditor}
    <ScheduledTaskEditor
      {selectedTask}
      on:save={(event) => saveTask(event.detail)}
      on:cancel={closeEditor}
    />
  {/if}
</main>
