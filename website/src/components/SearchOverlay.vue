<template>
  <div v-if="modelValue" ref="overlay" class="command-overlay" tabindex="-1" @keydown="onPanelKeydown">
    <div class="command-backdrop" @click="close"></div>
    <div class="command-panel" role="dialog" aria-modal="true" aria-label="全局命令与搜索">
      <div class="command-search">
        <span class="command-spark" aria-hidden="true"></span>
        <label class="command-field">
          <span class="material-symbols-rounded command-field__icon" aria-hidden="true">search</span>
          <input
            ref="inputRef"
            v-model="q"
            type="search"
            class="command-input"
            placeholder="搜索文章，或输入页面名称快速前往…"
            autocomplete="off"
            @input="onInput"
          />
        </label>
        <kbd class="command-esc">ESC</kbd>
      </div>

      <div ref="bodyRef" class="command-body">
        <section v-if="!q.trim()" class="command-section" aria-label="快速前往">
          <div class="command-section__heading">
            <span>快速前往</span>
            <small>COMMANDS</small>
          </div>
          <div class="command-grid">
            <a
              v-for="(command, index) in quickCommands"
              :key="command.href"
              v-cursor="'GO'"
              :class="['command-card', { 'is-selected': selectedIndex === index }]"
              :href="command.href"
              :target="command.external ? '_blank' : undefined"
              :rel="command.external ? 'noopener noreferrer' : undefined"
              :data-command-index="index"
              @mouseenter="selectedIndex = index"
              @click="close"
            >
              <span class="command-card__icon material-symbols-rounded" aria-hidden="true">{{ command.icon }}</span>
              <span class="command-card__copy">
                <strong>{{ command.label }}</strong>
                <small>{{ command.description }}</small>
              </span>
              <span class="command-card__arrow material-symbols-rounded" aria-hidden="true">arrow_forward</span>
            </a>
          </div>

          <div class="command-tip">
            <span class="material-symbols-rounded" aria-hidden="true">keyboard</span>
            <span>输入关键词搜索全部文章，也可以用 ↑ ↓ 选择、Enter 打开。</span>
          </div>
        </section>

        <section v-else class="command-section" aria-label="搜索结果">
          <div class="command-section__heading">
            <span>搜索结果</span>
            <small v-if="loading">正在加载…</small>
            <small v-else>{{ combinedResults.length }} RESULTS</small>
          </div>

          <div v-if="error" class="command-empty">加载文章失败：{{ error }}</div>
          <div v-else-if="!loading && combinedResults.length === 0" class="command-empty">
            <span class="empty-spark" aria-hidden="true"></span>
            <strong>没有找到匹配内容</strong>
            <small>换一个关键词，或者直接输入“白板 / Demo / 文章”。</small>
          </div>

          <div v-else class="command-results">
            <a
              v-for="(result, index) in combinedResults"
              :key="`${result.type}-${result.key}`"
              v-cursor="'OPEN'"
              :class="['command-result', { 'is-selected': selectedIndex === index }]"
              :href="result.href"
              :target="result.external ? '_blank' : undefined"
              :rel="result.external ? 'noopener noreferrer' : undefined"
              :data-command-index="index"
              @mouseenter="selectedIndex = index"
              @click="close"
            >
              <span class="command-result__icon material-symbols-rounded" aria-hidden="true">{{ result.icon }}</span>
              <span class="command-result__copy">
                <span class="command-result__topline">
                  <strong v-if="result.type === 'command'">{{ result.title }}</strong>
                  <strong v-else v-html="result.title"></strong>
                  <em>{{ result.badge }}</em>
                </span>
                <span v-if="result.type === 'command'" class="command-result__desc">{{ result.description }}</span>
                <span v-else class="command-result__desc" v-html="result.summary"></span>
              </span>
              <span class="command-result__arrow material-symbols-rounded" aria-hidden="true">north_east</span>
            </a>
          </div>
        </section>
      </div>

      <footer class="command-footer" aria-hidden="true">
        <span><kbd>↑</kbd><kbd>↓</kbd> 选择</span>
        <span><kbd>↵</kbd> 打开</span>
        <span><kbd>ESC</kbd> 关闭</span>
        <span class="command-footer__brand"><i></i>PLDZ</span>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";
import SimpleSearch from "../utils/search-engine.js";
import { getAllArticles } from "../utils/apis";

const props = defineProps({
  modelValue: { type: Boolean, default: false },
});
const emit = defineEmits(["update:modelValue"]);

const q = ref("");
const loading = ref(false);
const loaded = ref(false);
const error = ref("");
const data = ref([]);
const articleResults = ref([]);
const engine = ref(null);
const selectedIndex = ref(0);
const inputRef = ref(null);
const bodyRef = ref(null);

const quickCommands = [
  { label: "首页", description: "回到项目与最近内容", href: "/", icon: "home", keywords: "首页 home 项目" },
  { label: "文章 / 教程", description: "浏览专栏、教程与笔记", href: "/articles", icon: "auto_stories", keywords: "文章 教程 专栏 library" },
  { label: "临时白板", description: "暂存文本、图片与截图", href: "/whiteboard", icon: "note_stack", keywords: "白板 临时 缓存 文本 图片" },
  { label: "Live Demos", description: "直接体验可运行项目", href: "/livedemo", icon: "play_circle", keywords: "demo demos live 演示 项目" },
  { label: "GitHub", description: "查看开源项目与代码", href: "https://github.com/hipldz", icon: "code", keywords: "github 开源 代码", external: true },
];

const normalizedQuery = computed(() => q.value.trim().toLowerCase());
const matchingCommands = computed(() => {
  const text = normalizedQuery.value;
  if (!text) return [];
  return quickCommands
    .filter((item) => `${item.label} ${item.description} ${item.keywords}`.toLowerCase().includes(text))
    .map((item) => ({
      type: "command",
      key: item.href,
      href: item.href,
      external: item.external,
      icon: item.icon,
      title: item.label,
      description: item.description,
      badge: item.external ? "EXTERNAL" : "GO",
    }));
});

const combinedResults = computed(() => {
  const articles = articleResults.value.slice(0, 7).map(({ item }) => ({
    type: "article",
    key: item.id,
    href: `/article/${item.id}`,
    icon: "article",
    title: highlight(item).title,
    summary: highlight(item).summary,
    badge: item.category || "ARTICLE",
  }));
  return [...matchingCommands.value, ...articles].slice(0, 9);
});

const selectableCount = computed(() => (normalizedQuery.value ? combinedResults.value.length : quickCommands.length));

function focusInput() {
  nextTick(() => inputRef.value?.focus?.());
}

function close() {
  emit("update:modelValue", false);
}

async function ensureData() {
  if (loaded.value || loading.value) return;
  try {
    loading.value = true;
    error.value = "";
    const res = await getAllArticles();
    data.value = Array.isArray(res) ? res : [];
    engine.value = new SimpleSearch({
      fields: ["title", "summary", "tags", "category"],
      threshold: 0.2,
    }).load(data.value);
    loaded.value = true;
    onInput();
  } catch (e) {
    error.value = e?.message || String(e);
  } finally {
    loading.value = false;
  }
}

function onInput() {
  selectedIndex.value = 0;
  const text = q.value.trim();
  articleResults.value = text && engine.value ? engine.value.search(text) : [];
}

function highlight(item) {
  if (!engine.value) return { title: item.title || "", summary: item.summary || "" };
  return engine.value.highlight(item, q.value || "");
}

function openSelected() {
  const selector = `[data-command-index="${selectedIndex.value}"]`;
  bodyRef.value?.querySelector(selector)?.click();
}

function moveSelection(delta) {
  const count = selectableCount.value;
  if (!count) return;
  selectedIndex.value = (selectedIndex.value + delta + count) % count;
  nextTick(() => {
    bodyRef.value?.querySelector(`[data-command-index="${selectedIndex.value}"]`)?.scrollIntoView?.({ block: "nearest" });
  });
}

function onPanelKeydown(event) {
  if (event.key === "Escape") {
    event.preventDefault();
    close();
    return;
  }
  if (event.key === "ArrowDown") {
    event.preventDefault();
    moveSelection(1);
    return;
  }
  if (event.key === "ArrowUp") {
    event.preventDefault();
    moveSelection(-1);
    return;
  }
  if (event.key === "Enter" && !event.isComposing) {
    event.preventDefault();
    openSelected();
  }
}

onBeforeUnmount(() => {
  document.documentElement.classList.remove("command-palette-open");
});

watch(
  () => props.modelValue,
  (open) => {
    document.documentElement.classList.toggle("command-palette-open", open);
    if (!open) return;
    q.value = "";
    articleResults.value = [];
    selectedIndex.value = 0;
    focusInput();
    ensureData();
  },
  { immediate: true },
);
</script>

<style scoped>
.command-overlay {
  position: fixed;
  inset: 0;
  z-index: 10010;
}
.command-backdrop {
  position: absolute;
  inset: 0;
  background: color-mix(in srgb, var(--app-overlay) 82%, transparent);
}
.command-panel {
  position: absolute;
  left: 50%;
  top: max(86px, 10vh);
  translate: -50% 0;
  width: min(760px, calc(100vw - 28px));
  max-height: min(700px, 78vh);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border: 1px solid color-mix(in srgb, var(--app-border-strong) 74%, transparent);
  border-radius: 24px;
  background: color-mix(in srgb, var(--app-surface) 97%, var(--brand-tint));
  color: var(--app-text);
  box-shadow:
    0 28px 90px rgba(22, 29, 45, 0.19),
    0 3px 18px rgba(22, 29, 45, 0.07);
}
.command-search {
  position: relative;
  min-height: 68px;
  padding: 10px 12px 10px 18px;
  display: grid;
  grid-template-columns: 18px minmax(0, 1fr) auto;
  align-items: center;
  gap: 9px;
  border-bottom: 1px solid var(--app-border);
}
.command-spark,
.empty-spark,
.command-footer__brand i {
  display: inline-block;
  width: 14px;
  height: 14px;
  background: var(--accent);
  clip-path: polygon(50% 0, 62% 38%, 100% 50%, 62% 62%, 50% 100%, 38% 62%, 0 50%, 38% 38%);
}
.command-spark {
  opacity: 0.9;
}
.command-field {
  min-width: 0;
  display: grid;
  grid-template-columns: 22px minmax(0, 1fr);
  align-items: center;
  gap: 8px;
}
.command-field__icon {
  color: var(--app-text-soft);
  font-size: 20px;
}
.command-input {
  width: 100%;
  min-width: 0;
  padding: 8px 0;
  border: 0;
  outline: 0 !important;
  background: transparent;
  color: var(--app-text);
  font-size: 15px;
  font-weight: 560;
  box-shadow: none !important;
}
.command-input::placeholder {
  color: var(--app-text-soft);
}
.command-esc,
.command-footer kbd {
  border: 1px solid var(--app-border);
  background: var(--app-surface-sunken);
  color: var(--app-text-soft);
  font-family: var(--font-sans);
  font-size: 9px;
  font-weight: 700;
  line-height: 1;
  box-shadow: inset 0 -1px 0 color-mix(in srgb, var(--app-border-strong) 55%, transparent);
}
.command-esc {
  padding: 5px 7px;
  border-radius: 7px;
}
.command-body {
  min-height: 250px;
  overflow: auto;
  overscroll-behavior: contain;
  padding: 12px;
}
.command-section {
  display: grid;
  gap: 10px;
}
.command-section__heading {
  min-height: 30px;
  padding: 2px 7px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  color: var(--app-text-muted);
  font-size: 11px;
  font-weight: 700;
}
.command-section__heading small {
  color: var(--app-text-soft);
  font-size: 8.5px;
  letter-spacing: 0.14em;
}
.command-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 7px;
}
.command-card {
  min-width: 0;
  min-height: 76px;
  padding: 12px;
  display: grid;
  grid-template-columns: 38px minmax(0, 1fr) 26px;
  align-items: center;
  gap: 10px;
  border: 1px solid transparent;
  border-radius: 15px;
  background: var(--app-surface-sunken);
  color: inherit;
  text-decoration: none;
  transition:
    border-color 160ms var(--app-ease),
    background-color 160ms var(--app-ease),
    transform 160ms var(--app-ease);
}
.command-card.is-selected {
  border-color: var(--accent-line);
  background: var(--app-surface);
  transform: translateY(-1px);
}
.command-card__icon,
.command-result__icon {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border: 1px solid var(--app-border);
  border-radius: 12px;
  background: var(--app-surface);
  color: var(--accent);
  font-size: 19px;
}
.command-card__copy {
  min-width: 0;
  display: grid;
  gap: 2px;
}
.command-card__copy strong {
  overflow: hidden;
  color: var(--app-text);
  font-size: 12.5px;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.command-card__copy small {
  overflow: hidden;
  color: var(--app-text-soft);
  font-size: 10.5px;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.command-card__arrow,
.command-result__arrow {
  color: var(--app-text-soft);
  font-size: 16px;
  transition:
    transform 160ms var(--app-ease),
    color 160ms var(--app-ease);
}
.command-card.is-selected .command-card__arrow,
.command-result.is-selected .command-result__arrow {
  color: var(--accent);
  transform: translateX(2px);
}
.command-tip {
  min-height: 46px;
  margin-top: 2px;
  padding: 0 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-radius: 13px;
  color: var(--app-text-soft);
  font-size: 10.5px;
}
.command-tip .material-symbols-rounded {
  color: var(--accent);
  font-size: 17px;
}
.command-results {
  display: grid;
  gap: 3px;
}
.command-result {
  min-width: 0;
  padding: 10px 11px;
  display: grid;
  grid-template-columns: 38px minmax(0, 1fr) 24px;
  align-items: center;
  gap: 11px;
  border: 1px solid transparent;
  border-radius: 14px;
  color: inherit;
  text-decoration: none;
  transition:
    border-color 150ms var(--app-ease),
    background-color 150ms var(--app-ease);
}
.command-result.is-selected {
  border-color: var(--accent-line);
  background: var(--accent-weak);
}
.command-result__copy {
  min-width: 0;
  display: grid;
  gap: 3px;
}
.command-result__topline {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}
.command-result__topline strong {
  min-width: 0;
  overflow: hidden;
  color: var(--app-text);
  font-size: 12.5px;
  font-style: normal;
  font-weight: 680;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.command-result__topline em {
  flex: 0 0 auto;
  color: var(--app-text-soft);
  font-size: 8px;
  font-style: normal;
  font-weight: 750;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.command-result__desc {
  overflow: hidden;
  color: var(--app-text-muted);
  font-size: 10.5px;
  line-height: 1.45;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.command-empty {
  min-height: 220px;
  padding: 36px 20px;
  display: grid;
  place-items: center;
  align-content: center;
  gap: 8px;
  color: var(--app-text-soft);
  text-align: center;
}
.command-empty .empty-spark {
  width: 20px;
  height: 20px;
  margin-bottom: 3px;
  opacity: 0.42;
}
.command-empty strong {
  color: var(--app-text-muted);
  font-size: 13px;
}
.command-empty small {
  max-width: 340px;
  font-size: 10.5px;
  line-height: 1.6;
}
.command-footer {
  min-height: 42px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  border-top: 1px solid var(--app-border);
  color: var(--app-text-soft);
  font-size: 9.5px;
}
.command-footer span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.command-footer kbd {
  min-width: 20px;
  padding: 3px 5px;
  border-radius: 5px;
  text-align: center;
}
.command-footer__brand {
  margin-left: auto;
  font-weight: 750;
  letter-spacing: 0.12em;
}
.command-footer__brand i {
  width: 9px;
  height: 9px;
  opacity: 0.75;
}
:deep(mark) {
  padding: 0 1px;
  border-radius: 3px;
  background: var(--accent-selection);
  color: inherit;
}

@media (max-width: 640px) {
  .command-panel {
    top: 68px;
    width: calc(100vw - 16px);
    max-height: calc(100vh - 78px);
    border-radius: 20px;
  }
  .command-search {
    min-height: 60px;
    padding-inline: 14px 10px;
  }
  .command-spark {
    display: none;
  }
  .command-search {
    grid-template-columns: minmax(0, 1fr) auto;
  }
  .command-grid {
    grid-template-columns: 1fr;
  }
  .command-body {
    padding: 9px;
  }
  .command-footer {
    display: none;
  }
  .command-card {
    min-height: 68px;
  }
}

/* v2.8: give the command palette one memorable surface without adding a library. */
.command-panel::before {
  content: "";
  position: absolute;
  z-index: 3;
  inset: 0 14% auto;
  height: 1px;
  pointer-events: none;
  background: linear-gradient(90deg, transparent, color-mix(in srgb, var(--accent) 50%, transparent), transparent);
  opacity: 0.78;
}
.command-panel::after {
  content: "";
  position: absolute;
  z-index: 0;
  right: -110px;
  top: -130px;
  width: 280px;
  height: 280px;
  border: 1px solid color-mix(in srgb, var(--accent) 8%, transparent);
  border-radius: 50%;
  pointer-events: none;
}
.command-search,
.command-body,
.command-footer {
  position: relative;
  z-index: 1;
}
.command-spark {
  animation: command-spark-arrive 520ms cubic-bezier(0.16, 1, 0.3, 1) both;
}
@keyframes command-spark-arrive {
  from {
    opacity: 0;
    transform: rotate(-28deg) scale(0.28);
  }
  62% {
    opacity: 1;
    transform: rotate(9deg) scale(1.18);
  }
  to {
    opacity: 0.9;
    transform: rotate(0) scale(1);
  }
}
.command-card.is-selected,
.command-result.is-selected {
  box-shadow:
    inset 0 1px 0 color-mix(in srgb, #fff 62%, transparent),
    0 7px 22px color-mix(in srgb, var(--accent) 6%, transparent);
}

/* v2.9 · spatial command palette */
.command-backdrop {
  background:
    radial-gradient(circle at 50% 18%, color-mix(in srgb, var(--accent) 10%, transparent), transparent 34%),
    color-mix(in srgb, var(--app-overlay) 87%, transparent);
}
.command-panel {
  border-color: color-mix(in srgb, var(--accent-line) 62%, var(--app-border));
  border-radius: 28px;
  background:
    radial-gradient(circle at 86% -12%, color-mix(in srgb, var(--accent) 8%, transparent), transparent 29%),
    color-mix(in srgb, var(--app-surface) 96%, var(--brand-tint));
  box-shadow:
    0 42px 120px rgba(18, 27, 45, 0.27),
    0 12px 34px rgba(18, 27, 45, 0.09),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
}
.command-panel::before {
  inset: 0 8% auto;
  height: 2px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    color-mix(in srgb, #8fb6d2 62%, transparent) 33%,
    color-mix(in srgb, var(--accent) 72%, transparent) 52%,
    transparent 100%
  );
  opacity: 0.95;
  animation: command-beam 3.6s ease-in-out infinite;
}
.command-panel::after {
  right: -88px;
  top: -116px;
  width: 310px;
  height: 310px;
  border-color: color-mix(in srgb, var(--accent) 13%, transparent);
  box-shadow: inset 0 0 0 38px color-mix(in srgb, var(--accent) 1.8%, transparent);
}
.command-search {
  min-height: 76px;
}
.command-input {
  font-size: 17px;
  letter-spacing: -0.012em;
}
.command-spark {
  width: 17px;
  height: 17px;
  filter: drop-shadow(0 6px 12px color-mix(in srgb, var(--accent) 20%, transparent));
}
.command-card,
.command-result {
  overflow: hidden;
  position: relative;
}
.command-card::before,
.command-result::before {
  content: "";
  position: absolute;
  left: -22%;
  top: -120%;
  width: 42%;
  height: 330%;
  pointer-events: none;
  opacity: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.7), transparent);
  transform: rotate(18deg) translateX(-120%);
  transition:
    transform 620ms cubic-bezier(0.16, 1, 0.3, 1),
    opacity 180ms ease;
}
.command-card.is-selected,
.command-result.is-selected {
  transform: translate3d(3px, -2px, 0) scale(1.008);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.75),
    0 12px 30px color-mix(in srgb, var(--accent) 9%, transparent);
}
.command-card.is-selected::before,
.command-result.is-selected::before {
  opacity: 0.42;
  transform: rotate(18deg) translateX(330%);
}
.command-card.is-selected .command-card__icon,
.command-result.is-selected .command-result__icon {
  transform: rotate(-3deg) scale(1.06);
  box-shadow: 0 8px 20px color-mix(in srgb, var(--accent) 10%, transparent);
}
.command-card__icon,
.command-result__icon {
  transition:
    transform 280ms cubic-bezier(0.16, 1, 0.3, 1),
    box-shadow 280ms ease;
}
@keyframes command-beam {
  0%,
  100% {
    transform: scaleX(0.48);
    opacity: 0.52;
  }
  50% {
    transform: scaleX(1);
    opacity: 1;
  }
}
@media (max-width: 640px) {
  .command-panel {
    border-radius: 22px;
  }
  .command-search {
    min-height: 64px;
  }
  .command-input {
    font-size: 16px;
  }
}
@media (prefers-reduced-motion: reduce) {
  .command-panel::before {
    animation: none;
  }
  .command-card::before,
  .command-result::before {
    display: none;
  }
}

/* ============================================================
   v4.0 · Command palette visual QA
   ============================================================ */
.command-panel {
  top: clamp(74px, 9vh, 108px);
}
.command-section__heading small {
  font-size: 9.5px;
  line-height: 1.3;
}
.command-card__copy strong,
.command-result__topline strong {
  line-height: 1.3;
}
.command-card__copy small,
.command-result__desc,
.command-tip,
.command-empty small {
  font-size: 11px;
  line-height: 1.5;
}
.command-result__topline em {
  font-size: 9px;
  line-height: 1.3;
}
.command-footer {
  font-size: 10px;
}
@media (max-width: 640px) {
  .command-panel {
    top: 66px;
  }
}

/* v4.1 · Command palette becomes a touch-first sheet on phones */
@media (max-width: 640px) {
  .command-backdrop {
    backdrop-filter: blur(4px);
  }
  .command-panel {
    inset: 62px 6px 6px !important;
    top: 62px !important;
    left: 6px !important;
    width: auto !important;
    max-height: none !important;
    translate: 0 0 !important;
    border-radius: 22px !important;
  }
  .command-search {
    min-height: 64px !important;
    padding: 9px 12px !important;
  }
  .command-input {
    font-size: 16px !important;
  }
  .command-body {
    min-height: 0 !important;
    flex: 1;
    padding: 8px !important;
  }
  .command-grid {
    grid-template-columns: 1fr !important;
  }
  .command-card {
    min-height: 68px !important;
    grid-template-columns: 40px minmax(0, 1fr) 24px !important;
  }
  .command-card__copy strong,
  .command-result__topline strong {
    font-size: 13px !important;
  }
  .command-card__copy small,
  .command-result__desc {
    font-size: 11px !important;
  }
  .command-result {
    min-height: 64px;
    padding: 9px 10px;
  }
  .command-panel::after {
    display: none;
  }
}
</style>
