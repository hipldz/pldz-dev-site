<template>
  <MobileDrawer v-model="isMobileMenuOpen" subtitle="Interactive projects & experiments">
    <p>Live Demo</p>
    <p>选择一个Demo, 打开预览或查看源码。</p>
  </MobileDrawer>

  <HeaderBar :route-name="'Demos'" :scroll="true" @toggle-mobile-menu="onToggleMobileMenu" />

  <div class="main-container">
    <main class="live-lab-shell">
      <section v-reveal class="lab-masthead" aria-labelledby="livedemo-title">
        <div class="lab-masthead__copy" data-reveal-item>
          <p class="lab-kicker"><span aria-hidden="true"></span> Live lab / runs 01—{{ formatCount(mockData.length) }}</p>
          <h1 id="livedemo-title">
            <span class="lab-title__live">Live</span><i class="lab-title__slash" aria-hidden="true">/</i><span class="lab-title__demo">Demo</span>
          </h1>
          <p class="lab-masthead__lead">选择实验，预览运行效果，再决定打开 Demo 或查看源码。</p>
        </div>

        <div class="lab-masthead__status" data-reveal-item aria-label="实验台状态">
          <div class="lab-status-cell">
            <span>{{ formatCount(mockData.length) }} experiments</span>
            <strong>{{ formatCount(mockData.length) }}</strong>
          </div>
          <div class="lab-status-cell lab-status-cell--ready">
            <span><i aria-hidden="true"></i> Ready</span>
            <strong>READY</strong>
          </div>
          <div class="lab-status-cell lab-status-cell--flow">
            <span>Select · Preview · Open</span>
            <p class="layout-handnote lab-status-signature">Preview, play, build.</p>
          </div>
        </div>
      </section>

      <section v-if="loading" class="lab-state" aria-live="polite">
        <div class="lab-state__glyph" aria-hidden="true"><span></span><span></span></div>
        <p>正在准备实验台…</p>
      </section>

      <section v-else-if="loadError" class="lab-state lab-state--error" aria-live="polite">
        <span class="material-symbols-rounded" aria-hidden="true">error</span>
        <p>{{ loadError }}</p>
        <button type="button" @click="loadDemos">重新加载</button>
      </section>

      <section v-else-if="activeDemo" id="demo-list" class="lab-console" aria-label="Live Demo 实验台">
        <aside class="lab-runs" aria-label="实验项目">
          <div class="lab-runs__head">
            <div>
              <span class="lab-runs__eyebrow">RUN INDEX</span>
              <strong>{{ formatCount(mockData.length) }} experiments</strong>
            </div>
            <span class="lab-runs__hint">click to stage</span>
          </div>

          <div class="lab-runs__list" role="list">
            <button
              v-for="(demo, index) in mockData"
              :key="demo.folder || demo.title || demo.url || index"
              :class="['lab-run', { 'is-active': activeDemoIndex === index }]"
              type="button"
              role="listitem"
              :aria-current="activeDemoIndex === index ? 'true' : undefined"
              @focus="selectDemo(index)"
              @click="selectDemo(index)"
            >
              <span class="lab-run__number">{{ formatCount(index + 1) }}</span>
              <span class="lab-run__copy">
                <small>{{ demo.folder || "experiment" }}</small>
                <strong>{{ demo.title || "未命名 Demo" }}</strong>
              </span>
              <span class="lab-run__state" aria-hidden="true">
                <i></i>
                {{ activeDemoIndex === index ? "STAGED" : "READY" }}
              </span>
              <span class="material-symbols-rounded lab-run__arrow" aria-hidden="true">arrow_forward</span>
            </button>
          </div>

          <div class="lab-runs__footer">
            <span class="material-symbols-rounded" aria-hidden="true">bolt</span>
            <p>动态资源只在你主动播放后加载，避免后台解码和无意义流量。</p>
          </div>
        </aside>

        <div class="lab-stage" aria-live="polite">
          <div class="lab-stage__topbar">
            <div class="lab-stage__path">
              <span class="lab-stage__status-dot" :class="{ 'is-live': isLivePreview }" aria-hidden="true"></span>
              <span>LAB</span>
              <i>/</i>
              <strong>{{ activeDemo.folder || "experiment" }}</strong>
              <i>/</i>
              <span>{{ isLivePreview ? "live" : "cover" }}</span>
            </div>
            <div class="lab-stage__counter">RUN {{ formatCount(activeDemoIndex + 1) }} — {{ formatCount(mockData.length) }}</div>
          </div>

          <figure v-cursor="'OPEN'" class="lab-viewport">
            <div class="lab-viewport__grid" aria-hidden="true"></div>
            <div class="lab-viewport__halo" aria-hidden="true"></div>

            <Transition name="lab-media" mode="out-in">
              <div :key="`${activeDemoKey}-${isLivePreview}-${mediaOverride}`" class="lab-media-frame">
                <img
                  :src="activeMediaSrc"
                  :alt="`${activeDemo.title || 'Demo'} ${isLivePreview ? '动态预览' : '预览图'}`"
                  decoding="async"
                  loading="eager"
                  @error="handleMediaError"
                />
              </div>
            </Transition>

            <div class="lab-viewport__stamp" aria-hidden="true">
              <span>{{ formatCount(activeDemoIndex + 1) }}</span>
              <small>{{ isLivePreview ? "LIVE RUN" : "STAGED" }}</small>
            </div>

            <div class="lab-action-dock" aria-label="Demo 操作">
              <button v-if="activeDemo.previewgif" :class="['lab-action', { 'is-active': isLivePreview }]" type="button" @click="toggleLivePreview">
                <span class="material-symbols-rounded" aria-hidden="true">{{ isLivePreview ? "pause" : "play_arrow" }}</span>
                <span>{{ isLivePreview ? "回到封面" : "播放预览" }}</span>
              </button>
              <button class="lab-action lab-action--primary" type="button" :disabled="!activeDemo.url" @click="onGoPreview(activeDemo.url)">
                <span class="material-symbols-rounded" aria-hidden="true">open_in_new</span>
                <span>打开 Demo</span>
              </button>
              <a v-if="activeDemo.sourcelink" class="lab-action" :href="activeDemo.sourcelink" target="_blank" rel="noopener noreferrer">
                <span class="material-symbols-rounded" aria-hidden="true">code</span>
                <span>源码</span>
              </a>
            </div>
          </figure>

          <div class="lab-stage__caption">
            <div class="lab-stage__title">
              <p>
                <span>{{ activeDemo.folder || "experiment" }}</span>
                <time v-if="activeDemo.date" :datetime="activeDemo.date">{{ fmtDate(activeDemo.date) }}</time>
              </p>
              <h2>{{ activeDemo.title || "未命名 Demo" }}</h2>
            </div>
            <p class="lab-stage__description">{{ activeDemo.description || "可以直接打开体验的实验项目。" }}</p>
          </div>
        </div>
      </section>

      <section v-else class="lab-state" aria-live="polite">
        <div class="lab-state__glyph" aria-hidden="true"><span></span><span></span></div>
        <p>暂时没有可以运行的实验。</p>
      </section>

      <footer class="lab-footnote" aria-label="Live Lab 说明">
        <span>PERSONAL LAB / BUILD IN PUBLIC</span>
        <p>小实验不必成为大项目，也值得留下可运行的版本。</p>
      </footer>
    </main>
  </div>

  <FooterBar />
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import FooterBar from "../components/FooterBar.vue";
import HeaderBar from "../components/HeaderBar.vue";
import MobileDrawer from "../components/MobileDrawer.vue";
import { getAllLiveDemos } from "../utils/apis";

const isMobileMenuOpen = ref(false);
const mockData = ref([]);
const activeDemoIndex = ref(0);
const isLivePreview = ref(false);
const mediaOverride = ref("");
const loading = ref(true);
const loadError = ref("");

const activeDemo = computed(() => mockData.value[activeDemoIndex.value] || null);
const activeDemoKey = computed(() => activeDemo.value?.folder || activeDemo.value?.title || activeDemoIndex.value);
const activeMediaSrc = computed(() => {
  if (mediaOverride.value) return mediaOverride.value;
  const demo = activeDemo.value;
  if (!demo) return "/404.jpg";
  if (isLivePreview.value && demo.previewgif) return demo.previewgif;
  return demo.thumbnail || "/404.jpg";
});

const formatCount = (value) => String(Math.max(0, Number(value) || 0)).padStart(2, "0");

function fmtDate(value) {
  if (!value) return "";
  const plain = String(value).match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (plain) return `${plain[1]}-${plain[2]}-${plain[3]}`;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function selectDemo(index) {
  if (!Number.isInteger(index) || index < 0 || index >= mockData.value.length) return;
  if (activeDemoIndex.value === index) return;
  activeDemoIndex.value = index;
}

function toggleLivePreview() {
  if (!activeDemo.value?.previewgif) return;
  isLivePreview.value = !isLivePreview.value;
  mediaOverride.value = "";
}

function handleMediaError() {
  const demo = activeDemo.value;
  if (!demo) {
    mediaOverride.value = "/404.jpg";
    return;
  }

  if (isLivePreview.value && demo.thumbnail && mediaOverride.value !== demo.thumbnail) {
    isLivePreview.value = false;
    mediaOverride.value = demo.thumbnail;
    return;
  }

  if (mediaOverride.value !== "/404.jpg") mediaOverride.value = "/404.jpg";
}

function onGoPreview(url) {
  if (!url) return;
  const finalUrl = /^https?:\/\//i.test(url) ? url : `${window.location.origin.replace(/\/$/, "")}/${String(url).replace(/^\//, "")}`;
  window.open(finalUrl, "_blank", "noopener,noreferrer");
}

function onToggleMobileMenu() {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
}

async function loadDemos() {
  loading.value = true;
  loadError.value = "";
  try {
    const response = await getAllLiveDemos();
    mockData.value = Array.isArray(response) ? response.filter(Boolean) : [];
    activeDemoIndex.value = 0;
  } catch (error) {
    console.error("Failed to load live demos", error);
    mockData.value = [];
    loadError.value = "Demo 暂时加载失败，请稍后重试。";
  } finally {
    loading.value = false;
  }
}

watch(activeDemoIndex, () => {
  isLivePreview.value = false;
  mediaOverride.value = "";
});

onMounted(() => {
  document.body.classList.add("route-live-lab");
  loadDemos();
});

onBeforeUnmount(() => {
  document.body.classList.remove("route-live-lab");
});
</script>

<style scoped>
@import url("../assets/views/main-container.css");

:global(body.route-live-lab) {
  background:
    radial-gradient(circle at 84% 9%, color-mix(in srgb, var(--accent) 5%, transparent), transparent 27rem),
    radial-gradient(circle at 6% 58%, color-mix(in srgb, var(--brand-support) 3.5%, transparent), transparent 25rem), var(--app-bg);
}

.main-container {
  width: min(1280px, calc(100% - 2 * var(--app-page-gutter)));
  display: block;
  padding: 106px 0 78px;
}

.live-lab-shell {
  --lab-line: color-mix(in srgb, var(--app-border-strong) 72%, transparent);
  --lab-line-soft: color-mix(in srgb, var(--app-border) 82%, transparent);
  --lab-workspace: color-mix(in srgb, var(--app-surface) 90%, var(--accent) 1.8%);
  --lab-rail: color-mix(in srgb, var(--app-surface-sunken) 86%, var(--app-surface));
  --lab-stage: color-mix(in srgb, var(--app-surface) 95%, var(--accent) 1%);
  --lab-grid: color-mix(in srgb, var(--accent) 8%, transparent);
  --lab-accent-soft: color-mix(in srgb, var(--accent) 8%, var(--app-surface));
  display: grid;
  gap: clamp(28px, 4vw, 48px);
}

.lab-masthead {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1.12fr) minmax(360px, 0.78fr);
  gap: clamp(30px, 5vw, 76px);
  align-items: end;
  padding: 26px 2px 7px;
}
.lab-masthead::after {
  content: "";
  position: absolute;
  right: 0;
  bottom: -14px;
  width: min(42%, 460px);
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--app-border-strong));
}
.lab-kicker {
  margin: 0 0 13px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 8px;
  font-weight: 740;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.lab-kicker > span {
  width: 20px;
  height: 20px;
  display: grid;
  place-items: center;
  border: 1px solid var(--accent-line);
  border-radius: 50%;
  background: color-mix(in srgb, var(--app-surface) 76%, transparent);
}
.lab-kicker > span::before {
  content: "";
  width: 8px;
  height: 8px;
  background: var(--accent);
  clip-path: polygon(50% 0, 62% 38%, 100% 50%, 62% 62%, 50% 100%, 38% 62%, 0 50%, 38% 38%);
}
.lab-masthead h1 {
  margin: 0;
  color: var(--app-text);
  font-family: var(--font-display);
  font-size: clamp(54px, 7.3vw, 88px);
  font-weight: 590;
  letter-spacing: -0.072em;
  line-height: 0.91;
}
.lab-masthead__lead {
  max-width: 680px;
  margin: 22px 0 0;
  color: var(--app-text-muted);
  font-size: 13.5px;
  line-height: 1.82;
}

.lab-masthead__meta {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}
.lab-meta-item {
  position: relative;
  min-height: 82px;
  padding: 15px 14px;
  display: grid;
  align-content: center;
  gap: 4px;
  border: 1px solid var(--app-border);
  border-radius: 17px;
  background: color-mix(in srgb, var(--app-surface) 84%, transparent);
  box-shadow: inset 0 1px 0 color-mix(in srgb, #fff 62%, transparent);
}
.lab-meta-item span {
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 7px;
  font-weight: 740;
  letter-spacing: 0.12em;
}
.lab-meta-item strong {
  color: var(--app-text);
  font-size: 10.5px;
  font-weight: 650;
}
.lab-meta-item--signal {
  padding-left: 31px;
}
.lab-meta-item--signal i {
  position: absolute;
  left: 13px;
  top: 50%;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--app-green);
  box-shadow: 0 0 0 5px color-mix(in srgb, var(--app-green) 8%, transparent);
  transform: translateY(-50%);
}

.lab-console {
  position: relative;
  min-width: 0;
  display: grid;
  grid-template-columns: minmax(230px, 0.31fr) minmax(0, 1fr);
  overflow: hidden;
  border: 1px solid var(--lab-line);
  border-radius: 29px;
  background: var(--lab-workspace);
  box-shadow:
    0 24px 70px rgba(31, 43, 63, 0.075),
    inset 0 1px 0 color-mix(in srgb, #fff 62%, transparent);
}
.lab-console::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 79% 5%, color-mix(in srgb, var(--accent) 6%, transparent), transparent 27%),
    linear-gradient(120deg, transparent 0 67%, color-mix(in srgb, var(--accent) 2.4%, transparent) 67% 67.1%, transparent 67.1%);
}

.lab-runs {
  position: relative;
  z-index: 2;
  min-width: 0;
  padding: 22px 16px 18px;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--lab-line-soft);
  background: var(--lab-rail);
}
.lab-runs::after {
  content: "";
  position: absolute;
  left: 29px;
  top: 100px;
  bottom: 58px;
  width: 1px;
  pointer-events: none;
  background: linear-gradient(180deg, color-mix(in srgb, var(--accent) 22%, var(--app-border)), var(--app-border) 74%, transparent);
}
.lab-runs__head {
  min-height: 62px;
  padding: 0 8px 14px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid var(--lab-line-soft);
}
.lab-runs__head > div {
  display: grid;
  gap: 4px;
}
.lab-runs__eyebrow,
.lab-runs__hint {
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 8px;
  font-weight: 720;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.lab-runs__head strong {
  color: var(--app-text);
  font-size: 11.5px;
  font-weight: 640;
}
.lab-runs__hint {
  margin-top: 2px;
  opacity: 0.72;
}
.lab-runs__list {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 4px;
  padding-top: 9px;
}
.lab-run {
  position: relative;
  width: 100%;
  min-width: 0;
  min-height: 66px;
  padding: 10px 8px;
  display: grid;
  grid-template-columns: 27px minmax(0, 1fr) auto 18px;
  align-items: center;
  gap: 8px;
  border: 1px solid transparent;
  border-radius: 13px;
  background: transparent;
  color: var(--app-text);
  text-align: left;
  cursor: pointer;
  transition:
    background-color 180ms ease,
    border-color 180ms ease,
    transform 240ms cubic-bezier(0.16, 1, 0.3, 1),
    box-shadow 220ms ease;
}
.lab-run::before {
  content: "";
  position: absolute;
  left: 7px;
  top: 50%;
  width: 8px;
  height: 8px;
  border: 2px solid var(--app-surface-sunken);
  border-radius: 50%;
  background: var(--app-border-strong);
  box-shadow: 0 0 0 1px var(--app-border-strong);
  transform: translate(-50%, -50%);
  transition:
    background-color 180ms ease,
    box-shadow 180ms ease,
    transform 220ms ease;
}
.lab-run.is-active {
  border-color: color-mix(in srgb, var(--accent) 20%, var(--app-border));
  background: color-mix(in srgb, var(--app-surface) 92%, var(--accent) 2%);
  box-shadow: 0 7px 19px rgba(31, 43, 63, 0.045);
  transform: translateX(2px);
}
.lab-run.is-active::before {
  background: var(--accent);
  box-shadow:
    0 0 0 1px var(--accent),
    0 0 0 5px color-mix(in srgb, var(--accent) 7%, transparent);
  transform: translate(-50%, -50%) scale(1.08);
}
.lab-run__number,
.lab-run__state {
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 8px;
  font-weight: 720;
  letter-spacing: 0.07em;
}
.lab-run__copy {
  min-width: 0;
  display: grid;
  gap: 2px;
}
.lab-run__copy small {
  overflow: hidden;
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 7.5px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-overflow: ellipsis;
  text-transform: uppercase;
  white-space: nowrap;
}
.lab-run__copy strong {
  overflow: hidden;
  color: var(--app-text);
  font-size: 11px;
  font-weight: 620;
  letter-spacing: -0.015em;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.lab-run__state {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  opacity: 0.65;
}
.lab-run__state i {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--app-border-strong);
}
.lab-run.is-active .lab-run__state {
  color: var(--accent);
  opacity: 1;
}
.lab-run.is-active .lab-run__state i {
  background: var(--app-green);
}
.lab-run__arrow {
  color: var(--app-text-soft);
  font-size: 13px;
  opacity: 0.56;
  transition:
    transform 200ms ease,
    opacity 180ms ease,
    color 180ms ease;
}
.lab-run.is-active .lab-run__arrow {
  color: var(--accent);
  opacity: 1;
  transform: translateX(2px);
}
.lab-runs__footer {
  margin-top: auto;
  padding: 16px 8px 2px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  color: var(--app-text-soft);
}
.lab-runs__footer .material-symbols-rounded {
  margin-top: 1px;
  color: var(--accent);
  font-size: 13px;
}
.lab-runs__footer p {
  margin: 0;
  font-size: 9px;
  line-height: 1.6;
}

.lab-stage {
  position: relative;
  z-index: 1;
  min-width: 0;
  padding: clamp(18px, 2.4vw, 29px);
  display: grid;
  align-content: start;
  background: var(--lab-stage);
}
.lab-stage__topbar {
  min-height: 38px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 8px;
  font-weight: 720;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.lab-stage__path {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 7px;
}
.lab-stage__path strong {
  max-width: 34vw;
  overflow: hidden;
  color: var(--app-text);
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.lab-stage__path i {
  color: var(--app-border-strong);
  font-style: normal;
}
.lab-stage__status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--app-border-strong);
}
.lab-stage__status-dot.is-live {
  background: var(--app-green);
  box-shadow: 0 0 0 5px color-mix(in srgb, var(--app-green) 8%, transparent);
  animation: labPulse 1.9s ease-in-out infinite;
}
.lab-stage__counter {
  white-space: nowrap;
}

.lab-viewport {
  position: relative;
  isolation: isolate;
  width: 100%;
  aspect-ratio: 16 / 9;
  margin: 0;
  overflow: hidden;
  border: 1px solid var(--lab-line);
  border-radius: 23px;
  background:
    radial-gradient(circle at 78% 14%, color-mix(in srgb, var(--accent) 7%, transparent), transparent 32%),
    color-mix(in srgb, var(--app-surface-sunken) 83%, var(--app-surface));
  box-shadow:
    inset 0 1px 0 color-mix(in srgb, #fff 65%, transparent),
    0 17px 44px rgba(31, 43, 63, 0.07);
}
.lab-viewport::after {
  content: "";
  position: absolute;
  z-index: 0;
  inset: 12px;
  pointer-events: none;
  border: 1px solid color-mix(in srgb, var(--accent) 7%, transparent);
  border-radius: 16px;
}
.lab-viewport__grid {
  position: absolute;
  z-index: 0;
  inset: 0;
  opacity: 0.55;
  background-image: linear-gradient(var(--lab-grid) 1px, transparent 1px), linear-gradient(90deg, var(--lab-grid) 1px, transparent 1px);
  background-size: 30px 30px;
  mask-image: radial-gradient(circle at center, #000, transparent 78%);
}
.lab-viewport__halo {
  position: absolute;
  z-index: 0;
  right: -12%;
  top: -36%;
  width: 56%;
  aspect-ratio: 1;
  border-radius: 50%;
  background: radial-gradient(circle, color-mix(in srgb, var(--accent) 9%, transparent), transparent 68%);
  pointer-events: none;
}
.lab-media-frame {
  position: absolute;
  z-index: 1;
  inset: clamp(18px, 3vw, 34px) clamp(18px, 3.2vw, 40px) clamp(58px, 7vw, 82px);
  overflow: hidden;
  border: 1px solid var(--app-border);
  border-radius: 17px;
  background: var(--app-surface);
  box-shadow:
    0 19px 42px rgba(31, 43, 63, 0.09),
    inset 0 1px 0 color-mix(in srgb, #fff 70%, transparent);
}
.lab-media-frame img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: contain;
  object-position: center;
  background: var(--app-surface-sunken);
}
.lab-viewport__stamp {
  position: absolute;
  z-index: 3;
  left: clamp(28px, 4vw, 52px);
  bottom: clamp(22px, 3vw, 34px);
  display: flex;
  align-items: baseline;
  gap: 8px;
  pointer-events: none;
}
.lab-viewport__stamp span {
  color: var(--app-text);
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 560;
  letter-spacing: -0.06em;
  line-height: 1;
}
.lab-viewport__stamp small {
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 7.5px;
  font-weight: 740;
  letter-spacing: 0.12em;
}

.lab-action-dock {
  position: absolute;
  z-index: 4;
  right: clamp(24px, 3.5vw, 44px);
  bottom: clamp(18px, 2.5vw, 30px);
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px;
  border: 1px solid color-mix(in srgb, var(--app-border-strong) 80%, transparent);
  border-radius: 14px;
  background: color-mix(in srgb, var(--app-surface) 86%, transparent);
  box-shadow:
    0 14px 38px rgba(31, 43, 63, 0.1),
    inset 0 1px 0 color-mix(in srgb, #fff 72%, transparent);
  backdrop-filter: blur(12px);
}
.lab-action {
  min-height: 36px;
  padding: 0 11px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 1px solid transparent;
  border-radius: 10px;
  background: transparent;
  color: var(--app-text-muted);
  font: inherit;
  font-size: 9px;
  font-weight: 660;
  text-decoration: none;
  cursor: pointer;
}
.lab-action .material-symbols-rounded {
  font-size: 15px;
}
.lab-action:hover,
.lab-action.is-active {
  border-color: var(--app-border);
  background: var(--app-surface-sunken);
  color: var(--app-text);
}
.lab-action--primary {
  background: var(--accent);
  color: var(--app-on-accent);
  box-shadow: 0 7px 20px color-mix(in srgb, var(--accent) 15%, transparent);
}
.lab-action--primary:hover {
  background: var(--accent-hover);
  color: var(--app-on-accent);
}
.lab-action:disabled {
  opacity: 0.38;
  cursor: not-allowed;
}

.lab-stage__caption {
  padding: 20px 2px 2px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(220px, 0.44fr);
  gap: clamp(24px, 4vw, 52px);
  align-items: end;
}
.lab-stage__title > p {
  margin: 0 0 7px;
  display: flex;
  gap: 9px;
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 8px;
  font-weight: 720;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.lab-stage__title > p > * + *::before {
  content: "·";
  margin-right: 9px;
  color: var(--app-border-strong);
}
.lab-stage__title h2 {
  margin: 0;
  color: var(--app-text);
  font-family: var(--font-display);
  font-size: clamp(25px, 3vw, 38px);
  font-weight: 610;
  letter-spacing: -0.045em;
  line-height: 1.08;
}
.lab-stage__description {
  margin: 0;
  color: var(--app-text-muted);
  font-size: 10.5px;
  line-height: 1.68;
}

.lab-state {
  min-height: 400px;
  display: grid;
  align-content: center;
  justify-items: center;
  gap: 13px;
  border: 1px solid var(--app-border);
  border-radius: 26px;
  background: color-mix(in srgb, var(--app-surface) 72%, transparent);
  color: var(--app-text-muted);
  text-align: center;
}
.lab-state__glyph {
  position: relative;
  width: 48px;
  height: 48px;
}
.lab-state__glyph span {
  position: absolute;
  inset: 50% auto auto 50%;
  width: 18px;
  height: 18px;
  border: 1px solid var(--accent-line);
  border-radius: 50%;
  transform: translate(-50%, -50%);
}
.lab-state__glyph span + span {
  width: 7px;
  height: 7px;
  border: 0;
  background: var(--accent);
  box-shadow: 0 0 0 7px color-mix(in srgb, var(--accent) 8%, transparent);
}
.lab-state .material-symbols-rounded {
  color: var(--accent);
  font-size: 28px;
}
.lab-state p {
  margin: 0;
}
.lab-state button {
  min-height: 36px;
  padding: 0 13px;
  border: 1px solid var(--app-border);
  border-radius: 10px;
  background: var(--app-surface);
  color: var(--app-text);
  cursor: pointer;
}
.lab-state--error .material-symbols-rounded {
  color: var(--app-red);
}

.lab-footnote {
  padding: 18px 2px 0;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 24px;
  border-top: 1px solid var(--app-border);
  color: var(--app-text-soft);
}
.lab-footnote span {
  font-family: var(--font-mono);
  font-size: 8px;
  font-weight: 720;
  letter-spacing: 0.13em;
}
.lab-footnote p {
  margin: 0;
  font-size: 9.5px;
}

.lab-media-enter-active,
.lab-media-leave-active {
  transition:
    opacity 180ms ease,
    transform 360ms cubic-bezier(0.16, 1, 0.3, 1),
    filter 220ms ease;
}
.lab-media-enter-from {
  opacity: 0;
  transform: translateY(8px) scale(1.012);
  filter: blur(4px);
}
.lab-media-leave-to {
  opacity: 0;
  transform: translateY(-5px) scale(0.993);
  filter: blur(3px);
}

@keyframes labPulse {
  0%,
  100% {
    opacity: 0.62;
    box-shadow: 0 0 0 4px color-mix(in srgb, var(--app-green) 6%, transparent);
  }
  50% {
    opacity: 1;
    box-shadow: 0 0 0 8px color-mix(in srgb, var(--app-green) 2%, transparent);
  }
}

@media (hover: hover) and (pointer: fine) {
  .lab-run:hover:not(.is-active) {
    border-color: color-mix(in srgb, var(--app-border-strong) 68%, transparent);
    background: color-mix(in srgb, var(--app-surface) 64%, transparent);
    transform: translateX(2px);
  }
  .lab-run:hover .lab-run__arrow {
    opacity: 0.9;
    transform: translateX(2px);
  }
  .lab-viewport:hover {
    border-color: color-mix(in srgb, var(--accent) 20%, var(--app-border-strong));
  }
}

@media (max-width: 1050px) {
  .lab-masthead {
    grid-template-columns: 1fr;
    gap: 26px;
  }
  .lab-masthead__meta {
    max-width: 680px;
  }
  .lab-console {
    grid-template-columns: 210px minmax(0, 1fr);
  }
  .lab-run {
    grid-template-columns: 25px minmax(0, 1fr) 16px;
  }
  .lab-run__state {
    display: none;
  }
}

@media (max-width: 820px) {
  .main-container {
    padding-top: 88px;
  }
  .lab-masthead h1 {
    font-size: clamp(50px, 12vw, 72px);
  }
  .lab-console {
    grid-template-columns: 1fr;
    border-radius: 24px;
  }
  .lab-runs {
    padding: 15px 14px 13px;
    border-right: 0;
    border-bottom: 1px solid var(--lab-line-soft);
  }
  .lab-runs::after {
    display: none;
  }
  .lab-runs__head {
    min-height: 44px;
    padding-bottom: 9px;
  }
  .lab-runs__list {
    display: flex;
    gap: 7px;
    overflow-x: auto;
    padding: 8px 0 2px;
    scroll-snap-type: x proximity;
    scrollbar-width: none;
  }
  .lab-runs__list::-webkit-scrollbar {
    display: none;
  }
  .lab-run {
    flex: 0 0 min(72vw, 280px);
    min-height: 62px;
    padding: 9px 10px;
    grid-template-columns: 24px minmax(0, 1fr) 16px;
    border: 1px solid var(--app-border);
    background: color-mix(in srgb, var(--app-surface) 70%, transparent);
    scroll-snap-align: start;
  }
  .lab-run::before {
    display: none;
  }
  .lab-run.is-active {
    border-color: var(--accent-line);
    background: var(--accent-weak);
    transform: none;
  }
  .lab-runs__footer {
    display: none;
  }
  .lab-stage {
    padding: 15px;
  }
  .lab-stage__caption {
    grid-template-columns: 1fr;
    gap: 9px;
  }
}

@media (max-width: 580px) {
  .live-lab-shell {
    gap: 27px;
  }
  .lab-masthead {
    padding-top: 12px;
  }
  .lab-masthead__lead {
    margin-top: 16px;
    font-size: 12px;
  }
  .lab-masthead__meta {
    grid-template-columns: 1fr 1fr;
  }
  .lab-meta-item {
    min-height: 68px;
    padding: 12px 11px;
    border-radius: 14px;
  }
  .lab-meta-item:nth-child(3) {
    display: none;
  }
  .lab-stage__topbar {
    min-height: 34px;
  }
  .lab-stage__counter {
    display: none;
  }
  .lab-stage__path strong {
    max-width: 52vw;
  }
  .lab-viewport {
    aspect-ratio: 4 / 3;
    border-radius: 18px;
  }
  .lab-viewport::after {
    inset: 8px;
    border-radius: 13px;
  }
  .lab-media-frame {
    inset: 13px 13px 58px;
    border-radius: 13px;
  }
  .lab-action-dock {
    left: 13px;
    right: 13px;
    bottom: 10px;
    justify-content: center;
    overflow-x: auto;
  }
  .lab-action {
    min-height: 36px;
    padding: 0 9px;
  }
  .lab-action > span:last-child {
    display: none;
  }
  .lab-action--primary > span:last-child {
    display: inline;
  }
  .lab-viewport__stamp {
    display: none;
  }
  .lab-stage__caption {
    padding-top: 16px;
  }
  .lab-stage__title h2 {
    font-size: 28px;
  }
  .lab-stage__description {
    font-size: 10px;
  }
  .lab-footnote {
    align-items: flex-start;
    flex-direction: column;
    gap: 7px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .lab-stage__status-dot.is-live {
    animation: none;
  }
}

/* ============================================================
   v4.0 · Live Lab precision QA — centering, readable microtype
   ============================================================ */
.main-container {
  width: min(1180px, calc(100% - 2 * var(--app-page-gutter)));
  padding-top: 104px;
}
.live-lab-shell {
  gap: clamp(26px, 3.6vw, 42px);
}
.lab-masthead {
  grid-template-columns: minmax(0, 1.08fr) minmax(340px, 0.76fr);
  gap: clamp(32px, 4.5vw, 64px);
  padding: 18px 2px 8px;
}
.lab-kicker {
  margin-bottom: 11px;
  font-size: 9.5px;
  line-height: 1.35;
}
.lab-masthead h1 {
  font-size: clamp(52px, 6.8vw, 82px);
  line-height: 0.98;
  padding-bottom: 0.04em;
}
.lab-masthead__lead {
  max-width: 62ch;
  margin-top: 16px;
  font-size: 13.5px;
  line-height: 1.72;
}
.lab-masthead__meta {
  align-self: end;
}
.lab-meta-item {
  min-height: 76px;
  padding: 13px 14px;
}
.lab-meta-item span {
  font-size: 8.5px;
  line-height: 1.35;
}
.lab-meta-item strong {
  font-size: 11px;
  line-height: 1.35;
}

.lab-console {
  grid-template-columns: minmax(228px, 0.29fr) minmax(0, 1fr);
  border-radius: 26px;
}
.lab-runs {
  padding: 20px 15px 17px;
}
.lab-runs__head {
  min-height: 58px;
  padding-bottom: 12px;
}
.lab-runs__eyebrow,
.lab-runs__hint {
  font-size: 9px;
  line-height: 1.35;
}
.lab-runs__head strong {
  font-size: 12px;
  line-height: 1.35;
}
.lab-run {
  min-height: 68px;
  padding: 10px 9px;
}
.lab-run__number,
.lab-run__state {
  font-size: 9px;
  line-height: 1.3;
}
.lab-run__copy small {
  font-size: 8.5px;
  line-height: 1.35;
}
.lab-run__copy strong {
  font-size: 11.5px;
  line-height: 1.35;
}
.lab-runs__footer p {
  font-size: 10px;
  line-height: 1.55;
}

.lab-stage {
  min-width: 0;
}
.lab-stage__topbar {
  min-height: 42px;
}
.lab-stage__path,
.lab-stage__counter {
  font-size: 9px;
  line-height: 1.35;
}
.lab-viewport {
  border-radius: 22px;
}
.lab-media-frame {
  inset: clamp(18px, 2.5vw, 30px) clamp(18px, 2.8vw, 34px) clamp(60px, 6vw, 76px);
}
.lab-viewport__stamp small {
  font-size: 8.5px;
}
.lab-action {
  min-height: 38px;
  padding-inline: 12px;
  font-size: 10.5px;
  line-height: 1;
}
.lab-stage__caption {
  padding-top: 18px;
  grid-template-columns: minmax(0, 1fr) minmax(220px, 0.42fr);
  gap: clamp(24px, 3.5vw, 46px);
}
.lab-stage__title > p {
  margin-bottom: 7px;
  font-size: 9.5px;
  line-height: 1.35;
}
.lab-stage__title h2 {
  font-size: clamp(25px, 2.8vw, 36px);
  line-height: 1.1;
  padding-bottom: 0.03em;
}
.lab-stage__description {
  max-width: 48ch;
  justify-self: end;
  font-size: 12px;
  line-height: 1.65;
}
.lab-footnote span {
  font-size: 9px;
  line-height: 1.3;
}
.lab-footnote p {
  font-size: 10.5px;
  line-height: 1.5;
}

@media (max-width: 1050px) {
  .lab-masthead {
    grid-template-columns: 1fr;
    gap: 22px;
  }
  .lab-masthead__meta {
    max-width: 640px;
  }
}
@media (max-width: 820px) {
  .main-container {
    padding-top: 84px;
  }
  .lab-console {
    border-radius: 22px;
  }
  .lab-stage__caption {
    grid-template-columns: 1fr;
  }
  .lab-stage__description {
    justify-self: start;
    max-width: 62ch;
  }
}
@media (max-width: 580px) {
  .main-container {
    padding-top: 74px;
  }
  .lab-masthead h1 {
    font-size: clamp(46px, 14vw, 64px);
  }
  .lab-masthead__lead {
    font-size: 12.5px;
  }
  .lab-action {
    font-size: 10.5px;
  }
  .lab-stage__title h2 {
    font-size: 26px;
  }
  .lab-stage__description {
    font-size: 11.5px;
  }
}

/* ============================================================
   v4.1 · Live Lab mobile rebuild — swipe index + focused stage
   ============================================================ */
@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .main-container {
    width: 100% !important;
    padding: 76px 14px 46px !important;
  }
  .live-lab-shell {
    gap: 26px !important;
  }
  .lab-masthead {
    grid-template-columns: 1fr !important;
    gap: 18px !important;
    padding: 18px 0 4px !important;
  }
  .lab-masthead::after {
    display: none !important;
  }
  .lab-kicker {
    font-size: 9px !important;
  }
  .lab-masthead h1 {
    font-size: clamp(40px, 11.5vw, 58px) !important;
    line-height: 1 !important;
  }
  .lab-masthead__lead {
    max-width: none !important;
    margin-top: 13px !important;
    font-size: 13px !important;
    line-height: 1.65 !important;
  }
  .lab-masthead__meta {
    width: calc(100% + 28px) !important;
    margin-inline: -14px !important;
    padding: 0 14px 4px !important;
    display: flex !important;
    gap: 8px !important;
    overflow-x: auto !important;
    scrollbar-width: none;
  }
  .lab-masthead__meta::-webkit-scrollbar {
    display: none;
  }
  .lab-meta-item {
    flex: 0 0 150px !important;
    min-height: 66px !important;
  }

  .lab-console {
    display: block !important;
    overflow: visible !important;
    border: 0 !important;
    border-radius: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
  }
  .lab-console::before {
    display: none !important;
  }
  .lab-runs {
    margin-bottom: 14px !important;
    padding: 12px !important;
    border: 1px solid var(--lab-line-soft) !important;
    border-radius: 18px !important;
    background: var(--lab-rail) !important;
  }
  .lab-runs::after {
    display: none !important;
  }
  .lab-runs__head {
    min-height: 38px !important;
    padding: 0 2px 8px !important;
  }
  .lab-runs__list {
    display: flex !important;
    gap: 8px !important;
    padding: 6px 0 0 !important;
    overflow-x: auto !important;
    scroll-snap-type: x mandatory;
    scrollbar-width: none;
  }
  .lab-runs__list::-webkit-scrollbar {
    display: none;
  }
  .lab-run {
    flex: 0 0 min(76vw, 270px) !important;
    min-height: 62px !important;
    grid-template-columns: 26px minmax(0, 1fr) 18px !important;
    gap: 8px !important;
    padding: 9px 10px !important;
    border: 1px solid var(--app-border) !important;
    background: var(--app-surface) !important;
    transform: none !important;
    scroll-snap-align: start;
  }
  .lab-run__state {
    display: none !important;
  }
  .lab-run__number {
    font-size: 10px !important;
  }
  .lab-run__copy small {
    font-size: 10px !important;
    line-height: 1.3 !important;
  }
  .lab-run__copy strong {
    font-size: 12px !important;
    line-height: 1.3 !important;
  }
  .lab-runs__footer {
    display: none !important;
  }

  .lab-stage {
    padding: 12px 0 0 !important;
    background: transparent !important;
  }
  .lab-stage__topbar {
    min-height: 34px !important;
    padding-inline: 2px !important;
  }
  .lab-stage__counter {
    display: none !important;
  }
  .lab-stage__path strong {
    max-width: 58vw !important;
  }
  .lab-viewport {
    aspect-ratio: 4 / 3 !important;
    border-radius: 20px !important;
    box-shadow: 0 14px 36px rgba(31, 43, 63, 0.06) !important;
  }
  .lab-viewport::after {
    inset: 8px !important;
    border-radius: 14px !important;
  }
  .lab-media-frame {
    inset: 12px 12px 66px !important;
    border-radius: 14px !important;
  }
  .lab-viewport__stamp {
    display: none !important;
  }
  .lab-action-dock {
    left: 12px !important;
    right: 12px !important;
    bottom: 11px !important;
    width: auto !important;
    justify-content: stretch !important;
    gap: 5px !important;
    padding: 5px !important;
    overflow: visible !important;
  }
  .lab-action {
    flex: 1 1 0 !important;
    min-height: 42px !important;
    padding: 0 8px !important;
    font-size: 10px !important;
  }
  .lab-action > span:last-child {
    display: inline !important;
    white-space: nowrap;
  }
  .lab-stage__caption {
    grid-template-columns: 1fr !important;
    gap: 10px !important;
    padding: 16px 2px 0 !important;
  }
  .lab-stage__title h2 {
    font-size: 27px !important;
  }
  .lab-stage__description {
    justify-self: start !important;
    max-width: none !important;
    font-size: 12.5px !important;
  }
  .lab-footnote {
    align-items: flex-start !important;
    flex-direction: column !important;
    gap: 7px !important;
  }
}
@media (max-width: 470px) {
  .main-container {
    padding-inline: 12px !important;
  }
  .lab-masthead__meta {
    width: calc(100% + 24px) !important;
    margin-inline: -12px !important;
    padding-inline: 12px !important;
  }
  .lab-meta-item {
    flex-basis: 138px !important;
  }
  .lab-viewport {
    aspect-ratio: 1 / 1.05 !important;
  }
  .lab-media-frame {
    inset: 10px 10px 62px !important;
  }
  .lab-action {
    font-size: 0 !important;
  }
  .lab-action .material-symbols-rounded {
    font-size: 20px !important;
  }
  .lab-action--primary {
    font-size: 10px !important;
  }
  .lab-action--primary .material-symbols-rounded {
    font-size: 18px !important;
  }
}

/* ============================================================
   v4.4 · Live Lab alignment pass — real timeline geometry
   ============================================================ */
.lab-masthead__meta {
  align-items: stretch;
}
.lab-meta-item {
  min-height: 78px;
  align-content: center;
  justify-items: start;
  gap: 5px;
}
.lab-meta-item span,
.lab-meta-item strong {
  line-height: 1.3;
}
.lab-meta-item span {
  font-size: 9px;
}
.lab-meta-item strong {
  font-size: 11.5px;
}

.lab-console {
  grid-template-columns: minmax(258px, 0.3fr) minmax(0, 1fr);
}
.lab-runs {
  padding: 22px 18px 18px;
}
/* Old rail line was offset from every node. The list now owns the line. */
.lab-runs::after {
  display: none;
}
.lab-runs__head {
  min-height: 62px;
  padding: 0 2px 13px;
  align-items: center;
}
.lab-runs__head > div {
  gap: 5px;
}
.lab-runs__eyebrow,
.lab-runs__hint {
  font-size: 9px;
  line-height: 1.3;
}
.lab-runs__head strong {
  font-size: 12.5px;
  line-height: 1.35;
}
.lab-runs__hint {
  margin-top: 0;
  text-align: right;
}
.lab-runs__list {
  position: relative;
  z-index: 1;
  gap: 3px;
  padding-top: 12px;
}
.lab-runs__list::before {
  content: "";
  position: absolute;
  z-index: 0;
  left: 14px;
  top: 48px;
  bottom: 36px;
  width: 1px;
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--accent) 30%, var(--app-border-strong)),
    color-mix(in srgb, var(--app-border-strong) 76%, transparent) 68%,
    transparent
  );
  pointer-events: none;
}
.lab-run {
  z-index: 1;
  min-height: 72px;
  padding: 10px 8px 10px 0;
  grid-template-columns: 28px minmax(0, 1fr) minmax(48px, auto) 18px;
  align-items: center;
  gap: 10px;
  border-radius: 14px;
}
.lab-run::before {
  display: none;
}
.lab-run.is-active {
  transform: none;
}
.lab-run__number {
  position: relative;
  z-index: 2;
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  border: 1px solid color-mix(in srgb, var(--app-border-strong) 80%, transparent);
  border-radius: 50%;
  background: var(--lab-rail);
  color: var(--app-text-soft);
  font-size: 9px;
  line-height: 1;
  transition:
    color 180ms ease,
    border-color 180ms ease,
    background-color 180ms ease,
    box-shadow 200ms ease;
}
.lab-run.is-active .lab-run__number {
  border-color: color-mix(in srgb, var(--accent) 44%, var(--app-border));
  background: color-mix(in srgb, var(--app-surface) 88%, var(--accent) 6%);
  color: var(--accent);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent) 7%, transparent);
}
.lab-run__copy {
  min-width: 0;
  align-self: center;
  display: grid;
  gap: 4px;
}
.lab-run__copy small {
  font-size: 9px;
  line-height: 1.25;
  letter-spacing: 0.075em;
}
.lab-run__copy strong {
  font-size: 12.5px;
  line-height: 1.3;
  letter-spacing: -0.012em;
}
.lab-run__state {
  min-width: 48px;
  justify-content: center;
  font-size: 9px;
  line-height: 1;
}
.lab-run__arrow {
  display: grid;
  width: 18px;
  height: 18px;
  place-items: center;
  font-size: 14px;
  line-height: 1;
}
.lab-runs__footer {
  padding-inline: 0 2px;
}

.lab-stage__topbar {
  min-height: 44px;
  align-items: center;
  line-height: 1;
}
.lab-stage__path {
  min-height: 24px;
  align-items: center;
  gap: 8px;
}
.lab-stage__status-dot {
  flex: 0 0 6px;
}
.lab-stage__counter {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
}
.lab-stage__caption {
  align-items: start;
}
.lab-stage__title > p {
  min-height: 20px;
  align-items: center;
  line-height: 1.3;
}
.lab-stage__title > p time {
  display: inline-flex;
  align-items: center;
}
.lab-stage__description {
  padding-top: 1px;
}

@media (hover: hover) and (pointer: fine) {
  .lab-run:hover:not(.is-active) .lab-run__number {
    border-color: var(--accent-line);
    color: var(--accent);
  }
}

@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .lab-runs__list::before {
    display: none !important;
  }
  .lab-run {
    grid-template-columns: 28px minmax(0, 1fr) 18px !important;
    padding-left: 8px !important;
  }
  .lab-run__number {
    width: 28px !important;
    height: 28px !important;
    background: color-mix(in srgb, var(--app-surface) 88%, transparent) !important;
  }
  .lab-runs__head {
    align-items: center !important;
  }
}

/* v4.5 · Replace dashboard-like metadata with a personal handwritten note. */
.lab-masthead__signature {
  position: relative;
  justify-self: end;
  align-self: end;
  margin: 0 8px 10px 0;
  display: inline-flex;
  align-items: center;
  gap: 14px;
  color: color-mix(in srgb, var(--accent) 68%, var(--app-text-soft));
  font-family: Caveat, cursive;
  font-size: clamp(30px, 3vw, 42px);
  font-weight: 550;
  letter-spacing: 0.01em;
  line-height: 1;
  white-space: nowrap;
  transform: rotate(-2deg);
}
.lab-masthead__signature::after {
  content: "";
  width: clamp(42px, 5vw, 72px);
  height: 1px;
  background: linear-gradient(90deg, currentColor, transparent);
  opacity: 0.42;
  transform: rotate(-2deg);
}

@media (max-width: 1050px) {
  .lab-masthead__signature {
    justify-self: start;
    margin: -4px 0 0 4px;
  }
}

@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .lab-masthead {
    gap: 17px !important;
  }
  .lab-masthead__signature {
    gap: 10px;
    margin: -2px 0 0 3px;
    font-size: clamp(26px, 7.5vw, 31px);
  }
  .lab-masthead__signature::after {
    width: 36px;
  }
}

/* ============================================================
   v5.0 · Live Lab launch strip
   ============================================================ */
.main-container {
  width: min(1180px, calc(100% - 2 * var(--app-page-gutter)));
  padding-top: 104px;
}
.live-lab-shell {
  gap: 36px;
}
.lab-masthead {
  min-height: 178px;
  grid-template-columns: minmax(0, 1fr) minmax(430px, 0.86fr);
  align-items: center;
  gap: clamp(44px, 6vw, 88px);
  padding: 17px 0 28px;
  border-bottom: 1px solid color-mix(in srgb, var(--app-border-strong) 68%, transparent);
}
.lab-masthead::after {
  display: none;
}
.lab-kicker {
  margin-bottom: 12px;
  gap: 10px;
  color: var(--app-text-soft);
  font-size: 9px;
  letter-spacing: 0.14em;
}
.lab-kicker > span {
  width: 9px;
  height: 9px;
  border: 0;
  background: var(--app-green);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--app-green) 8%, transparent);
}
.lab-kicker > span::before {
  display: none;
}
.lab-masthead h1 {
  font-size: clamp(46px, 5.2vw, 62px);
  font-weight: 610;
  line-height: 0.98;
  letter-spacing: -0.06em;
}
.lab-masthead__lead {
  max-width: 610px;
  margin-top: 13px;
  font-size: 13.5px;
  line-height: 1.7;
}
.lab-masthead__signature {
  display: none;
}
.lab-masthead__status {
  min-width: 0;
  display: grid;
  grid-template-columns: 0.85fr 0.8fr 1.35fr;
  align-items: stretch;
  border-left: 1px solid color-mix(in srgb, var(--app-border-strong) 68%, transparent);
}
.lab-status-cell {
  min-width: 0;
  min-height: 84px;
  padding: 11px clamp(18px, 2vw, 28px);
  display: grid;
  align-content: center;
  gap: 10px;
  border-right: 1px solid var(--app-border);
}
.lab-status-cell:last-child {
  border-right: 0;
}
.lab-status-cell span {
  overflow: hidden;
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 8.5px;
  font-weight: 700;
  letter-spacing: 0.09em;
  line-height: 1.35;
  text-overflow: ellipsis;
  text-transform: uppercase;
  white-space: nowrap;
}
.lab-status-cell strong {
  color: var(--app-text);
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 620;
  line-height: 1;
}
.lab-status-cell--ready span {
  display: flex;
  align-items: center;
  gap: 8px;
}
.lab-status-cell--ready i {
  width: 8px;
  height: 8px;
  flex: 0 0 auto;
  border-radius: 50%;
  background: var(--app-green);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--app-green) 8%, transparent);
}
.lab-status-signature {
  gap: 9px;
  font-size: clamp(24px, 2vw, 30px);
}
.lab-status-signature::after {
  width: clamp(26px, 3vw, 42px);
}

@media (max-width: 1050px) {
  .lab-masthead {
    min-height: 0;
    grid-template-columns: 1fr;
    gap: 24px;
    padding-bottom: 26px;
  }
  .lab-masthead__status {
    width: min(100%, 650px);
  }
}

@media (max-width: 820px) {
  .main-container {
    padding-top: 84px;
  }
}

@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .main-container {
    padding-top: 76px !important;
  }
  .live-lab-shell {
    gap: 24px !important;
  }
  .lab-masthead {
    min-height: 0 !important;
    display: block !important;
    padding: 14px 0 18px !important;
    border-bottom: 1px solid var(--app-border) !important;
  }
  .lab-kicker,
  .lab-masthead__status {
    display: none !important;
  }
  .lab-masthead h1 {
    font-size: clamp(36px, 11vw, 48px) !important;
  }
  .lab-masthead__lead {
    margin-top: 9px !important;
    font-size: 12.5px !important;
  }
}

/* ============================================================
   v5.1 · Quieter color, local hover, more expressive type
   ============================================================ */
:global(body.route-live-lab) {
  background: var(--app-bg);
}
.live-lab-shell {
  --lab-line: color-mix(in srgb, var(--app-border-strong) 58%, transparent);
  --lab-line-soft: color-mix(in srgb, var(--app-border) 74%, transparent);
  --lab-workspace: var(--app-surface);
  --lab-rail: color-mix(in srgb, var(--app-surface-sunken) 58%, var(--app-surface));
  --lab-stage: var(--app-surface);
  --lab-grid: color-mix(in srgb, var(--accent) 4.5%, transparent);
  gap: 30px;
}
.lab-masthead {
  min-height: 154px;
  grid-template-columns: minmax(360px, 0.88fr) minmax(500px, 1fr);
  gap: clamp(38px, 5vw, 70px);
  padding: 12px 0 23px;
}
.lab-kicker {
  margin-bottom: 10px;
}
.lab-kicker > span {
  width: 7px;
  height: 7px;
  background: var(--accent);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 7%, transparent);
}
.lab-masthead h1 {
  display: flex;
  align-items: baseline;
  gap: clamp(8px, 1vw, 13px);
  font-size: clamp(42px, 4.2vw, 52px);
  font-weight: 610;
  line-height: 1;
  letter-spacing: -0.042em;
}
.lab-title__slash {
  color: color-mix(in srgb, var(--accent) 54%, var(--app-text-soft));
  font-family: var(--font-mono);
  font-size: 13px;
  font-style: normal;
  font-weight: 520;
  letter-spacing: 0;
  transform: translateY(-0.45em);
}
.lab-title__demo {
  color: color-mix(in srgb, var(--app-text) 78%, var(--app-text-muted));
  font-weight: 430;
}
.lab-masthead__lead {
  margin-top: 11px;
  font-size: 12.75px;
}
.lab-masthead__status {
  border-left-color: color-mix(in srgb, var(--app-border-strong) 52%, transparent);
}
.lab-status-cell {
  min-height: 72px;
  padding: 9px clamp(17px, 1.8vw, 24px);
  gap: 8px;
  border-right-color: color-mix(in srgb, var(--app-border) 72%, transparent);
}
.lab-status-cell strong {
  font-size: 22px;
  font-weight: 570;
}
.lab-status-cell--ready strong {
  color: color-mix(in srgb, var(--app-green) 70%, var(--app-text));
}
.lab-status-cell--ready i {
  width: 6px;
  height: 6px;
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--app-green) 7%, transparent);
}
.lab-status-signature {
  font-size: clamp(23px, 1.85vw, 28px);
}

.lab-console {
  border-radius: 22px;
  background: var(--app-surface);
  box-shadow:
    0 14px 42px rgba(31, 43, 63, 0.045),
    inset 0 1px 0 color-mix(in srgb, #fff 56%, transparent);
}
.lab-console::before {
  display: none;
}
.lab-runs {
  background: var(--lab-rail);
}
.lab-run {
  transition:
    background-color 160ms ease,
    border-color 160ms ease,
    box-shadow 180ms ease;
}
.lab-run.is-active {
  border-color: color-mix(in srgb, var(--accent) 15%, var(--app-border));
  background: color-mix(in srgb, var(--app-surface) 96%, var(--accent) 4%);
  box-shadow: inset 2px 0 0 color-mix(in srgb, var(--accent) 74%, transparent);
  transform: none;
}
.lab-run.is-active .lab-run__number {
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 5%, transparent);
}
.lab-stage {
  background: var(--lab-stage);
}
.lab-viewport {
  border-color: color-mix(in srgb, var(--app-border-strong) 66%, transparent);
  background: color-mix(in srgb, var(--app-surface-sunken) 72%, var(--app-surface));
  box-shadow:
    inset 0 1px 0 color-mix(in srgb, #fff 52%, transparent),
    0 10px 30px rgba(31, 43, 63, 0.045);
}
.lab-viewport__grid {
  opacity: 0.28;
}
.lab-viewport__halo {
  opacity: 0.34;
}
.lab-media-frame {
  box-shadow:
    0 12px 30px rgba(31, 43, 63, 0.065),
    inset 0 1px 0 color-mix(in srgb, #fff 58%, transparent);
}
.lab-action-dock {
  border-color: color-mix(in srgb, var(--app-border-strong) 72%, transparent);
  background: color-mix(in srgb, var(--app-surface) 94%, transparent);
  box-shadow: 0 8px 22px rgba(31, 43, 63, 0.065);
  backdrop-filter: none;
}

@media (hover: hover) and (pointer: fine) {
  .lab-run:hover:not(.is-active) {
    border-color: transparent;
    background: color-mix(in srgb, var(--app-surface) 91%, var(--accent) 2.5%);
    box-shadow: inset 2px 0 0 color-mix(in srgb, var(--accent) 22%, transparent);
    transform: none;
  }
  .lab-run:hover .lab-run__arrow {
    color: var(--accent);
    opacity: 0.8;
    transform: translateX(1px);
  }
  .lab-viewport:hover {
    border-color: color-mix(in srgb, var(--accent) 15%, var(--app-border-strong));
  }
  .lab-action:hover,
  .lab-action.is-active {
    border-color: transparent;
    background: var(--accent-weak);
    color: var(--accent);
  }
  .lab-action--primary:hover {
    background: var(--accent-hover);
    color: var(--app-on-accent);
  }
}

@media (max-width: 1050px) {
  .lab-masthead {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .live-lab-shell {
    gap: 20px !important;
  }
  .lab-masthead {
    padding-block: 11px 15px !important;
  }
  .lab-masthead h1 {
    gap: 7px;
    font-size: clamp(32px, 9.5vw, 40px) !important;
    letter-spacing: -0.035em;
  }
  .lab-title__slash {
    display: none;
  }
  .lab-masthead__lead {
    font-size: 12px !important;
  }
  .lab-console {
    border-radius: 19px;
    box-shadow: 0 10px 28px rgba(31, 43, 63, 0.035);
  }
}
</style>
