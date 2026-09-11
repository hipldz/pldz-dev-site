<template>
  <MobileDrawer v-model="isMobileMenuOpen" subtitle="文章目录" :show-nav-placeholder="false">
    <ChapterBlock :headings="headings"></ChapterBlock>
  </MobileDrawer>

  <!-- 顶部导航栏 -->
  <HeaderBar :scroll="true" @toggle-mobile-menu="toggleMobileMenu"></HeaderBar>

  <!-- 主体内容 -->
  <div class="main-container article-layout" id="article-main-container">
    <!-- 左侧边栏 -->
    <aside class="sidebar sidebar-sticky">
      <div class="sidebar-item sidebar-card sidebar-article-chapter">
        <ChapterBlock :headings="headings"></ChapterBlock>
      </div>
    </aside>
    <!-- 中间内容区 -->
    <main class="content article-shell">
      <header class="article-header card-surface">
        <div class="article-topline">
          <div class="article-kicker" aria-label="文章信息">
            <span class="article-signature" aria-hidden="true">✦</span>
            <span>ARTICLE</span>
            <i>/</i>
            <span>{{ article.meta.category || "NOTE" }}</span>
          </div>
          <p class="layout-handnote article-handnote" aria-hidden="true">Read, think, write.</p>
        </div>
        <h1 class="article-title">{{ article.meta.title }}</h1>
        <div class="article-meta">
          <time class="article-meta-item" :datetime="article.meta.date">{{ article.meta.date }}</time>
          <span>{{ article.views }} 次阅读</span>
          <span v-if="headings.length">{{ headings.length }} 个章节</span>
        </div>
        <div v-if="article.meta.tags?.length" class="article-tags" aria-label="文章标签">
          <span v-for="tag in article.meta.tags.slice(0, 5)" :key="tag">{{ tag }}</span>
        </div>
      </header>

      <div class="article-content card-surface" @click="onArticleContentClick">
        <article class="markdown-body" v-html="renderedHtml"></article>
      </div>
      <div class="next-previous-article card-surface">
        <span>其他文章</span>
        <PrevNext :id="article.id" :category="article.meta.category"></PrevNext>
      </div>
      <div class="comments-content card-surface">
        <span> 评论留言 </span>
        <CommentForm :article-id="article.id"></CommentForm>
      </div>
    </main>
  </div>

  <div class="fab-container" aria-label="文章快捷操作">
    <div class="fab-actions">
      <button class="fab-item fab-scroll" type="button" @click="onToTop" id="to-top" title="回到顶部" aria-label="回到顶部">
        <span class="fab-emoji" aria-hidden="true">✦</span><span class="fab-direction" aria-hidden="true">↑</span>
      </button>
      <button class="fab-item fab-scroll" type="button" @click="onToBottom" id="to-bottom" title="前往底部" aria-label="前往底部">
        <span class="fab-emoji" aria-hidden="true">✦</span><span class="fab-direction" aria-hidden="true">↓</span>
      </button>
      <button
        v-show="article.meta.csdn"
        class="fab-item csdn-icon fab-brand"
        type="button"
        id="to-csdn"
        @click="onGotoLink(article.meta.csdn)"
        title="CSDN"
        aria-label="打开 CSDN"
      ></button>
      <button
        v-show="article.meta.juejin"
        class="fab-item juejin-icon fab-brand"
        type="button"
        id="to-juejin"
        @click="onGotoLink(article.meta.juejin)"
        title="掘金"
        aria-label="打开掘金"
      ></button>
      <button
        v-show="article.meta.github"
        class="fab-item github-icon fab-brand"
        type="button"
        id="to-github"
        @click="onGotoLink(article.meta.github)"
        title="GitHub"
        aria-label="打开 GitHub"
      ></button>
      <button
        v-show="article.meta.gitee"
        class="fab-item gitee-icon fab-brand"
        type="button"
        id="to-gitee"
        @click="onGotoLink(article.meta.gitee)"
        title="Gitee"
        aria-label="打开 Gitee"
      ></button>
    </div>
  </div>

  <Teleport to="body">
    <Transition name="image-lightbox">
      <div v-if="lightbox.open" class="image-lightbox" role="dialog" aria-modal="true" aria-label="文章图片预览" @click.self="closeImageLightbox">
        <div class="image-lightbox__chrome">
          <div class="image-lightbox__meta">
            <span class="image-lightbox__signature" aria-hidden="true">✦</span>
            <span>ORIGINAL IMAGE</span>
          </div>
          <div class="image-lightbox__actions">
            <button class="image-lightbox__close" type="button" aria-label="关闭图片预览" @click="closeImageLightbox">
              <span aria-hidden="true">×</span>
            </button>
          </div>
        </div>

        <figure class="image-lightbox__figure" :class="{ 'is-loading': lightbox.loading, 'is-error': lightbox.error }" @click.self="closeImageLightbox">
          <div v-if="lightbox.loading && !lightbox.error" class="image-lightbox__loading" aria-live="polite">
            <span class="image-lightbox__loading-mark" aria-hidden="true">✦</span>
            <span>正在载入原图</span>
          </div>
          <div v-if="lightbox.error" class="image-lightbox__error">
            <span class="image-lightbox__error-mark" aria-hidden="true">✦</span>
            <strong>原图暂时无法载入</strong>
            <span>你仍然可以通过右上角直接打开原图链接。</span>
          </div>
          <img
            v-show="!lightbox.error"
            class="image-lightbox__image"
            :src="lightbox.src"
            :alt="lightbox.alt"
            @load="onLightboxImageLoad"
            @error="onLightboxImageError"
          />
          <figcaption v-if="lightbox.alt" class="image-lightbox__caption">{{ lightbox.alt }}</figcaption>
        </figure>
      </div>
    </Transition>
  </Teleport>

  <!-- 底部的信息栏 -->
  <FooterBar></FooterBar>
</template>

<script setup>
import "highlight.js/styles/github-dark.css";

import HeaderBar from "../components/HeaderBar.vue";
import FooterBar from "../components/FooterBar.vue";
import MobileDrawer from "../components/MobileDrawer.vue";

import ChapterBlock from "../components/article-page/ChapterBlock.vue";
import PrevNext from "../components/article-page/PrevNext.vue";
import CommentForm from "../components/article-page/CommentForm.vue";

import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import { getArticle } from "../utils/apis";
import { renderMarkdown } from "../utils/markdown.js";
import { refreshAnalyticsBindings, trackArticleView } from "../utils/analytics";

const props = defineProps({
  id: {
    type: String,
    required: true,
    default: "",
  },
});

const isMobileMenuOpen = ref(false);
const lightbox = ref({
  open: false,
  src: "",
  alt: "",
  loading: false,
  error: false,
});
let previousDocumentOverflow = "";

const article = ref({ id: "", content: "", meta: { title: "", date: "", category: "", tags: [], csdn: "", juejin: "", github: "", gitee: "" }, views: 0 });
const renderedHtml = ref("");
const headings = ref([]);

function closeMobileMenu() {
  isMobileMenuOpen.value = false;
}

function toggleMobileMenu() {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
}

/**
 * 滚动到页面顶部
 * @returns {void}
 */
function onToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

/**
 * 滚动到页面底部
 * @returns {void}
 */
function onToBottom() {
  window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
}

function onGotoLink(url) {
  window.open(url, "_blank");
}

async function copyCode(text) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }

  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "true");
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
}

function openImageLightbox(src, alt = "") {
  if (!src) return;

  previousDocumentOverflow = document.documentElement.style.overflow;
  document.documentElement.style.overflow = "hidden";
  lightbox.value = {
    open: true,
    src,
    alt,
    loading: true,
    error: false,
  };
}

function closeImageLightbox() {
  if (!lightbox.value.open) return;
  lightbox.value.open = false;
  document.documentElement.style.overflow = previousDocumentOverflow;
}

function onLightboxImageLoad() {
  lightbox.value.loading = false;
  lightbox.value.error = false;
}

function onLightboxImageError() {
  lightbox.value.loading = false;
  lightbox.value.error = true;
}

function onWindowKeydown(event) {
  if (event.key === "Escape" && lightbox.value.open) {
    closeImageLightbox();
  }
}

async function onArticleContentClick(event) {
  const imageLink = event.target?.closest(".markdown-image-link");
  if (imageLink) {
    event.preventDefault();
    const image = imageLink.querySelector("img");
    openImageLightbox(imageLink.dataset.originalSrc || imageLink.href, image?.alt || "");
    return;
  }

  const button = event.target?.closest(".code-block__copy");
  if (!button) return;

  const encodedCode = button.dataset.code || "";
  const text = decodeURIComponent(encodedCode);
  const initialText = button.textContent || "复制";

  try {
    await copyCode(text);
    button.textContent = "已复制";
  } catch {
    button.textContent = "失败";
  }

  window.setTimeout(() => {
    button.textContent = initialText;
  }, 1500);
}

function updateRenderedContent() {
  const result = renderMarkdown(article.value.content || "");
  renderedHtml.value = result.html;
  headings.value = result.headings;
}

async function loadArticle() {
  const res = await getArticle(props.id);
  if (!res) return;

  article.value = res;
  updateRenderedContent();
  trackArticleView({
    articleId: res.id,
    articleTitle: res.meta?.title || res.id,
  });
  refreshAnalyticsBindings();
}

function handleResize() {
  if (window.innerWidth > 768) {
    closeMobileMenu();
  }
}

onMounted(async () => {
  window.addEventListener("resize", handleResize, { passive: true });
  window.addEventListener("keydown", onWindowKeydown);
  await loadArticle();
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);
  window.removeEventListener("keydown", onWindowKeydown);
  if (lightbox.value.open) {
    document.documentElement.style.overflow = previousDocumentOverflow;
  }
});

watch(
  () => props.id,
  async (newId, oldId) => {
    if (!newId || newId === oldId) return;
    closeImageLightbox();
    await loadArticle();
  },
);

watch(
  () => article.value.content,
  () => {
    updateRenderedContent();
  },
);
</script>

<style scoped>
@import url("../assets/views/main-container.css");

:global(body) {
  background: radial-gradient(circle at 84% 9%, color-mix(in srgb, var(--accent) 4.5%, transparent), transparent 27rem), var(--app-bg);
  color: var(--app-text);
}

.article-layout {
  max-width: 1280px;
  padding-top: var(--app-page-top);
  padding-left: 20px;
  padding-right: 20px;
  padding-bottom: 40px;
  gap: 48px;
  align-items: flex-start;
}

.card-surface,
.sidebar-card,
.article-shell {
  background: transparent;
  border: none;
  border-radius: 0;
  box-shadow: none;
}

.sidebar {
  box-sizing: border-box;
  background: transparent;
  border-radius: 0;
  padding: 8px 24px 0 0;
  border-right: none;
}

.sidebar-sticky {
  position: sticky;
  top: 92px;
  height: calc(100vh - 92px);
}

.sidebar-article-chapter {
  max-height: calc(100vh - 120px);
}

.article-shell {
  background: transparent;
  border: none;
  box-shadow: none;
  display: grid;
  gap: 24px;
  max-width: none;
  min-width: 0;
  padding-left: 4px;
}

.content.article-shell {
  max-width: 880px;
  width: 100%;
}

.article-header {
  padding: 8px 0 0;
  background: transparent;
  border: none;
  border-radius: 0;
  box-shadow: none;
  max-width: 760px;
}

.article-title {
  font-size: clamp(30px, 4.2vw, 44px);
  font-weight: 800;
  color: var(--app-text);
  margin: 0 0 14px;
  line-height: 1.08;
  letter-spacing: -0.015em;
  display: none;
}

.article-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px 20px;
  color: var(--app-text-muted);
  font-size: 13px;
}

.article-meta span {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0;
  background: transparent;
}

.article-meta-item {
  color: var(--accent);
}

.article-content {
  padding: 0;
  line-height: 1.8;
  font-size: 16px;
  max-width: 760px;
}

.next-previous-article {
  padding: 22px 0 0;
  background: transparent;
  border: none;
  border-top: 1px solid var(--app-border);
  border-radius: 0;
  max-width: 760px;
}

.comments-content {
  padding: 22px 0 0;
  min-height: 600px;
  background: transparent;
  border: none;
  border-top: 1px solid var(--app-border);
  border-radius: 0;
  max-width: 760px;
}

.comments-content span,
.next-previous-article span {
  display: inline-block;
  margin-bottom: 18px;
  font-family: var(--font-display);
  font-size: 19px;
  font-weight: 600;
  color: var(--app-text);
}

.sidebar-card {
  overflow: hidden;
}

.markdown-body {
  color: var(--app-text);
  font-size: 16px;
  line-height: 1.85;
  word-break: break-word;
  max-width: 100%;
}

.markdown-body :deep(*) {
  box-sizing: border-box;
}

.markdown-body :deep(> *:first-child) {
  margin-top: 0;
}

.markdown-body :deep(> *:last-child) {
  margin-bottom: 0;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4),
.markdown-body :deep(h5),
.markdown-body :deep(h6) {
  color: var(--app-text);
  line-height: 1.4;
  letter-spacing: -0.015em;
  font-weight: 600;
  margin-top: 2.25em;
  margin-bottom: 0.9em;
  scroll-margin-top: 96px;
}

.markdown-body :deep(h1) {
  font-family: var(--font-display);
  font-size: clamp(28px, 3vw, 38px);
}

.markdown-body :deep(h2) {
  font-family: var(--font-display);
  font-size: clamp(23px, 2.4vw, 30px);
  padding-bottom: 0;
  border-bottom: 0;
}

.markdown-body :deep(h3) {
  font-size: 1.5rem;
}

.markdown-body :deep(h4) {
  font-size: 1.22rem;
}

.markdown-body :deep(p),
.markdown-body :deep(ul),
.markdown-body :deep(ol),
.markdown-body :deep(blockquote),
.markdown-body :deep(table),
.markdown-body :deep(pre) {
  margin: 1em 0;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 1.4em;
}

.markdown-body :deep(li + li) {
  margin-top: 0.4em;
}

.markdown-body :deep(a) {
  color: var(--app-blue);
  text-decoration: none;
}

.markdown-body :deep(a:hover) {
  text-decoration: underline;
}

.markdown-body :deep(code) {
  padding: 0.16em 0.42em;
  border-radius: var(--app-radius-sm);
  background: var(--accent-weak);
  color: var(--accent-hover);
  font-size: 0.92em;
  font-family: var(--font-mono);
}

.markdown-body :deep(pre) {
  padding: 22px 24px;
  line-height: 1.7;
  border-radius: var(--app-radius-lg);
  background: #25334b;
  color: #e8eaed;
  overflow-x: auto;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.06);
}

.markdown-body :deep(pre code) {
  padding: 0;
  background: transparent;
  color: inherit;
}

.markdown-body :deep(.code-block) {
  margin: 1.2em 0;
  max-width: 100%;
  border-radius: var(--app-radius-lg);
  overflow: hidden;
  background: #25334b;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.06);
}

.markdown-body :deep(.code-block__header) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.025);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.markdown-body :deep(.code-block__lang) {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #bdc1c6;
}

.markdown-body :deep(.code-block__copy) {
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 6px;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.08);
  color: #e8eaed;
  font-size: 12px;
  line-height: 1;
  cursor: pointer;
  transition:
    border-color 0.2s ease,
    background-color 0.2s ease,
    color 0.2s ease;
}

.markdown-body :deep(.code-block__copy:hover) {
  border-color: rgba(255, 255, 255, 0.35);
  background: rgba(255, 255, 255, 0.12);
  color: #ffffff;
}

.markdown-body :deep(.code-block pre) {
  margin: 0;
  padding: 18px 20px 20px;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.markdown-body :deep(.code-block .hljs) {
  display: block;
  overflow-x: auto;
  padding: 0;
  background: transparent;
}

.markdown-body :deep(blockquote) {
  padding: 10px 22px;
  border-left: 3px solid var(--brand-support);
  border-radius: 0 12px 12px 0;
  background: var(--brand-support-tint);
  color: var(--app-text-muted);
}

.markdown-body :deep(hr) {
  border: none;
  height: 1px;
  background: var(--app-border);
  margin: 2em 0;
}

.markdown-body :deep(.markdown-image-link) {
  position: relative;
  display: block;
  width: fit-content;
  max-width: 100%;
  margin: 1.7em auto;
  border-radius: 18px;
  cursor: zoom-in;
  outline: none;
}

.markdown-body :deep(.markdown-image-link::after) {
  content: "✦  查看原图";
  position: absolute;
  right: 12px;
  bottom: 12px;
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 11px;
  border: 1px solid color-mix(in srgb, var(--app-border) 72%, transparent);
  border-radius: 999px;
  background: color-mix(in srgb, var(--app-surface) 86%, transparent);
  color: var(--app-text);
  box-shadow: var(--app-shadow-sm);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  font-family: var(--font-ui);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.02em;
  opacity: 0;
  transform: translateY(5px);
  transition:
    opacity 180ms ease,
    transform 180ms ease;
  pointer-events: none;
}

.markdown-body :deep(.markdown-image-link:hover::after),
.markdown-body :deep(.markdown-image-link:focus-visible::after) {
  opacity: 1;
  transform: translateY(0);
}

.markdown-body :deep(.markdown-image-link:focus-visible) {
  box-shadow: 0 0 0 3px var(--brand-tint);
}

.markdown-body :deep(img) {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 0;
  border-radius: 18px;
  box-shadow: none;
  transition:
    transform 220ms cubic-bezier(0.2, 0.75, 0.25, 1),
    filter 220ms ease;
}

@media (hover: hover) and (pointer: fine) {
  .markdown-body :deep(.markdown-image-link:hover img) {
    transform: scale(1.006);
    filter: saturate(1.02) contrast(1.01);
  }
}

.markdown-body :deep(table) {
  width: fit-content;
  display: block;
  max-width: 100%;
  overflow-x: auto;
  border-collapse: collapse;
  border-radius: var(--app-radius-md);
  border: 1px solid var(--app-border);
}

.markdown-body :deep(thead) {
  background: var(--app-surface-sunken);
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  padding: 12px 14px;
  border-bottom: 1px solid var(--app-border);
  text-align: left;
}

.markdown-body :deep(tr:last-child td) {
  border-bottom: none;
}

.top-icon {
  background: url("../assets/svgs/top-48.svg") no-repeat center;
  background-size: 60%;
}

.message-icon {
  background: url("../assets/svgs/message-48.svg") no-repeat center;
  background-size: 60%;
}

.csdn-icon {
  background: url("../assets/svgs/csdn-48.svg") no-repeat center;
  background-size: 60%;
}

.juejin-icon {
  background: url("../assets/svgs/juejin-48.svg") no-repeat center;
  background-size: 60%;
}

.github-icon {
  background: url("../assets/svgs/github-48.svg") no-repeat center;
  background-size: 60%;
}

.gitee-icon {
  background: url("../assets/svgs/gitee-48.svg") no-repeat center;
  background-size: 60%;
}

.fab-container {
  position: fixed;
  right: 18px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 50;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.fab-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}

.fab-item {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background-color: var(--brand-tint);
  border: 1px solid var(--accent-line);
  box-shadow: var(--app-shadow-sm);
  background-size: 60% !important;
  background-position: center !important;
  background-repeat: no-repeat !important;
}

/* Article image lightbox --------------------------------------------------- */
.image-lightbox {
  position: fixed;
  inset: 0;
  z-index: 10006;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  gap: 18px;
  padding: 18px clamp(18px, 3vw, 42px) 28px;
  background:
    radial-gradient(circle at 50% 18%, color-mix(in srgb, var(--brand-tint) 72%, transparent), transparent 34%),
    color-mix(in srgb, var(--app-bg) 90%, rgba(7, 13, 24, 0.22));
  backdrop-filter: blur(18px) saturate(0.9);
  -webkit-backdrop-filter: blur(18px) saturate(0.9);
}

.image-lightbox__chrome {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  min-height: 46px;
}

.image-lightbox__meta,
.image-lightbox__actions {
  display: flex;
  align-items: center;
}

.image-lightbox__meta {
  gap: 9px;
  color: var(--app-text-muted);
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.14em;
}

.image-lightbox__signature {
  color: var(--accent);
  font-size: 15px;
}

.image-lightbox__actions {
  gap: 8px;
}

.image-lightbox__source,
.image-lightbox__close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 42px;
  border: 1px solid var(--app-border);
  background: color-mix(in srgb, var(--app-surface) 90%, transparent);
  color: var(--app-text);
  box-shadow: var(--app-shadow-sm);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.image-lightbox__source {
  gap: 7px;
  padding: 0 15px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  text-decoration: none;
}

.image-lightbox__source:hover {
  color: var(--accent);
  border-color: var(--accent-line);
}

.image-lightbox__close {
  width: 42px;
  padding: 0;
  border-radius: 50%;
  font-family: var(--font-display);
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
}

.image-lightbox__figure {
  position: relative;
  min-width: 0;
  min-height: 0;
  margin: 0;
  display: grid;
  place-items: center;
  align-content: center;
  gap: 12px;
}

.image-lightbox__image {
  display: block;
  max-width: min(94vw, 1600px);
  max-height: calc(100vh - 126px);
  width: auto;
  height: auto;
  object-fit: contain;
  border-radius: clamp(12px, 1.5vw, 20px);
  box-shadow: 0 28px 90px rgba(28, 43, 68, 0.16);
  opacity: 1;
  transform: scale(1);
  transition:
    opacity 180ms ease,
    transform 260ms cubic-bezier(0.2, 0.75, 0.25, 1);
}

.image-lightbox__figure.is-loading .image-lightbox__image {
  opacity: 0;
  transform: scale(0.985);
}

.image-lightbox__loading,
.image-lightbox__error {
  position: absolute;
  inset: 50% auto auto 50%;
  transform: translate(-50%, -50%);
  display: grid;
  justify-items: center;
  gap: 8px;
  color: var(--app-text-muted);
  text-align: center;
}

.image-lightbox__loading {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.08em;
}

.image-lightbox__loading-mark {
  color: var(--accent);
  font-size: 25px;
  animation: lightboxPulse 1.1s ease-in-out infinite alternate;
}

.image-lightbox__error {
  width: min(320px, 80vw);
  padding: 24px;
  border: 1px solid var(--app-border);
  border-radius: 20px;
  background: var(--app-surface);
  box-shadow: var(--app-shadow-md);
}

.image-lightbox__error strong {
  color: var(--app-text);
  font-size: 15px;
}

.image-lightbox__error span:last-child {
  font-size: 12px;
  line-height: 1.65;
}

.image-lightbox__error-mark {
  color: var(--accent);
  font-size: 22px;
}

.image-lightbox__caption {
  max-width: min(720px, 86vw);
  color: var(--app-text-muted);
  font-size: 12px;
  line-height: 1.5;
  text-align: center;
}

.image-lightbox-enter-active,
.image-lightbox-leave-active {
  transition: opacity 180ms ease;
}

.image-lightbox-enter-active .image-lightbox__figure,
.image-lightbox-leave-active .image-lightbox__figure {
  transition:
    transform 240ms cubic-bezier(0.2, 0.75, 0.25, 1),
    opacity 180ms ease;
}

.image-lightbox-enter-from,
.image-lightbox-leave-to {
  opacity: 0;
}

.image-lightbox-enter-from .image-lightbox__figure {
  opacity: 0;
  transform: scale(0.975);
}

.image-lightbox-leave-to .image-lightbox__figure {
  opacity: 0;
  transform: scale(0.99);
}

@keyframes lightboxPulse {
  from {
    opacity: 0.42;
    transform: scale(0.92) rotate(0deg);
  }
  to {
    opacity: 1;
    transform: scale(1.08) rotate(12deg);
  }
}

/* 响应式设计 */
@media (max-width: 1200px) {
}

@media (max-width: 992px) {
}

@media (max-width: 768px) {
  .fab-container {
    top: auto;
    bottom: 16px;
    right: 16px;
    max-width: calc(100% - 32px);
    transform: none;
  }

  .fab-actions {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 8px;
  }

  .article-layout {
    padding-top: 88px;
    padding-left: 14px;
    padding-right: 14px;
    gap: 16px;
    max-width: 100%;
  }

  .sidebar-sticky {
    position: static;
    height: auto;
  }

  .sidebar {
    width: 100%;
    padding: 0 0 12px;
    border-right: none;
    border-bottom: 1px solid var(--app-border);
  }

  .article-title {
    font-size: 30px;
  }

  .article-header,
  .article-content,
  .next-previous-article,
  .comments-content {
    padding-left: 0;
    padding-right: 0;
    max-width: none;
  }

  .article-shell {
    padding-left: 0;
  }

  .markdown-body :deep(pre) {
    padding: 16px 16px 18px;
    border-radius: 15px;
    font-size: 13px;
    line-height: 1.7;
  }

  .markdown-body :deep(.code-block) {
    border-radius: 16px;
  }

  .markdown-body :deep(.code-block__header) {
    padding: 9px 12px;
  }

  .markdown-body :deep(.code-block__lang),
  .markdown-body :deep(.code-block__copy) {
    font-size: 11px;
  }

  .markdown-body :deep(.code-block pre) {
    padding: 14px 14px 16px;
  }

  .markdown-body :deep(.code-block .hljs) {
    font-size: 12.5px;
    line-height: 1.7;
  }
}

@media (max-width: 480px) {
  .article-layout {
    padding-left: 16px;
    padding-right: 16px;
  }

  .article-title {
    font-size: 24px;
  }

  .markdown-body :deep(code) {
    padding: 0.12em 0.34em;
    font-size: 0.84em;
  }

  .markdown-body :deep(pre) {
    padding: 14px 14px 16px;
    border-radius: 14px;
    font-size: 13px;
    line-height: 1.65;
  }

  .markdown-body :deep(.code-block) {
    margin: 1em 0;
    border-radius: 14px;
  }

  .markdown-body :deep(.code-block__header) {
    padding: 8px 10px;
    gap: 8px;
  }

  .markdown-body :deep(.code-block__lang) {
    min-width: 0;
    font-size: 11px;
    letter-spacing: 0.05em;
  }

  .markdown-body :deep(.code-block__copy) {
    flex: 0 0 auto;
    padding: 4px 8px;
    font-size: 11px;
  }

  .markdown-body :deep(.code-block pre) {
    padding: 12px 12px 14px;
  }

  .markdown-body :deep(.code-block .hljs) {
    font-size: 12px;
    line-height: 1.65;
  }
}

/* 横屏小屏幕优化 */
@media (max-width: 768px) and (orientation: landscape) {
}

@media (max-width: 640px) {
  .image-lightbox {
    gap: 10px;
    padding: 10px 10px max(16px, env(safe-area-inset-bottom));
  }

  .image-lightbox__chrome {
    min-height: 44px;
  }

  .image-lightbox__meta {
    font-size: 9px;
  }

  .image-lightbox__source {
    min-height: 40px;
    padding: 0 12px;
  }

  .image-lightbox__close {
    width: 40px;
    height: 40px;
    min-height: 40px;
  }

  .image-lightbox__image {
    max-width: calc(100vw - 20px);
    max-height: calc(100vh - 102px - env(safe-area-inset-bottom));
    border-radius: 12px;
  }

  .markdown-body :deep(.markdown-image-link::after) {
    opacity: 1;
    transform: none;
    right: 8px;
    bottom: 8px;
    min-height: 28px;
    padding: 0 9px;
    font-size: 10px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .image-lightbox__loading-mark {
    animation: none;
  }
  .image-lightbox__image,
  .image-lightbox-enter-active,
  .image-lightbox-leave-active,
  .image-lightbox-enter-active .image-lightbox__figure,
  .image-lightbox-leave-active .image-lightbox__figure {
    transition: none;
  }
}

/* ============================================================
   v4.0 · Article reading QA — prevent glyph clipping and drift
   ============================================================ */
.article-layout {
  width: min(1180px, calc(100% - 2 * var(--app-page-gutter)));
  max-width: 1180px;
  padding-left: 0;
  padding-right: 0;
  gap: clamp(34px, 4vw, 54px);
}
.content.article-shell {
  max-width: 820px;
}
.article-header,
.article-content,
.next-previous-article,
.comments-content {
  max-width: 760px;
}
.article-meta {
  gap: 7px 16px;
  font-size: 12.5px;
  line-height: 1.5;
}
.markdown-body {
  font-size: 16px;
  line-height: 1.86;
}
.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4),
.markdown-body :deep(h5),
.markdown-body :deep(h6) {
  overflow: visible;
  text-wrap: balance;
  line-height: 1.34;
  padding-bottom: 0.03em;
}
.markdown-body :deep(p),
.markdown-body :deep(li) {
  text-wrap: pretty;
}
@media (max-width: 900px) {
  .article-layout {
    width: min(100%, calc(100% - 28px));
  }
}
@media (max-width: 640px) {
  .article-layout {
    width: min(100%, calc(100% - 22px));
    gap: 22px;
  }
  .markdown-body {
    font-size: 15.5px;
  }
}

/* ============================================================
   v4.1 · Article mobile reading contract
   ============================================================ */
@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .article-layout {
    width: 100% !important;
    max-width: 100% !important;
    display: block !important;
    padding: 76px 16px 42px !important;
  }
  .sidebar {
    display: none !important;
  }
  .content.article-shell,
  .article-shell,
  .article-header,
  .article-content,
  .next-previous-article,
  .comments-content {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
  }
  .article-shell {
    padding: 0 !important;
    gap: 20px !important;
  }
  .article-meta {
    gap: 6px 12px !important;
    font-size: 11.5px !important;
  }
  .markdown-body {
    font-size: 15.5px !important;
    line-height: 1.82 !important;
    overflow-wrap: anywhere;
  }
  .markdown-body :deep(img) {
    max-width: 100% !important;
    height: auto !important;
  }
  .markdown-body :deep(table) {
    min-width: 560px;
  }
  .markdown-body :deep(.table-wrapper),
  .markdown-body :deep(table) {
    overflow-x: auto;
  }
  .markdown-body :deep(pre),
  .markdown-body :deep(.code-block) {
    max-width: 100% !important;
    overflow-x: auto !important;
  }
  .fab-container {
    right: 12px !important;
    bottom: 12px !important;
  }
  .fab-item {
    width: 42px !important;
    height: 42px !important;
  }
}
@media (max-width: 430px) {
  .article-layout {
    padding-inline: 13px !important;
  }
  .markdown-body {
    font-size: 15px !important;
  }
}

/* ============================================================
   v4.4 · Reading folio — quiet editorial rhythm, richer details
   ============================================================ */
.article-layout {
  width: min(1160px, calc(100% - 2 * var(--app-page-gutter)));
  max-width: 1160px;
  gap: clamp(38px, 4.8vw, 64px);
  padding-top: 118px;
}
.sidebar {
  width: 214px;
  flex: 0 0 214px;
  padding: 8px 22px 0 0;
}
.sidebar-sticky {
  top: 106px;
  height: calc(100vh - 118px);
}
.sidebar-article-chapter {
  max-height: calc(100vh - 142px);
}
.content.article-shell {
  width: min(100%, 860px);
  max-width: 860px;
  gap: 32px;
  padding-left: 0;
}
.article-header,
.article-content,
.next-previous-article,
.comments-content {
  max-width: 840px;
}
.article-header {
  position: relative;
  padding: 2px 0 26px;
  border-bottom: 1px solid color-mix(in srgb, var(--app-border-strong) 70%, transparent);
}
.article-header::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: -1px;
  width: 68px;
  height: 1px;
  background: color-mix(in srgb, var(--accent) 72%, var(--app-border-strong));
}
.article-kicker {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 17px;
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 9px;
  font-weight: 730;
  letter-spacing: 0.12em;
  line-height: 1.4;
  text-transform: uppercase;
}
.article-kicker i {
  color: var(--app-border-strong);
  font-style: normal;
}
.article-signature {
  display: inline-grid;
  width: 20px;
  height: 20px;
  place-items: center;
  color: var(--accent);
  font-family: var(--font-sans);
  font-size: 15px;
  line-height: 1;
}
.article-title {
  display: block;
  max-width: 780px;
  margin: 0 0 18px;
  color: var(--app-text);
  font-family: var(--font-display);
  font-size: clamp(38px, 4.4vw, 58px);
  font-weight: 650;
  letter-spacing: -0.045em;
  line-height: 1.08;
  text-wrap: balance;
}
.article-meta {
  gap: 8px 18px;
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.045em;
  line-height: 1.5;
}
.article-meta span,
.article-meta time {
  min-height: 20px;
}
.article-meta > * + *::before {
  content: "·";
  margin-right: 18px;
  color: var(--app-border-strong);
}
.article-meta-item {
  color: var(--accent);
}
.article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 15px;
}
.article-tags span {
  min-height: 26px;
  padding: 0 9px;
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--app-border);
  border-radius: 999px;
  background: color-mix(in srgb, var(--app-surface) 72%, transparent);
  color: var(--app-text-muted);
  font-size: 10px;
  font-weight: 560;
}

.article-content {
  padding: 0;
}
.markdown-body {
  max-width: 840px;
  color: var(--app-text);
  font-size: 16.5px;
  line-height: 1.92;
  counter-reset: article-section;
}
/* The API title is the stable page masthead; avoid a duplicated markdown H1. */
.markdown-body :deep(> h1:first-child) {
  display: none;
}
.markdown-body :deep(> p),
.markdown-body :deep(> ul),
.markdown-body :deep(> ol),
.markdown-body :deep(> blockquote),
.markdown-body :deep(> h2),
.markdown-body :deep(> h3),
.markdown-body :deep(> h4),
.markdown-body :deep(> h5),
.markdown-body :deep(> h6),
.markdown-body :deep(> hr) {
  max-width: 740px;
}
.markdown-body :deep(> p:first-child),
.markdown-body :deep(> h1:first-child + p) {
  color: color-mix(in srgb, var(--app-text) 84%, var(--app-text-muted));
  font-size: 18px;
  line-height: 1.9;
}
.markdown-body :deep(h2) {
  counter-increment: article-section;
  margin-top: 2.8em;
  margin-bottom: 0.85em;
  font-size: clamp(25px, 2.5vw, 31px);
  font-weight: 650;
  letter-spacing: -0.028em;
}
.markdown-body :deep(h2)::before {
  content: counter(article-section, decimal-leading-zero) " /";
  display: block;
  margin-bottom: 7px;
  color: var(--accent);
  font-family: var(--font-mono);
  font-size: 9px;
  font-weight: 720;
  letter-spacing: 0.12em;
  line-height: 1.3;
}
.markdown-body :deep(h3) {
  margin-top: 2.2em;
  font-size: 21px;
  font-weight: 640;
  letter-spacing: -0.018em;
}
.markdown-body :deep(p) {
  color: color-mix(in srgb, var(--app-text) 86%, var(--app-text-muted));
}
.markdown-body :deep(strong) {
  color: var(--app-text);
  font-weight: 680;
}
.markdown-body :deep(a) {
  color: var(--accent-hover);
  text-decoration: underline;
  text-decoration-color: color-mix(in srgb, var(--accent) 26%, transparent);
  text-decoration-thickness: 1px;
  text-underline-offset: 0.2em;
  transition:
    color 180ms ease,
    text-decoration-color 180ms ease;
}
.markdown-body :deep(a:hover) {
  color: var(--accent);
  text-decoration-color: currentColor;
}
.markdown-body :deep(blockquote) {
  position: relative;
  margin-block: 1.7em;
  padding: 18px 20px 18px 24px;
  border: 0;
  border-left: 2px solid color-mix(in srgb, var(--accent) 52%, var(--app-border-strong));
  border-radius: 0 14px 14px 0;
  background: color-mix(in srgb, var(--accent-weak) 42%, transparent);
  color: var(--app-text-muted);
}
.markdown-body :deep(blockquote p:first-child) {
  margin-top: 0;
}
.markdown-body :deep(blockquote p:last-child) {
  margin-bottom: 0;
}
.markdown-body :deep(p:has(> img:only-child)) {
  max-width: 840px;
  margin: 2.1em 0;
  padding: 7px;
  border: 1px solid color-mix(in srgb, var(--app-border-strong) 72%, transparent);
  border-radius: 23px;
  background: color-mix(in srgb, var(--app-surface) 88%, transparent);
  box-shadow:
    0 16px 40px rgba(31, 43, 63, 0.055),
    inset 0 1px 0 color-mix(in srgb, #fff 62%, transparent);
}
.markdown-body :deep(p:has(> img:only-child) > img) {
  width: 100%;
  margin: 0;
  border-radius: 17px;
}
.markdown-body :deep(.code-block),
.markdown-body :deep(> pre),
.markdown-body :deep(> table) {
  max-width: 840px;
}
.markdown-body :deep(.code-block) {
  margin: 1.8em 0;
  border-radius: 18px;
  box-shadow:
    0 14px 34px rgba(21, 31, 49, 0.11),
    inset 0 0 0 1px rgba(255, 255, 255, 0.055);
}
.markdown-body :deep(.code-block__header) {
  padding: 11px 14px;
}
.markdown-body :deep(.code-block__lang) {
  font-size: 10px;
  letter-spacing: 0.11em;
}
.markdown-body :deep(.code-block__copy) {
  border-radius: 8px;
}
.markdown-body :deep(hr) {
  margin: 2.8em 0;
  background: color-mix(in srgb, var(--app-border-strong) 68%, transparent);
}

.next-previous-article,
.comments-content {
  padding-top: 28px;
  border-top-color: color-mix(in srgb, var(--app-border-strong) 68%, transparent);
}
.next-previous-article > span,
.comments-content > span {
  margin-bottom: 18px;
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 9px;
  font-weight: 720;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

/* Signature scroll controls: same four-point language used on Home. */
.top-icon,
.message-icon {
  background-image: none;
}
.fab-container {
  right: 20px;
  gap: 8px;
}
.fab-actions {
  gap: 8px;
}
.fab-item {
  position: relative;
  width: 42px;
  height: 42px;
  padding: 0;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--app-border-strong) 76%, transparent);
  border-radius: 50%;
  background-color: color-mix(in srgb, var(--app-surface) 88%, transparent);
  box-shadow:
    0 9px 24px rgba(31, 43, 63, 0.07),
    inset 0 1px 0 color-mix(in srgb, #fff 70%, transparent);
  color: var(--app-text-muted);
  cursor: pointer;
  backdrop-filter: blur(10px);
  transition:
    transform 220ms cubic-bezier(0.16, 1, 0.3, 1),
    border-color 180ms ease,
    color 180ms ease,
    background-color 180ms ease;
}
.fab-scroll {
  display: grid;
  place-items: center;
}
.fab-emoji {
  position: absolute;
  left: 9px;
  top: 7px;
  color: var(--accent);
  font-size: 9px;
  line-height: 1;
  opacity: 0.8;
  transition: transform 220ms cubic-bezier(0.16, 1, 0.3, 1);
}
.fab-direction {
  color: var(--app-text);
  font-family: var(--font-display);
  font-size: 17px;
  font-weight: 520;
  line-height: 1;
  transition:
    transform 220ms cubic-bezier(0.16, 1, 0.3, 1),
    color 180ms ease;
}
.fab-item:hover {
  border-color: var(--accent-line);
  background-color: color-mix(in srgb, var(--app-surface) 93%, var(--accent) 2%);
  color: var(--accent);
  transform: translateY(-2px);
}
.fab-scroll:hover .fab-emoji {
  transform: rotate(18deg) scale(1.12);
}
#to-top:hover .fab-direction {
  transform: translateY(-2px);
  color: var(--accent);
}
#to-bottom:hover .fab-direction {
  transform: translateY(2px);
  color: var(--accent);
}

@media (max-width: 900px) {
  .article-layout {
    gap: 28px;
  }
  .sidebar {
    width: 190px;
    flex-basis: 190px;
    padding-right: 16px;
  }
}
@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .article-layout {
    padding-top: 82px !important;
  }
  .article-header {
    padding-bottom: 22px;
  }
  .article-kicker {
    margin-bottom: 13px;
    font-size: 8.5px;
  }
  .article-title {
    margin-bottom: 14px;
    font-size: clamp(30px, 9.4vw, 42px);
    line-height: 1.12;
  }
  .article-meta {
    gap: 6px 12px !important;
    font-size: 9.5px !important;
  }
  .article-meta > * + *::before {
    margin-right: 12px;
  }
  .article-tags {
    margin-top: 12px;
  }
  .article-tags span {
    min-height: 24px;
    font-size: 9.5px;
  }
  .markdown-body {
    font-size: 15.5px !important;
    line-height: 1.86 !important;
  }
  .markdown-body :deep(> p:first-child),
  .markdown-body :deep(> h1:first-child + p) {
    font-size: 16.5px;
    line-height: 1.82;
  }
  .markdown-body :deep(h2) {
    margin-top: 2.3em;
    font-size: 24px;
  }
  .markdown-body :deep(h3) {
    font-size: 19px;
  }
  .markdown-body :deep(p:has(> img:only-child)) {
    margin: 1.5em 0;
    padding: 5px;
    border-radius: 17px;
  }
  .markdown-body :deep(p:has(> img:only-child) > img) {
    border-radius: 13px;
  }
  .fab-container {
    right: 12px !important;
    bottom: 14px !important;
  }
  .fab-actions {
    flex-direction: column !important;
  }
  .fab-item {
    width: 42px !important;
    height: 42px !important;
  }
  .fab-brand {
    display: none !important;
  }
}

/* ============================================================
   v5.0 · Shared editorial header language
   ============================================================ */
.article-layout {
  width: min(1180px, calc(100% - 2 * var(--app-page-gutter)));
  max-width: 1180px;
  padding-top: 110px;
}
.article-topline {
  min-height: 36px;
  margin-bottom: 13px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 28px;
}
.article-topline .article-kicker {
  min-width: 0;
  margin-bottom: 0;
}
.article-handnote {
  flex: 0 0 auto;
  font-size: clamp(22px, 1.8vw, 27px);
}
.article-handnote::after {
  width: 34px;
}
.article-header {
  padding-top: 0;
}

@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .article-layout {
    padding-top: 82px !important;
  }
  .article-topline {
    min-height: 30px;
    margin-bottom: 10px;
    display: block;
  }
}

/* v5.1 · Reading hover stays subordinate to the text. */
@media (hover: hover) and (pointer: fine) {
  .markdown-body :deep(.markdown-image-link:hover img) {
    transform: scale(1.003);
    filter: saturate(1.01);
  }
  .fab-item:hover {
    transform: translateY(-1px);
  }
}
</style>
