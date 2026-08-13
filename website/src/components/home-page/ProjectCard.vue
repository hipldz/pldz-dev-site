<template>
  <article class="project-card">
    <div class="project-cover">
      <img :src="project.cover" :alt="project.title" />
    </div>

    <div class="project-body">
      <h3>{{ project.title }}</h3>
      <p>{{ project.description }}</p>

      <div class="tag-list">
        <span v-for="tag in project.tags" :key="tag" class="tag-chip">{{ tag }}</span>
      </div>
    </div>

    <div class="card-actions">
      <a class="button-primary button-small" :href="project.tutorialLink">看教程</a>
      <a class="button-ghost button-small" :href="project.repoLink" target="_blank" rel="noopener noreferrer">看仓库</a>
    </div>
  </article>
</template>

<script setup>
defineProps({
  project: {
    type: Object,
    required: true,
  },
});
</script>

<style scoped>
.project-card {
  display: grid;
  gap: 20px;
  padding: 18px;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-lg);
  box-shadow: var(--app-shadow-sm);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, background-color 0.2s ease;
}

.project-card:hover {
  transform: translateY(-1px);
  box-shadow: var(--app-shadow-md);
  border-color: var(--app-border-strong);
  background: var(--app-surface);
}

.project-cover {
  border-radius: var(--app-radius-md);
  overflow: hidden;
  aspect-ratio: 16 / 9;
  background: var(--app-surface-sunken);
}

.project-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.project-body {
  display: grid;
  gap: 12px;
}

.project-body h3 {
  margin: 0;
  color: var(--app-text);
  font-size: 20px;
  line-height: 1.35;
}

.project-body p {
  margin: 0;
  color: var(--app-text-muted);
  line-height: 1.75;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid var(--app-border);
  background: var(--app-surface);
  color: var(--app-text-muted);
  font-size: 12px;
}

.card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

@media (max-width: 640px) {
  .project-card {
    padding: 14px;
  }
}
</style>
