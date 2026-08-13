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
      <div class="article-header card-surface">
        <h1 class="article-title">{{ article.meta.title }}</h1>
        <div class="article-meta">
          <span class="article-meta-item">{{ article.meta.date }}</span>
          <span>{{ article.views }} 次阅读</span>
          <span>{{ article.meta.category }}</span>
        </div>
      </div>

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

  <div class="fab-container">
    <div class="fab-actions">
      <div class="fab-item message-icon" @click="onToBottom" id="to-bottom" title="到底部"></div>
      <div class="fab-item top-icon" @click="onToTop" id="to-top" title="到顶部"></div>
      <div v-show="article.meta.csdn" class="fab-item csdn-icon" id="to-csdn" @click="onGotoLink(article.meta.csdn)" title="CSDN"></div>
      <div v-show="article.meta.juejin" class="fab-item juejin-icon" id="to-juejin" @click="onGotoLink(article.meta.juejin)" title="掘金"></div>
      <div v-show="article.meta.github" class="fab-item github-icon" id="to-github" @click="onGotoLink(article.meta.github)" title="GitHub"></div>
      <div v-show="article.meta.gitee" class="fab-item gitee-icon" id="to-gitee" @click="onGotoLink(article.meta.gitee)" title="Gitee"></div>
    </div>
  </div>

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

async function onArticleContentClick(event) {
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
  await loadArticle();
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);
});

watch(
  () => props.id,
  async (newId, oldId) => {
    if (!newId || newId === oldId) return;
    await loadArticle();
  }
);

watch(
  () => article.value.content,
  () => {
    updateRenderedContent();
  }
);
</script>

<style scoped>
@import url("../assets/views/main-container.css");

:global(body) {
  background: var(--app-bg);
  color: var(--app-text);
}

.article-layout {
  max-width: 1280px;
  padding-top: 88px;
  padding-left: 20px;
  padding-right: 20px;
  padding-bottom: 40px;
  gap: 32px;
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
  padding: 8px 30px 0 0;
  border-right: 1px solid var(--app-border);
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
  letter-spacing: -0.04em;
  display: none;
}

.article-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  color: var(--app-text-muted);
  font-size: 13px;
}

.article-meta span {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 11px;
  border-radius: 999px;
  border: 1px solid var(--app-border);
  background: var(--app-surface);
}

.article-meta-item {
  color: var(--app-text-muted);
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
  line-height: 1.25;
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
  line-height: 1.12;
  letter-spacing: -0.04em;
  margin-top: 2.1em;
  margin-bottom: 0.9em;
  scroll-margin-top: 96px;
}

.markdown-body :deep(h1) {
  font-family: var(--font-display);
  font-size: 2.4rem;
}

.markdown-body :deep(h2) {
  font-family: var(--font-display);
  font-size: 1.9rem;
  padding-bottom: 0.42em;
  border-bottom: 1px solid var(--app-border);
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
  border-radius: var(--app-radius-lg);
  background: linear-gradient(180deg, #2c2823 0%, #262220 100%);
  color: #ece4d8;
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
  background: linear-gradient(180deg, #2c2823 0%, #262220 100%);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.06);
}

.markdown-body :deep(.code-block__header) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 14px;
  background: rgba(20, 17, 15, 0.35);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.markdown-body :deep(.code-block__lang) {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #e3b496;
}

.markdown-body :deep(.code-block__copy) {
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 999px;
  padding: 5px 10px;
  background: rgba(255, 255, 255, 0.08);
  color: #ece4d8;
  font-size: 12px;
  line-height: 1;
  cursor: pointer;
  transition: border-color 0.2s ease, background-color 0.2s ease, color 0.2s ease;
}

.markdown-body :deep(.code-block__copy:hover) {
  border-color: rgba(227, 180, 150, 0.5);
  background: rgba(189, 88, 54, 0.32);
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
  padding: 16px 18px;
  border-left: 3px solid var(--accent);
  border-radius: 0 var(--app-radius-md) var(--app-radius-md) 0;
  background: var(--app-surface-sunken);
  color: var(--app-text-muted);
}

.markdown-body :deep(hr) {
  border: none;
  height: 1px;
  background: linear-gradient(90deg, rgba(150, 135, 115, 0), rgba(150, 135, 115, 0.6), rgba(150, 135, 115, 0));
  margin: 2em 0;
}

.markdown-body :deep(img) {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 1.6em auto;
  border-radius: 16px;
  box-shadow: none;
}

.markdown-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  overflow: hidden;
  border-radius: 16px;
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
  background-color: var(--app-surface);
  border: 1px solid var(--app-border);
  box-shadow: var(--app-shadow-sm);
  background-size: 60% !important;
  background-position: center !important;
  background-repeat: no-repeat !important;
}

/* 响应式设计 */
@media (max-width: 1200px) {
}

@media (max-width: 992px) {
}

@media (max-width: 768px) {
  .article-layout {
    padding-top: 78px;
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
    padding-left: 10px;
    padding-right: 10px;
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
</style>
