<template>
  <MobileDrawer v-model="isMobileMenuOpen" subtitle="项目、教程、仓库和 Live Demo">
    <p>欢迎来到「爬楼的猪 Dev」</p>
    <p>项目、教程、仓库、Live Demo ... ...</p>
  </MobileDrawer>

  <HeaderBar :route-name="'首页'" :scroll="true" @toggle-mobile-menu="onToggleMobileMenu" />

  <div class="home-page">
    <main class="home-main">
      <section class="hero-section" aria-labelledby="home-title">
        <div class="hero-copy">
          <h1 id="home-title" class="hero-title">
            <span class="hero-title__emoji" aria-hidden="true">🎉</span>
            <span class="hero-title__text">欢迎来到</span>
            <span class="hero-title__pill">爬楼的猪 <strong>Dev</strong></span>
          </h1>
          <p class="hero-subtitle">项目教程 &amp; Live Demo</p>
          <p class="hero-description">分享和记录一些我个人在做的，感兴趣的工具和内容 😁</p>

          <div class="hero-actions">
            <a class="button-primary hero-button" href="/articles">查看项目教程</a>
            <a
              class="button-ghost hero-button"
              href="/livedemo"
              data-analytics-cta="live_demo"
              data-analytics-source="home.hero"
              data-analytics-label="查看 Demo / GitHub"
            >
              查看 Demo / GitHub
            </a>
          </div>
        </div>
      </section>

      <section id="live-demo" class="demo-lab-section" aria-labelledby="demo-lab-title">
        <div class="section-heading section-heading--lab">
          <div>
            <p class="section-kicker">Live Demo</p>
            <h2 id="demo-lab-title">在线体验</h2>
          </div>
          <div class="section-heading-side">
            <a class="section-link" href="/livedemo">全部 Demo<span class="link-arrow" aria-hidden="true"></span></a>
          </div>
        </div>

        <div class="demo-workbench" aria-label="Demo workspace">
          <div class="ide-titlebar">
            <span class="ide-dot ide-dot--red"></span>
            <span class="ide-dot ide-dot--yellow"></span>
            <span class="ide-dot ide-dot--green"></span>
            <span>{{ selectedDemo.url }}</span>
          </div>

          <div class="ide-body">
            <aside class="demo-rail" aria-label="Demo 文件列表">
              <button
                v-for="(demo, index) in demos"
                :key="demo.folder"
                type="button"
                :class="['demo-tab', { 'demo-tab--active': index === activeDemoIndex }]"
                @click="setActiveDemo(index)"
              >
                <span class="demo-tab__number">{{ formatNumber(index + 1) }}</span>
                <span class="demo-tab__copy">
                  <strong>{{ demo.title }}</strong>
                  <span>demos/{{ demo.folder }}/preview.html</span>
                </span>
                <span class="demo-tab__status demo-tab__status--done">online</span>
              </button>
            </aside>

            <div class="lab-stage">
              <div class="ide-tabs" role="tablist" aria-label="Demo 文件">
                <button
                  :class="['ide-tab', { 'ide-tab--active': activeIdeFile === 'readme' }]"
                  type="button"
                  role="tab"
                  :aria-selected="activeIdeFile === 'readme'"
                  @click="activeIdeFile = 'readme'"
                >
                  README.md
                </button>
                <button
                  :class="['ide-tab', { 'ide-tab--active': activeIdeFile === 'preview' }]"
                  type="button"
                  role="tab"
                  :aria-selected="activeIdeFile === 'preview'"
                  @click="activeIdeFile = 'preview'"
                >
                  preview.html
                </button>
              </div>

              <div v-if="activeIdeFile === 'readme'" class="ide-canvas">
                <article class="ide-editor" aria-label="Demo README">
                  <div class="editor-path">live-demo / {{ selectedDemo.folder }} / README.md</div>
                  <pre><code><span class="editor-line"><span>01</span><b># {{ selectedDemo.title }}</b></span>
<span class="editor-line"><span>02</span><b></b></span>
<span class="editor-line"><span>03</span><b>status: online</b></span>
<span class="editor-line"><span>04</span><b>route: {{ selectedDemo.url }}</b></span>
<span class="editor-line"><span>05</span><b>source: {{ selectedDemo.sourcelink }}</b></span>
<span class="editor-line"><span>06</span><b></b></span>
<span class="editor-line"><span>07</span><b>## what to try</b></span>
<span class="editor-line"><span>08</span><b>{{ selectedDemo.description }}</b></span>
<span class="editor-line"><span>09</span><b></b></span>
<span class="editor-line"><span>10</span><b>## workspace</b></span>
<span class="editor-line"><span>11</span><b>live-demo/{{ selectedDemo.folder }}/</b></span></code></pre>
                  <div class="editor-actions">
                    <a
                      class="button-primary button-small"
                      :href="selectedDemo.url"
                      target="_blank"
                      rel="noopener noreferrer"
                      data-analytics-cta="live_demo"
                      :data-analytics-source="`home.demo_ide.${selectedDemo.folder || 'unknown'}`"
                      :data-analytics-label="selectedDemo.title || '在线体验'"
                    >
                      在线打开
                    </a>
                    <a class="button-ghost button-small" :href="selectedDemo.sourcelink" target="_blank" rel="noopener noreferrer">GitHub</a>
                  </div>
                </article>

                <a
                  class="ide-preview"
                  :href="selectedDemo.url || '/livedemo'"
                  target="_blank"
                  rel="noopener noreferrer"
                  data-analytics-cta="live_demo"
                  :data-analytics-source="`home.demo_ide.preview.${selectedDemo.folder || 'unknown'}`"
                  :data-analytics-label="selectedDemo.title || '在线体验'"
                >
                  <div class="preview-toolbar">
                    <span>{{ selectedDemo.url }}</span>
                    <strong>running</strong>
                  </div>
                  <div class="preview-frame">
                    <img
                      v-if="selectedDemo.previewgif || selectedDemo.thumbnail"
                      :src="selectedDemo.previewgif || selectedDemo.thumbnail"
                      :alt="selectedDemo.title"
                    />
                    <div v-else class="result-placeholder" aria-hidden="true">{{ selectedDemo.title?.slice(0, 2).toUpperCase() || "DE" }}</div>
                  </div>
                </a>
              </div>

              <div v-else ref="previewPanel" class="iframe-preview">
                <div class="iframe-toolbar">
                  <span>{{ selectedDemo.url }}</span>
                  <div class="iframe-actions">
                    <a :href="selectedDemo.url" target="_blank" rel="noopener noreferrer">新窗口打开</a>
                    <button type="button" aria-label="切换全屏预览" title="切换全屏预览" @click="togglePreviewFullscreen">全屏</button>
                  </div>
                </div>
                <iframe
                  v-if="selectedDemo.url?.startsWith('/')"
                  :key="selectedDemo.folder"
                  :src="selectedDemo.url"
                  :title="`${selectedDemo.title} 在线预览`"
                  loading="lazy"
                  allow="fullscreen; clipboard-read; clipboard-write"
                  allowfullscreen
                  referrerpolicy="strict-origin-when-cross-origin"
                ></iframe>
                <div v-else class="iframe-fallback">
                  <img v-if="selectedDemo.thumbnail" :src="selectedDemo.thumbnail" :alt="selectedDemo.title" />
                  <p>该项目是外部地址，无法嵌入预览。</p>
                  <a class="button-primary button-small" :href="selectedDemo.url" target="_blank" rel="noopener noreferrer">新窗口打开</a>
                </div>
              </div>

              <div class="ide-statusbar" aria-hidden="true">
                <span>{{ selectedDemo.title }}</span>
                <span>{{ selectedDemo.sourcelink }}</span>
                <span>ready</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="blog-section" aria-labelledby="blog-title">
        <div class="section-heading">
          <div>
            <p class="section-kicker">Blog</p>
            <h2 id="blog-title">文章</h2>
          </div>
          <div class="section-heading-side">
            <a class="section-link" href="/articles">全部文章<span class="link-arrow" aria-hidden="true"></span></a>
          </div>
        </div>

        <div class="featured-reading">
          <article v-for="article in hotArticles" :key="article.id" class="article-row">
            <a class="article-cover" :href="article.tutorialLink" aria-hidden="true" tabindex="-1">
              <img :src="article.cover" :alt="article.title" loading="lazy" decoding="async" />
            </a>
            <div class="article-copy">
              <div class="article-meta">
                <span>{{ article.category || article.tags?.[0] || "文章" }}</span>
                <span v-if="article.date">{{ article.date }}</span>
              </div>
              <h3>
                <a :href="article.tutorialLink">{{ article.title }}</a>
              </h3>
              <p>{{ article.description }}</p>
              <div class="article-bottom">
                <div class="tag-list">
                  <span v-for="tag in article.tags" :key="tag" class="tag-chip">{{ tag }}</span>
                </div>
                <a class="text-link" :href="article.tutorialLink">看教程<span class="link-arrow" aria-hidden="true"></span></a>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="about-panel" aria-labelledby="about-title">
        <div class="about-avatar">
          <img :src="'/api/v1/website/image/avatar/admin.jpg'" alt="爬楼的猪的头像" />
        </div>

        <div class="about-content">
          <div class="about-header">
            <div class="about-copy">
              <h2 id="about-title">关于我</h2>
              <p>平时写点项目、工具脚本、页面小实验和部署笔记</p>
            </div>
          </div>

          <div class="about-links" aria-label="我的主页">
            <a class="about-card about-card--csdn" href="https://blog.csdn.net/qq_42727752" target="_blank" rel="noopener noreferrer">
              <span class="about-card__logo about-card__logo--csdn"><img src="../assets/svgs/csdn.png" alt="CSDN" /></span>
              <span class="about-card__separator" aria-hidden="true">·</span>
              <span>技术文章</span>
            </a>
            <a class="about-card about-card--juejin" href="https://juejin.cn/user/2590907894607726" target="_blank" rel="noopener noreferrer">
              <span class="about-card__logo about-card__logo--juejin"><img src="../assets/svgs/juejin.svg" alt="掘金" /></span>
              <span class="about-card__separator" aria-hidden="true">·</span>
              <span>前端笔记</span>
            </a>
            <a class="about-card about-card--github" :href="githubLink" target="_blank" rel="noopener noreferrer">
              <span class="about-card__logo about-card__logo--github"><img src="../assets/svgs/github.svg" alt="" /><strong>GitHub</strong></span>
              <span class="about-card__separator" aria-hidden="true">·</span>
              <span>开源项目</span>
            </a>
            <a class="about-card about-card--gitee" href="https://gitee.com/pldz" target="_blank" rel="noopener noreferrer">
              <span class="about-card__logo about-card__logo--gitee"><img src="../assets/svgs/gitee.svg" alt="Gitee" /></span>
              <span class="about-card__separator" aria-hidden="true">·</span>
              <span>国内镜像</span>
            </a>
            <a class="about-card about-card--bilibili" href="https://space.bilibili.com/438387423" target="_blank" rel="noopener noreferrer">
              <span class="about-card__logo about-card__logo--bilibili"><img src="../assets/svgs/bilibili.png" alt="Bilibili" /></span>
              <span class="about-card__separator" aria-hidden="true">·</span>
              <span>视频内容</span>
            </a>
          </div>
        </div>
      </section>
    </main>

    <FooterBar />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import FooterBar from "../components/FooterBar.vue";
import HeaderBar from "../components/HeaderBar.vue";
import MobileDrawer from "../components/MobileDrawer.vue";
import { getAllLiveDemos, getAllArticles } from "../utils/apis";

const isMobileMenuOpen = ref(false);
const activeDemoIndex = ref(0);
const activeIdeFile = ref("readme");
const previewPanel = ref(null);

const hotArticles = ref([]);
const demos = ref([]);

const githubLink = "https://github.com/pldz1";

const selectedDemo = computed(() => demos.value[activeDemoIndex.value] || {});

function formatNumber(value) {
  return String(value).padStart(2, "0");
}

function setActiveDemo(index) {
  activeDemoIndex.value = index;
  activeIdeFile.value = "readme";
}

function togglePreviewFullscreen() {
  if (document.fullscreenElement) {
    document.exitFullscreen();
    return;
  }
  previewPanel.value?.requestFullscreen();
}

function normalizeTags(tags) {
  if (Array.isArray(tags)) return tags.filter(Boolean).slice(0, 4);
  if (typeof tags === "string") {
    return tags
      .split(/[,\s]+/)
      .map((item) => item.trim())
      .filter(Boolean)
      .slice(0, 4);
  }
  return [];
}

function normalizeHotArticle(article, index) {
  const articleLink = article?.id ? `/article/${article.id}` : "/articles";

  return {
    id: article?.id || `hot-article-${index}`,
    title: article?.title || "未命名文章",
    description: article?.summary || "暂无描述",
    cover: article?.thumbnail || "/404.jpg",
    tags: normalizeTags(article?.tags),
    category: article?.category || "",
    date: article?.date || "",
    tutorialLink: articleLink,
    repoLink: article?.github || article?.gitee || article?.csdn || articleLink,
  };
}

async function loadHomeData() {
  const [articles, livedemos] = await Promise.all([getAllArticles(), getAllLiveDemos()]);

  hotArticles.value = [...articles]
    .sort((a, b) => String(b.date).localeCompare(String(a.date)))
    .filter((article) => article?.id && article?.title)
    .slice(0, 3)
    .map(normalizeHotArticle);

  demos.value = livedemos.slice(0, 4);
  activeDemoIndex.value = 0;
}

function onToggleMobileMenu() {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
}

function onCloseMobileMenu() {
  isMobileMenuOpen.value = false;
}

function onResize() {
  if (window.innerWidth > 840) {
    onCloseMobileMenu();
  }
}

onMounted(() => {
  window.addEventListener("resize", onResize);
  loadHomeData();
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", onResize);
});
</script>

<style scoped>
:global(body) {
  background: radial-gradient(circle at top left, color-mix(in srgb, var(--accent) 8%, transparent), transparent 34rem),
    linear-gradient(180deg, var(--app-bg), var(--app-bg));
  color: var(--app-text);
}

.home-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}

.home-main {
  position: relative;
  z-index: 1;
  width: min(1160px, calc(100% - 40px));
  margin: 0 auto;
  padding: 76px 0 50px;
}

.hero-section {
  position: relative;
  display: flex;
  min-height: calc(100vh - 76px);
  min-height: calc(100svh - 76px);
  align-items: center;
  justify-content: center;
  padding: 24px 0 48px;
  text-align: center;
}

.hero-copy {
  display: grid;
  justify-items: center;
  width: 100%;
  max-width: 860px;
  min-width: 0;
  padding: 32px 8px;
}

.section-kicker {
  margin: 0 0 16px;
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.18em;
  line-height: 1;
  text-transform: uppercase;
}

.hero-title {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin: 0;
  color: var(--app-text);
  font-family: var(--font-sans);
  font-size: clamp(30px, 3.35vw, 44px);
  font-weight: 900;
  line-height: 1.02;
  letter-spacing: 0;
}

.hero-title__emoji {
  line-height: 1;
  transform: translateY(2px);
}

.hero-title__text,
.hero-title__pill {
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
}

.hero-title__pill {
  padding: 0.06em 0.34em 0.12em;
  border: 2px solid color-mix(in srgb, var(--app-text) 88%, transparent);
  border-radius: 13px;
  background: var(--app-surface);
  box-shadow: 4px 4px 0 color-mix(in srgb, var(--accent) 22%, transparent);
}

.hero-title__pill strong {
  margin-left: 0.18em;
  font-weight: 900;
}

.hero-subtitle {
  margin: 16px 0 0;
  color: color-mix(in srgb, var(--accent) 72%, var(--app-text));
  font-size: 17px;
  font-weight: 650;
  line-height: 1.5;
}

.hero-description {
  max-width: 580px;
  margin: 12px auto 0;
  color: var(--app-text-muted);
  font-size: 15px;
  line-height: 1.78;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
  margin-top: 20px;
}

.hero-button {
  height: 40px;
  padding: 0 16px;
}

.hero-points {
  display: grid;
  gap: 10px;
  max-width: 540px;
  margin: 18px 0 0;
  padding: 0;
  list-style: none;
}

.hero-points li {
  position: relative;
  padding-left: 22px;
  color: var(--app-text-muted);
  font-size: 15px;
  line-height: 1.75;
}

.hero-points li::before {
  content: "";
  position: absolute;
  top: 0.78em;
  left: 0;
  width: 8px;
  height: 8px;
  border: 2px solid var(--accent);
  border-radius: 999px;
  background: var(--app-surface);
}

.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 24px;
  margin-bottom: 20px;
}

.section-heading h2,
.about-copy h2 {
  margin: 0;
  color: var(--app-text);
  font-family: var(--font-display);
  font-weight: 700;
  line-height: 1.2;
}

.section-heading h2 {
  font-size: 30px;
  letter-spacing: -0.02em;
}

.section-heading-side {
  display: grid;
  justify-items: end;
  gap: 10px;
}

.section-link,
.text-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--accent);
  text-decoration: none;
  font-weight: 650;
}

.section-link {
  font-size: 14px;
}

.link-arrow {
  width: 16px;
  height: 16px;
  flex: 0 0 auto;
  background: currentColor;
  mask: url("../assets/svgs/arrow-right-16.svg") center / contain no-repeat;
  -webkit-mask: url("../assets/svgs/arrow-right-16.svg") center / contain no-repeat;
  transform: translateY(1px);
}

.demo-lab-section {
  position: relative;
  scroll-margin-top: 76px;
  margin: 0 0 48px;
  padding: 24px;
  border: 1px solid color-mix(in srgb, var(--accent) 28%, var(--app-border));
  border-radius: 18px;
  background: linear-gradient(180deg, color-mix(in srgb, var(--accent) 7%, transparent), transparent 210px),
    repeating-linear-gradient(90deg, transparent 0 31px, color-mix(in srgb, var(--app-border) 42%, transparent) 31px 32px),
    linear-gradient(180deg, color-mix(in srgb, var(--app-surface) 96%, transparent), var(--app-surface));
  box-shadow: none;
}

.demo-lab-section::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(90deg, transparent, color-mix(in srgb, var(--app-green) 18%, transparent), transparent);
  opacity: 0.24;
  transform: translateX(-72%);
  animation: labSweep 7s ease-in-out infinite;
  pointer-events: none;
}

.section-heading--lab {
  position: static;
  margin: 0 0 20px;
  padding: 0;
  background: transparent;
}

.demo-workbench {
  display: grid;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--app-text) 22%, var(--app-border));
  border-radius: 16px;
  background: #111827;
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.14);
}

.ide-titlebar {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 40px;
  padding: 0 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(248, 251, 255, 0.72);
  font-size: 12px;
}

.ide-titlebar strong {
  margin-left: 6px;
  color: #f8fbff;
  font-family: var(--font-mono);
  font-size: 12px;
}

.ide-titlebar > span:last-child {
  margin-left: auto;
  overflow: hidden;
  color: rgba(248, 251, 255, 0.52);
  font-family: var(--font-mono);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ide-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
}

.ide-dot--red {
  background: #ff6b6b;
}

.ide-dot--yellow {
  background: #ffd166;
}

.ide-dot--green {
  background: #63d297;
}

.ide-body {
  display: grid;
  grid-template-columns: minmax(230px, 0.27fr) minmax(0, 1fr);
  height: clamp(470px, 39vw, 510px);
  min-height: 0;
}

.demo-rail {
  display: grid;
  align-content: start;
  gap: 6px;
  min-width: 0;
  min-height: 0;
  padding: 12px 10px;
  overflow: auto;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  background: #0f1724;
}

.demo-tab {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 9px;
  width: 100%;
  min-height: 58px;
  padding: 9px;
  border: 1px solid transparent;
  border-radius: 10px;
  background: transparent;
  color: rgba(248, 251, 255, 0.82);
  text-align: left;
  cursor: pointer;
  box-shadow: none;
}

.demo-tab:hover,
.demo-tab--active {
  border-color: rgba(112, 232, 255, 0.2);
  background: rgba(255, 255, 255, 0.07);
  box-shadow: inset 3px 0 0 #70e8ff;
  transform: none;
}

.demo-tab--active .demo-tab__number {
  animation: numberPulse 1.45s ease-in-out infinite;
}

.demo-tab__number {
  color: #63d297;
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 800;
}

.demo-tab__copy {
  display: grid;
  min-width: 0;
  gap: 6px;
}

.demo-tab__copy strong {
  overflow: hidden;
  color: #f8fbff;
  font-size: 13px;
  line-height: 1.35;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.demo-tab__copy span {
  overflow: hidden;
  color: rgba(248, 251, 255, 0.5);
  font-family: var(--font-mono);
  font-size: 11px;
  line-height: 1.45;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.demo-tab__status {
  grid-column: 2;
  justify-self: start;
  padding: 3px 7px;
  border: 1px solid rgba(99, 210, 151, 0.28);
  border-radius: 999px;
  color: #63d297;
  font-family: var(--font-mono);
  font-size: 10px;
}

.lab-stage {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  min-width: 0;
  min-height: 0;
  background: radial-gradient(circle at 78% 12%, rgba(112, 232, 255, 0.09), transparent 30%), #111827;
}

.ide-tabs {
  display: flex;
  min-width: 0;
  overflow: hidden;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.ide-tab {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 14px;
  border: 0;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  background: transparent;
  color: rgba(248, 251, 255, 0.54);
  cursor: pointer;
  font-family: var(--font-mono);
  font-size: 12px;
}

.ide-tab:hover {
  color: rgba(248, 251, 255, 0.82);
}

.ide-tab:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: -2px;
}

.ide-tab--active {
  background: rgba(255, 255, 255, 0.06);
  color: #f8fbff;
}

.ide-canvas {
  display: grid;
  grid-template-columns: minmax(0, 0.92fr) minmax(300px, 0.72fr);
  gap: 12px;
  min-height: 0;
  padding: 14px;
}

.ide-editor,
.ide-preview {
  min-height: 0;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  background: rgba(15, 23, 36, 0.72);
}

.ide-editor {
  display: grid;
  grid-template-rows: auto 1fr auto;
  min-width: 0;
  min-height: 0;
}

.editor-path,
.preview-toolbar {
  min-height: 34px;
  padding: 0 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(248, 251, 255, 0.56);
  font-family: var(--font-mono);
  font-size: 11px;
  line-height: 34px;
}

.ide-editor pre {
  margin: 0;
  padding: 14px 0;
  min-height: 0;
  overflow: auto;
}

.ide-editor code {
  display: grid;
  gap: 2px;
  font-family: var(--font-mono);
  font-size: 11px;
  line-height: 1.68;
}

.editor-line {
  display: grid;
  grid-template-columns: 36px minmax(0, 1fr);
  gap: 12px;
  padding: 0 14px;
  align-items: center;
}

.editor-line span {
  color: rgba(248, 251, 255, 0.28);
  text-align: right;
}

.editor-line b {
  overflow: hidden;
  color: #d9e7ff;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: pre-wrap;
}

.editor-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.ide-preview {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  min-width: 0;
  color: inherit;
  text-decoration: none;
}

.preview-toolbar {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  line-height: 1;
}

.preview-toolbar strong {
  color: #63d297;
  font-size: 11px;
}

.preview-frame {
  display: grid;
  min-height: 0;
  padding: 14px;
  background: linear-gradient(135deg, rgba(112, 232, 255, 0.08), transparent 40%), rgba(248, 251, 255, 0.03);
  place-items: center;
}

.preview-frame img {
  width: 100%;
  max-height: 100%;
  object-fit: contain;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 12px;
  box-shadow: 0 22px 46px rgba(0, 0, 0, 0.22);
  transition: transform 260ms var(--app-ease);
}

.ide-preview:hover .preview-frame img {
  transform: translateY(-2px) scale(1.01);
}

.iframe-preview {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  min-width: 0;
  min-height: 410px;
  margin: 14px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  background: #fff;
}

.iframe-toolbar {
  display: flex;
  min-width: 0;
  min-height: 38px;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 0 10px 0 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: #172235;
  color: rgba(248, 251, 255, 0.62);
  font-family: var(--font-mono);
  font-size: 11px;
}

.iframe-toolbar > span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.iframe-actions {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 6px;
}

.iframe-actions a,
.iframe-actions button {
  display: inline-flex;
  height: 27px;
  align-items: center;
  padding: 0 9px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 7px;
  background: rgba(255, 255, 255, 0.05);
  color: #d9e7ff;
  cursor: pointer;
  font: inherit;
  text-decoration: none;
}

.iframe-actions a:hover,
.iframe-actions button:hover {
  border-color: rgba(112, 232, 255, 0.4);
  background: rgba(112, 232, 255, 0.08);
}

.iframe-preview iframe {
  width: 100%;
  height: 100%;
  min-height: 0;
  border: 0;
  background: #fff;
}

.iframe-preview:fullscreen {
  margin: 0;
  border: 0;
  border-radius: 0;
}

.iframe-fallback {
  display: grid;
  align-content: center;
  justify-items: center;
  gap: 14px;
  padding: 24px;
  background: #111827;
  color: rgba(248, 251, 255, 0.7);
  text-align: center;
}

.iframe-fallback img {
  width: min(460px, 100%);
  max-height: 240px;
  border-radius: 12px;
  object-fit: contain;
}

.iframe-fallback p {
  margin: 0;
}

.result-placeholder {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 96px;
  height: 96px;
  border: 1px solid color-mix(in srgb, var(--app-green) 34%, var(--app-border));
  border-radius: 22px;
  background: var(--app-surface);
  color: var(--app-green);
  font-size: 20px;
  font-weight: 800;
}

.ide-statusbar {
  display: flex;
  gap: 18px;
  align-items: center;
  min-height: 30px;
  padding: 0 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: #0f1724;
  color: rgba(248, 251, 255, 0.52);
  font-family: var(--font-mono);
  font-size: 11px;
}

.ide-statusbar span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ide-statusbar span:last-child {
  margin-left: auto;
  color: #63d297;
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  color: var(--app-text-soft);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.article-copy h3 {
  margin: 0;
  color: var(--app-text);
  font-size: 19px;
  line-height: 1.35;
}

.article-copy p,
.about-copy p {
  margin: 0;
  color: var(--app-text-muted);
  line-height: 1.75;
}

.article-bottom,
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.blog-section {
  margin-bottom: 48px;
}

.featured-reading {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.article-row {
  display: grid;
  grid-template-rows: auto 1fr;
  min-width: 0;
  overflow: hidden;
  border: 1px solid var(--app-border);
  border-radius: 12px;
  background: color-mix(in srgb, var(--app-surface) 92%, transparent);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
  transition: border-color 180ms var(--app-ease), box-shadow 180ms var(--app-ease), transform 180ms var(--app-ease);
}

.article-cover {
  display: block;
  overflow: hidden;
  aspect-ratio: 16 / 9;
  border-bottom: 1px solid var(--app-border);
  background: var(--app-surface-sunken);
}

.article-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 220ms var(--app-ease);
}

.article-row:hover {
  border-color: color-mix(in srgb, var(--accent) 34%, var(--app-border));
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.1);
  transform: translateY(-2px);
}

.article-row:hover .article-cover img {
  transform: scale(1.035);
}

.article-copy {
  display: flex;
  flex-direction: column;
  min-width: 0;
  gap: 10px;
  padding: 16px;
}

.article-copy h3 a {
  color: inherit;
  text-decoration: none;
}

.article-copy h3 a:hover {
  color: var(--accent);
}

.article-copy p {
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  font-size: 14px;
}

.article-bottom {
  align-items: flex-start;
  flex-direction: column;
  justify-content: flex-end;
  margin-top: auto;
}

@keyframes labSweep {
  0%,
  42% {
    transform: translateX(-72%);
  }
  72%,
  100% {
    transform: translateX(72%);
  }
}

@keyframes numberPulse {
  0%,
  100% {
    text-shadow: 0 0 0 transparent;
  }
  50% {
    text-shadow: 0 0 12px color-mix(in srgb, var(--app-green) 72%, transparent);
  }
}

.about-panel {
  position: relative;
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr);
  gap: 14px;
  align-items: start;
  margin-top: 8px;
  padding: 14px 8px;
  border-top: 1px solid color-mix(in srgb, var(--accent) 10%, var(--app-border));
  background: radial-gradient(circle at 70% 14%, color-mix(in srgb, var(--accent) 7%, transparent), transparent 44%),
    linear-gradient(105deg, color-mix(in srgb, var(--app-surface) 78%, transparent), transparent 76%);
}

.about-avatar {
  width: 72px;
  height: 72px;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--app-border) 72%, transparent);
  border-radius: 999px;
  background: var(--app-surface);
  box-shadow: 0 12px 32px color-mix(in srgb, var(--app-text) 7%, transparent);
}

.about-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.about-content {
  display: grid;
  gap: 12px;
  min-width: 0;
}

.about-header {
  display: flex;
  align-items: start;
}

.about-copy {
  display: grid;
  gap: 3px;
}

.about-copy h2 {
  font-size: 23px;
  font-weight: 800;
  letter-spacing: -0.03em;
}

.about-copy p {
  margin: 0;
  color: var(--app-text-muted);
  font-size: 13px;
  line-height: 1.4;
}

.about-links {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
}

.about-card {
  --about-card-accent: var(--accent);
  --about-card-tint: color-mix(in srgb, var(--about-card-accent) 10%, var(--app-surface));
  display: flex;
  min-width: 0;
  height: 46px;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 0 9px;
  border: 1px solid color-mix(in srgb, var(--about-card-accent) 22%, var(--app-border));
  border-radius: 10px;
  background: color-mix(in srgb, var(--app-surface) 93%, transparent);
  color: var(--app-text-muted);
  font-size: 12px;
  text-decoration: none;
  white-space: nowrap;
  transition: border-color 180ms var(--app-ease), box-shadow 180ms var(--app-ease), transform 180ms var(--app-ease);
}

.about-card:hover {
  border-color: color-mix(in srgb, var(--about-card-accent) 48%, var(--app-border));
  box-shadow: 0 10px 24px color-mix(in srgb, var(--about-card-accent) 9%, transparent);
  transform: translateY(-2px);
}

.about-card--csdn {
  --about-card-accent: #f35b3f;
}

.about-card--juejin {
  --about-card-accent: #1e80ff;
}

.about-card--github {
  --about-card-accent: #57606a;
}

.about-card--gitee {
  --about-card-accent: #c71d23;
}

.about-card--bilibili {
  --about-card-accent: #00aeec;
}

.about-card__logo {
  display: flex;
  width: 64px;
  height: 30px;
  flex: 0 0 64px;
  align-items: center;
  justify-content: center;
}

.about-card__logo img {
  display: block;
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.about-card__logo--csdn {
  width: 58px;
  flex-basis: 58px;
}

.about-card__logo--juejin {
  width: 66px;
  flex-basis: 66px;
}

.about-card__logo--gitee {
  width: 62px;
  flex-basis: 62px;
}

.about-card__logo--bilibili {
  width: 56px;
  flex-basis: 56px;
}

.about-card__logo--github {
  gap: 5px;
}

.about-card__logo--github img {
  width: 22px;
  height: 22px;
}

.about-card__logo--github strong {
  color: var(--app-text);
  font-size: 13px;
  font-weight: 750;
}

.about-card__separator {
  color: var(--app-text-soft);
}

@media (max-width: 1080px) {
  .section-heading--lab {
    position: static;
  }

  .ide-body,
  .ide-canvas {
    grid-template-columns: 1fr;
  }

  .ide-body {
    height: auto;
    min-height: 0;
  }

  .demo-rail {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    max-height: 260px;
    border-right: 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .featured-reading {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .about-links {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 840px) {
  .home-main {
    width: min(100%, calc(100% - 24px));
    padding-top: 78px;
  }

  .section-heading {
    flex-direction: row;
  }

  .section-heading-side {
    justify-items: start;
  }

  .demo-lab-section {
    padding: 22px;
  }

  .demo-rail {
    grid-template-columns: 1fr;
  }

  .article-row {
    grid-template-columns: 1fr;
  }

  .featured-reading {
    grid-template-columns: 1fr;
    padding: 8px 16px;
  }

  .article-cover {
    max-width: none;
  }

  .ide-canvas {
    gap: 12px;
    padding: 12px;
  }

  .ide-editor {
    height: 360px;
  }

  .ide-preview {
    height: 320px;
  }

  .iframe-preview {
    height: 360px;
    min-height: 0;
    margin: 12px;
  }

  .ide-tabs {
    overflow-x: auto;
  }

  .ide-statusbar {
    flex-wrap: wrap;
    gap: 8px 14px;
    padding: 8px 12px;
  }

  .about-panel {
    grid-template-columns: 64px minmax(0, 1fr);
    gap: 14px;
    align-items: start;
  }

  .about-avatar {
    width: 64px;
    height: 64px;
  }

  .about-copy h2 {
    font-size: 22px;
  }
}

@media (max-width: 640px) {
  .home-main {
    width: min(100%, calc(100% - 16px));
    padding-bottom: 40px;
  }

  .hero-section {
    gap: 34px;
    padding-top: 4px;
    padding-bottom: 48px;
  }

  .hero-title {
    font-size: 34px;
  }

  .hero-title__pill {
    border-radius: 12px;
    box-shadow: 4px 4px 0 color-mix(in srgb, var(--accent) 24%, transparent);
  }

  .hero-subtitle,
  .hero-description {
    font-size: 16px;
  }

  .demo-lab-section {
    border-radius: 16px;
  }

  .about-panel {
    display: block;
    padding: 12px 4px;
  }

  .about-avatar {
    position: absolute;
    top: 12px;
    left: 4px;
    width: 52px;
    height: 52px;
  }

  .about-content {
    gap: 12px;
  }

  .about-header {
    min-height: 52px;
    padding-left: 64px;
  }

  .about-copy {
    min-width: 0;
  }

  .about-copy h2 {
    font-size: 21px;
  }

  .about-copy p {
    overflow: hidden;
    font-size: 13px;
    line-height: 1.45;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .about-links {
    grid-template-columns: repeat(6, minmax(0, 1fr));
    gap: 9px;
  }

  .about-card {
    grid-column: span 2;
    height: 42px;
    justify-content: center;
    padding: 0 8px;
  }

  .about-card:nth-child(4),
  .about-card:nth-child(5) {
    grid-column: span 3;
  }

  .about-card__separator,
  .about-card__separator + span {
    display: none;
  }

  .about-card__logo {
    height: 27px;
  }
}
</style>
