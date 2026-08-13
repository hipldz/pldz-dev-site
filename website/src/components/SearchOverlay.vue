<template>
  <div v-if="modelValue" class="overlay" @keydown.esc="close" tabindex="-1" ref="overlay">
    <div class="backdrop" @click="close"></div>
    <div class="panel" role="dialog" aria-modal="true">
      <div class="header">
        <input ref="inputRef" v-model="q" type="search" class="input" placeholder="搜索文章、标签、分类" @input="onInput" />
        <button class="close" @click="close"></button>
      </div>
      <div class="body">
        <div v-if="loading" class="empty">加载中…</div>
        <div v-else-if="error" class="empty">加载数据失败：{{ error }}</div>
        <template v-else>
          <div v-if="!q.trim()" class="empty">开始输入以搜索</div>
          <template v-else>
            <div class="meta">共 {{ list.length }} 条结果</div>
            <div v-if="list.length === 0" class="empty">没有匹配结果</div>
            <a class="result" v-for="({ item, score }, i) in list" :key="item.id ?? i" :href="`/article/${item.id}`">
              <div class="title" v-html="highlight(item).title"></div>
              <div class="desc" v-html="highlight(item).summary"></div>
              <div class="tags">
                <span v-if="item.category" class="tag tag--cat">{{ item.category }}</span>
                <span v-for="(t, ti) in item.tags || []" :key="ti" class="tag">{{ t }}</span>
              </div>
              <div class="meta small">匹配度 {{ (score * 100).toFixed(0) }}%</div>
            </a>
          </template>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from "vue";
import SimpleSearch from "../utils/search-engine.js";
import { getAllArticles } from "../utils/apis";

const props = defineProps({
  modelValue: { type: Boolean, default: false },
});
const emit = defineEmits(["update:modelValue"]);

const q = ref("");
const loading = ref(true);
const error = ref("");
const data = ref([]);
const list = ref([]);
const engine = ref(null);

const inputRef = ref(null);

function focusInput() {
  const el = inputRef.value;
  if (el && typeof el.focus === "function") el.focus();
}

function close() {
  emit("update:modelValue", false);
}

async function loadData() {
  try {
    loading.value = true;
    const res = await getAllArticles();
    data.value = Array.isArray(res) ? res : [];
    engine.value = new SimpleSearch({
      fields: ["title", "summary", "tags", "category"],
      threshold: 0.2,
    }).load(data.value);
    list.value = [];
    loading.value = false;
  } catch (e) {
    error.value = e && e.message ? e.message : String(e);
    loading.value = false;
  }
}

function onInput() {
  if (!engine.value) return;
  const text = (q.value || "").trim();
  list.value = text ? engine.value.search(text) : [];
}

function highlight(item) {
  if (!engine.value) return { title: item.title || "", summary: item.summary || "" };
  return engine.value.highlight(item, q.value || "");
}

watch(
  () => props.modelValue,
  (v) => {
    if (v) nextTick(focusInput);
  }
);

onMounted(() => {
  if (props.modelValue) nextTick(focusInput);
  loadData();
});
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  z-index: 10010;
}
.backdrop {
  position: absolute;
  inset: 0;
  background: rgba(42, 36, 32, 0.45);
}
.panel {
  position: absolute;
  left: 50%;
  top: 10vh;
  transform: translateX(-50%);
  width: min(920px, calc(100vw - 2rem));
  max-height: 80vh;
  background: var(--panel-bg, var(--app-surface));
  color: var(--panel-fg, var(--app-text));
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-xl);
  box-shadow: var(--app-shadow-popover);
  display: flex;
  flex-direction: column;
}
.header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.9rem 0.9rem 0.35rem;
}
.input {
  flex: 1;
  padding: 0.75rem 0.95rem;
  font-size: 16px;
  border: 1px solid var(--app-border);
  border-radius: 16px;
  background: var(--app-surface);
  color: var(--app-text);
  outline: none;
}
.input:focus {
  border-color: var(--accent-line);
  box-shadow: 0 0 0 4px var(--accent-weak);
}
.close {
  appearance: none;
  border: none;
  background: transparent;
  font-size: 22px;
  line-height: 1;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
  width: 38px;
  height: 38px;
  border-radius: 999px;
  color: var(--app-text-muted);
  background: url("../assets/svgs/close-24.svg") no-repeat center;
}
.body {
  padding: 0.5rem 0.9rem 1rem;
  overflow: auto;
}
.result {
  display: block;
  padding: 0.85rem;
  border-radius: 18px;
  border: 1px solid var(--app-border);
  margin: 0.5rem 0;
  text-decoration: none;
  color: inherit;
  background: var(--app-surface);
  transition: transform 0.18s ease, border-color 0.18s ease, background-color 0.18s ease;
}
.result:hover {
  transform: translateY(-1px);
  border-color: var(--accent-line);
  background: var(--app-surface-sunken);
}
.title {
  font-weight: 600;
  font-size: 17px;
  margin-bottom: 0.25rem;
}
.desc {
  color: var(--app-text-muted);
  margin-bottom: 0.25rem;
}
.tags {
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
}
.tag {
  font-size: 12px;
  background: rgba(120, 105, 85, 0.08);
  border-radius: 999px;
  padding: 0.1rem 0.5rem;
  color: var(--app-text-muted);
}
.tag--cat {
  background: var(--accent-weak);
  color: var(--app-blue);
}
.meta {
  color: var(--app-text-soft);
  font-size: 12px;
}
.meta.small {
  color: var(--app-text-soft);
}
mark {
  background: rgba(255, 214, 10, 0.36);
  border-radius: 4px;
}
@media (prefers-color-scheme: dark) {
  .panel {
    --panel-bg: #141414;
    --panel-fg: #f0f0f0;
  }
  .input {
    border-color: #333;
    background: #1f1f1f;
    color: #f0f0f0;
  }
  .result {
    border-color: #2a2a2a;
  }
  .tag {
    background: #202020;
    color: #bbb;
  }
}
</style>
