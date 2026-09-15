<template>
  <Teleport to="body">
    <Transition name="article-gallery">
      <div
        v-if="modelValue && currentImage"
        class="article-gallery"
        role="dialog"
        aria-modal="true"
        aria-label="文章图片预览"
        @click.self="close"
      >
        <header class="article-gallery__header">
          <div class="article-gallery__meta">
            <span aria-hidden="true">✦</span>
            <span>文章图片</span>
            <span class="article-gallery__counter">{{ currentIndex + 1 }} / {{ images.length }}</span>
          </div>
          <div class="article-gallery__actions">
            <a :href="currentImage.originalSrc" target="_blank" rel="noopener noreferrer" aria-label="在新窗口打开原图">查看原图</a>
            <button ref="closeButton" type="button" aria-label="关闭图片预览" @click="close">×</button>
          </div>
        </header>

        <div
          :class="['article-gallery__stage', { 'is-single': !hasMultiple }]"
          @click.self="close"
          @touchstart.passive="onTouchStart"
          @touchend.passive="onTouchEnd"
        >
          <button v-if="hasMultiple" class="article-gallery__arrow is-previous" type="button" aria-label="上一张图片" @click="previous">‹</button>

          <figure :class="['article-gallery__figure', { 'is-loading': loading, 'is-error': error }]">
            <div v-if="loading && !error" class="article-gallery__status" aria-live="polite">
              <span aria-hidden="true">✦</span>
              <span>正在载入原图</span>
            </div>
            <div v-if="error" class="article-gallery__error">
              <span aria-hidden="true">✦</span>
              <strong>原图暂时无法载入</strong>
              <span>可以使用右上角的链接直接查看原图。</span>
            </div>
            <img
              v-show="!error"
              :key="currentImage.originalSrc"
              class="article-gallery__image"
              :src="currentImage.originalSrc"
              :alt="currentImage.alt"
              @load="onImageLoad"
              @error="onImageError"
            />
            <figcaption v-if="currentImage.alt">{{ currentImage.alt }}</figcaption>
          </figure>

          <button v-if="hasMultiple" class="article-gallery__arrow is-next" type="button" aria-label="下一张图片" @click="next">›</button>
        </div>

        <div v-if="hasMultiple" class="article-gallery__filmstrip" aria-label="文章图片列表">
          <button
            v-for="(image, index) in images"
            :key="`${image.src}-${index}`"
            :ref="(element) => setThumbnailRef(element, index)"
            type="button"
            :class="{ 'is-active': index === currentIndex }"
            :aria-label="`查看第 ${index + 1} 张图片${image.alt ? `：${image.alt}` : ''}`"
            :aria-current="index === currentIndex ? 'true' : undefined"
            @click="select(index)"
          >
            <img :src="image.src" :alt="image.alt" loading="lazy" decoding="async" />
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = defineProps({
  modelValue: { type: Boolean, required: true },
  images: { type: Array, default: () => [] },
  initialIndex: { type: Number, default: 0 },
});

const emit = defineEmits(["update:modelValue"]);
const currentIndex = ref(0);
const loading = ref(true);
const error = ref(false);
const closeButton = ref(null);
const thumbnailRefs = [];
let previousDocumentOverflow = "";
let touchStartX = null;
let touchStartY = null;

const images = computed(() => props.images || []);
const currentImage = computed(() => images.value[currentIndex.value]);
const hasMultiple = computed(() => images.value.length > 1);

function normalizedIndex(index) {
  const length = images.value.length;
  return length ? ((index % length) + length) % length : 0;
}

function setThumbnailRef(element, index) {
  if (element) thumbnailRefs[index] = element;
}

function select(index) {
  const nextIndex = normalizedIndex(index);
  if (nextIndex === currentIndex.value) return;
  currentIndex.value = nextIndex;
  loading.value = true;
  error.value = false;
}

function previous() {
  select(currentIndex.value - 1);
}

function next() {
  select(currentIndex.value + 1);
}

function close() {
  emit("update:modelValue", false);
}

function onImageLoad() {
  loading.value = false;
  error.value = false;
}

function onImageError() {
  loading.value = false;
  error.value = true;
}

function preloadNeighbors() {
  if (!hasMultiple.value) return;
  for (const index of [normalizedIndex(currentIndex.value - 1), normalizedIndex(currentIndex.value + 1)]) {
    const source = images.value[index]?.originalSrc;
    if (source) new Image().src = source;
  }
}

function onKeydown(event) {
  if (!props.modelValue) return;
  if (event.key === "Escape") close();
  if (event.key === "ArrowLeft") previous();
  if (event.key === "ArrowRight") next();
}

function onTouchStart(event) {
  touchStartX = event.changedTouches?.[0]?.clientX ?? null;
  touchStartY = event.changedTouches?.[0]?.clientY ?? null;
}

function onTouchEnd(event) {
  if (touchStartX === null || touchStartY === null) return;
  const endX = event.changedTouches?.[0]?.clientX ?? touchStartX;
  const endY = event.changedTouches?.[0]?.clientY ?? touchStartY;
  const horizontalDistance = endX - touchStartX;
  const verticalDistance = endY - touchStartY;
  touchStartX = null;
  touchStartY = null;
  if (Math.abs(horizontalDistance) < 48 || Math.abs(horizontalDistance) <= Math.abs(verticalDistance)) return;
  horizontalDistance > 0 ? previous() : next();
}

watch(
  () => props.modelValue,
  async (open) => {
    if (open) {
      currentIndex.value = normalizedIndex(props.initialIndex);
      loading.value = true;
      error.value = false;
      previousDocumentOverflow = document.documentElement.style.overflow;
      document.documentElement.style.overflow = "hidden";
      await nextTick();
      closeButton.value?.focus();
      preloadNeighbors();
    } else {
      document.documentElement.style.overflow = previousDocumentOverflow;
    }
  },
);

watch(currentIndex, async () => {
  await nextTick();
  thumbnailRefs[currentIndex.value]?.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
  preloadNeighbors();
});

onMounted(() => {
  window.addEventListener("keydown", onKeydown);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", onKeydown);
  if (props.modelValue) document.documentElement.style.overflow = previousDocumentOverflow;
});
</script>

<style scoped>
.article-gallery {
  position: fixed;
  inset: 0;
  z-index: 10006;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  gap: 14px;
  padding: 18px clamp(14px, 3vw, 42px) max(18px, env(safe-area-inset-bottom));
  background: radial-gradient(circle at 50% 18%, color-mix(in srgb, var(--brand-tint) 72%, transparent), transparent 34%),
    color-mix(in srgb, var(--app-bg) 90%, rgba(7, 13, 24, 0.22));
  backdrop-filter: blur(18px) saturate(0.9);
}
.article-gallery__header,
.article-gallery__meta,
.article-gallery__actions {
  display: flex;
  align-items: center;
}
.article-gallery__header {
  min-height: 46px;
  justify-content: space-between;
  gap: 16px;
}
.article-gallery__meta {
  gap: 9px;
  color: var(--app-text-muted);
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.12em;
}
.article-gallery__meta > span:first-child { color: var(--accent); font-size: 15px; }
.article-gallery__counter { color: var(--app-text); letter-spacing: 0.06em; }
.article-gallery__actions { gap: 8px; }
.article-gallery__actions a,
.article-gallery__actions button {
  min-height: 42px;
  border: 1px solid var(--app-border);
  background: color-mix(in srgb, var(--app-surface) 90%, transparent);
  color: var(--app-text);
  box-shadow: var(--app-shadow-sm);
  cursor: pointer;
}
.article-gallery__actions a {
  display: inline-flex;
  align-items: center;
  padding: 0 14px;
  border-radius: 999px;
  font-size: 12px;
  text-decoration: none;
}
.article-gallery__actions button { width: 42px; padding: 0; border-radius: 50%; font-size: 24px; }
.article-gallery__stage {
  position: relative;
  min-width: 0;
  min-height: 0;
  display: grid;
  grid-template-columns: 52px minmax(0, 1fr) 52px;
  align-items: center;
  gap: 12px;
}
.article-gallery__stage.is-single {
  grid-template-columns: minmax(0, 1fr);
}
.article-gallery__figure {
  min-width: 0;
  min-height: 0;
  height: 100%;
  margin: 0;
  display: grid;
  place-items: center;
  align-content: center;
  gap: 10px;
}
.article-gallery__image {
  display: block;
  max-width: 100%;
  max-height: calc(100vh - 218px);
  width: auto;
  height: auto;
  object-fit: contain;
  border-radius: clamp(10px, 1.5vw, 20px);
  box-shadow: 0 28px 90px rgba(28, 43, 68, 0.16);
  transition: opacity 180ms ease, transform 240ms ease;
}
.article-gallery__figure.is-loading .article-gallery__image { opacity: 0; transform: scale(0.985); }
.article-gallery__figure figcaption { max-width: min(720px, 76vw); color: var(--app-text-muted); font-size: 12px; text-align: center; }
.article-gallery__status,
.article-gallery__error {
  position: absolute;
  left: 50%;
  top: 50%;
  z-index: 1;
  display: grid;
  justify-items: center;
  gap: 8px;
  transform: translate(-50%, -50%);
  color: var(--app-text-muted);
  text-align: center;
}
.article-gallery__status { font-family: var(--font-mono); font-size: 11px; }
.article-gallery__status > span:first-child { color: var(--accent); font-size: 24px; animation: gallery-pulse 1.1s ease-in-out infinite alternate; }
.article-gallery__error { width: min(320px, 80vw); padding: 22px; border: 1px solid var(--app-border); border-radius: 18px; background: var(--app-surface); }
.article-gallery__error strong { color: var(--app-text); }
.article-gallery__error span:last-child { font-size: 12px; }
.article-gallery__arrow {
  width: 46px;
  height: 46px;
  border: 1px solid var(--app-border);
  border-radius: 50%;
  background: color-mix(in srgb, var(--app-surface) 88%, transparent);
  color: var(--app-text);
  font-family: var(--font-display);
  font-size: 32px;
  line-height: 1;
  cursor: pointer;
}
.article-gallery__arrow:hover,
.article-gallery__actions a:hover,
.article-gallery__actions button:hover { border-color: var(--accent-line); color: var(--accent); }
.article-gallery__filmstrip {
  width: fit-content;
  max-width: min(820px, 88vw);
  margin: 0 auto;
  padding: 5px;
  display: flex;
  gap: 8px;
  overflow-x: auto;
  overscroll-behavior-inline: contain;
  scrollbar-width: thin;
}
.article-gallery__filmstrip button {
  flex: 0 0 76px;
  width: 76px;
  height: 54px;
  padding: 3px;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--app-border) 80%, transparent);
  border-radius: 10px;
  background: color-mix(in srgb, var(--app-surface) 82%, transparent);
  opacity: 0.58;
  cursor: pointer;
  transition: opacity 160ms ease, border-color 160ms ease, transform 160ms ease;
}
.article-gallery__filmstrip button:hover { opacity: 0.86; }
.article-gallery__filmstrip button.is-active { border-color: var(--accent); opacity: 1; transform: translateY(-2px); }
.article-gallery__filmstrip img { width: 100%; height: 100%; object-fit: cover; border-radius: 6px; }
.article-gallery-enter-active,
.article-gallery-leave-active { transition: opacity 180ms ease; }
.article-gallery-enter-from,
.article-gallery-leave-to { opacity: 0; }
@keyframes gallery-pulse { to { opacity: 0.45; transform: rotate(12deg) scale(0.92); } }
@media (max-width: 640px) {
  .article-gallery { gap: 9px; padding: 9px 9px max(12px, env(safe-area-inset-bottom)); }
  .article-gallery__meta { font-size: 9px; }
  .article-gallery__actions a { display: none; }
  .article-gallery__stage { display: block; }
  .article-gallery__figure { height: 100%; }
  .article-gallery__image { max-height: calc(100vh - 174px - env(safe-area-inset-bottom)); }
  .article-gallery__arrow { position: absolute; top: 50%; z-index: 2; width: 42px; height: 42px; transform: translateY(-50%); background: color-mix(in srgb, var(--app-surface) 76%, transparent); }
  .article-gallery__arrow.is-previous { left: 6px; }
  .article-gallery__arrow.is-next { right: 6px; }
  .article-gallery__filmstrip { width: fit-content; max-width: calc(100vw - 18px); }
  .article-gallery__filmstrip button { flex-basis: 64px; width: 64px; height: 48px; }
}
@media (prefers-reduced-motion: reduce) {
  .article-gallery *,
  .article-gallery-enter-active,
  .article-gallery-leave-active { animation: none !important; transition: none !important; scroll-behavior: auto !important; }
}
</style>
