<template>
  <article class="demo-card">
    <div class="demo-main">
      <div v-if="demo.thumbnail || demo.previewgif" class="demo-thumb demo-thumb--image" aria-hidden="true">
        <img :src="demo.thumbnail || demo.previewgif" :alt="demo.title" loading="lazy" decoding="async" />
      </div>
      <div v-else class="demo-thumb" aria-hidden="true">{{ demo.title.slice(0, 2).toUpperCase() }}</div>

      <div class="demo-copy">
        <div class="demo-title-row">
          <h3>{{ demo.title }}</h3>
          <span :class="['status-pill', `status-pill--${demo.status}`]">{{ statusText }}</span>
        </div>
        <p>{{ demo.description }}</p>
      </div>
    </div>

    <div class="demo-actions">
      <a
        class="button-primary button-compact"
        :href="demo.demoLink"
        target="_blank"
        rel="noopener noreferrer"
        data-analytics-cta="live_demo"
        :data-analytics-source="`home.demo_card.${demo.id || demo.title || 'unknown'}`"
        :data-analytics-label="demo.title || '在线体验'"
      >
        在线打开
      </a>
      <a class="button-ghost button-compact" :href="demo.repoLink" target="_blank" rel="noopener noreferrer">GitHub</a>
    </div>
  </article>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  demo: {
    type: Object,
    required: true,
  },
});

const statusTextMap = {
  done: "已完成",
  building: "开发中",
  experimental: "实验",
};

const statusText = computed(() => statusTextMap[props.demo.status] || props.demo.status);
</script>

<style scoped>
.demo-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 16px 18px;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-lg);
  box-shadow: var(--app-shadow-sm);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, background-color 0.2s ease;
}

.demo-card:hover {
  transform: translateY(-1px);
  box-shadow: var(--app-shadow-md);
  border-color: var(--app-border-strong);
  background: var(--app-surface);
}

.demo-main {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 14px;
}

.demo-thumb {
  width: 52px;
  height: 52px;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--app-radius-md);
  background: linear-gradient(135deg, #f3ece0, #fbf8f2);
  border: 1px solid var(--app-border);
  color: var(--app-blue);
  font-size: 13px;
  font-weight: 700;
  overflow: hidden;
}

.demo-thumb--image {
  background: var(--app-surface);
  border-color: var(--app-border);
}

.demo-thumb--image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.demo-copy {
  min-width: 0;
  display: grid;
  gap: 8px;
}

.demo-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.demo-title-row h3 {
  margin: 0;
  color: var(--app-text);
  font-size: 17px;
  line-height: 1.3;
}

.demo-copy p {
  margin: 0;
  color: var(--app-text-muted);
  line-height: 1.6;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 26px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid var(--app-border);
}

.status-pill--done {
  color: var(--app-green);
  background: rgba(93, 122, 74, 0.12);
}

.status-pill--building {
  color: var(--app-orange);
  background: rgba(185, 130, 47, 0.14);
}

.status-pill--experimental {
  color: var(--accent);
  background: var(--accent-weak);
}

.demo-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

@media (max-width: 840px) {
  .demo-card {
    align-items: flex-start;
    flex-direction: column;
  }

  .demo-actions {
    width: 100%;
    flex-wrap: wrap;
  }
}

@media (max-width: 640px) {
  .demo-copy p {
    white-space: normal;
  }
}
</style>
