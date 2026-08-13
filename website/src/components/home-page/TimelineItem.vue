<template>
  <li class="timeline-item">
    <a :href="item.link" class="timeline-link">
      <span class="timeline-type">{{ item.type }}</span>
      <span class="timeline-title">{{ item.title }}</span>
      <span class="timeline-date">{{ formattedDate }}</span>
      <span class="timeline-action">看看</span>
    </a>
  </li>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
});

const formattedDate = computed(() => (props.item.date || "").replaceAll("-", "."));
</script>

<style scoped>
.timeline-item + .timeline-item {
  border-top: 1px solid var(--app-border);
}

.timeline-link {
  min-height: 58px;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto auto;
  align-items: center;
  gap: 14px;
  padding: 14px 0;
  text-decoration: none;
}

.timeline-type {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 68px;
  height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  background: rgba(120, 105, 85, 0.08);
  color: var(--app-text-muted);
  font-size: 12px;
  text-transform: lowercase;
}

.timeline-title {
  color: var(--app-text);
  line-height: 1.5;
}

.timeline-date {
  color: var(--app-text-soft);
  font-size: 14px;
}

.timeline-action {
  color: var(--app-blue);
  font-size: 14px;
  font-weight: 600;
}

@media (max-width: 840px) {
  .timeline-link {
    grid-template-columns: auto minmax(0, 1fr);
    align-items: start;
  }

  .timeline-date,
  .timeline-action {
    margin-left: 82px;
  }
}

@media (max-width: 640px) {
  .timeline-link {
    gap: 10px;
  }

  .timeline-date,
  .timeline-action {
    margin-left: 0;
  }
}
</style>
