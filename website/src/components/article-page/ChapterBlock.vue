<template>
  <div class="catalog-card">
    <div class="catalog-card-header">
      <div>
        <span class="catalog-eyebrow">ON THIS PAGE</span><strong>文章目录</strong>
      </div>
      <span class="progress">{{ progress }}</span>
    </div>

    <div class="catalog-content">
      <div v-if="props.headings.length" class="catalog-list">
        <button
          v-for="item in props.headings"
          :key="item.id"
          type="button"
          :class="['catalog-link', `catalog-link--depth-${item.depth}`, { 'is-active': activeId === item.id }]"
          @click="scrollToHeading(item.id)"
        >
          {{ item.text }}
        </button>
      </div>
      <div v-else class="catalog-empty">还没有目录</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from "vue";

const props = defineProps({
  headings: {
    type: Array,
    default: () => [],
  },
});

const progress = ref("0%");
const activeId = ref("");

function handleScroll() {
  const st = window.scrollY;
  const sh = document.documentElement.scrollHeight;
  const ch = window.innerHeight;
  const maxScroll = sh - ch;

  // 更新进度条
  progress.value = maxScroll > 0 ? `${Math.floor((st / maxScroll) * 100)}%` : "0%";

  let currentActiveId = "";
  for (const item of props.headings) {
    const element = document.getElementById(item.id);
    if (!element) continue;

    if (element.getBoundingClientRect().top <= 140) {
      currentActiveId = item.id;
    } else {
      break;
    }
  }

  activeId.value = currentActiveId;
}

function scrollToHeading(id) {
  const element = document.getElementById(id);
  if (!element) return;

  const targetTop = element.getBoundingClientRect().top + window.scrollY - 96;
  window.scrollTo({ top: targetTop, behavior: "smooth" });
}

onMounted(() => {
  window.addEventListener("scroll", handleScroll);
  nextTick(() => handleScroll());
});

onUnmounted(() => {
  window.removeEventListener("scroll", handleScroll);
});
</script>

<style scoped>
.catalog-card { padding-top: 2px; }
.catalog-card-header {
  margin-bottom: 14px;
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 12px;
}
.catalog-card-header > div { display: grid; gap: 4px; }
.catalog-eyebrow {
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 8px;
  font-weight: 720;
  letter-spacing: .12em;
  line-height: 1.3;
}
.catalog-card-header strong {
  color: var(--app-text);
  font-size: 12px;
  font-weight: 630;
  line-height: 1.4;
}
.progress {
  min-width: 34px;
  min-height: 22px;
  padding: 0 7px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--app-border);
  border-radius: 999px;
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 8px;
  font-weight: 680;
  letter-spacing: .04em;
}
.catalog-content {
  position: relative;
  max-height: calc(100vh - 164px);
  padding-right: 4px;
  overflow-y: auto;
}
.catalog-list { display: grid; gap: 2px; }
.catalog-link {
  position: relative;
  width: 100%;
  min-width: 0;
  padding: 7px 8px 7px 15px;
  overflow: hidden;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: var(--app-text-muted);
  font: inherit;
  font-size: 11.5px;
  line-height: 1.55;
  text-align: left;
  text-overflow: ellipsis;
  cursor: pointer;
  transition: color 180ms ease, background-color 180ms ease, transform 220ms cubic-bezier(.16,1,.3,1);
}
.catalog-link::before {
  content: "";
  position: absolute;
  left: 3px;
  top: 50%;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--app-border-strong);
  transform: translateY(-50%);
  transition: background-color 180ms ease, box-shadow 180ms ease, transform 180ms ease;
}
.catalog-link:hover {
  color: var(--app-text);
  background: color-mix(in srgb, var(--app-surface-sunken) 74%, transparent);
}
.catalog-link.is-active {
  color: var(--app-text);
  background: color-mix(in srgb, var(--accent-weak) 52%, transparent);
  font-weight: 620;
}
.catalog-link.is-active::before {
  background: var(--accent);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent) 8%, transparent);
  transform: translateY(-50%) scale(1.05);
}
.catalog-link--depth-2 { padding-left: 24px; font-size: 11px; }
.catalog-link--depth-2::before { left: 12px; }
.catalog-link--depth-3 { padding-left: 32px; font-size: 10.5px; }
.catalog-link--depth-3::before { left: 20px; }
.catalog-link--depth-4,
.catalog-link--depth-5,
.catalog-link--depth-6 { padding-left: 38px; font-size: 10.5px; }
.catalog-link--depth-4::before,
.catalog-link--depth-5::before,
.catalog-link--depth-6::before { left: 26px; }
.catalog-empty { padding: 8px 0; color: var(--app-text-soft); font-size: 11px; }
.catalog-content::-webkit-scrollbar { width: 3px; }
.catalog-content::-webkit-scrollbar-thumb { background: color-mix(in srgb, var(--app-text-soft) 24%, transparent); border-radius: 999px; }
.catalog-content::-webkit-scrollbar-track { background: transparent; }
@media (max-width: 768px) {
  .catalog-card { padding-top: 0; }
  .catalog-content { max-height: none; padding-right: 0; }
  .catalog-link { min-height: 42px; display: flex; align-items: center; font-size: 13px; }
}
</style>
