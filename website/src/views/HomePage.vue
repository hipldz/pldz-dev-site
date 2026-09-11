<template>
  <MobileDrawer v-model="isMobileMenuOpen" subtitle="项目、教程、仓库和 Live Demo">
    <p>欢迎来到「Hi 爬楼的猪」</p>
    <p>项目、教程、仓库、Live Demo ... ...</p>
  </MobileDrawer>

  <HeaderBar :route-name="'首页'" :scroll="true" @toggle-mobile-menu="onToggleMobileMenu" />

  <div class="home-page">
    <main class="home-main">
      <section id="hero" class="hero-section" aria-labelledby="home-title">
        <div class="hero-aurora hero-aurora--a" data-motion-layer="0.42" aria-hidden="true"></div>
        <div class="hero-aurora hero-aurora--b" data-motion-layer="-0.36" aria-hidden="true"></div>
        <div class="hero-grid" aria-hidden="true"></div>

        <div class="hero-layout">
          <div class="hero-copy" data-motion-layer="0.16">
            <p class="hero-eyebrow"><span class="hero-spark" aria-hidden="true"></span>PLDZ · DEVELOPER LAB</p>
            <h1 id="home-title" class="hero-title">
              Hi 爬楼的猪<br />
              <span class="hero-title__gradient">Exploring what's possible with AI.</span>
            </h1>
            <p class="hero-description">
              <span class="hero-description__desktop">项目、教程、工具与 Live Demo.</span>
              <span class="hero-description__mobile">项目、教程与技术笔记。</span>
            </p>
            <div class="hero-actions">
              <a v-magnetic="10" class="button-primary hero-button hero-button--primary" href="/articles"
                ><span>浏览项目教程</span><span class="material-symbols-rounded ui-icon" aria-hidden="true">arrow_forward</span></a
              >
              <a
                v-magnetic="8"
                class="button-ghost hero-button"
                href="/livedemo"
                data-analytics-cta="live_demo"
                data-analytics-source="home.hero"
                data-analytics-label="查看 Live Demo"
              >
                <span class="material-symbols-rounded ui-icon" aria-hidden="true">play_circle</span><span>查看 Live Demo</span>
              </a>
            </div>
            <div class="hero-footnote" aria-label="内容范围"><span>Projects</span><i></i><span>Tutorials</span><i></i><span>Experiments</span></div>
          </div>

          <div class="hero-stage" data-motion-layer="0.82" aria-hidden="true">
            <div class="hero-stage__halo"></div>
            <div class="hero-stage__ring hero-stage__ring--outer"></div>
            <div class="hero-stage__ring hero-stage__ring--inner"></div>
            <div class="hero-stage__core">
              <span class="hero-stage__core-spark"></span>
              <span class="material-symbols-rounded" style="font-size: 64px">auto_awesome</span>
            </div>
            <span class="hero-beam hero-beam--one" aria-hidden="true"><i></i></span>
            <span class="hero-beam hero-beam--two" aria-hidden="true"><i></i></span>

            <div class="hero-signal hero-signal--one" data-motion-layer="1.15">
              <span class="material-symbols-rounded">hub</span>
              <span><small>SHARE</small><strong>What works</strong></span>
            </div>
            <div class="hero-signal hero-signal--two" data-motion-layer="-0.9">
              <span class="material-symbols-rounded">lightbulb</span>
              <span><small>LEARN</small><strong>Stay curious</strong></span>
            </div>
            <div class="hero-signal hero-signal--three" data-motion-layer="1.35">
              <span class="material-symbols-rounded">terminal</span>
              <span><small>BUILD</small><strong>Ideas into reality</strong></span>
            </div>
          </div>
        </div>
      </section>

      <section v-reveal id="live-demo" class="demo-lab-section experiment-roadmap-section" aria-labelledby="demo-lab-title">
        <div class="section-heading section-heading--lab roadmap-heading" data-reveal-item>
          <div class="section-heading__copy">
            <p class="section-kicker">Live demo</p>
            <h2 id="demo-lab-title">在线预览</h2>
          </div>
          <div class="section-heading-side">
            <a class="section-link" href="/livedemo">全部 Demo<span class="material-symbols-rounded ui-icon" aria-hidden="true">arrow_forward</span></a>
          </div>
          <span class="section-handnote" aria-hidden="true">Build, test, learn.</span>
        </div>

        <a class="mobile-demo-teaser" href="/livedemo" aria-label="进入 Live Demo 实验室">
          <span class="mobile-demo-teaser__visual" aria-hidden="true">
            <img :src="selectedDemo.thumbnail || '/404.jpg'" alt="" loading="lazy" decoding="async" />
            <span class="mobile-demo-teaser__spark"></span>
          </span>
          <span class="mobile-demo-teaser__copy">
            <small>LIVE DEMO</small>
            <strong>实验与可运行项目</strong>
            <span>{{ demos.length || 0 }} 个项目 · 点进去再慢慢玩</span>
          </span>
          <span class="material-symbols-rounded mobile-demo-teaser__arrow" aria-hidden="true">arrow_forward</span>
        </a>

        <div data-reveal-item class="experiment-roadmap" aria-label="Live Demo 项目路线图">
          <div class="roadmap-topline">
            <div>
              <span>DISCOVERY TRAIL</span>
              <strong>{{ formatNumber(demos.length) }} experiments</strong>
            </div>
            <div class="roadmap-topline__legend" aria-hidden="true">
              <span>idea</span><i></i><span>build</span><i></i><span>ship</span><i></i><span>learn</span>
            </div>
          </div>

          <div class="roadmap-stations">
            <div class="roadmap-line" aria-hidden="true"><span :style="{ width: roadmapProgress }"></span></div>
            <button
              v-for="(demo, index) in demos"
              :key="demo.folder || demo.title || index"
              :class="['roadmap-stop', { 'is-active': index === activeDemoIndex }]"
              type="button"
              :aria-current="index === activeDemoIndex ? 'true' : undefined"
              @click="setActiveDemo(index)"
            >
              <span class="roadmap-stop__node" aria-hidden="true"
                ><i></i><em>{{ formatNumber(index + 1) }}</em></span
              >
              <span class="roadmap-stop__copy">
                <small>{{ demo.folder || "experiment" }}</small>
                <strong>{{ demo.title || "Live Demo" }}</strong>
              </span>
            </button>
          </div>

          <Transition name="roadmap-focus" mode="out-in">
            <article :key="selectedDemo.folder || activeDemoIndex" class="roadmap-focus">
              <div class="roadmap-focus__copy">
                <p class="roadmap-focus__eyebrow">NOW EXPLORING / {{ formatNumber(activeDemoIndex + 1) }}</p>
                <h3>{{ selectedDemo.title || "Live Demo" }}</h3>
                <p class="roadmap-focus__description">{{ selectedDemo.description }}</p>
                <div class="roadmap-focus__actions">
                  <a
                    class="roadmap-primary"
                    :href="selectedDemo.url || '/livedemo'"
                    target="_blank"
                    rel="noopener noreferrer"
                    data-analytics-cta="live_demo"
                    :data-analytics-source="`home.roadmap.${selectedDemo.folder || 'unknown'}`"
                    :data-analytics-label="selectedDemo.title || '在线体验'"
                  >
                    <span>打开这个 Demo</span><span class="material-symbols-rounded" aria-hidden="true">arrow_outward</span>
                  </a>
                  <a class="roadmap-secondary" href="/livedemo">浏览全部 Demo</a>
                </div>
              </div>

              <a
                v-cursor="'OPEN'"
                class="roadmap-preview"
                :href="selectedDemo.url || '/livedemo'"
                target="_blank"
                rel="noopener noreferrer"
                :aria-label="`打开 ${selectedDemo.title || 'Live Demo'}`"
              >
                <div class="roadmap-preview__topbar">
                  <span>SPECIMEN / {{ formatNumber(activeDemoIndex + 1) }}</span>
                  <span class="material-symbols-rounded" aria-hidden="true">north_east</span>
                </div>
                <div class="roadmap-preview__media">
                  <img :src="selectedDemo.thumbnail || '/404.jpg'" :alt="selectedDemo.title || 'Live Demo'" loading="lazy" decoding="async" />
                </div>
                <span class="roadmap-preview__caption">{{ selectedDemo.folder || "experiment" }}</span>
              </a>
            </article>
          </Transition>

          <div class="roadmap-footer" aria-hidden="true">
            <span>SMALL EXPERIMENTS / REAL OUTPUTS</span>
            <span>{{ formatNumber(activeDemoIndex + 1) }} — {{ formatNumber(demos.length) }}</span>
          </div>
        </div>
      </section>

      <section v-reveal id="notes" class="blog-section" aria-labelledby="blog-title">
        <div class="section-heading section-heading--notes" data-reveal-item>
          <div class="section-heading__copy">
            <p class="section-kicker">Notes</p>
            <h2 id="blog-title">最近更新</h2>
          </div>
          <div class="section-heading-side">
            <a class="section-link" href="/articles">全部文章<span class="material-symbols-rounded ui-icon" aria-hidden="true">arrow_forward</span></a>
          </div>
          <span class="section-handnote" aria-hidden="true">Read, think, write.</span>
        </div>

        <div class="notes-stack">
          <article data-reveal-item v-for="(article, index) in hotArticles" :key="article.id" class="note-row">
            <span class="note-row__number">{{ formatNumber(index + 1) }}</span>
            <div class="note-row__copy">
              <div class="note-row__meta">
                <span>{{ article.category || article.tags?.[0] || "文章" }}</span>
                <span v-if="article.date">{{ article.date }}</span>
              </div>
              <h3>
                <a :href="article.tutorialLink">{{ article.title }}</a>
              </h3>
              <p>{{ article.description }}</p>
            </div>
            <a v-cursor="'READ'" data-reveal-media class="note-row__media" :href="article.tutorialLink" :aria-label="article.title">
              <img :src="article.cover" :alt="article.title" loading="lazy" decoding="async" />
            </a>
            <a class="note-row__arrow" :href="article.tutorialLink" aria-label="阅读全文">
              <span class="material-symbols-rounded" aria-hidden="true">arrow_outward</span>
            </a>
          </article>
        </div>
      </section>

      <section v-reveal id="about" class="about-panel" aria-labelledby="about-title">
        <div class="about-profile" data-reveal-item>
          <div class="about-profile__copy">
            <h2 id="about-title">ABOUT</h2>
            <p class="about-lead">持续更新一些东西,记录自己做的事情。</p>
            <p class="about-intro">项目、工具、页面实验与部署笔记。</p>
          </div>

          <div class="about-avatar-stage" aria-hidden="true">
            <div class="about-avatar">
              <img :src="'/api/v1/website/image/avatar/admin.jpg'" alt="" loading="lazy" decoding="async" />
            </div>
            <span class="about-handnote">Build<br />Learn<br />Share</span>
          </div>
        </div>

        <div class="about-directory" data-reveal-item>
          <div class="about-directory__heading">
            <div>
              <p class="about-directory__eyebrow">Elsewhere</p>
              <h3>Find me on other platforms</h3>
              <p class="about-directory__hint">不同的平台放不同的内容，偶尔更新，也欢迎来逛逛。</p>
            </div>
          </div>

          <div class="about-links" aria-label="我的公开主页与内容">
            <a v-cursor="'VISIT'" class="about-card" href="https://blog.csdn.net/qq_42727752" target="_blank" rel="noopener noreferrer">
              <span class="about-card__icon"><img :src="csdnIcon" alt="" aria-hidden="true" /></span>
              <span class="about-card__copy"><strong>CSDN</strong><small>技术文章</small><span>记录技术思考与实践</span></span>
              <span class="material-symbols-rounded about-card__arrow" aria-hidden="true">arrow_forward</span>
            </a>

            <a v-cursor="'VISIT'" class="about-card" href="https://juejin.cn/user/2590907894607726" target="_blank" rel="noopener noreferrer">
              <span class="about-card__icon"><img :src="juejinIcon" alt="" aria-hidden="true" /></span>
              <span class="about-card__copy"><strong>掘金</strong><small>前端笔记</small><span>前端、工程化与工具</span></span>
              <span class="material-symbols-rounded about-card__arrow" aria-hidden="true">arrow_forward</span>
            </a>

            <a v-cursor="'VISIT'" class="about-card" :href="githubLink" target="_blank" rel="noopener noreferrer">
              <span class="about-card__icon"><img :src="githubIcon" alt="" aria-hidden="true" /></span>
              <span class="about-card__copy"><strong>GitHub</strong><small>开源项目</small><span>代码、项目与实验</span></span>
              <span class="material-symbols-rounded about-card__arrow" aria-hidden="true">arrow_forward</span>
            </a>

            <a v-cursor="'VISIT'" class="about-card" href="https://gitee.com/pldz" target="_blank" rel="noopener noreferrer">
              <span class="about-card__icon"><img :src="giteeIcon" alt="" aria-hidden="true" /></span>
              <span class="about-card__copy"><strong>Gitee</strong><small>国内镜像</small><span>同步开源项目与代码</span></span>
              <span class="material-symbols-rounded about-card__arrow" aria-hidden="true">arrow_forward</span>
            </a>

            <a v-cursor="'VISIT'" class="about-card" href="https://space.bilibili.com/438387423" target="_blank" rel="noopener noreferrer">
              <span class="about-card__icon"><img :src="bilibiliIcon" alt="" aria-hidden="true" /></span>
              <span class="about-card__copy"><strong>Bilibili</strong><small>视频内容</small><span>教程、演示与生活</span></span>
              <span class="material-symbols-rounded about-card__arrow" aria-hidden="true">arrow_forward</span>
            </a>
          </div>
        </div>
      </section>
    </main>

    <nav class="section-dock" aria-label="首页章节">
      <a
        v-for="item in sectionNav"
        :key="item.id"
        :class="['section-dock__item', { 'is-active': activeSection === item.id }]"
        :href="`#${item.id}`"
        :aria-label="item.label"
      >
        <span class="section-dock__label">{{ item.label }}</span>
        <span class="section-dock__mark" aria-hidden="true"></span>
      </a>
    </nav>

    <FooterBar />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import FooterBar from "../components/FooterBar.vue";
import HeaderBar from "../components/HeaderBar.vue";
import MobileDrawer from "../components/MobileDrawer.vue";
import csdnIcon from "../assets/svgs/csdn.png";
import juejinIcon from "../assets/svgs/juejin.svg";
import githubIcon from "../assets/svgs/github.svg";
import giteeIcon from "../assets/svgs/gitee.svg";
import bilibiliIcon from "../assets/svgs/bilibili.svg";
import { getAllLiveDemos, getAllArticles } from "../utils/apis";

const isMobileMenuOpen = ref(false);
const activeDemoIndex = ref(0);
const activeSection = ref("live-demo");
let sectionObserver = null;

const hotArticles = ref([]);
const demos = ref([]);

const githubLink = "https://github.com/hipldz";
const sectionNav = [
  { id: "hero", label: "Hero" },
  { id: "live-demo", label: "Live Demo" },
  { id: "notes", label: "Articles" },
  { id: "about", label: "About" },
];

const selectedDemo = computed(() => demos.value[activeDemoIndex.value] || {});

function formatNumber(value) {
  return String(value).padStart(2, "0");
}

function setActiveDemo(index) {
  if (!Number.isInteger(index) || index < 0 || index >= demos.value.length) return;
  activeDemoIndex.value = index;
}

const roadmapProgress = computed(() => {
  const total = demos.value.length;
  if (total <= 1) return "0%";
  return `${Math.min(100, Math.max(0, (activeDemoIndex.value / (total - 1)) * 100))}%`;
});

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

async function loadRecentArticles() {
  try {
    const articles = await getAllArticles();
    hotArticles.value = [...articles]
      .sort((a, b) => String(b.date).localeCompare(String(a.date)))
      .filter((article) => article?.id && article?.title)
      .slice(0, 3)
      .map(normalizeHotArticle);
  } catch (error) {
    console.warn("Failed to load recent articles", error);
    hotArticles.value = [];
  }
}

async function loadDemoPreview() {
  try {
    const livedemos = await getAllLiveDemos();
    demos.value = livedemos.slice(0, 4);
    activeDemoIndex.value = 0;
  } catch (error) {
    console.warn("Failed to load demo preview", error);
    demos.value = [];
  }
}

function loadHomeData() {
  // Mobile Home is content-first: articles should never wait for the optional
  // experiment preview request to finish.
  void loadRecentArticles();
  void loadDemoPreview();
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

  if (typeof IntersectionObserver !== "undefined") {
    sectionObserver = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) activeSection.value = entry.target.id;
        }
      },
      { rootMargin: "-24% 0px -66% 0px", threshold: 0 },
    );
    sectionNav.forEach(({ id }) => {
      const element = document.getElementById(id);
      if (element) sectionObserver.observe(element);
    });
  }
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", onResize);
  sectionObserver?.disconnect();
  sectionObserver = null;
});
</script>

<style scoped>
.home-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}

.home-main {
  position: relative;
  z-index: 1;
  width: min(var(--app-page-width), calc(100% - 2 * var(--app-page-gutter)));
  margin: 0 auto;
  padding: 104px 0 56px;
}

.hero-section {
  position: relative;
  min-height: clamp(500px, 66svh, 680px);
  margin-bottom: var(--app-section-gap);
  display: grid;
  place-items: center;
  overflow: hidden;
  border-bottom: 1px solid var(--app-border);
  isolation: isolate;
}

.hero-section::before {
  content: "";
  position: absolute;
  z-index: -2;
  width: min(760px, 78vw);
  aspect-ratio: 1.35;
  border-radius: 50%;
  background: radial-gradient(circle at 48% 48%, color-mix(in srgb, var(--accent) 13%, transparent), transparent 66%);
  opacity: 0.75;
  transform: translateY(-7%);
  pointer-events: none;
}

.hero-ambient {
  position: absolute;
  z-index: -1;
  width: 260px;
  height: 260px;
  border-radius: 50%;
  opacity: 0.09;
  pointer-events: none;
}
.hero-ambient--one {
  top: 12%;
  left: 3%;
  background: #5f7fbd;
}
.hero-ambient--two {
  right: 5%;
  bottom: 7%;
  background: #7fa6ca;
}

.hero-copy {
  width: min(860px, 100%);
  display: grid;
  justify-items: center;
  padding: 56px 24px 70px;
  text-align: center;
}

.hero-eyebrow,
.section-kicker,
.demo-overview__eyebrow {
  margin: 0;
  color: var(--app-text-soft);
  font-size: 11px;
  font-weight: 680;
  letter-spacing: 0.14em;
  line-height: 1.2;
  text-transform: uppercase;
}
.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
  color: var(--accent);
}
.hero-spark,
.lab-mark,
.placeholder-spark {
  display: inline-block;
  width: 15px;
  height: 15px;
  background: var(--brand-gradient);
  clip-path: polygon(50% 0, 62% 38%, 100% 50%, 62% 62%, 50% 100%, 38% 62%, 0 50%, 38% 38%);
}

.hero-title {
  margin: 0;
  color: var(--app-text);
  font-family: var(--font-display);
  font-size: clamp(44px, 6.1vw, 76px);
  font-weight: 610;
  letter-spacing: -0.055em;
  line-height: 1.08;
  text-wrap: balance;
}

.hero-title__gradient {
  display: inline-block;
  margin-top: 0.12em;
  background: var(--brand-gradient);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
  font-size: 58px;
  letter-spacing: 1px;
}

.hero-description {
  max-width: 660px;
  margin: 26px auto 0;
  color: var(--app-text-muted);
  font-size: clamp(16px, 1.7vw, 18px);
  line-height: 1.8;
  text-wrap: balance;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-top: 32px;
}
.hero-button {
  min-width: 144px;
  height: 46px;
  padding: 0 20px;
}

.hero-footnote {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 34px;
  color: var(--app-text-soft);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.hero-footnote i {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--app-border-strong);
}

.section-heading {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 28px;
  margin-bottom: 26px;
}
.section-heading > div:first-child {
  max-width: 720px;
}
.section-kicker {
  margin-bottom: 10px;
  color: var(--accent);
}
.section-heading h2 {
  margin: 0;
  color: var(--app-text);
  font-family: var(--font-display);
  font-weight: 610;
  letter-spacing: -0.035em;
  line-height: 1.2;
}
.section-heading h2 {
  font-size: clamp(28px, 3vw, 36px);
}
.section-description {
  max-width: 620px;
  margin: 9px 0 0;
  color: var(--app-text-muted);
  font-size: 14px;
  line-height: 1.7;
}
.section-heading-side {
  flex: 0 0 auto;
  padding-bottom: 2px;
}
.section-link,
.text-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: var(--accent);
  font-size: 13.5px;
  font-weight: 620;
  text-decoration: none;
}
.link-arrow {
  width: 15px;
  height: 15px;
  flex: 0 0 auto;
  background: currentColor;
  mask: url("../assets/svgs/arrow-right-16.svg") center / contain no-repeat;
  -webkit-mask: url("../assets/svgs/arrow-right-16.svg") center / contain no-repeat;
  transition: transform 180ms var(--app-ease);
}
@media (hover: hover) and (prefers-reduced-motion: no-preference) {
  .section-link:hover .link-arrow,
  .text-link:hover .link-arrow,
  .button-primary:hover .link-arrow {
    transform: translateX(3px);
  }
}

.demo-lab-section,
.blog-section {
  margin-bottom: var(--app-section-gap);
  scroll-margin-top: 90px;
}
.demo-workbench {
  overflow: hidden;
  border: 1px solid var(--app-border);
  border-radius: 24px;
  background: var(--app-surface);
  box-shadow: 0 18px 55px rgba(31, 36, 52, 0.065);
}
.ide-titlebar {
  min-height: 54px;
  padding: 0 18px;
  display: flex;
  align-items: center;
  gap: 9px;
  border-bottom: 1px solid var(--app-border);
  background: var(--app-surface);
  color: var(--app-text-soft);
  font-size: 12px;
}
.ide-titlebar .lab-mark {
  width: 14px;
  height: 14px;
}
.ide-titlebar strong {
  color: var(--app-text);
  font-size: 12.5px;
  font-weight: 650;
}
.ide-titlebar > span:last-child {
  min-width: 0;
  margin-left: auto;
  overflow: hidden;
  font-family: var(--font-mono);
  font-size: 10.5px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ide-body {
  display: grid;
  grid-template-columns: minmax(230px, 0.3fr) minmax(0, 1fr);
  min-height: 500px;
}
.demo-rail {
  min-width: 0;
  padding: 12px;
  display: grid;
  align-content: start;
  gap: 6px;
  border-right: 1px solid var(--app-border);
  background: var(--app-surface-sunken);
}
.demo-tab {
  width: 100%;
  min-height: 76px;
  padding: 11px 12px;
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr) auto;
  align-items: start;
  gap: 8px;
  border: 1px solid transparent;
  border-radius: 14px;
  background: transparent;
  color: var(--app-text-muted);
  text-align: left;
  cursor: pointer;
}
.demo-tab:hover {
  background: color-mix(in srgb, var(--app-surface) 74%, transparent);
}
.demo-tab--active {
  border-color: var(--app-border);
  background: var(--app-surface);
  box-shadow: var(--app-shadow-sm);
}
.demo-tab__number {
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 10.5px;
  line-height: 1.7;
}
.demo-tab--active .demo-tab__number {
  color: var(--accent);
}
.demo-tab__copy {
  min-width: 0;
  display: grid;
  gap: 5px;
}
.demo-tab__copy strong {
  overflow: hidden;
  color: var(--app-text);
  font-size: 13px;
  font-weight: 620;
  line-height: 1.4;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.demo-tab__copy span {
  overflow: hidden;
  color: var(--app-text-soft);
  font-size: 11px;
  line-height: 1.45;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.demo-tab__status {
  margin-top: 1px;
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 3px 7px;
  border-radius: 999px;
  background: var(--accent-weak);
  color: var(--accent);
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.demo-tab__status .material-symbols-rounded {
  font-size: 13px;
}

.lab-stage {
  min-width: 0;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  background: var(--app-surface);
}
.ide-tabs {
  display: flex;
  gap: 4px;
  min-height: 52px;
  align-items: center;
  padding: 0 14px;
  border-bottom: 1px solid var(--app-border);
}
.ide-tab {
  height: 34px;
  padding: 0 13px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--app-text-muted);
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
}
.ide-tab:hover {
  background: var(--app-hover-bg);
  color: var(--app-text);
}
.ide-tab--active {
  background: var(--accent-weak);
  color: var(--accent);
}

.ide-canvas {
  min-height: 0;
  padding: 18px;
  display: grid;
  grid-template-columns: minmax(0, 0.86fr) minmax(300px, 0.74fr);
  gap: 16px;
}
.demo-overview,
.ide-preview {
  min-width: 0;
  overflow: hidden;
  border: 1px solid var(--app-border);
  border-radius: 18px;
  background: var(--app-surface);
}
.demo-overview {
  padding: clamp(24px, 3vw, 36px);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 28px;
}
.demo-overview__eyebrow {
  margin-bottom: 13px;
  color: var(--app-text-soft);
}
.demo-overview h3 {
  margin: 0;
  color: var(--app-text);
  font-size: clamp(24px, 2.6vw, 34px);
  font-weight: 610;
  letter-spacing: -0.035em;
  line-height: 1.16;
}
.demo-overview__description {
  margin: 14px 0 0;
  color: var(--app-text-muted);
  font-size: 14px;
  line-height: 1.8;
}
.demo-overview__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
  color: var(--app-text-soft);
  font-size: 11px;
}
.demo-overview__meta span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 9px;
  border-radius: 999px;
  background: var(--app-surface-sunken);
}
.demo-overview__meta .material-symbols-rounded {
  font-size: 15px;
  color: var(--accent);
}
.meta-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent);
}
.editor-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
}

.ide-preview {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  color: inherit;
  text-decoration: none;
}
.preview-toolbar,
.iframe-toolbar {
  min-height: 42px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 0 13px;
  border-bottom: 1px solid var(--app-border);
  color: var(--app-text-soft);
  font-size: 10.5px;
  font-weight: 650;
}
.preview-toolbar strong {
  color: var(--accent);
  font-size: 9px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.preview-frame {
  min-height: 0;
  padding: 16px;
  display: grid;
  place-items: center;
  overflow: hidden;
  background: radial-gradient(circle at 50% 18%, color-mix(in srgb, var(--accent) 10%, transparent), transparent 46%), var(--app-surface-sunken);
}
.preview-frame img {
  width: 100%;
  max-height: 100%;
  object-fit: contain;
  border: 1px solid var(--app-border);
  border-radius: 14px;
  box-shadow: 0 14px 34px rgba(27, 33, 49, 0.09);
  transition:
    transform 240ms var(--app-ease),
    box-shadow 240ms var(--app-ease);
}
@media (hover: hover) and (prefers-reduced-motion: no-preference) {
  .ide-preview:hover .preview-frame img {
    transform: translateY(-3px) scale(1.008);
    box-shadow: 0 18px 38px rgba(27, 33, 49, 0.12);
  }
}
.result-placeholder {
  width: 104px;
  height: 104px;
  display: grid;
  place-items: center;
  border: 1px solid var(--accent-line);
  border-radius: 28px;
  background: var(--app-surface);
  box-shadow: var(--app-shadow-md);
}
.placeholder-spark {
  width: 34px;
  height: 34px;
}

.iframe-preview {
  min-width: 0;
  min-height: 410px;
  margin: 16px;
  overflow: hidden;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  border: 1px solid var(--app-border);
  border-radius: 18px;
  background: #fff;
}
.iframe-toolbar {
  background: var(--app-surface-sunken);
  font-family: var(--font-mono);
}
.iframe-toolbar > span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.iframe-actions {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 5px;
}
.iframe-actions a,
.iframe-actions button {
  height: 28px;
  padding: 0 9px;
  border: 1px solid var(--app-border);
  border-radius: 9px;
  background: var(--app-surface);
  color: var(--app-text-muted);
  cursor: pointer;
  font: inherit;
  text-decoration: none;
}
.iframe-actions a:hover,
.iframe-actions button:hover {
  border-color: var(--accent-line);
  color: var(--accent);
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
  color: var(--app-text-muted);
  text-align: center;
}
.iframe-fallback img {
  width: min(460px, 100%);
  max-height: 240px;
  border-radius: 14px;
  object-fit: contain;
}
.iframe-fallback p {
  margin: 0;
}
.ide-statusbar {
  min-height: 34px;
  padding: 0 14px;
  display: flex;
  align-items: center;
  gap: 16px;
  border-top: 1px solid var(--app-border);
  background: var(--app-surface-sunken);
  color: var(--app-text-soft);
  font-size: 10.5px;
}
.ide-statusbar span:last-child {
  margin-left: auto;
}

.featured-reading {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.article-row {
  min-width: 0;
  overflow: hidden;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  border: 1px solid var(--app-border);
  border-radius: 22px;
  background: var(--app-surface);
  box-shadow: none;
  transition:
    transform 220ms var(--app-ease),
    border-color 180ms var(--app-ease),
    box-shadow 220ms var(--app-ease);
}

.article-cover {
  position: relative;
  display: block;
  overflow: hidden;
  aspect-ratio: 16 / 9;
  border-bottom: 1px solid var(--app-border);
  background: var(--app-surface-sunken);
}

.article-cover::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 62%, rgba(12, 16, 27, 0.12));
  opacity: 0;
  transition: opacity 220ms var(--app-ease);
}

.article-cover img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
  object-position: center;
  transition: transform 340ms var(--app-ease);
}

.article-copy {
  min-width: 0;
  min-height: 214px;
  padding: 20px 21px 19px;
  display: flex;
  flex-direction: column;
  gap: 9px;
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  color: var(--app-text-soft);
  font-size: 10px;
  font-weight: 680;
  letter-spacing: 0.065em;
  text-transform: uppercase;
}

.article-copy h3 {
  margin: 0;
  color: var(--app-text);
  font-family: var(--font-display);
  font-size: clamp(16px, 1.55vw, 19px);
  font-weight: 650;
  letter-spacing: -0.025em;
  line-height: 1.42;
}

.article-row:first-child .article-copy h3 {
  font-size: clamp(17px, 1.7vw, 20px);
}

.article-copy h3 a {
  color: inherit;
  text-decoration: none;
}
.article-copy h3 a:hover {
  color: var(--accent);
}

.article-copy p {
  margin: 0;
  display: -webkit-box;
  overflow: hidden;
  color: var(--app-text-muted);
  font-size: 12.5px;
  line-height: 1.7;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.article-bottom {
  margin-top: auto;
  padding-top: 8px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.article-bottom :deep(.tag-chip) {
  height: 25px;
  padding: 0 9px;
  background: var(--app-surface-sunken);
  border: 0;
  color: var(--app-text-soft);
  font-size: 10px;
}
.article-bottom .text-link {
  margin-left: auto;
  color: var(--app-text);
  font-size: 11.5px;
}
.article-bottom .text-link:hover {
  color: var(--accent);
}
.article-bottom .ui-icon {
  font-size: 16px;
}

@media (hover: hover) and (prefers-reduced-motion: no-preference) {
  .article-row:hover {
    transform: translateY(-2px);
    border-color: var(--accent-line);
    box-shadow: 0 14px 36px rgba(31, 36, 52, 0.065);
  }
  .article-row:hover .article-cover img {
    transform: scale(1.018);
  }
  .article-row:hover .article-cover::after {
    opacity: 1;
  }
}

.about-panel {
  position: relative;
  display: grid;
  grid-template-columns: minmax(300px, 0.82fr) minmax(0, 1.18fr);
  align-items: center;
  gap: clamp(30px, 4.5vw, 58px);
  padding: 52px 0 54px;
  border-top: 1px solid var(--app-border);
  border-bottom: 1px solid var(--app-border);
}

.about-panel::before {
  content: "";
  position: absolute;
  left: 22%;
  top: 32px;
  width: 82px;
  height: 42px;
  opacity: 0.28;
  background-image: radial-gradient(circle, color-mix(in srgb, var(--accent) 34%, transparent) 1px, transparent 1.2px);
  background-size: 10px 10px;
  pointer-events: none;
}

.about-profile,
.about-directory {
  min-width: 0;
}

.about-profile {
  position: relative;
  display: grid;
  align-content: center;
  gap: 23px;
  padding: 6px 0 8px;
}

.about-profile::after {
  content: "PLDZ / BUILD · LEARN · SHARE";
  position: absolute;
  left: 0;
  bottom: -20px;
  color: color-mix(in srgb, var(--app-text-soft) 76%, transparent);
  font-size: 8.5px;
  font-weight: 700;
  letter-spacing: 0.16em;
  white-space: nowrap;
}

.about-profile__copy {
  max-width: 430px;
}

.about-profile h2 {
  margin: 3px 0 0;
  color: var(--app-text);
  font-family: var(--font-display);
  font-size: clamp(28px, 2.6vw, 36px);
  font-weight: 670;
  line-height: 1.14;
  letter-spacing: -0.045em;
}

.about-lead {
  margin: 11px 0 0;
  color: var(--app-text-muted);
  font-size: 14.5px;
  font-weight: 520;
  line-height: 1.65;
}

.about-intro {
  max-width: 430px;
  margin: 20px 0 0;
  color: var(--app-text-muted);
  font-size: 13.5px;
  line-height: 1.82;
}

.about-signature {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin-top: 20px;
}

.about-signature > span {
  min-height: 32px;
  padding: 0 11px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--app-border);
  border-radius: 999px;
  background: color-mix(in srgb, var(--app-surface) 88%, transparent);
  color: var(--app-text-muted);
  font-size: 11px;
  font-weight: 620;
}

.about-signature .material-symbols-rounded {
  color: var(--accent);
  font-size: 15px;
  font-variation-settings: "wght" 380;
}

.about-avatar-stage {
  display: flex;
  align-items: center;
  gap: 19px;
}

.about-avatar {
  width: 94px;
  height: 94px;
  flex: 0 0 94px;
  overflow: hidden;
  padding: 4px;
  border: 1px solid var(--app-border-strong);
  border-radius: 50%;
  background: var(--app-surface);
  box-shadow: 0 12px 30px rgba(34, 43, 61, 0.055);
}

.about-avatar img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
  border-radius: 50%;
}

.about-handnote {
  color: color-mix(in srgb, var(--accent) 67%, var(--app-text-soft));
  font-family: Caveat, cursive;
  font-size: 24px;
  font-weight: 550;
  line-height: 0.92;
  letter-spacing: 0.02em;
  transform: rotate(-4deg);
}

.about-directory {
  position: relative;
  overflow: visible;
  padding: 8px 0 8px clamp(24px, 3vw, 36px);
  border-left: 1px solid var(--app-border);
}

.about-directory::before {
  content: "";
  position: absolute;
  left: -1px;
  top: 9px;
  width: 2px;
  height: 54px;
  border-radius: 999px;
  background: linear-gradient(180deg, var(--accent), color-mix(in srgb, var(--accent) 10%, transparent));
}

.about-directory::after {
  content: "";
  position: absolute;
  z-index: 0;
  width: 96px;
  height: 54px;
  right: 8px;
  top: -12px;
  opacity: 0.18;
  background-image: radial-gradient(circle, color-mix(in srgb, var(--accent) 36%, transparent) 1px, transparent 1.2px);
  background-size: 11px 11px;
  pointer-events: none;
}

.about-directory__heading {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 18px;
}

.about-directory__eyebrow {
  margin: 0 0 5px;
  color: var(--accent);
  font-size: 9.5px;
  font-weight: 760;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.about-directory__heading h3 {
  margin: 0;
  color: var(--app-text);
  font-family: var(--font-display);
  font-size: clamp(21px, 2vw, 27px);
  font-weight: 660;
  letter-spacing: -0.035em;
  line-height: 1.28;
}

.about-directory__hint {
  max-width: 500px;
  margin: 6px 0 0;
  color: var(--app-text-soft);
  font-size: 11.5px;
  line-height: 1.6;
}

.about-links {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 9px;
}

.about-card {
  position: relative;
  min-width: 0;
  min-height: 78px;
  padding: 13px 14px;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) 28px;
  align-items: center;
  gap: 12px;
  border: 1px solid color-mix(in srgb, var(--app-border) 90%, transparent);
  border-radius: 16px;
  background: color-mix(in srgb, var(--app-surface) 95%, var(--app-surface-sunken));
  color: var(--app-text);
  text-decoration: none;
  transition:
    transform 190ms var(--app-ease),
    border-color 190ms var(--app-ease),
    background-color 190ms var(--app-ease),
    box-shadow 190ms var(--app-ease);
}

.about-card:nth-child(4),
.about-card:nth-child(5) {
  grid-column: auto;
}

.about-card:nth-child(5) {
  grid-column: 1 / -1;
}

.about-card__icon {
  min-width: 58px;
  width: 58px;
  height: 40px;
  padding: 6px 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border: 1px solid var(--app-border);
  border-radius: 11px;
  background: #fff;
}

.about-card__icon img {
  width: auto;
  height: auto;
  max-width: 48px;
  max-height: 23px;
  display: block;
  object-fit: contain;
}

.about-card__copy {
  min-width: 0;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: baseline;
  gap: 1px 8px;
}

.about-card__copy strong {
  overflow: hidden;
  color: var(--app-text);
  font-size: 12.75px;
  font-weight: 710;
  line-height: 1.35;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.about-card__copy small {
  min-width: 0;
  overflow: hidden;
  color: var(--app-text-muted);
  font-size: 10.5px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.about-card__copy > span {
  grid-column: 1 / -1;
  min-width: 0;
  margin-top: 4px;
  overflow: hidden;
  color: var(--app-text-soft);
  font-size: 10.25px;
  line-height: 1.45;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.about-card__arrow {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: var(--accent-weak);
  color: var(--accent);
  font-size: 15px;
  transition:
    transform 190ms var(--app-ease),
    background-color 190ms var(--app-ease);
}

@media (hover: hover) and (prefers-reduced-motion: no-preference) {
  .about-card:hover {
    transform: translateY(-2px);
    border-color: var(--accent-line);
    background: var(--app-surface);
    box-shadow: 0 10px 26px rgba(31, 40, 58, 0.05);
  }
  .about-card:hover .about-card__arrow {
    transform: translateX(2px);
    background: var(--accent-weak-hover);
  }
}

.section-dock {
  position: fixed;
  z-index: 20;
  right: max(16px, calc((100vw - var(--app-page-width)) / 2 - 64px));
  top: 50%;
  translate: 0 -50%;
  display: grid;
  gap: 8px;
}
.section-dock__item {
  min-height: 28px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 9px;
  color: var(--app-text-soft);
  text-decoration: none;
}
.section-dock__label {
  max-width: 0;
  overflow: hidden;
  opacity: 0;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  white-space: nowrap;
  transition:
    max-width 220ms var(--app-ease),
    opacity 180ms var(--app-ease),
    color 180ms var(--app-ease);
}
.section-dock__mark {
  width: 7px;
  height: 7px;
  flex: 0 0 7px;
  border-radius: 50%;
  background: var(--app-border-strong);
  transition:
    width 180ms var(--app-ease),
    height 180ms var(--app-ease),
    background-color 180ms var(--app-ease),
    transform 220ms var(--app-ease);
}
.section-dock__item:hover .section-dock__label,
.section-dock__item:focus-visible .section-dock__label,
.section-dock__item.is-active .section-dock__label {
  max-width: 72px;
  opacity: 1;
}
.section-dock__item.is-active {
  color: var(--accent);
}
.section-dock__item.is-active .section-dock__mark {
  width: 11px;
  height: 11px;
  flex-basis: 11px;
  border-radius: 0;
  background: var(--accent);
  clip-path: polygon(50% 0, 62% 38%, 100% 50%, 62% 62%, 50% 100%, 38% 62%, 0 50%, 38% 38%);
  transform: rotate(0deg);
}

/* Progressive disclosure keeps the workbench dense until a project is selected. */
.demo-tab:not(.demo-tab--active) .demo-tab__copy > span {
  display: none;
}
.demo-tab:not(.demo-tab--active) .demo-tab__status {
  opacity: 0.46;
}
.demo-tab--active .demo-tab__status {
  opacity: 1;
}

@media (hover: hover) and (pointer: fine) {
  .demo-tab:not(.demo-tab--active):hover .demo-tab__copy > span {
    display: block;
  }
  .demo-tab:not(.demo-tab--active):hover .demo-tab__status {
    opacity: 1;
  }
}

@media (max-width: 1180px) {
  .section-dock {
    display: none;
  }
}

@media (max-width: 1080px) {
  .ide-body {
    grid-template-columns: 1fr;
    min-height: 0;
  }
  .demo-rail {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    border-right: 0;
    border-bottom: 1px solid var(--app-border);
  }
  .featured-reading {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .about-panel {
    grid-template-columns: 1fr;
    gap: 30px;
  }
  .about-profile {
    grid-template-columns: minmax(0, 1fr) auto;
    align-items: end;
  }
  .about-profile::after {
    display: none;
  }
  .about-directory {
    padding: 28px 0 0;
    border-left: 0;
    border-top: 1px solid var(--app-border);
  }
  .about-directory::before {
    left: 0;
    top: -1px;
    width: 54px;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), color-mix(in srgb, var(--accent) 10%, transparent));
  }
  .about-links {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .home-main {
    padding-top: 84px;
  }
  .hero-section {
    min-height: 510px;
  }
  .hero-copy {
    padding-inline: 8px;
  }
  .ide-canvas {
    grid-template-columns: 1fr;
  }
  .ide-preview {
    min-height: 320px;
  }
  .about-panel {
    gap: 28px;
    padding: 42px 0;
  }
  .about-profile {
    grid-template-columns: 1fr;
    gap: 22px;
  }
  .about-links {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .about-card,
  .about-card:nth-child(4) {
    grid-column: auto;
  }
  .about-card:nth-child(5) {
    grid-column: 1 / -1;
  }
}

@media (max-width: 640px) {
  .home-main {
    padding: 76px 0 40px;
  }
  .hero-section {
    min-height: 470px;
    margin-bottom: 64px;
  }
  .hero-copy {
    padding: 44px 0 54px;
  }
  .hero-title {
    font-size: clamp(38px, 11vw, 54px);
  }
  .hero-description {
    padding-inline: 8px;
    font-size: 15px;
  }
  .hero-footnote {
    margin-top: 28px;
    font-size: 9.5px;
  }
  .section-heading {
    align-items: flex-end;
    gap: 14px;
  }
  .section-description {
    font-size: 13px;
  }
  .section-heading-side {
    white-space: nowrap;
  }
  .demo-workbench {
    border-radius: 20px;
  }
  .ide-titlebar {
    min-height: 50px;
    padding-inline: 14px;
  }
  .ide-titlebar strong {
    font-size: 11.5px;
  }
  .demo-rail {
    grid-template-columns: 1fr;
    padding: 9px;
  }
  .demo-tab {
    min-height: 68px;
  }
  .ide-canvas {
    padding: 10px;
    gap: 10px;
  }
  .demo-overview {
    padding: 24px 20px;
  }
  .iframe-preview {
    height: 360px;
    min-height: 0;
    margin: 10px;
  }
  .featured-reading {
    grid-template-columns: 1fr;
  }
  .article-copy {
    min-height: 0;
  }
  .about-panel {
    padding: 38px 0;
  }
  .about-avatar {
    width: 84px;
    height: 84px;
    flex-basis: 84px;
  }
  .about-handnote {
    font-size: 21px;
  }
  .about-intro {
    margin-top: 17px;
  }
  .about-signature {
    margin-top: 18px;
  }
  .about-directory {
    padding: 24px 0 0;
  }
  .about-directory__heading {
    margin-bottom: 16px;
  }
  .about-links {
    grid-template-columns: 1fr;
  }
  .about-card,
  .about-card:nth-child(4),
  .about-card:nth-child(5) {
    grid-column: auto;
    min-height: 72px;
  }
}

@media (max-width: 420px) {
  .hero-title {
    font-size: 36px;
  }
  .hero-actions {
    width: 100%;
  }
  .hero-button {
    flex: 1 1 100%;
  }
  .section-heading h2 {
    font-size: 27px;
  }
  .section-description {
    display: none;
  }
  .about-directory {
    padding-inline: 0;
  }
  .about-card {
    min-height: 68px;
    padding: 12px;
    gap: 10px;
  }
  .about-card__icon {
    width: 52px;
    min-width: 52px;
  }
  .about-card__copy > span {
    margin-top: 3px;
  }
}

/* v2.8 signature orbit: no continuous animation, it only responds to the pointer field. */
.hero-signature {
  position: absolute;
  z-index: -1;
  right: clamp(18px, 8vw, 118px);
  top: 23%;
  width: 154px;
  height: 154px;
  opacity: 0.72;
  pointer-events: none;
  transition:
    opacity 360ms var(--app-ease),
    translate 500ms cubic-bezier(0.16, 1, 0.3, 1);
}
.hero-signature__orbit {
  position: absolute;
  inset: 0;
  border: 1px solid color-mix(in srgb, var(--accent) 17%, transparent);
  border-radius: 50%;
  transform: rotate(-18deg) scale(0.98);
  transition:
    transform 700ms cubic-bezier(0.16, 1, 0.3, 1),
    border-color 320ms var(--app-ease);
}
.hero-signature__orbit::before {
  content: "";
  position: absolute;
  left: 19px;
  top: -3px;
  width: 26px;
  height: 6px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--accent) 32%, transparent);
}
.hero-signature__orbit--inner {
  inset: 31px;
  border-color: color-mix(in srgb, var(--brand-support) 15%, transparent);
  transform: rotate(34deg);
}
.hero-signature__spark {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 26px;
  height: 26px;
  background: linear-gradient(145deg, color-mix(in srgb, var(--accent) 82%, #fff), color-mix(in srgb, var(--brand-support) 68%, #fff));
  clip-path: polygon(50% 0, 62% 38%, 100% 50%, 62% 62%, 50% 100%, 38% 62%, 0 50%, 38% 38%);
  transform: translate(-50%, -50%) rotate(-10deg);
  box-shadow: 0 14px 34px color-mix(in srgb, var(--accent) 15%, transparent);
  transition: transform 520ms cubic-bezier(0.16, 1, 0.3, 1);
}
.hero-signature__dot {
  position: absolute;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--accent) 52%, transparent);
  transition: transform 600ms cubic-bezier(0.16, 1, 0.3, 1);
}
.hero-signature__dot--one {
  right: 15px;
  top: 43px;
}
.hero-signature__dot--two {
  left: 22px;
  bottom: 29px;
  width: 4px;
  height: 4px;
  opacity: 0.66;
}
.hero-section.is-field-active .hero-signature {
  opacity: 0.94;
}
.hero-section.is-field-active .hero-signature__orbit {
  transform: rotate(12deg) scale(1.025);
  border-color: color-mix(in srgb, var(--accent) 26%, transparent);
}
.hero-section.is-field-active .hero-signature__orbit--inner {
  transform: rotate(-12deg) scale(0.96);
}
.hero-section.is-field-active .hero-signature__spark {
  transform: translate(-50%, -50%) rotate(8deg) scale(1.08);
}
.hero-section.is-field-active .hero-signature__dot--one {
  transform: translate(4px, -5px);
}
.hero-section.is-field-active .hero-signature__dot--two {
  transform: translate(-4px, 5px);
}

@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .hero-signature {
    right: 3%;
    top: 18%;
    width: 118px;
    height: 118px;
    opacity: 0.38;
  }
  .hero-signature__orbit--inner {
    inset: 24px;
  }
}
@media (max-width: 640px) {
  .hero-signature {
    display: none;
  }
}

/* ============================================================
   v2.9 · Visual Signature / cinematic home composition
   ============================================================ */
.home-page::before {
  content: "";
  position: absolute;
  z-index: 0;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(90deg, transparent 0 49.93%, color-mix(in srgb, var(--app-border) 32%, transparent) 50%, transparent 50.07%) 50% 0 /
    min(1160px, calc(100% - 32px)) 100% no-repeat;
  opacity: 0.55;
}

.hero-section {
  min-height: clamp(610px, 78svh, 780px);
  place-items: stretch;
  overflow: visible;
  border-bottom-color: color-mix(in srgb, var(--app-border) 82%, transparent);
}
.hero-section::before {
  width: min(880px, 76vw);
  aspect-ratio: 1.45;
  left: 42%;
  top: 4%;
  background:
    radial-gradient(circle at 44% 48%, color-mix(in srgb, var(--accent) 14%, transparent), transparent 54%),
    radial-gradient(circle at 68% 32%, color-mix(in srgb, #8eb9d7 10%, transparent), transparent 42%);
  opacity: 0.94;
  transform: none;
}
.hero-layout {
  width: 100%;
  min-height: inherit;
  display: grid;
  grid-template-columns: minmax(0, 1.03fr) minmax(390px, 0.97fr);
  align-items: center;
  gap: clamp(34px, 5vw, 76px);
  padding: 8px 0 84px;
}
.hero-copy {
  width: auto;
  justify-items: start;
  padding: 32px 0 42px;
  text-align: left;
  animation: hero-copy-arrive 780ms cubic-bezier(0.16, 1, 0.3, 1) both;
}
.hero-eyebrow {
  margin-bottom: 25px;
}
.hero-title {
  max-width: 720px;
  font-size: clamp(48px, 5.45vw, 70px);
  line-height: 1.04;
  text-wrap: pretty;
}
.hero-title__gradient {
  background-image: linear-gradient(105deg, #415f9f 0%, #6688ba 44%, #6da0c5 72%, #415f9f 100%);
  background-size: 220% 100%;
  animation: hero-title-sheen 8s ease-in-out infinite;
}
.hero-description {
  max-width: 610px;
  margin: 27px 0 0;
  text-align: left;
}
.hero-actions {
  justify-content: flex-start;
  margin-top: 34px;
}
.hero-button {
  position: relative;
  overflow: visible;
}
.hero-button--primary::after {
  content: "";
  position: absolute;
  right: -7px;
  top: -7px;
  width: 11px;
  height: 11px;
  background: #88a9d3;
  opacity: 0;
  clip-path: polygon(50% 0, 62% 38%, 100% 50%, 62% 62%, 50% 100%, 38% 62%, 0 50%, 38% 38%);
  transform: rotate(-18deg) scale(0.4);
  transition:
    opacity 220ms ease,
    transform 360ms cubic-bezier(0.16, 1, 0.3, 1);
}
.hero-button--primary:hover::after {
  opacity: 0.9;
  transform: rotate(18deg) scale(1);
}
.hero-footnote {
  justify-content: flex-start;
}

.hero-grid {
  position: absolute;
  z-index: -3;
  right: -8%;
  top: 7%;
  width: 62%;
  height: 78%;
  opacity: 0.28;
  pointer-events: none;
  background-image:
    linear-gradient(color-mix(in srgb, var(--accent) 8%, transparent) 1px, transparent 1px),
    linear-gradient(90deg, color-mix(in srgb, var(--accent) 8%, transparent) 1px, transparent 1px);
  background-size: 34px 34px;
  -webkit-mask-image: radial-gradient(ellipse at 58% 46%, #000 0%, rgba(0, 0, 0, 0.72) 34%, transparent 72%);
  mask-image: radial-gradient(ellipse at 58% 46%, #000 0%, rgba(0, 0, 0, 0.72) 34%, transparent 72%);
}
.hero-aurora {
  position: absolute;
  z-index: -2;
  border-radius: 50%;
  pointer-events: none;
  opacity: 0.65;
  transform: translate3d(0, 0, 0);
}
.hero-aurora--a {
  right: 2%;
  top: 13%;
  width: 420px;
  height: 300px;
  background: radial-gradient(ellipse at 42% 50%, rgba(107, 145, 196, 0.15), rgba(126, 174, 205, 0.05) 48%, transparent 72%);
  animation: hero-aurora-a 12s ease-in-out infinite alternate;
}
.hero-aurora--b {
  right: 25%;
  bottom: 10%;
  width: 330px;
  height: 240px;
  background: radial-gradient(ellipse at 58% 48%, rgba(111, 164, 196, 0.11), rgba(91, 121, 175, 0.04) 50%, transparent 73%);
  animation: hero-aurora-b 15s ease-in-out infinite alternate;
}

.hero-stage {
  position: relative;
  width: min(100%, 500px);
  aspect-ratio: 1.08;
  justify-self: end;
  transform-style: preserve-3d;
  perspective: 900px;
  animation: hero-stage-arrive 900ms 100ms cubic-bezier(0.16, 1, 0.3, 1) both;
}
.hero-stage__halo {
  position: absolute;
  inset: 15% 8% 10% 12%;
  border-radius: 50%;
  background: radial-gradient(circle, color-mix(in srgb, var(--accent) 13%, transparent), color-mix(in srgb, #8db8d3 6%, transparent) 46%, transparent 70%);
  transform: rotate(-9deg);
}
.hero-stage__ring {
  position: absolute;
  left: 50%;
  top: 48%;
  width: 68%;
  aspect-ratio: 1;
  border: 1px solid color-mix(in srgb, var(--accent) 24%, transparent);
  border-radius: 50%;
  transform-style: preserve-3d;
}
.hero-stage__ring--outer {
  transform: translate(-50%, -50%) rotateX(68deg) rotateZ(-18deg);
  animation: orbit-outer 18s linear infinite;
}
.hero-stage__ring--outer::before,
.hero-stage__ring--inner::before {
  content: "";
  position: absolute;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #6d8fc0;
  box-shadow: 0 0 0 7px color-mix(in srgb, var(--accent) 8%, transparent);
}
.hero-stage__ring--outer::before {
  left: 15%;
  top: 7%;
}
.hero-stage__ring--inner {
  width: 49%;
  border-style: dashed;
  border-color: color-mix(in srgb, var(--brand-support) 23%, transparent);
  transform: translate(-50%, -50%) rotateX(70deg) rotateZ(28deg);
  animation: orbit-inner 14s linear infinite reverse;
}
.hero-stage__ring--inner::before {
  right: 8%;
  bottom: 18%;
  width: 7px;
  height: 7px;
  background: #8aabc8;
}
.hero-stage__core {
  position: absolute;
  left: 50%;
  top: 48%;
  width: 132px;
  height: 132px;
  display: grid;
  place-items: center;
  border: 1px solid rgba(255, 255, 255, 0.84);
  border-radius: 36px;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.91), rgba(236, 242, 249, 0.74));
  box-shadow:
    0 28px 75px rgba(55, 78, 115, 0.16),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
  transform: translate(-50%, -50%) rotate(-8deg);
  backdrop-filter: blur(8px);
}
.hero-stage__core::after {
  content: "";
  position: absolute;
  inset: 11px;
  border: 1px solid color-mix(in srgb, var(--accent) 12%, transparent);
  border-radius: 28px;
}
.hero-stage__core-spark {
  position: absolute;
  right: 18px;
  top: 17px;
  width: 20px;
  height: 20px;
  background: linear-gradient(145deg, #5578b3, #7da8c8);
  clip-path: polygon(50% 0, 62% 38%, 100% 50%, 62% 62%, 50% 100%, 38% 62%, 0 50%, 38% 38%);
  animation: core-spark 4.5s ease-in-out infinite;
}
.hero-stage__core-code {
  color: color-mix(in srgb, var(--accent) 78%, var(--app-text));
  font-family: var(--font-mono);
  font-size: 29px;
  font-weight: 700;
  letter-spacing: -0.08em;
}
.hero-signal {
  position: absolute;
  min-width: 188px;
  min-height: 68px;
  padding: 11px 14px;
  display: flex;
  align-items: center;
  gap: 11px;
  border: 1px solid rgba(255, 255, 255, 0.76);
  border-radius: 17px;
  background: color-mix(in srgb, var(--app-surface) 78%, transparent);
  box-shadow:
    0 16px 40px rgba(39, 55, 82, 0.09),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
}
.hero-signal > span:last-child {
  display: grid;
  gap: 2px;
}
.hero-signal small {
  color: var(--app-text-soft);
  font-size: 8px;
  font-weight: 760;
  letter-spacing: 0.12em;
}
.hero-signal strong {
  color: var(--app-text);
  font-size: 11.5px;
  font-weight: 700;
}
.hero-signal--one {
  left: 1%;
  top: 17%;
  animation: float-card-one 6s ease-in-out infinite alternate;
}
.hero-signal--two {
  right: -1%;
  top: 59%;
  animation: float-card-two 7s 1s ease-in-out infinite alternate;
}
.hero-signal--three {
  left: 4%;
  bottom: 5%;
  animation: float-card-three 8s 0.5s ease-in-out infinite alternate;
}
.hero-signal__dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #5e84bd;
  box-shadow: 0 0 0 6px rgba(94, 132, 189, 0.09);
}
.hero-signal .material-symbols-rounded {
  width: 31px;
  height: 31px;
  display: grid;
  place-items: center;
  border-radius: 10px;
  background: var(--accent-weak);
  color: var(--accent);
  font-size: 17px;
}
.hero-signal__number {
  width: 31px;
  height: 31px;
  display: grid;
  place-items: center;
  border: 1px solid var(--accent-line);
  border-radius: 10px;
  color: var(--accent);
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 800;
}

.hero-scroll-cue {
  position: absolute;
  left: 0;
  bottom: 20px;
  display: inline-flex;
  align-items: center;
  gap: 9px;
  color: var(--app-text-soft);
}
.hero-scroll-cue span {
  width: 38px;
  height: 1px;
  overflow: hidden;
  background: var(--app-border);
}
.hero-scroll-cue span::after {
  content: "";
  display: block;
  width: 40%;
  height: 100%;
  background: var(--accent);
  animation: scroll-cue 2.6s ease-in-out infinite;
}
.hero-scroll-cue small {
  font-size: 7.5px;
  font-weight: 730;
  letter-spacing: 0.16em;
}

.section-index {
  position: absolute;
  z-index: -1;
  right: 0;
  top: -28px;
  color: color-mix(in srgb, var(--accent) 9%, transparent);
  font-family: var(--font-display);
  font-size: clamp(68px, 8vw, 112px);
  font-weight: 760;
  line-height: 1;
  letter-spacing: -0.08em;
  pointer-events: none;
  user-select: none;
}
.section-heading {
  position: relative;
}

/* The Live Lab becomes a short cinematic product chapter instead of another flat block. */
.demo-lab-section {
  display: grid;
  grid-template-columns: minmax(190px, 0.28fr) minmax(0, 1fr);
  align-items: start;
  gap: clamp(24px, 3.8vw, 48px);
  padding: clamp(40px, 5vw, 66px) 0;
  border-bottom: 1px solid var(--app-border);
}
.section-heading--lab {
  position: sticky;
  top: 118px;
  align-self: start;
  min-width: 0;
  display: grid;
  align-items: start;
  justify-items: start;
  gap: 0;
  margin: 0;
  padding-top: 10px;
}
.section-heading--lab .section-heading-side {
  margin-top: 24px;
  padding: 0;
}
.section-heading--lab .section-description {
  margin-top: 13px;
}
.section-heading--lab .section-index {
  left: -4px;
  right: auto;
  top: -52px;
}
.demo-workbench {
  min-width: 0;
  border-color: color-mix(in srgb, var(--app-border-strong) 78%, transparent);
  box-shadow:
    0 28px 70px rgba(36, 50, 78, 0.09),
    inset 0 1px 0 rgba(255, 255, 255, 0.72);
}
.demo-workbench::before {
  content: "";
  position: absolute;
  z-index: 0;
  inset: 0 20% auto;
  height: 1px;
  background: linear-gradient(90deg, transparent, color-mix(in srgb, var(--accent) 52%, transparent), transparent);
  pointer-events: none;
}

.blog-section {
  position: relative;
  padding: clamp(48px, 6vw, 78px) 0;
  border-bottom: 1px solid var(--app-border);
}
.blog-section .section-heading {
  margin-bottom: 30px;
}
.article-row {
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.62);
}
.article-row .article-bottom {
  opacity: 0.68;
  transform: translateY(2px);
  transition:
    opacity 220ms ease,
    transform 260ms cubic-bezier(0.16, 1, 0.3, 1);
}
.article-row:hover .article-bottom,
.article-row:focus-within .article-bottom {
  opacity: 1;
  transform: none;
}

.about-panel {
  overflow: visible;
}
.section-index--about {
  left: -4px;
  top: -36px;
  right: auto;
}
.about-card {
  transform-style: preserve-3d;
}
.about-card__icon {
  transition: transform 360ms cubic-bezier(0.16, 1, 0.3, 1);
}
.about-card:hover .about-card__icon {
  transform: translateZ(18px) rotate(-2deg) scale(1.035);
}

/* v3.0 signal beams: two light data paths make the hero stage feel connected rather than decorative. */
.hero-beam {
  position: absolute;
  z-index: 0;
  left: 50%;
  top: 48%;
  width: 156px;
  height: 1px;
  overflow: visible;
  pointer-events: none;
  transform-origin: 0 50%;
  background: linear-gradient(90deg, color-mix(in srgb, var(--accent) 34%, transparent), color-mix(in srgb, var(--accent) 6%, transparent));
  opacity: 0.48;
}
.hero-beam::after {
  content: "";
  position: absolute;
  inset: -4px 0;
  background-image: repeating-linear-gradient(90deg, transparent 0 10px, color-mix(in srgb, var(--accent) 16%, transparent) 10px 11px);
  opacity: 0.65;
}
.hero-beam i {
  position: absolute;
  z-index: 1;
  left: 0;
  top: -2.5px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #7da0c7;
  box-shadow:
    0 0 0 4px color-mix(in srgb, var(--accent) 7%, transparent),
    0 0 10px color-mix(in srgb, var(--accent) 24%, transparent);
  animation: hero-beam-packet 3.4s ease-in-out infinite;
}
.hero-beam--one {
  transform: rotate(-146deg) translateX(7px);
  width: 148px;
}
.hero-beam--two {
  transform: rotate(23deg) translateX(8px);
  width: 142px;
}
.hero-beam--two i {
  animation-delay: 1.15s;
}
.hero-stage:hover .hero-beam {
  opacity: 0.76;
}
@keyframes hero-beam-packet {
  0%,
  8% {
    opacity: 0;
    translate: 0 0;
  }
  20% {
    opacity: 1;
  }
  74% {
    opacity: 0.9;
  }
  100% {
    opacity: 0;
    translate: 142px 0;
  }
}

@keyframes hero-copy-arrive {
  from {
    opacity: 0;
    transform: translate3d(-18px, 20px, 0);
  }
  to {
    opacity: 1;
    transform: none;
  }
}
@keyframes hero-stage-arrive {
  from {
    opacity: 0;
    transform: translate3d(22px, 26px, 0) scale(0.94);
  }
  to {
    opacity: 1;
    transform: none;
  }
}
@keyframes hero-title-sheen {
  0%,
  18%,
  100% {
    background-position: 0% 50%;
  }
  52%,
  72% {
    background-position: 100% 50%;
  }
}
@keyframes hero-aurora-a {
  to {
    transform: translate3d(-34px, 22px, 0) scale(1.08);
  }
}
@keyframes hero-aurora-b {
  to {
    transform: translate3d(26px, -18px, 0) scale(0.94);
  }
}
@keyframes orbit-outer {
  to {
    transform: translate(-50%, -50%) rotateX(68deg) rotateZ(342deg);
  }
}
@keyframes orbit-inner {
  to {
    transform: translate(-50%, -50%) rotateX(70deg) rotateZ(388deg);
  }
}
@keyframes core-spark {
  0%,
  100% {
    transform: rotate(-12deg) scale(0.9);
    opacity: 0.72;
  }
  50% {
    transform: rotate(12deg) scale(1.14);
    opacity: 1;
  }
}
@keyframes float-card-one {
  to {
    transform: translate3d(7px, -12px, 0) rotate(0.8deg);
  }
}
@keyframes float-card-two {
  to {
    transform: translate3d(-8px, 10px, 0) rotate(-0.7deg);
  }
}
@keyframes float-card-three {
  to {
    transform: translate3d(10px, -8px, 0) rotate(0.6deg);
  }
}
@keyframes scroll-cue {
  0%,
  100% {
    transform: translateX(-110%);
  }
  50% {
    transform: translateX(250%);
  }
}

@media (max-width: 1080px) {
  .hero-layout {
    grid-template-columns: minmax(0, 1fr) minmax(330px, 0.78fr);
    gap: 24px;
  }
  .hero-stage {
    width: min(100%, 420px);
  }
  .hero-signal {
    min-width: 164px;
  }
  .demo-lab-section {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  .section-heading--lab {
    position: relative;
    top: auto;
    display: flex;
    align-items: end;
    justify-content: space-between;
  }
  .section-heading--lab .section-heading-side {
    margin-top: 0;
  }
  .section-heading--lab .section-index {
    left: auto;
    right: 0;
    top: -34px;
  }
}
@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .hero-section {
    min-height: 650px;
    overflow: hidden;
  }
  .hero-layout {
    grid-template-columns: 1fr;
    padding: 42px 0 64px;
  }
  .hero-copy {
    justify-items: center;
    padding: 26px 0 4px;
    text-align: center;
  }
  .hero-description {
    margin-inline: auto;
    text-align: center;
  }
  .hero-actions,
  .hero-footnote {
    justify-content: center;
  }
  .hero-stage {
    width: min(88vw, 390px);
    justify-self: center;
    aspect-ratio: 1.35;
    margin-top: -22px;
    opacity: 0.9;
  }
  .hero-stage__core {
    width: 105px;
    height: 105px;
    border-radius: 28px;
  }
  .hero-stage__core::after {
    border-radius: 21px;
  }
  .hero-signal {
    min-width: 150px;
    min-height: 58px;
    padding: 9px 11px;
  }
  .hero-signal strong {
    font-size: 10.5px;
  }
  .hero-signal--one {
    left: 1%;
    top: 7%;
  }
  .hero-signal--two {
    right: 0;
    top: 51%;
  }
  .hero-signal--three {
    left: 7%;
    bottom: 2%;
  }
  .hero-scroll-cue {
    display: none;
  }
}
@media (max-width: 640px) {
  .hero-section {
    min-height: 600px;
    margin-bottom: 46px;
  }
  .hero-layout {
    padding-top: 28px;
    gap: 12px;
  }
  .hero-copy {
    padding-inline: 0;
  }
  .hero-title {
    font-size: clamp(38px, 11vw, 52px);
  }
  .hero-stage {
    width: min(94vw, 350px);
    margin-top: -8px;
  }
  .hero-signal {
    min-width: 138px;
    border-radius: 14px;
    backdrop-filter: none;
  }
  .hero-signal--three {
    display: none;
  }
  .hero-grid {
    width: 100%;
    right: -28%;
    opacity: 0.18;
  }
  .section-index {
    font-size: 72px;
    top: -22px;
  }
  .demo-lab-section,
  .blog-section {
    padding: 40px 0;
  }
  .section-heading--lab {
    display: block;
  }
  .section-heading--lab .section-heading-side {
    margin-top: 17px;
  }
}
@media (max-width: 420px) {
  .hero-section {
    min-height: 570px;
  }
  .hero-stage {
    transform: scale(0.92);
    transform-origin: center top;
    margin-bottom: -30px;
  }
  .hero-signal--one {
    left: 0;
  }
  .hero-signal--two {
    right: -2%;
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero-copy,
  .hero-stage,
  .hero-aurora,
  .hero-stage__ring,
  .hero-stage__core-spark,
  .hero-signal,
  .hero-scroll-cue span::after,
  .hero-title__gradient,
  .hero-beam i {
    animation: none !important;
  }
}

/* ============================================================
   v3.1 · Editorial polish — less card chrome, stronger composition
   ============================================================ */
.home-page::before {
  display: none;
}

.hero-section {
  margin-bottom: clamp(54px, 7vw, 92px);
  border-bottom: 0;
}
.hero-title__gradient {
  background: none;
  color: color-mix(in srgb, var(--accent) 86%, var(--app-text));
  -webkit-text-fill-color: currentColor;
  animation: none;
}
.hero-stage__ring {
  border-color: color-mix(in srgb, var(--accent) 18%, transparent);
}
.hero-stage__ring--inner {
  border-color: color-mix(in srgb, var(--brand-support) 16%, transparent);
}
.hero-stage__core {
  border-radius: 40px;
  background: linear-gradient(145deg, color-mix(in srgb, var(--app-surface) 94%, transparent), color-mix(in srgb, var(--brand-tint) 74%, transparent));
  box-shadow:
    0 32px 80px rgba(53, 71, 103, 0.13),
    inset 0 1px 0 rgba(255, 255, 255, 0.88);
}
.hero-signal {
  min-width: 172px;
  border-color: color-mix(in srgb, var(--app-border-strong) 46%, transparent);
  background: color-mix(in srgb, var(--app-surface) 72%, transparent);
  box-shadow:
    0 14px 34px rgba(39, 55, 82, 0.065),
    inset 0 1px 0 rgba(255, 255, 255, 0.66);
}
.hero-beam {
  opacity: 0.34;
}
.hero-grid {
  opacity: 0.19;
}

/* Section headings use a typographic rail instead of floating oversized decoration. */
.section-heading {
  position: relative;
  padding-top: 18px;
  border-top: 1px solid color-mix(in srgb, var(--app-border-strong) 58%, transparent);
}
.section-heading::before {
  content: "";
  position: absolute;
  left: 0;
  top: -1px;
  width: 62px;
  height: 2px;
  border-radius: 999px;
  background: linear-gradient(90deg, color-mix(in srgb, var(--accent) 78%, #fff), color-mix(in srgb, var(--accent) 8%, transparent));
}
.section-index {
  z-index: 0;
  right: 0;
  top: -15px;
  color: transparent;
  -webkit-text-stroke: 1px color-mix(in srgb, var(--accent) 15%, transparent);
  font-size: clamp(58px, 6.4vw, 88px);
  font-weight: 650;
  letter-spacing: -0.06em;
}
.section-heading > div,
.section-heading-side {
  position: relative;
  z-index: 1;
}

/* Live Lab: one composed product surface, not a stack of bordered boxes. */
.demo-lab-section {
  position: relative;
  grid-template-columns: minmax(190px, 0.26fr) minmax(0, 1fr);
  gap: clamp(30px, 4.8vw, 62px);
  padding: clamp(54px, 7vw, 84px) 0 clamp(66px, 8vw, 96px);
  border-bottom: 0;
}
.demo-lab-section::before {
  content: "";
  position: absolute;
  z-index: -2;
  right: -6vw;
  top: 12%;
  width: min(820px, 76vw);
  height: 72%;
  border-radius: 44% 56% 50% 50% / 52% 42% 58% 48%;
  background: radial-gradient(ellipse at 56% 42%, color-mix(in srgb, var(--accent) 5.5%, transparent), transparent 67%);
  pointer-events: none;
}
.section-heading--lab {
  top: 106px;
  padding-top: 18px;
  border-top: 1px solid color-mix(in srgb, var(--app-border-strong) 58%, transparent);
}
.section-heading--lab .section-index {
  left: auto;
  right: 0;
  top: -15px;
}
.demo-workbench {
  padding: 8px;
  border: 1px solid color-mix(in srgb, var(--app-border-strong) 62%, transparent);
  border-radius: 30px;
  background: linear-gradient(145deg, color-mix(in srgb, var(--brand-tint) 72%, var(--app-surface)), var(--app-surface));
  box-shadow:
    0 34px 86px rgba(39, 53, 80, 0.095),
    inset 0 1px 0 rgba(255, 255, 255, 0.74);
}
.demo-workbench::before {
  display: none;
}
.ide-titlebar {
  min-height: 44px;
  padding: 0 12px 0 10px;
  border-bottom: 0;
  background: transparent;
}
.ide-titlebar > span:last-child {
  opacity: 0.72;
}
.ide-body {
  min-height: 520px;
  grid-template-columns: minmax(205px, 0.27fr) minmax(0, 1fr);
  gap: 8px;
}
.demo-rail {
  padding: 8px;
  gap: 3px;
  border: 0;
  border-radius: 21px;
  background: color-mix(in srgb, var(--app-surface) 66%, transparent);
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--app-border) 70%, transparent);
}
.demo-tab {
  position: relative;
  min-height: 72px;
  border: 0;
  border-radius: 14px;
}
.demo-tab::before {
  content: "";
  position: absolute;
  left: 0;
  top: 18%;
  width: 2px;
  height: 64%;
  border-radius: 999px;
  background: var(--accent);
  opacity: 0;
  transform: scaleY(0.25);
  transition:
    opacity 180ms ease,
    transform 280ms cubic-bezier(0.16, 1, 0.3, 1);
}
.demo-tab--active {
  border-color: transparent;
  background: var(--app-surface);
  box-shadow: 0 7px 22px rgba(34, 46, 69, 0.055);
}
.demo-tab--active::before {
  opacity: 0.8;
  transform: scaleY(1);
}
.demo-tab__status {
  padding: 0;
  background: transparent;
}
.lab-stage {
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--app-border) 82%, transparent);
  border-radius: 21px;
  background: var(--app-surface);
  box-shadow: 0 10px 32px rgba(35, 48, 72, 0.045);
}
.ide-tabs {
  min-height: 48px;
  padding: 0 10px;
  background: color-mix(in srgb, var(--app-surface) 96%, var(--brand-tint));
}
.ide-tab {
  border-radius: 10px;
}
.ide-tab--active {
  background: var(--app-surface-sunken);
  color: var(--app-text);
}
.ide-canvas {
  grid-template-columns: minmax(220px, 0.58fr) minmax(360px, 1fr);
  gap: 12px;
  padding: 12px;
  background: color-mix(in srgb, var(--app-surface-sunken) 62%, var(--app-surface));
}
.demo-overview {
  padding: clamp(24px, 2.7vw, 34px);
  border: 0;
  background: transparent;
}
.demo-overview__description {
  max-width: 440px;
}
.demo-overview__meta span {
  background: color-mix(in srgb, var(--app-surface) 68%, transparent);
}
.ide-preview {
  border-color: color-mix(in srgb, var(--app-border-strong) 72%, transparent);
  border-radius: 17px;
  background: var(--app-surface);
  box-shadow: 0 16px 38px rgba(30, 43, 66, 0.075);
}
.preview-frame {
  padding: 12px;
}
.ide-statusbar {
  display: none;
}

/* Notes: images become the cards; copy becomes editorial metadata below them. */
.blog-section {
  isolation: isolate;
  padding: clamp(64px, 8vw, 100px) 0 clamp(72px, 9vw, 112px);
  border-bottom: 0;
}
.blog-section::before {
  content: "";
  position: absolute;
  z-index: -2;
  inset: 13% -8vw 6%;
  border-radius: 48px;
  background: linear-gradient(135deg, color-mix(in srgb, var(--brand-tint) 60%, transparent), transparent 46%);
  opacity: 0.72;
  pointer-events: none;
}
.blog-section .section-heading {
  margin-bottom: 34px;
}
.featured-reading {
  gap: clamp(18px, 2.2vw, 28px);
}
.article-row {
  position: relative;
  overflow: visible;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}
.article-row::before {
  position: absolute;
  z-index: 4;
  left: 14px;
  top: 13px;
  min-width: 30px;
  height: 26px;
  padding: 0 7px;
  display: inline-grid;
  place-items: center;
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.82);
  color: #566170;
  font-family: var(--font-mono);
  font-size: 8px;
  font-weight: 760;
  letter-spacing: 0.06em;
  box-shadow: 0 6px 20px rgba(23, 33, 50, 0.055);
  backdrop-filter: blur(8px);
}
.article-row:nth-child(1)::before {
  content: "01";
}
.article-row:nth-child(2)::before {
  content: "02";
}
.article-row:nth-child(3)::before {
  content: "03";
}
.article-cover {
  aspect-ratio: 16 / 10;
  border: 1px solid color-mix(in srgb, var(--app-border-strong) 66%, transparent);
  border-radius: 24px;
  box-shadow: 0 18px 46px rgba(34, 46, 69, 0.065);
  transform-origin: 50% 70%;
}
.article-copy {
  min-height: 190px;
  padding: 17px 4px 0;
  gap: 8px;
}
.article-copy h3 {
  font-size: clamp(17px, 1.55vw, 20px);
}
.article-copy p {
  -webkit-line-clamp: 2;
  color: color-mix(in srgb, var(--app-text-muted) 88%, transparent);
}
.article-bottom {
  padding-top: 7px;
}
.article-bottom :deep(.tag-chip):nth-child(n + 2) {
  display: none;
}
.article-row:hover {
  transform: none;
  border-color: transparent;
  box-shadow: none;
}
.article-row:hover .article-cover {
  transform: translateY(-5px) rotateX(0.7deg);
  box-shadow: 0 26px 58px rgba(35, 48, 73, 0.11);
}
.article-row .article-bottom {
  opacity: 0.58;
}
.article-row:hover .article-bottom,
.article-row:focus-within .article-bottom {
  opacity: 1;
}

/* About: one connected social shelf instead of five independent cards. */
.about-panel {
  isolation: isolate;
  grid-template-columns: minmax(300px, 0.72fr) minmax(0, 1.28fr);
  align-items: center;
  gap: clamp(42px, 6vw, 76px);
  padding: clamp(70px, 8vw, 104px) 0 clamp(68px, 8vw, 98px);
  border-top: 0;
  border-bottom: 0;
}
.about-panel::before {
  left: -7%;
  top: 12%;
  width: 360px;
  height: 300px;
  opacity: 1;
  border-radius: 50%;
  background: radial-gradient(circle at 42% 46%, color-mix(in srgb, var(--accent) 6%, transparent), transparent 68%);
  background-size: auto;
  pointer-events: none;
}
.about-profile {
  gap: 20px;
}
.about-profile::after {
  bottom: -30px;
}
.about-avatar-stage {
  align-items: center;
}
.about-avatar {
  width: 108px;
  height: 108px;
  flex-basis: 108px;
  box-shadow:
    0 18px 44px rgba(34, 45, 67, 0.075),
    0 0 0 7px color-mix(in srgb, var(--app-surface) 88%, transparent);
}
.about-directory {
  padding: 0;
  border-left: 0;
}
.about-directory::before {
  left: 0;
  top: auto;
  bottom: -18px;
  width: 84px;
  height: 1px;
  background: linear-gradient(90deg, var(--accent), transparent);
}
.about-directory::after {
  right: 2%;
  top: -22px;
  width: 118px;
  height: 62px;
  opacity: 0.13;
}
.about-directory__heading {
  margin-bottom: 22px;
}
.about-links {
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 0;
  overflow: hidden;
  border-top: 1px solid color-mix(in srgb, var(--app-border-strong) 64%, transparent);
  border-bottom: 1px solid color-mix(in srgb, var(--app-border-strong) 64%, transparent);
  border-radius: 0;
}
.about-card,
.about-card:nth-child(4),
.about-card:nth-child(5) {
  grid-column: auto;
  min-height: 126px;
  padding: 18px 13px 16px;
  display: flex;
  align-items: flex-start;
  flex-direction: column;
  gap: 12px;
  border: 0;
  border-right: 1px solid color-mix(in srgb, var(--app-border) 88%, transparent);
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}
.about-card:last-child {
  border-right: 0;
}
.about-card__icon {
  width: 54px;
  min-width: 54px;
  height: 37px;
  padding: 5px 7px;
  border-color: color-mix(in srgb, var(--app-border) 78%, transparent);
  border-radius: 10px;
  box-shadow: 0 5px 14px rgba(35, 45, 65, 0.035);
}
.about-card__copy {
  width: 100%;
  display: grid;
  grid-template-columns: 1fr;
  gap: 3px;
}
.about-card__copy strong {
  font-size: 12.5px;
}
.about-card__copy small {
  font-size: 9.75px;
  color: var(--app-text-soft);
}
.about-card__copy > span {
  display: none;
}
.about-card__arrow {
  position: absolute;
  right: 10px;
  top: 15px;
  width: 24px;
  height: 24px;
  background: transparent;
  color: var(--app-text-soft);
  font-size: 14px;
}
.about-card:hover {
  transform: none;
  border-color: transparent;
  background: color-mix(in srgb, var(--accent-weak) 56%, transparent);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.55);
}
.about-card:hover .about-card__icon {
  transform: translateY(-3px) rotate(-2deg) scale(1.04);
}
.about-card:hover .about-card__arrow {
  transform: translate(2px, -2px);
  color: var(--accent);
  background: transparent;
}

@media (max-width: 1080px) {
  .section-heading--lab {
    top: auto;
  }
  .ide-canvas {
    grid-template-columns: minmax(0, 0.72fr) minmax(320px, 1fr);
  }
  .about-panel {
    grid-template-columns: 1fr;
    gap: 38px;
  }
  .about-directory {
    padding-top: 0;
    border-top: 0;
  }
  .about-links {
    grid-template-columns: repeat(5, minmax(0, 1fr));
  }
}
@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .section-heading {
    padding-top: 15px;
  }
  .demo-workbench {
    padding: 6px;
    border-radius: 24px;
  }
  .ide-body {
    grid-template-columns: 1fr;
    min-height: 0;
  }
  .demo-rail {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .lab-stage {
    border-radius: 18px;
  }
  .ide-canvas {
    grid-template-columns: 1fr;
  }
  .featured-reading {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .article-row:nth-child(3) {
    grid-column: 1 / -1;
    width: calc(50% - 9px);
  }
  .about-links {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  .about-card:nth-child(3) {
    border-right: 0;
  }
  .about-card:nth-child(4) {
    border-top: 1px solid var(--app-border);
  }
  .about-card:nth-child(5) {
    border-top: 1px solid var(--app-border);
    border-right: 0;
  }
}
@media (max-width: 640px) {
  .hero-section {
    margin-bottom: 34px;
  }
  .demo-lab-section,
  .blog-section,
  .about-panel {
    padding-block: 48px;
  }
  .section-index {
    font-size: 58px;
    top: -10px;
  }
  .demo-workbench {
    padding: 5px;
  }
  .demo-rail {
    grid-template-columns: 1fr;
  }
  .ide-titlebar > span:last-child {
    display: none;
  }
  .featured-reading {
    grid-template-columns: 1fr;
  }
  .article-row:nth-child(3) {
    grid-column: auto;
    width: auto;
  }
  .article-copy {
    min-height: 0;
    padding-top: 14px;
  }
  .about-links {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .about-card,
  .about-card:nth-child(4),
  .about-card:nth-child(5) {
    min-height: 108px;
    border-right: 1px solid var(--app-border);
    border-top: 1px solid var(--app-border);
  }
  .about-card:nth-child(1),
  .about-card:nth-child(2) {
    border-top: 0;
  }
  .about-card:nth-child(2n) {
    border-right: 0;
  }
  .about-card:nth-child(5) {
    border-right: 1px solid var(--app-border);
  }
}
@media (max-width: 420px) {
  .about-links {
    grid-template-columns: 1fr;
  }
  .about-card,
  .about-card:nth-child(4),
  .about-card:nth-child(5) {
    min-height: 82px;
    flex-direction: row;
    align-items: center;
    border-right: 0;
    border-top: 1px solid var(--app-border);
  }
  .about-card:first-child {
    border-top: 0;
  }
  .about-card__copy {
    width: auto;
  }
  .about-card__arrow {
    top: 50%;
    transform: translateY(-50%);
  }
  .about-card:hover .about-card__arrow {
    transform: translate(2px, calc(-50% - 1px));
  }
}

/* ============================================================
   v3.2 · Art-direction pass — hierarchy before decoration
   ============================================================ */
.hero-section {
  min-height: clamp(560px, 72svh, 760px);
  overflow: visible;
}
.hero-layout {
  width: 100%;
  grid-template-columns: minmax(0, 0.92fr) minmax(420px, 1.08fr);
  gap: clamp(26px, 4.2vw, 70px);
}
.hero-copy {
  align-content: center;
  padding: 56px 0 92px;
}
.hero-title {
  max-width: 760px;
  font-size: clamp(48px, 5.75vw, 74px);
  line-height: 1.04;
  letter-spacing: -0.062em;
}
.hero-description {
  max-width: 590px;
  margin-top: 24px;
}
.hero-stage {
  min-height: 500px;
  border-radius: 48px;
}
.hero-stage::before {
  content: "";
  position: absolute;
  inset: 11% 6% 9%;
  z-index: -1;
  border: 1px solid color-mix(in srgb, var(--accent) 10%, transparent);
  border-radius: 44% 56% 58% 42% / 52% 43% 57% 48%;
  transform: rotate(-7deg);
  opacity: 0.8;
}
.hero-stage::after {
  content: "";
  position: absolute;
  right: 4%;
  bottom: 7%;
  width: 92px;
  height: 92px;
  opacity: 0.22;
  background-image: radial-gradient(circle, color-mix(in srgb, var(--accent) 42%, transparent) 1px, transparent 1.2px);
  background-size: 11px 11px;
  -webkit-mask-image: radial-gradient(circle, #000 18%, transparent 72%);
  mask-image: radial-gradient(circle, #000 18%, transparent 72%);
}
.hero-stage__core {
  box-shadow:
    0 34px 90px rgba(42, 57, 83, 0.13),
    0 0 0 1px rgba(255, 255, 255, 0.72) inset;
}
.hero-signal {
  backdrop-filter: blur(11px) saturate(0.88);
}

/* Headings get one deliberate editorial annotation instead of more boxes. */
.section-heading {
  min-height: 104px;
}
.section-heading::after {
  content: "PLDZ / FIELD NOTES";
  position: absolute;
  right: 2px;
  top: 17px;
  color: color-mix(in srgb, var(--app-text-soft) 58%, transparent);
  font-family: var(--font-mono);
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.13em;
}
.section-heading-side {
  padding-top: 38px;
}
.section-index {
  top: -22px;
  font-size: clamp(66px, 7vw, 94px);
  -webkit-text-stroke-color: color-mix(in srgb, var(--accent) 12%, transparent);
}

/* Recent writing: two balanced covers, followed by one horizontal editorial story. */
.featured-reading {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: clamp(30px, 3.2vw, 46px) clamp(22px, 2.6vw, 34px);
}
.featured-reading .article-row:nth-child(2) {
  padding-top: 32px;
}
.featured-reading .article-row:nth-child(3) {
  grid-column: 1 / -1;
  grid-template-columns: minmax(300px, 0.74fr) minmax(0, 1.26fr);
  grid-template-rows: 1fr;
  align-items: center;
  gap: clamp(24px, 4vw, 58px);
  padding-top: clamp(28px, 3.2vw, 42px);
  border-top: 1px solid color-mix(in srgb, var(--app-border-strong) 66%, transparent);
}
.featured-reading .article-row:nth-child(3)::before {
  top: calc(clamp(28px, 3.2vw, 42px) + 13px);
}
.featured-reading .article-row:nth-child(3) .article-cover {
  aspect-ratio: 16 / 9;
}
.featured-reading .article-row:nth-child(3) .article-copy {
  min-height: 0;
  padding: 4px 0;
  align-self: center;
}
.featured-reading .article-row:nth-child(3) .article-copy h3 {
  font-size: clamp(21px, 2.2vw, 30px);
  line-height: 1.28;
}
.featured-reading .article-row:nth-child(3) .article-copy p {
  max-width: 620px;
  font-size: 13.5px;
  -webkit-line-clamp: 3;
}
.article-cover {
  border-radius: 26px;
  background: linear-gradient(145deg, color-mix(in srgb, var(--brand-tint) 72%, var(--app-surface-sunken)), var(--app-surface-sunken));
}
.article-cover::before {
  content: "";
  position: absolute;
  z-index: 2;
  inset: 11px;
  border: 1px solid rgba(255, 255, 255, 0.36);
  border-radius: 18px;
  opacity: 0.42;
  pointer-events: none;
  transition:
    opacity 260ms ease,
    inset 340ms cubic-bezier(0.16, 1, 0.3, 1);
}
.article-row:hover .article-cover::before {
  inset: 8px;
  opacity: 0.78;
}
@media (hover: hover) and (prefers-reduced-motion: no-preference) {
  .featured-reading .article-row {
    transition: opacity 260ms ease;
  }
  .featured-reading:has(.article-row:hover) .article-row:not(:hover) {
    opacity: 0.68;
  }
  .featured-reading:has(.article-row:hover) .article-row:not(:hover) .article-cover {
    transform: scale(0.992);
  }
}

/* About becomes a small social constellation, not five equal UI cells. */
.about-panel {
  grid-template-columns: minmax(320px, 0.82fr) minmax(0, 1.18fr);
  gap: clamp(52px, 7vw, 92px);
  padding-block: clamp(78px, 9vw, 116px);
}
.about-panel::after {
  content: "BUILD  /  LEARN  /  SHARE";
  position: absolute;
  z-index: -1;
  right: -1%;
  top: 9%;
  color: color-mix(in srgb, var(--accent) 7%, transparent);
  font-family: var(--font-display);
  font-size: clamp(44px, 5.4vw, 76px);
  font-weight: 720;
  letter-spacing: -0.055em;
  white-space: nowrap;
  pointer-events: none;
}
.about-profile {
  position: relative;
}
.about-avatar {
  width: 116px;
  height: 116px;
  flex-basis: 116px;
}
.about-directory__heading {
  max-width: 560px;
}
.about-links {
  position: relative;
  overflow: visible;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
  padding: 31px 0 0;
  border: 0;
}
.about-links::before {
  content: "";
  position: absolute;
  left: 8%;
  right: 8%;
  top: 57px;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    color-mix(in srgb, var(--accent) 21%, var(--app-border)),
    color-mix(in srgb, var(--accent) 21%, var(--app-border)),
    transparent
  );
  pointer-events: none;
}
.about-links::after {
  content: "";
  position: absolute;
  z-index: 2;
  left: 8%;
  top: 56px;
  width: 28px;
  height: 3px;
  border-radius: 999px;
  background: linear-gradient(90deg, transparent, color-mix(in srgb, var(--accent) 62%, #fff), transparent);
  opacity: 0.5;
  pointer-events: none;
}
@media (hover: hover) and (prefers-reduced-motion: no-preference) {
  .about-panel.is-spotlight .about-links::after {
    animation: about-signal 5.8s cubic-bezier(0.45, 0, 0.55, 1) infinite;
  }
}
@keyframes about-signal {
  0%,
  12% {
    transform: translateX(0);
    opacity: 0;
  }
  22% {
    opacity: 0.55;
  }
  68% {
    opacity: 0.55;
  }
  80%,
  100% {
    transform: translateX(min(38vw, 430px));
    opacity: 0;
  }
}
.about-card,
.about-card:nth-child(4),
.about-card:nth-child(5) {
  min-height: 112px;
  padding: 0 7px;
  align-items: center;
  text-align: center;
  gap: 11px;
  border: 0;
  background: transparent;
}
.about-card::before {
  content: "";
  position: absolute;
  z-index: 0;
  top: 21px;
  left: 50%;
  width: 7px;
  height: 7px;
  border: 4px solid var(--app-bg);
  border-radius: 50%;
  background: color-mix(in srgb, var(--accent) 70%, #fff);
  transform: translate(-50%, -50%) scale(0.72);
  opacity: 0.55;
  transition:
    transform 260ms cubic-bezier(0.16, 1, 0.3, 1),
    opacity 220ms ease;
}
.about-card__icon {
  position: relative;
  z-index: 3;
  width: 64px;
  min-width: 64px;
  height: 54px;
  margin-top: 0;
  padding: 8px 10px;
  border-radius: 17px;
  background: #fff;
  box-shadow:
    0 12px 30px rgba(34, 46, 70, 0.07),
    inset 0 1px 0 rgba(255, 255, 255, 0.78);
}
.about-card__copy {
  justify-items: center;
  gap: 2px;
}
.about-card__copy strong {
  font-size: 12px;
}
.about-card__copy small {
  font-size: 9px;
  letter-spacing: 0.03em;
}
.about-card__arrow {
  right: calc(50% - 43px);
  top: 6px;
  transform: translateY(3px) scale(0.8);
  opacity: 0;
}
.about-card:hover {
  background: transparent;
}
.about-card:hover::before {
  transform: translate(-50%, -50%) scale(1);
  opacity: 0.95;
}
.about-card:hover .about-card__icon {
  transform: translateY(-7px) rotate(-2deg) scale(1.045);
  box-shadow: 0 18px 38px rgba(34, 46, 70, 0.11);
}
.about-card:hover .about-card__arrow {
  transform: translate(2px, -1px) scale(1);
  opacity: 1;
}

/* The dock is a small navigational instrument, not another card. */
.section-dock {
  right: clamp(10px, 2vw, 28px);
}
.section-dock__item {
  min-height: 31px;
}
.section-dock__mark {
  width: 7px;
  height: 7px;
}
.section-dock__item.is-active .section-dock__mark {
  transform: rotate(45deg) scale(1.16);
  border-radius: 1px;
}

@media (max-width: 1080px) {
  .hero-layout {
    grid-template-columns: minmax(0, 1fr) minmax(380px, 0.9fr);
  }
  .about-panel::after {
    font-size: 52px;
    top: 4%;
  }
}
@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .hero-section {
    overflow: hidden;
  }
  .hero-layout {
    grid-template-columns: 1fr;
  }

  .section-heading::after {
    display: none;
  }
  .section-heading-side {
    padding-top: 0;
  }
  .featured-reading .article-row:nth-child(2) {
    padding-top: 0;
  }
  .featured-reading .article-row:nth-child(3) {
    grid-template-columns: minmax(250px, 0.78fr) minmax(0, 1.22fr);
  }
  .about-panel::after {
    top: 2%;
    right: 0;
    font-size: 44px;
  }
  .about-links {
    grid-template-columns: repeat(5, minmax(0, 1fr));
  }
}
@media (max-width: 640px) {
  .hero-section {
    min-height: 620px;
  }
  .hero-copy {
    padding-bottom: 24px;
  }
  .hero-stage {
    min-height: 300px;
  }
  .featured-reading {
    grid-template-columns: 1fr;
    gap: 30px;
  }
  .featured-reading .article-row:nth-child(3) {
    grid-column: auto;
    grid-template-columns: 1fr;
    gap: 0;
    padding-top: 30px;
  }
  .featured-reading .article-row:nth-child(3) .article-copy {
    padding-top: 14px;
  }
  .about-panel {
    padding-block: 54px;
    gap: 44px;
  }
  .about-panel::after {
    display: none;
  }
  .about-links {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 18px 8px;
    padding-top: 10px;
  }
  .about-links::before,
  .about-links::after {
    display: none;
  }
  .about-card,
  .about-card:nth-child(4),
  .about-card:nth-child(5) {
    min-height: 92px;
    border: 0;
    padding: 0 5px;
  }
  .about-card::before {
    display: none;
  }
  .about-card__icon {
    width: 56px;
    min-width: 56px;
    height: 47px;
    border-radius: 15px;
  }
  .about-card__arrow {
    display: none;
  }
}
@media (max-width: 420px) {
  .about-links {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .about-card,
  .about-card:nth-child(4),
  .about-card:nth-child(5) {
    min-height: 86px;
    flex-direction: column;
    align-items: center;
    border: 0;
  }
  .about-card__copy {
    width: 100%;
  }
}

/* ============================================================
   v3.3 · Editorial scale calibration — smaller, sharper stories
   ============================================================ */
.blog-section .section-heading {
  min-height: 88px;
  margin-bottom: 24px;
}
.blog-section .section-heading-side {
  padding-top: 25px;
}

.featured-reading {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0 clamp(18px, 2vw, 25px);
  align-items: start;
}
.featured-reading .article-row:nth-child(1) {
  padding-top: 0;
}
.featured-reading .article-row:nth-child(2) {
  padding-top: 22px;
}
.featured-reading .article-row:nth-child(3) {
  grid-column: auto;
  grid-template-columns: 1fr;
  grid-template-rows: auto minmax(0, 1fr);
  gap: 0;
  padding-top: 7px;
  border-top: 0;
  align-items: stretch;
}
.featured-reading .article-row:nth-child(3)::before {
  top: 20px;
}
.featured-reading .article-row:nth-child(3) .article-cover {
  aspect-ratio: 16 / 10;
}
.featured-reading .article-row:nth-child(3) .article-copy {
  min-height: 0;
  padding: 14px 3px 0;
}
.featured-reading .article-row:nth-child(3) .article-copy h3 {
  font-size: clamp(16px, 1.45vw, 19px);
  line-height: 1.36;
}
.featured-reading .article-row:nth-child(3) .article-copy p {
  max-width: none;
  font-size: 11.75px;
  -webkit-line-clamp: 2;
}

.article-cover {
  aspect-ratio: 16 / 10;
  border-radius: 21px;
  box-shadow: 0 13px 36px rgba(34, 46, 69, 0.055);
}
.article-cover::before {
  inset: 9px;
  border-radius: 15px;
  opacity: 0.34;
}
.article-row:hover .article-cover::before {
  inset: 7px;
  opacity: 0.66;
}

.article-copy {
  min-height: 0;
  padding: 14px 3px 0;
  gap: 6px;
}
.article-meta {
  font-size: 8.7px;
  gap: 6px;
}
.article-copy h3,
.article-row:first-child .article-copy h3 {
  font-size: clamp(16px, 1.45vw, 19px);
  line-height: 1.36;
}
.article-copy p {
  font-size: 11.75px;
  line-height: 1.62;
  -webkit-line-clamp: 2;
}
.article-bottom {
  margin-top: 4px;
  padding-top: 4px;
  align-items: center;
}
.article-bottom :deep(.tag-chip) {
  height: 21px;
  padding-inline: 7px;
  font-size: 8.5px;
}
.article-bottom .text-link {
  font-size: 10px;
}
.article-bottom .ui-icon {
  font-size: 14px;
}

@media (hover: hover) and (prefers-reduced-motion: no-preference) {
  .featured-reading:has(.article-row:hover) .article-row:not(:hover) {
    opacity: 0.76;
  }
  .featured-reading:has(.article-row:hover) .article-row:not(:hover) .article-cover {
    transform: scale(0.995);
  }
  .article-row:hover .article-cover {
    transform: translateY(-4px) rotateX(0.45deg);
    box-shadow: 0 21px 48px rgba(35, 48, 73, 0.09);
  }
}
@media (max-width: 920px) {
  .featured-reading {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 30px 20px;
  }
  .featured-reading .article-row:nth-child(2) {
    padding-top: 18px;
  }
  .featured-reading .article-row:nth-child(3) {
    grid-column: 1;
    padding-top: 0;
  }
}
@media (max-width: 640px) {
  .featured-reading {
    grid-template-columns: 1fr;
    gap: 32px;
  }
  .featured-reading .article-row:nth-child(2),
  .featured-reading .article-row:nth-child(3) {
    grid-column: auto;
    padding-top: 0;
  }
  .featured-reading .article-row:nth-child(3)::before {
    top: 13px;
  }
  .article-cover {
    border-radius: 20px;
  }
  .article-copy p {
    -webkit-line-clamp: 2;
  }
}

/* ============================================================
   v3.4 · Portfolio depth — soft frames, floating caption shelves
   ============================================================ */
.blog-section {
  --portfolio-radius: 30px;
  --portfolio-inner-radius: 22px;
}
.featured-reading {
  gap: 10px clamp(20px, 2.2vw, 28px);
}
.article-row {
  isolation: isolate;
}
.article-row::after {
  content: "";
  position: absolute;
  z-index: -1;
  left: 9%;
  right: 9%;
  top: 18px;
  height: 52%;
  border-radius: 42px;
  background: radial-gradient(ellipse at 50% 18%, color-mix(in srgb, var(--accent) 8%, transparent), transparent 72%);
  opacity: 0.62;
  transform: translateY(8px) scale(0.96);
  transition:
    opacity 320ms ease,
    transform 520ms cubic-bezier(0.16, 1, 0.3, 1);
  pointer-events: none;
}
.article-cover {
  box-sizing: border-box;
  padding: 7px;
  overflow: hidden;
  border-radius: var(--portfolio-radius);
  border-color: color-mix(in srgb, var(--app-border-strong) 54%, transparent);
  background:
    radial-gradient(circle at 18% 8%, color-mix(in srgb, var(--accent) 6%, transparent), transparent 38%),
    linear-gradient(145deg, color-mix(in srgb, var(--app-surface) 74%, var(--brand-tint)), var(--app-surface-sunken));
  box-shadow:
    0 18px 44px rgba(35, 47, 70, 0.065),
    0 2px 8px rgba(35, 47, 70, 0.025),
    inset 0 1px 0 rgba(255, 255, 255, 0.72);
}
.article-cover img {
  border-radius: var(--portfolio-inner-radius);
}
.article-cover::before {
  inset: 7px;
  border-radius: var(--portfolio-inner-radius);
  border-color: rgba(255, 255, 255, 0.38);
  opacity: 0.54;
}
.article-cover::after {
  inset: 7px;
  border-radius: var(--portfolio-inner-radius);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.06), transparent 32%, rgba(20, 31, 48, 0.1)),
    radial-gradient(420px circle at var(--spot-x, 50%) var(--spot-y, 40%), color-mix(in srgb, var(--accent) 7%, transparent), transparent 68%);
  opacity: 0.48;
}
.article-copy,
.featured-reading .article-row:nth-child(3) .article-copy {
  position: relative;
  z-index: 4;
  min-height: 0;
  margin: -14px 11px 0;
  padding: 17px 16px 15px;
  border: 1px solid color-mix(in srgb, var(--app-border-strong) 55%, transparent);
  border-radius: 22px;
  background: color-mix(in srgb, var(--app-surface) 95%, transparent);
  box-shadow:
    0 15px 34px rgba(31, 43, 65, 0.065),
    inset 0 1px 0 rgba(255, 255, 255, 0.78);
  transition:
    transform 380ms cubic-bezier(0.16, 1, 0.3, 1),
    box-shadow 300ms ease,
    border-color 260ms ease;
}
.article-copy::before {
  content: "";
  position: absolute;
  left: 17px;
  top: -1px;
  width: 31px;
  height: 2px;
  border-radius: 999px;
  background: linear-gradient(90deg, color-mix(in srgb, var(--accent) 70%, #fff), transparent);
  opacity: 0.56;
}
.article-row::before {
  left: 17px;
  top: 16px;
  min-width: 31px;
  height: 25px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 8px 22px rgba(29, 41, 62, 0.07);
}
@media (hover: hover) and (prefers-reduced-motion: no-preference) {
  .article-row:hover::after {
    opacity: 0.95;
    transform: translateY(0) scale(1);
  }
  .article-row:hover .article-cover {
    transform: translateY(-6px) rotateX(0.65deg) scale(1.006);
    box-shadow:
      0 28px 68px rgba(35, 48, 73, 0.115),
      0 4px 14px rgba(35, 48, 73, 0.04);
  }
  .article-row:hover .article-copy {
    transform: translateY(-3px);
    border-color: color-mix(in srgb, var(--accent-line) 72%, var(--app-border));
    box-shadow:
      0 21px 46px rgba(31, 43, 65, 0.09),
      inset 0 1px 0 rgba(255, 255, 255, 0.82);
  }
}
@media (max-width: 920px) {
  .article-copy,
  .featured-reading .article-row:nth-child(3) .article-copy {
    margin-inline: 9px;
  }
}
@media (max-width: 640px) {
  .blog-section {
    --portfolio-radius: 25px;
    --portfolio-inner-radius: 18px;
  }
  .article-cover {
    padding: 6px;
  }
  .article-cover::before,
  .article-cover::after {
    inset: 6px;
  }
  .article-copy,
  .featured-reading .article-row:nth-child(3) .article-copy {
    margin: -11px 8px 0;
    padding: 15px 14px 14px;
    border-radius: 19px;
  }
}

/* ============================================================
   v3.5 · Editorial notes — portfolio objects, not stacked cards
   ============================================================ */
.featured-reading {
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 0 clamp(22px, 2.5vw, 32px);
  align-items: start;
}
.featured-reading .article-row,
.featured-reading .article-row:nth-child(1),
.featured-reading .article-row:nth-child(2),
.featured-reading .article-row:nth-child(3) {
  grid-column: span 4;
  padding-top: 0;
  display: block;
}
.featured-reading .article-row:nth-child(1),
.featured-reading .article-row:nth-child(2),
.featured-reading .article-row:nth-child(3) {
  grid-column: span 4;
}
.article-row::after {
  display: none;
}
.article-row::before {
  z-index: 5;
  left: 15px;
  top: 15px;
  min-width: 32px;
  height: 24px;
  border: 1px solid rgba(255, 255, 255, 0.58);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.84);
  color: #5b6878;
  box-shadow: 0 8px 22px rgba(29, 41, 62, 0.07);
  backdrop-filter: blur(8px);
}
.article-cover,
.featured-reading .article-row:nth-child(3) .article-cover {
  aspect-ratio: 16 / 10;
  padding: 6px;
  border-radius: 28px;
  border-color: color-mix(in srgb, var(--app-border-strong) 50%, transparent);
  box-shadow:
    0 22px 58px rgba(31, 43, 65, 0.07),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
}
.featured-reading .article-row:nth-child(1) .article-cover,
.featured-reading .article-row:nth-child(3) .article-cover {
  aspect-ratio: 16 / 10;
}
.article-cover::before,
.article-cover::after {
  inset: 6px;
  border-radius: 21px;
}
.article-cover img {
  border-radius: 21px;
}
.article-copy,
.featured-reading .article-row:nth-child(3) .article-copy {
  min-height: 0;
  margin: 0;
  padding: 16px 4px 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  transition: transform 320ms cubic-bezier(0.16, 1, 0.3, 1);
}
.article-copy::before {
  display: none;
}
.article-meta {
  min-height: 19px;
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.075em;
  text-transform: uppercase;
}
.article-copy h3,
.article-row:first-child .article-copy h3,
.featured-reading .article-row:nth-child(3) .article-copy h3 {
  margin-top: 7px;
  font-size: clamp(17px, 1.5vw, 21px);
  line-height: 1.3;
  letter-spacing: -0.035em;
}
.featured-reading .article-row:nth-child(1) .article-copy h3 {
  max-width: 94%;
  font-size: clamp(17px, 1.5vw, 21px);
}
.article-copy p,
.featured-reading .article-row:nth-child(3) .article-copy p {
  max-width: 94%;
  margin-top: 7px;
  font-size: 11.5px;
  line-height: 1.64;
  -webkit-line-clamp: 2;
  opacity: 0.76;
}
.article-bottom {
  margin-top: 12px;
  padding-top: 0;
  opacity: 0.7;
}
.article-bottom :deep(.tag-chip) {
  background: transparent;
  border: 1px solid color-mix(in srgb, var(--app-border-strong) 58%, transparent);
}
@media (hover: hover) and (prefers-reduced-motion: no-preference) {
  .featured-reading:has(.article-row:hover) .article-row:not(:hover) {
    opacity: 0.84;
  }
  .article-row:hover .article-cover {
    transform: translateY(-6px) rotate(0.18deg) scale(1.004);
    box-shadow:
      0 30px 72px rgba(31, 43, 65, 0.115),
      inset 0 1px 0 rgba(255, 255, 255, 0.86);
  }
  .article-row:nth-child(even):hover .article-cover {
    transform: translateY(-6px) rotate(-0.18deg) scale(1.004);
  }
  .article-row:hover .article-copy {
    transform: translateX(3px);
  }
}
@media (max-width: 980px) {
  .featured-reading {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 34px 22px;
  }
  .featured-reading .article-row,
  .featured-reading .article-row:nth-child(1),
  .featured-reading .article-row:nth-child(2),
  .featured-reading .article-row:nth-child(3) {
    grid-column: auto;
  }
  .featured-reading .article-row:nth-child(3) {
    width: 100%;
  }
  .featured-reading .article-row:nth-child(1) .article-cover,
  .featured-reading .article-row:nth-child(3) .article-cover {
    aspect-ratio: 16 / 10;
  }
}
@media (max-width: 640px) {
  .featured-reading {
    grid-template-columns: 1fr;
    gap: 38px;
  }
  .article-cover,
  .featured-reading .article-row:nth-child(1) .article-cover,
  .featured-reading .article-row:nth-child(3) .article-cover {
    aspect-ratio: 16 / 9;
    padding: 5px;
    border-radius: 24px;
  }
  .article-cover::before,
  .article-cover::after {
    inset: 5px;
    border-radius: 18px;
  }
  .article-cover img {
    border-radius: 18px;
  }
  .article-copy,
  .featured-reading .article-row:nth-child(3) .article-copy {
    padding: 14px 3px 0;
  }
  .article-copy p {
    max-width: 100%;
  }
}

/* ============================================================
   v3.6 · Notes as an editorial spread — hierarchy, not a card grid
   ============================================================ */
.featured-reading {
  position: relative;
  grid-template-columns: minmax(0, 1.16fr) minmax(300px, 0.72fr);
  grid-template-rows: repeat(2, minmax(0, 1fr));
  gap: 0 clamp(30px, 4vw, 52px);
  align-items: stretch;
}
.featured-reading::before {
  content: "NOTES / 03";
  position: absolute;
  right: 0;
  top: -35px;
  color: color-mix(in srgb, var(--app-text-soft) 55%, transparent);
  font-family: var(--font-mono);
  font-size: 7.5px;
  font-weight: 700;
  letter-spacing: 0.12em;
  pointer-events: none;
}
.featured-reading .article-row,
.featured-reading .article-row:nth-child(1),
.featured-reading .article-row:nth-child(2),
.featured-reading .article-row:nth-child(3) {
  grid-column: auto;
  padding: 0;
  display: block;
  min-width: 0;
}
.featured-reading .article-row:nth-child(1) {
  grid-column: 1;
  grid-row: 1 / span 2;
  padding-right: clamp(4px, 1vw, 12px);
}
.featured-reading .article-row:nth-child(2),
.featured-reading .article-row:nth-child(3) {
  grid-column: 2;
  display: grid;
  grid-template-columns: minmax(124px, 0.58fr) minmax(0, 1fr);
  align-items: center;
  gap: clamp(15px, 2vw, 22px);
  min-height: 0;
  padding: 19px 0;
  border-top: 1px solid var(--app-border);
}
.featured-reading .article-row:nth-child(3) {
  border-bottom: 1px solid var(--app-border);
}

.featured-reading .article-row::before {
  left: 14px;
  top: 14px;
  min-width: 30px;
  height: 23px;
  border: 1px solid rgba(255, 255, 255, 0.64);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.84);
  box-shadow: 0 8px 20px rgba(24, 36, 55, 0.06);
}
.featured-reading .article-row:nth-child(2)::before,
.featured-reading .article-row:nth-child(3)::before {
  left: 8px;
  top: 27px;
  min-width: 25px;
  height: 20px;
  font-size: 7px;
}

.featured-reading .article-row:nth-child(1) .article-cover,
.featured-reading .article-row:nth-child(2) .article-cover,
.featured-reading .article-row:nth-child(3) .article-cover {
  margin: 0;
  padding: 0;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--app-border-strong) 54%, transparent);
  background: var(--app-surface-sunken);
  box-shadow: 0 26px 64px rgba(30, 43, 65, 0.075);
}
.featured-reading .article-row:nth-child(1) .article-cover {
  aspect-ratio: 16 / 10;
  border-radius: 26px;
}
.featured-reading .article-row:nth-child(2) .article-cover,
.featured-reading .article-row:nth-child(3) .article-cover {
  aspect-ratio: 4 / 3;
  border-radius: 17px;
  box-shadow: 0 14px 32px rgba(30, 43, 65, 0.055);
}
.featured-reading .article-row .article-cover::before,
.featured-reading .article-row .article-cover::after {
  inset: 0;
  border-radius: inherit;
}
.featured-reading .article-row .article-cover img {
  border-radius: inherit;
}

.featured-reading .article-row:nth-child(1) .article-copy {
  padding: 21px 3px 0;
}
.featured-reading .article-row:nth-child(2) .article-copy,
.featured-reading .article-row:nth-child(3) .article-copy {
  align-self: center;
  padding: 0;
}
.featured-reading .article-row:nth-child(1) .article-copy h3 {
  max-width: 88%;
  margin-top: 8px;
  font-size: clamp(23px, 2.4vw, 32px);
  line-height: 1.18;
}
.featured-reading .article-row:nth-child(2) .article-copy h3,
.featured-reading .article-row:nth-child(3) .article-copy h3 {
  margin-top: 6px;
  font-size: clamp(15px, 1.4vw, 18px);
  line-height: 1.3;
}
.featured-reading .article-row:nth-child(2) .article-copy p,
.featured-reading .article-row:nth-child(3) .article-copy p {
  margin-top: 6px;
  font-size: 10.5px;
  line-height: 1.55;
  -webkit-line-clamp: 2;
}
.featured-reading .article-row:nth-child(2) .article-bottom,
.featured-reading .article-row:nth-child(3) .article-bottom {
  margin-top: 9px;
}
.featured-reading .article-row:nth-child(2) .tag-list,
.featured-reading .article-row:nth-child(3) .tag-list {
  display: none;
}
.featured-reading .article-row:nth-child(2) .text-link,
.featured-reading .article-row:nth-child(3) .text-link {
  margin-left: 0;
  font-size: 9.5px;
}

@media (hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference) {
  .featured-reading:has(.article-row:hover) .article-row:not(:hover) {
    opacity: 0.79;
  }
  .featured-reading .article-row:nth-child(1):hover .article-cover {
    transform: translateY(-5px) scale(1.003);
  }
  .featured-reading .article-row:nth-child(2):hover .article-cover,
  .featured-reading .article-row:nth-child(3):hover .article-cover {
    transform: translateX(-3px) scale(1.012);
  }
  .featured-reading .article-row:nth-child(2):hover .article-copy,
  .featured-reading .article-row:nth-child(3):hover .article-copy {
    transform: translateX(3px);
  }
}

@media (max-width: 900px) {
  .featured-reading {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
    gap: 0;
  }
  .featured-reading .article-row:nth-child(1) {
    grid-column: auto;
    grid-row: auto;
    padding: 0 0 28px;
    border-bottom: 1px solid var(--app-border);
  }
  .featured-reading .article-row:nth-child(2),
  .featured-reading .article-row:nth-child(3) {
    grid-column: auto;
    grid-template-columns: minmax(150px, 0.42fr) minmax(0, 1fr);
    padding: 22px 0;
  }
  .featured-reading .article-row:nth-child(1) .article-cover {
    aspect-ratio: 16 / 9;
  }
}

@media (max-width: 560px) {
  .featured-reading .article-row:nth-child(1) {
    padding-bottom: 24px;
  }
  .featured-reading .article-row:nth-child(2),
  .featured-reading .article-row:nth-child(3) {
    grid-template-columns: 112px minmax(0, 1fr);
    gap: 14px;
    padding: 18px 0;
  }
  .featured-reading .article-row:nth-child(1) .article-cover {
    border-radius: 22px;
  }
  .featured-reading .article-row:nth-child(2) .article-cover,
  .featured-reading .article-row:nth-child(3) .article-cover {
    border-radius: 14px;
  }
  .featured-reading .article-row:nth-child(1) .article-copy h3 {
    max-width: 100%;
    font-size: 22px;
  }
  .featured-reading .article-row:nth-child(2) .article-copy p,
  .featured-reading .article-row:nth-child(3) .article-copy p {
    display: none;
  }
}

/* ============================================================
   v3.7 · Notes index — portfolio rows with living thumbnails
   ============================================================ */
.notes-stack {
  position: relative;
  border-top: 1px solid var(--app-border-strong);
}
.note-row {
  position: relative;
  min-height: 154px;
  display: grid;
  grid-template-columns: 38px minmax(0, 1fr) minmax(180px, 245px) 30px;
  align-items: center;
  gap: clamp(15px, 2vw, 28px);
  padding: 18px 0;
  border-bottom: 1px solid var(--app-border);
  transition:
    opacity 180ms ease,
    transform 300ms cubic-bezier(0.16, 1, 0.3, 1);
}
.note-row::before {
  content: "";
  position: absolute;
  z-index: -1;
  inset: 8px -14px;
  border-radius: 18px;
  background: linear-gradient(90deg, color-mix(in srgb, var(--accent) 4%, transparent), transparent 72%);
  opacity: 0;
  transition: opacity 220ms ease;
}
.note-row__number {
  align-self: start;
  padding-top: 8px;
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 8px;
  font-weight: 720;
  letter-spacing: 0.08em;
}
.note-row__copy {
  min-width: 0;
}
.note-row__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}
.note-row__meta > * + *::before {
  content: "·";
  margin-right: 8px;
  color: var(--app-border-strong);
}
.note-row__copy h3 {
  max-width: 760px;
  margin: 7px 0 0;
  color: var(--app-text);
  font-family: var(--font-display);
  font-size: clamp(20px, 2.15vw, 30px);
  font-weight: 635;
  letter-spacing: -0.042em;
  line-height: 1.17;
}
.note-row__copy h3 a {
  color: inherit;
  text-decoration: none;
}
.note-row__copy p {
  max-width: 650px;
  margin: 8px 0 0;
  display: -webkit-box;
  overflow: hidden;
  color: var(--app-text-muted);
  font-size: 11.5px;
  line-height: 1.62;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}
.note-row__media {
  position: relative;
  aspect-ratio: 16 / 10;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--app-border-strong) 58%, transparent);
  border-radius: 17px;
  background: var(--app-surface-sunken);
  box-shadow: 0 12px 32px rgba(30, 43, 65, 0.05);
  transform-origin: 60% 50%;
}
.note-row__media img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
  transition: transform 360ms cubic-bezier(0.16, 1, 0.3, 1);
}
.note-row__arrow {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  border: 1px solid var(--app-border);
  border-radius: 50%;
  color: var(--app-text-soft);
  text-decoration: none;
  transition:
    color 180ms ease,
    border-color 180ms ease,
    transform 260ms cubic-bezier(0.16, 1, 0.3, 1),
    background-color 180ms ease;
}
.note-row__arrow .material-symbols-rounded {
  font-size: 15px;
}

@media (hover: hover) and (pointer: fine) {
  .notes-stack:has(.note-row:hover) .note-row:not(:hover) {
    opacity: 0.52;
  }
  .note-row:hover {
    transform: translateX(4px);
  }
  .note-row:hover::before {
    opacity: 1;
  }
  .note-row:hover .note-row__media img {
    transform: scale(1.035);
  }
  .note-row:hover .note-row__arrow {
    color: var(--accent);
    border-color: var(--accent-line);
    background: var(--accent-weak);
    transform: translate(2px, -2px);
  }
}

@media (max-width: 820px) {
  .note-row {
    grid-template-columns: 30px minmax(0, 1fr) 160px 28px;
    min-height: 132px;
    gap: 14px;
  }
  .note-row__copy h3 {
    font-size: 21px;
  }
  .note-row__copy p {
    display: none;
  }
}

@media (max-width: 600px) {
  .note-row {
    min-height: 0;
    grid-template-columns: 28px minmax(0, 1fr) 28px;
    grid-template-areas:
      "num copy arrow"
      ". media media";
    align-items: start;
    gap: 12px;
    padding: 18px 0 22px;
  }
  .note-row__number {
    grid-area: num;
  }
  .note-row__copy {
    grid-area: copy;
  }
  .note-row__arrow {
    grid-area: arrow;
  }
  .note-row__media {
    grid-area: media;
    width: min(100%, 420px);
    margin-top: 5px;
    border-radius: 15px;
  }
  .note-row__copy h3 {
    font-size: 19px;
  }
}

/* ============================================================
   v3.9 · Home Live Demo = discovery roadmap, not a mini /livedemo
   ============================================================ */
.experiment-roadmap-section {
  position: relative;
}
.roadmap-heading {
  margin-bottom: 20px;
}
.experiment-roadmap {
  position: relative;
  overflow: hidden;
  padding: clamp(22px, 3vw, 34px) clamp(20px, 3vw, 36px) 20px;
  border-top: 1px solid var(--app-border);
  border-bottom: 1px solid var(--app-border);
  background:
    radial-gradient(circle at 76% 18%, color-mix(in srgb, var(--accent) 7%, transparent), transparent 25rem),
    linear-gradient(180deg, color-mix(in srgb, var(--app-surface) 54%, transparent), color-mix(in srgb, var(--app-bg) 86%, transparent));
}
.experiment-roadmap::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.32;
  background-image: radial-gradient(circle, color-mix(in srgb, var(--accent) 28%, transparent) 0.7px, transparent 0.8px);
  background-size: 22px 22px;
  mask-image: linear-gradient(90deg, transparent 0, #000 17%, #000 84%, transparent 100%);
}
.roadmap-topline,
.roadmap-footer {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}
.roadmap-topline {
  margin-bottom: 24px;
}
.roadmap-topline > div:first-child {
  display: flex;
  align-items: baseline;
  gap: 10px;
}
.roadmap-topline span,
.roadmap-footer,
.roadmap-focus__eyebrow,
.roadmap-stop__copy small,
.roadmap-preview__topbar,
.roadmap-preview__caption {
  font-family: var(--font-mono);
  text-transform: uppercase;
  letter-spacing: 0.11em;
}
.roadmap-topline > div:first-child span {
  color: var(--accent);
  font-size: 8px;
  font-weight: 760;
}
.roadmap-topline > div:first-child strong {
  color: var(--app-text);
  font-size: 11px;
  font-weight: 670;
}
.roadmap-topline__legend {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--app-text-soft);
  font-size: 7px;
  font-weight: 700;
}
.roadmap-topline__legend i {
  width: 18px;
  height: 1px;
  background: var(--app-border-strong);
}
.roadmap-stations {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  padding: 0 3px 25px;
}
.roadmap-line {
  position: absolute;
  left: 12.5%;
  right: 12.5%;
  top: 19px;
  height: 1px;
  overflow: hidden;
  background: color-mix(in srgb, var(--app-border-strong) 72%, transparent);
}
.roadmap-line > span {
  position: absolute;
  inset: 0 auto 0 0;
  background: linear-gradient(90deg, color-mix(in srgb, var(--accent) 42%, var(--app-border-strong)), var(--accent));
  transition: width 420ms cubic-bezier(0.16, 1, 0.3, 1);
}
.roadmap-stop {
  position: relative;
  z-index: 2;
  min-width: 0;
  padding: 0 8px;
  display: grid;
  justify-items: center;
  gap: 11px;
  border: 0;
  background: transparent;
  color: inherit;
  text-align: center;
  cursor: pointer;
}
.roadmap-stop__node {
  position: relative;
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border: 1px solid var(--app-border-strong);
  border-radius: 50%;
  background: var(--app-bg);
  color: var(--app-text-soft);
  box-shadow: 0 0 0 7px color-mix(in srgb, var(--app-bg) 80%, transparent);
  transition:
    border-color 220ms ease,
    background-color 220ms ease,
    color 220ms ease,
    transform 320ms cubic-bezier(0.16, 1, 0.3, 1),
    box-shadow 220ms ease;
}
.roadmap-stop__node i {
  position: absolute;
  width: 10px;
  height: 10px;
  opacity: 0;
  background: var(--accent);
  clip-path: polygon(50% 0, 62% 38%, 100% 50%, 62% 62%, 50% 100%, 38% 62%, 0 50%, 38% 38%);
  transform: scale(0.55) rotate(22deg);
  transition:
    opacity 220ms ease,
    transform 320ms cubic-bezier(0.16, 1, 0.3, 1);
}
.roadmap-stop__node em {
  font-family: var(--font-mono);
  font-size: 7px;
  font-style: normal;
  font-weight: 760;
  letter-spacing: 0.05em;
}
.roadmap-stop__copy {
  min-width: 0;
  display: grid;
  gap: 3px;
}
.roadmap-stop__copy small {
  overflow: hidden;
  color: var(--app-text-soft);
  font-size: 6.5px;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.roadmap-stop__copy strong {
  overflow: hidden;
  color: var(--app-text-muted);
  font-size: 11px;
  font-weight: 610;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.roadmap-stop.is-active .roadmap-stop__node {
  border-color: color-mix(in srgb, var(--accent) 48%, var(--app-border-strong));
  background: color-mix(in srgb, var(--accent-weak) 86%, var(--app-surface));
  color: transparent;
  box-shadow:
    0 0 0 8px color-mix(in srgb, var(--accent) 5%, transparent),
    0 8px 22px color-mix(in srgb, var(--accent) 9%, transparent);
  transform: translateY(-2px);
}
.roadmap-stop.is-active .roadmap-stop__node i {
  opacity: 1;
  transform: scale(1) rotate(0);
}
.roadmap-stop.is-active .roadmap-stop__copy strong {
  color: var(--app-text);
}
.roadmap-stop.is-active .roadmap-stop__copy small {
  color: var(--accent);
}

.roadmap-focus {
  position: relative;
  z-index: 2;
  min-width: 0;
  display: grid;
  grid-template-columns: minmax(0, 0.76fr) minmax(360px, 1.05fr);
  gap: clamp(30px, 5vw, 70px);
  align-items: center;
  padding: clamp(26px, 4vw, 46px) 2px clamp(24px, 3vw, 36px);
  border-top: 1px solid var(--app-border);
}
.roadmap-focus__copy {
  min-width: 0;
  max-width: 540px;
}
.roadmap-focus__eyebrow {
  margin: 0 0 12px;
  color: var(--accent);
  font-size: 7.5px;
  font-weight: 760;
}
.roadmap-focus__copy h3 {
  margin: 0;
  color: var(--app-text);
  font-family: var(--font-display);
  font-size: clamp(31px, 3.9vw, 52px);
  font-weight: 600;
  letter-spacing: -0.055em;
  line-height: 1.02;
}
.roadmap-focus__description {
  max-width: 520px;
  margin: 17px 0 0;
  color: var(--app-text-muted);
  font-size: 13px;
  line-height: 1.8;
}
.roadmap-focus__signals {
  margin-top: 22px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px 18px;
  color: var(--app-text-soft);
  font-size: 10.5px;
}
.roadmap-focus__signals span {
  display: inline-flex;
  align-items: center;
  gap: 7px;
}
.roadmap-focus__signals i {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--accent) 68%, var(--brand-support));
}
.roadmap-focus__actions {
  margin-top: 26px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}
.roadmap-primary,
.roadmap-secondary {
  min-height: 40px;
  padding: 0 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  border-radius: 13px;
  text-decoration: none;
  font-size: 11px;
  font-weight: 650;
}
.roadmap-primary {
  background: var(--accent);
  color: var(--app-on-accent);
  box-shadow: 0 9px 24px color-mix(in srgb, var(--accent) 14%, transparent);
}
.roadmap-primary .material-symbols-rounded {
  font-size: 15px;
}
.roadmap-secondary {
  border: 1px solid var(--app-border);
  background: color-mix(in srgb, var(--app-surface) 80%, transparent);
  color: var(--app-text-muted);
}
.roadmap-preview {
  position: relative;
  min-width: 0;
  padding: 8px;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--app-border-strong) 74%, transparent);
  border-radius: 25px;
  background: color-mix(in srgb, var(--app-surface) 92%, var(--accent) 1.5%);
  color: inherit;
  text-decoration: none;
  box-shadow:
    0 24px 56px rgba(32, 43, 63, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.75);
}
.roadmap-preview::before {
  content: "";
  position: absolute;
  inset: -1px;
  pointer-events: none;
  border-radius: inherit;
  background: linear-gradient(120deg, transparent 28%, color-mix(in srgb, var(--accent) 10%, transparent), transparent 58%);
  opacity: 0;
  transform: translateX(-18%);
  transition:
    opacity 220ms ease,
    transform 600ms cubic-bezier(0.16, 1, 0.3, 1);
}
.roadmap-preview__topbar {
  min-height: 31px;
  padding: 0 7px 5px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--app-text-soft);
  font-size: 6.5px;
  font-weight: 730;
}
.roadmap-preview__topbar .material-symbols-rounded {
  font-size: 14px;
}
.roadmap-preview__media {
  position: relative;
  overflow: hidden;
  aspect-ratio: 16 / 9;
  border: 1px solid var(--app-border);
  border-radius: 18px;
  background: var(--app-surface-sunken);
}
.roadmap-preview__media img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: contain;
  background: var(--app-surface-sunken);
  transition: transform 480ms cubic-bezier(0.16, 1, 0.3, 1);
}
.roadmap-preview__caption {
  position: absolute;
  right: 17px;
  bottom: 16px;
  padding: 5px 7px;
  border: 1px solid color-mix(in srgb, var(--app-border-strong) 72%, transparent);
  border-radius: 8px;
  background: color-mix(in srgb, var(--app-surface) 82%, transparent);
  color: var(--app-text-soft);
  font-size: 6px;
  font-weight: 720;
  backdrop-filter: blur(9px);
}
.roadmap-footer {
  min-height: 31px;
  padding-top: 14px;
  border-top: 1px solid var(--app-border);
  color: var(--app-text-soft);
  font-size: 6.5px;
  font-weight: 720;
}
.roadmap-focus-enter-active,
.roadmap-focus-leave-active {
  transition:
    opacity 180ms ease,
    transform 360ms cubic-bezier(0.16, 1, 0.3, 1),
    filter 220ms ease;
}
.roadmap-focus-enter-from {
  opacity: 0;
  transform: translateY(10px);
  filter: blur(3px);
}
.roadmap-focus-leave-to {
  opacity: 0;
  transform: translateY(-5px);
  filter: blur(2px);
}

@media (hover: hover) and (pointer: fine) {
  .roadmap-stop:hover .roadmap-stop__node {
    border-color: var(--accent-line);
    transform: translateY(-2px);
  }
  .roadmap-stop:hover .roadmap-stop__copy strong {
    color: var(--app-text);
  }
  .roadmap-preview:hover::before {
    opacity: 1;
    transform: translateX(12%);
  }
  .roadmap-preview:hover .roadmap-preview__media img {
    transform: scale(1.018);
  }
  .roadmap-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 13px 30px color-mix(in srgb, var(--accent) 18%, transparent);
  }
  .roadmap-secondary:hover {
    border-color: var(--accent-line);
    color: var(--accent);
  }
}

@media (max-width: 920px) {
  .roadmap-stations {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
  }
  .roadmap-line {
    display: none;
  }
  .roadmap-stop {
    min-height: 64px;
    padding: 9px 10px;
    grid-template-columns: 38px minmax(0, 1fr);
    justify-items: stretch;
    align-items: center;
    text-align: left;
    border: 1px solid var(--app-border);
    border-radius: 14px;
    background: color-mix(in srgb, var(--app-surface) 76%, transparent);
  }
  .roadmap-stop__copy {
    min-width: 0;
  }
  .roadmap-stop.is-active {
    border-color: var(--accent-line);
    background: var(--accent-weak);
  }
  .roadmap-focus {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  .roadmap-focus__copy {
    max-width: 680px;
  }
  .roadmap-preview {
    width: min(720px, 100%);
  }
}

@media (max-width: 620px) {
  .experiment-roadmap {
    margin-inline: calc(var(--app-page-gutter) * -0.2);
    padding-inline: 14px;
  }
  .roadmap-topline__legend {
    display: none;
  }
  .roadmap-stations {
    display: flex;
    overflow-x: auto;
    gap: 8px;
    margin-inline: -3px;
    padding: 0 3px 20px;
    scroll-snap-type: x proximity;
    scrollbar-width: none;
  }
  .roadmap-stations::-webkit-scrollbar {
    display: none;
  }
  .roadmap-stop {
    flex: 0 0 min(75vw, 260px);
    scroll-snap-align: start;
  }
  .roadmap-focus {
    padding-top: 24px;
  }
  .roadmap-focus__copy h3 {
    font-size: clamp(29px, 10vw, 42px);
  }
  .roadmap-focus__signals {
    gap: 7px 13px;
  }
  .roadmap-primary,
  .roadmap-secondary {
    width: 100%;
  }
  .roadmap-preview {
    padding: 6px;
    border-radius: 20px;
  }
  .roadmap-preview__media {
    border-radius: 14px;
  }
  .roadmap-footer span:first-child {
    max-width: 70%;
  }
}

/* ============================================================
   v4.0 · Home precision pass — optical alignment, readable type
   ============================================================ */
.home-main {
  padding-top: 98px;
}
.hero-title,
.section-heading h2,
.note-row__copy h3,
.roadmap-focus__copy h3,
.about-profile h2,
.about-directory h3 {
  overflow: visible;
  text-wrap: balance;
}
.hero-description,
.section-description,
.note-row__copy p,
.roadmap-focus__description,
.about-intro,
.about-directory__hint {
  text-wrap: pretty;
}

/* Keep section numbering visible, but never behind the headline. */
.section-heading {
  min-height: 0;
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr) auto;
  align-items: end;
  gap: 0 18px;
  padding: 0 0 24px;
}
.section-heading::after {
  display: none;
}
.section-heading > div:first-of-type {
  min-width: 0;
}
.section-heading-side {
  align-self: end;
  padding: 0 0 3px;
}
.section-index {
  position: static;
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  align-self: start;
  margin-top: 3px;
  border: 1px solid color-mix(in srgb, var(--accent) 18%, var(--app-border));
  border-radius: 50%;
  background: color-mix(in srgb, var(--app-surface) 76%, transparent);
  color: var(--accent);
  font-family: var(--font-mono);
  font-size: 9.5px;
  font-weight: 760;
  letter-spacing: 0.05em;
  line-height: 1;
  opacity: 0.78;
  -webkit-text-stroke: 0;
}
.section-kicker {
  margin-bottom: 7px;
  font-size: 10px;
  letter-spacing: 0.13em;
  line-height: 1.2;
}
.section-heading h2 {
  line-height: 1.13;
  padding-bottom: 0.04em;
}
.section-description {
  margin-top: 9px;
  max-width: 62ch;
  font-size: 13px;
  line-height: 1.72;
}
.section-link {
  min-height: 36px;
  align-items: center;
}

/* Roadmap: align every text block and stop relying on tiny microtype. */
.roadmap-heading {
  margin-bottom: 8px;
}
.experiment-roadmap {
  padding-top: 28px;
  padding-bottom: 22px;
}
.roadmap-topline {
  margin-bottom: 22px;
}
.roadmap-topline > div:first-child span {
  font-size: 9px;
}
.roadmap-topline > div:first-child strong {
  font-size: 12px;
}
.roadmap-topline__legend {
  font-size: 8.5px;
}
.roadmap-stop {
  gap: 10px;
}
.roadmap-stop__copy small {
  font-size: 9px;
  line-height: 1.35;
}
.roadmap-stop__copy strong {
  font-size: 11.5px;
  line-height: 1.35;
}
.roadmap-stop__node em {
  font-size: 9px;
}
.roadmap-focus {
  grid-template-columns: minmax(0, 0.8fr) minmax(360px, 1fr);
  gap: clamp(34px, 5vw, 64px);
}
.roadmap-focus__copy {
  align-self: center;
}
.roadmap-focus__eyebrow {
  margin-bottom: 10px;
  font-size: 9px;
  line-height: 1.4;
}
.roadmap-focus__copy h3 {
  line-height: 1.06;
  padding-bottom: 0.05em;
}
.roadmap-focus__description {
  margin-top: 14px;
  font-size: 13.5px;
  line-height: 1.72;
}
.roadmap-focus__signals {
  margin-top: 18px;
  font-size: 11px;
}
.roadmap-primary,
.roadmap-secondary {
  min-height: 42px;
  padding-inline: 15px;
  font-size: 11.5px;
}
.roadmap-preview__topbar {
  font-size: 9px;
}
.roadmap-preview__caption {
  font-size: 9px;
}
.roadmap-footer {
  font-size: 9px;
}

/* Notes: stronger baselines, less cramped metadata. */
.notes-stack {
  margin-top: 2px;
}
.note-row {
  min-height: 150px;
  grid-template-columns: 38px minmax(0, 1fr) minmax(190px, 238px) 34px;
  gap: clamp(16px, 2vw, 26px);
  padding-block: 20px;
}
.note-row__number {
  padding-top: 5px;
  font-size: 9.5px;
  line-height: 1.3;
}
.note-row__meta {
  font-size: 9.5px;
  line-height: 1.35;
}
.note-row__copy h3 {
  margin-top: 8px;
  font-size: clamp(20px, 2vw, 27px);
  line-height: 1.2;
  padding-bottom: 0.03em;
}
.note-row__copy p {
  margin-top: 8px;
  max-width: 62ch;
  font-size: 12.5px;
  line-height: 1.68;
}
.note-row__media {
  align-self: center;
  border-radius: 18px;
}
.note-row__arrow {
  align-self: center;
}

/* About: make both columns optically centered and keep decoration behind copy. */
.about-panel {
  align-items: center;
  gap: clamp(48px, 6vw, 78px);
  padding-block: clamp(68px, 8vw, 96px);
}
.about-profile,
.about-directory {
  min-width: 0;
}
.about-profile__copy,
.about-directory__heading {
  position: relative;
  z-index: 3;
}
.about-profile .section-index--about {
  position: absolute;
  z-index: 4;
  top: 2px;
  right: 2px;
  left: auto;
  margin: 0;
}
.about-panel::after {
  z-index: -2;
  opacity: 0.72;
}
.about-intro {
  max-width: 48ch;
  font-size: 13px;
  line-height: 1.78;
}
.about-directory__hint {
  max-width: 52ch;
  font-size: 12.5px;
  line-height: 1.7;
}
.about-links {
  align-items: start;
}
.about-card {
  min-width: 0;
}
.about-card__copy strong {
  font-size: 12.5px;
  line-height: 1.25;
}
.about-card__copy small {
  font-size: 10px;
  line-height: 1.4;
}
.about-card__copy span {
  font-size: 9.5px;
  line-height: 1.45;
}
.about-card__icon {
  display: grid;
  place-items: center;
}
.about-card__icon img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

@media (max-width: 920px) {
  .section-heading {
    grid-template-columns: 30px minmax(0, 1fr) auto;
    gap: 0 14px;
  }
  .roadmap-focus {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 700px) {
  .home-main {
    padding-top: 78px;
  }
  .section-heading {
    grid-template-columns: 28px minmax(0, 1fr);
    row-gap: 12px;
    padding-bottom: 20px;
  }
  .section-heading-side {
    grid-column: 2;
    justify-self: start;
    padding: 0;
  }
  .section-index {
    width: 26px;
    height: 26px;
    font-size: 8.5px;
  }
  .section-description {
    font-size: 12.5px;
  }
  .note-row {
    grid-template-columns: 30px minmax(0, 1fr) 120px 30px;
    gap: 12px;
  }
  .note-row__copy p {
    display: none;
  }
  .about-profile .section-index--about {
    width: 26px;
    height: 26px;
  }
}
@media (max-width: 560px) {
  .section-heading-side {
    grid-column: 1 / -1;
  }
  .note-row {
    grid-template-columns: 26px minmax(0, 1fr) 28px;
  }
  .note-row__media {
    grid-column: 2 / -1;
    width: 100%;
  }
  .note-row__copy h3 {
    font-size: 19px;
  }
  .about-panel {
    padding-block: 50px;
  }
}

/* v4.0 · last-mile microcopy readability */
.hero-signal small {
  font-size: 9px;
  line-height: 1.35;
}
.hero-scroll-cue small {
  font-size: 9px;
  line-height: 1.35;
}

/* ============================================================
   v4.1 · Home mobile rebuild — one clear column, no desktop choreography
   ============================================================ */
@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .home-page {
    overflow-x: clip !important;
  }
  .home-main {
    width: 100% !important;
    padding: 78px 16px 46px !important;
  }
  .hero-section {
    min-height: 0 !important;
    margin-bottom: 54px !important;
    padding: 28px 0 38px !important;
    place-items: stretch !important;
    overflow: visible !important;
  }
  .hero-layout {
    display: grid !important;
    grid-template-columns: 1fr !important;
    gap: 28px !important;
  }
  .hero-copy {
    width: 100% !important;
    max-width: 680px !important;
    padding: 0 !important;
    justify-items: start !important;
    text-align: left !important;
  }
  .hero-eyebrow {
    margin-bottom: 14px !important;
    font-size: 9.5px !important;
  }
  .hero-title {
    font-size: clamp(38px, 10.5vw, 58px) !important;
    line-height: 1.06 !important;
    letter-spacing: -0.045em !important;
  }
  .hero-description {
    margin: 18px 0 0 !important;
    max-width: 38rem !important;
    font-size: 14px !important;
    line-height: 1.72 !important;
    text-align: left !important;
  }
  .hero-actions {
    justify-content: flex-start !important;
    margin-top: 24px !important;
    gap: 8px !important;
  }
  .hero-button {
    min-width: 0 !important;
    height: 44px !important;
    padding-inline: 15px !important;
  }
  .hero-footnote {
    justify-content: flex-start !important;
    margin-top: 24px !important;
    font-size: 9px !important;
  }
  .hero-scroll-cue {
    display: none !important;
  }
  .hero-stage {
    width: min(100%, 520px) !important;
    justify-self: center !important;
    transform: none !important;
  }

  .demo-lab-section,
  .blog-section {
    margin-bottom: 58px !important;
  }
  .section-heading,
  .section-heading--lab {
    min-height: 0 !important;
    margin: 0 0 20px !important;
    padding: 0 0 18px !important;
    display: grid !important;
    grid-template-columns: 30px minmax(0, 1fr) !important;
    gap: 0 12px !important;
    align-items: start !important;
  }
  .section-heading .section-index {
    position: static !important;
    grid-column: 1;
    grid-row: 1 / span 2;
  }
  .section-heading > div:first-of-type {
    grid-column: 2;
    min-width: 0;
  }
  .section-heading-side {
    grid-column: 2;
    width: auto !important;
    align-self: start !important;
    padding: 10px 0 0 !important;
  }
  .section-heading h2 {
    font-size: clamp(28px, 7.8vw, 38px) !important;
  }
  .section-description {
    max-width: none !important;
    font-size: 13px !important;
    line-height: 1.68 !important;
  }

  .experiment-roadmap {
    margin-inline: -16px !important;
    padding: 18px 16px 16px !important;
    overflow: hidden !important;
  }
  .roadmap-topline {
    margin-bottom: 14px !important;
    align-items: flex-start !important;
  }
  .roadmap-topline__legend {
    display: none !important;
  }
  .roadmap-stations {
    display: flex !important;
    gap: 9px !important;
    margin-inline: -16px !important;
    padding: 2px 16px 16px !important;
    overflow-x: auto !important;
    scroll-snap-type: x proximity;
    scrollbar-width: none;
  }
  .roadmap-stations::-webkit-scrollbar {
    display: none;
  }
  .roadmap-line {
    display: none !important;
  }
  .roadmap-stop {
    flex: 0 0 min(76vw, 270px) !important;
    min-height: 64px !important;
    padding: 9px 11px !important;
    grid-template-columns: 38px minmax(0, 1fr) !important;
    justify-items: stretch !important;
    align-items: center !important;
    gap: 10px !important;
    border: 1px solid var(--app-border) !important;
    border-radius: 16px !important;
    background: color-mix(in srgb, var(--app-surface) 84%, transparent) !important;
    text-align: left !important;
    scroll-snap-align: start;
  }
  .roadmap-stop__node {
    width: 36px !important;
    height: 36px !important;
    box-shadow: none !important;
  }
  .roadmap-stop__copy strong {
    font-size: 12px !important;
  }
  .roadmap-stop__copy small {
    font-size: 10px !important;
    line-height: 1.35 !important;
  }
  .roadmap-focus {
    grid-template-columns: 1fr !important;
    gap: 22px !important;
    padding: 24px 0 18px !important;
  }
  .roadmap-focus__copy {
    max-width: none !important;
  }
  .roadmap-focus__copy h3 {
    font-size: clamp(28px, 8vw, 38px) !important;
  }
  .roadmap-focus__description {
    font-size: 13px !important;
  }
  .roadmap-preview {
    width: 100% !important;
    padding: 7px !important;
    border-radius: 20px !important;
    transform: none !important;
  }
  .roadmap-preview__media {
    border-radius: 14px !important;
  }

  .notes-stack {
    width: 100% !important;
  }
  .note-row {
    min-height: 0 !important;
    grid-template-columns: 28px minmax(0, 1fr) 28px !important;
    grid-template-areas: "num copy arrow" "media media media" !important;
    gap: 12px !important;
    padding: 16px 0 20px !important;
  }
  .note-row__number {
    grid-area: num !important;
  }
  .note-row__copy {
    grid-area: copy !important;
    min-width: 0 !important;
  }
  .note-row__arrow {
    grid-area: arrow !important;
  }
  .note-row__media {
    grid-area: media !important;
    width: 100% !important;
    max-width: none !important;
    aspect-ratio: 16 / 9 !important;
    margin: 2px 0 0 !important;
  }
  .note-row__meta {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 6px 10px !important;
  }
  .note-row__copy h3 {
    font-size: 19px !important;
    line-height: 1.25 !important;
  }

  .about-panel {
    display: grid !important;
    grid-template-columns: 1fr !important;
    gap: 34px !important;
    padding: 42px 0 20px !important;
    align-items: start !important;
  }
  .about-panel::after {
    opacity: 0.25 !important;
  }
  .about-profile,
  .about-directory {
    min-width: 0 !important;
    max-width: none !important;
  }
  .about-avatar-stage {
    margin-top: 22px !important;
  }
  .about-avatar {
    width: 112px !important;
    height: 112px !important;
  }
  .about-handnote {
    font-size: 24px !important;
  }
  .about-directory__heading {
    margin-bottom: 16px !important;
  }
  .about-directory__hint {
    font-size: 12px !important;
  }
  .about-links {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    gap: 10px !important;
  }
  .about-card {
    min-width: 0 !important;
    padding: 12px !important;
  }
  .about-card__copy strong {
    font-size: 12px !important;
  }
  .section-dock {
    display: none !important;
  }
}
@media (max-width: 600px) {
  .home-main {
    padding-inline: 14px !important;
  }
  .hero-stage {
    display: none !important;
  }
  .hero-title br {
    display: none;
  }
  .hero-actions {
    width: 100%;
  }
  .hero-button {
    flex: 1 1 150px;
  }
  .experiment-roadmap {
    margin-inline: -14px !important;
    padding-inline: 14px !important;
  }
  .roadmap-stations {
    margin-inline: -14px !important;
    padding-inline: 14px !important;
  }
  .roadmap-focus__signals {
    display: grid !important;
    grid-template-columns: 1fr 1fr !important;
    gap: 8px 12px !important;
  }
  .roadmap-focus__actions {
    display: grid !important;
    grid-template-columns: 1fr !important;
  }
  .roadmap-primary,
  .roadmap-secondary {
    width: 100% !important;
  }
  .about-links {
    grid-template-columns: 1fr !important;
  }
}

/* ============================================================
   v4.2 · Mobile content-first home — blog first, spectacle second
   Mobile is not a compressed desktop portfolio. Keep the parts that
   read well on touch screens and collapse the rest into simple entry points.
   ============================================================ */
.mobile-demo-teaser {
  display: none;
}

@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .home-main {
    display: flex !important;
    flex-direction: column !important;
    gap: 0 !important;
    padding-top: 72px !important;
  }
  .hero-section {
    order: 1;
  }
  #notes {
    order: 2;
  }
  #live-demo {
    order: 3;
  }
  #about {
    order: 4;
  }

  /* Home hero becomes a compact blog masthead. */
  .hero-section {
    min-height: 0 !important;
    margin-bottom: 38px !important;
    padding: 34px 0 30px !important;
    border-bottom-color: color-mix(in srgb, var(--app-border) 72%, transparent) !important;
  }
  .hero-section::before,
  .hero-aurora,
  .hero-grid,
  .hero-stage,
  .hero-scroll-cue {
    display: none !important;
  }
  .hero-layout {
    display: block !important;
  }
  .hero-copy {
    max-width: 650px !important;
    padding: 0 !important;
    justify-items: start !important;
    text-align: left !important;
  }
  .hero-eyebrow {
    margin-bottom: 12px !important;
    font-size: 9px !important;
    letter-spacing: 0.13em !important;
  }
  .hero-spark {
    width: 11px !important;
    height: 11px !important;
  }
  .hero-title {
    max-width: 12.5em !important;
    font-size: clamp(34px, 9.4vw, 48px) !important;
    line-height: 1.08 !important;
    letter-spacing: -0.045em !important;
  }
  .hero-title br {
    display: none !important;
  }
  .hero-description {
    max-width: 35em !important;
    margin-top: 14px !important;
    font-size: 13.5px !important;
    line-height: 1.72 !important;
  }
  .hero-actions {
    margin-top: 20px !important;
    gap: 8px !important;
  }
  .hero-button {
    height: 42px !important;
    padding-inline: 14px !important;
    border-radius: 13px !important;
  }
  .hero-footnote {
    display: none !important;
  }

  /* Notes become the first substantial section and read like a mobile blog list. */
  .blog-section {
    margin-bottom: 44px !important;
    scroll-margin-top: 76px !important;
  }
  #notes .section-heading {
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) auto !important;
    gap: 10px 14px !important;
    margin-bottom: 8px !important;
    padding: 0 0 14px !important;
    align-items: end !important;
  }
  #notes .section-index {
    display: none !important;
  }
  #notes .section-heading > div:first-of-type {
    grid-column: 1 !important;
  }
  #notes .section-heading-side {
    grid-column: 2 !important;
    grid-row: 1 !important;
    align-self: end !important;
    padding: 0 0 2px !important;
  }
  #notes .section-kicker {
    margin-bottom: 5px !important;
    font-size: 9px !important;
  }
  #notes .section-heading h2 {
    font-size: clamp(29px, 8vw, 38px) !important;
    line-height: 1.08 !important;
  }
  #notes .section-description {
    grid-column: 1 / -1 !important;
    margin-top: 7px !important;
    font-size: 12.5px !important;
    line-height: 1.65 !important;
  }
  #notes .section-link {
    min-height: 36px !important;
    font-size: 11px !important;
  }

  .notes-stack {
    border-top-color: color-mix(in srgb, var(--app-border-strong) 78%, transparent) !important;
  }
  .note-row {
    min-height: 104px !important;
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) 104px !important;
    grid-template-areas: "copy media" !important;
    gap: 16px !important;
    align-items: center !important;
    padding: 16px 0 !important;
  }
  .note-row__number,
  .note-row__arrow {
    display: none !important;
  }
  .note-row__copy {
    grid-area: copy !important;
    min-width: 0 !important;
  }
  .note-row__media {
    grid-area: media !important;
    width: 104px !important;
    max-width: none !important;
    aspect-ratio: 4 / 3 !important;
    margin: 0 !important;
    border-radius: 13px !important;
    box-shadow: none !important;
  }
  .note-row__meta {
    gap: 5px 8px !important;
    font-size: 8.5px !important;
    line-height: 1.35 !important;
  }
  .note-row__copy h3 {
    margin-top: 6px !important;
    font-size: clamp(17px, 4.8vw, 20px) !important;
    line-height: 1.28 !important;
    letter-spacing: -0.025em !important;
    display: -webkit-box !important;
    overflow: hidden !important;
    -webkit-box-orient: vertical !important;
    -webkit-line-clamp: 2 !important;
  }
  .note-row__copy p {
    display: none !important;
  }

  /* The desktop roadmap is intentionally not reproduced on mobile. */
  .demo-lab-section {
    margin-bottom: 44px !important;
    padding: 0 !important;
  }
  #live-demo .section-heading,
  #live-demo .experiment-roadmap {
    display: none !important;
  }
  .mobile-demo-teaser {
    position: relative;
    min-height: 92px;
    display: grid !important;
    grid-template-columns: 72px minmax(0, 1fr) 28px;
    align-items: center;
    gap: 13px;
    padding: 10px 4px 10px 0;
    border-top: 1px solid var(--app-border);
    border-bottom: 1px solid var(--app-border);
    color: inherit;
    text-decoration: none;
  }
  .mobile-demo-teaser__visual {
    position: relative;
    width: 72px;
    aspect-ratio: 1.18;
    overflow: hidden;
    border: 1px solid var(--app-border);
    border-radius: 14px;
    background: var(--app-surface-sunken);
  }
  .mobile-demo-teaser__visual img {
    width: 100%;
    height: 100%;
    display: block;
    object-fit: cover;
  }
  .mobile-demo-teaser__spark {
    position: absolute;
    right: 7px;
    top: 7px;
    width: 9px;
    height: 9px;
    background: color-mix(in srgb, var(--accent) 78%, white);
    clip-path: polygon(50% 0, 62% 38%, 100% 50%, 62% 62%, 50% 100%, 38% 62%, 0 50%, 38% 38%);
    box-shadow: 0 0 15px color-mix(in srgb, var(--accent) 30%, transparent);
  }
  .mobile-demo-teaser__copy {
    min-width: 0;
    display: grid;
    gap: 2px;
  }
  .mobile-demo-teaser__copy small {
    color: var(--accent);
    font-family: var(--font-mono);
    font-size: 8px;
    font-weight: 760;
    letter-spacing: 0.11em;
  }
  .mobile-demo-teaser__copy strong {
    color: var(--app-text);
    font-family: var(--font-display);
    font-size: 16px;
    font-weight: 650;
    line-height: 1.25;
  }
  .mobile-demo-teaser__copy > span {
    overflow: hidden;
    color: var(--app-text-soft);
    font-size: 10.5px;
    line-height: 1.4;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .mobile-demo-teaser__arrow {
    color: var(--app-text-soft);
    font-size: 18px !important;
  }

  /* About is a compact footer-like identity block on phones, not another feature section. */
  .about-panel {
    gap: 22px !important;
    margin-top: 0 !important;
    padding: 34px 0 10px !important;
    border-top: 1px solid var(--app-border) !important;
  }
  .about-panel::before,
  .about-panel::after,
  .about-profile::after,
  .about-directory::before,
  .about-directory::after {
    display: none !important;
  }
  .about-profile .section-index--about,
  .about-avatar-stage,
  .about-signature {
    display: none !important;
  }
  .about-profile__copy {
    max-width: 36em !important;
  }
  .about-profile h2 {
    font-size: 28px !important;
    line-height: 1.12 !important;
  }
  .about-lead {
    margin-top: 8px !important;
    font-size: 13px !important;
  }
  .about-intro {
    margin-top: 12px !important;
    max-width: 38em !important;
    font-size: 12.5px !important;
    line-height: 1.72 !important;
  }
  .about-directory__heading {
    margin-bottom: 10px !important;
  }
  .about-directory__heading h3,
  .about-directory__hint {
    display: none !important;
  }
  .about-directory__eyebrow {
    font-size: 8.5px !important;
  }
  .about-links {
    display: flex !important;
    grid-template-columns: none !important;
    gap: 8px !important;
    margin-inline: -16px !important;
    padding: 2px 16px 8px !important;
    overflow-x: auto !important;
    scroll-snap-type: x proximity;
    scrollbar-width: none;
  }
  .about-links::-webkit-scrollbar {
    display: none;
  }
  .about-links::before,
  .about-links::after {
    display: none !important;
  }
  .about-card,
  .about-card:nth-child(4),
  .about-card:nth-child(5) {
    flex: 0 0 112px !important;
    min-height: 68px !important;
    padding: 9px 10px !important;
    display: grid !important;
    grid-template-columns: 34px minmax(0, 1fr) !important;
    gap: 8px !important;
    align-items: center !important;
    border: 1px solid var(--app-border) !important;
    border-radius: 14px !important;
    background: color-mix(in srgb, var(--app-surface) 72%, transparent) !important;
    scroll-snap-align: start;
  }
  .about-card::before {
    display: none !important;
  }
  .about-card__icon {
    width: 34px !important;
    height: 34px !important;
    margin: 0 !important;
    transform: none !important;
    box-shadow: none !important;
  }
  .about-card__copy {
    min-width: 0 !important;
    justify-items: start !important;
    gap: 1px !important;
  }
  .about-card__copy strong {
    font-size: 11px !important;
  }
  .about-card__copy small {
    font-size: 8.5px !important;
  }
  .about-card__copy > span,
  .about-card__arrow {
    display: none !important;
  }
}

@media (max-width: 560px) {
  .home-main {
    padding-inline: 15px !important;
  }
  .hero-section {
    padding-top: 27px !important;
    margin-bottom: 34px !important;
  }
  .hero-title {
    font-size: clamp(32px, 10vw, 42px) !important;
  }
  .hero-actions {
    width: 100% !important;
  }
  .hero-button--primary {
    flex: 1 1 auto !important;
  }
  .hero-actions .hero-button:not(.hero-button--primary) {
    display: none !important;
  }

  .note-row {
    grid-template-columns: minmax(0, 1fr) 88px !important;
    gap: 13px !important;
    padding-block: 14px !important;
  }
  .note-row__media {
    width: 88px !important;
    border-radius: 12px !important;
  }
  .note-row__copy h3 {
    font-size: 17px !important;
  }

  .about-links {
    margin-inline: -15px !important;
    padding-inline: 15px !important;
  }
}

@media (max-width: 390px) {
  .home-main {
    padding-inline: 13px !important;
  }
  .hero-title {
    font-size: 31px !important;
  }
  .hero-description {
    font-size: 13px !important;
  }
  #notes .section-heading {
    grid-template-columns: 1fr !important;
  }
  #notes .section-heading-side {
    grid-column: 1 !important;
    grid-row: auto !important;
    justify-self: start !important;
  }
  .note-row {
    grid-template-columns: minmax(0, 1fr) 80px !important;
    gap: 11px !important;
  }
  .note-row__media {
    width: 80px !important;
  }
  .about-links {
    margin-inline: -13px !important;
    padding-inline: 13px !important;
  }
}

/* v4.3 · Live Lab heading — one quiet editorial marker, not a control panel. */
.section-heading--lab {
  position: sticky;
  top: 106px;
  min-height: clamp(190px, 20vw, 250px);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
  gap: 0;
  margin: 0;
  padding: 18px 0 28px;
  overflow: hidden;
  border-top: 1px solid color-mix(in srgb, var(--app-border-strong) 58%, transparent);
  isolation: isolate;
}
.section-heading--lab .section-heading__copy {
  position: relative;
  z-index: 1;
  max-width: 100%;
}
.section-heading--lab .section-kicker {
  margin-bottom: 14px;
  color: var(--accent);
  font-size: 10px;
  letter-spacing: 0.16em;
}
.section-heading--lab h2 {
  max-width: 100%;
  font-size: clamp(38px, 4.4vw, 58px);
  line-height: 1.02;
  letter-spacing: -0.055em;
}
.section-heading--lab .section-description {
  display: none;
}
.section-heading--lab .section-heading-side {
  position: relative;
  z-index: 1;
  align-self: flex-start;
  margin-top: 24px;
  padding: 0;
}
.section-heading--lab .section-link {
  min-height: 30px;
  font-size: 12px;
}
.section-heading--lab .section-index {
  position: absolute;
  z-index: 0;
  right: 6px;
  top: auto;
  bottom: -0.16em;
  width: auto;
  height: auto;
  display: block;
  margin: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  color: color-mix(in srgb, var(--accent) 8%, transparent);
  font-family: var(--font-display);
  font-size: clamp(122px, 15vw, 205px);
  font-weight: 760;
  letter-spacing: -0.12em;
  line-height: 0.76;
  opacity: 0.84;
  pointer-events: none;
  -webkit-mask-image: none;
  mask-image: none;
  -webkit-text-stroke: 1px color-mix(in srgb, var(--accent) 12%, transparent);
}

@media (max-width: 1080px) {
  .demo-lab-section {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  .section-heading--lab {
    position: relative;
    top: auto;
    min-height: clamp(185px, 24vw, 240px);
  }
}

@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  #live-demo .section-heading--lab {
    min-height: 172px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    margin: 0 0 22px !important;
    padding: 16px 0 24px !important;
  }
  #live-demo .section-heading--lab .section-heading__copy {
    max-width: calc(100% - 18px) !important;
  }
  #live-demo .section-heading--lab .section-kicker {
    margin-bottom: 13px !important;
    font-size: 9px !important;
  }
  #live-demo .section-heading--lab h2 {
    font-size: clamp(42px, 12vw, 56px) !important;
    line-height: 1.04 !important;
  }
  #live-demo .section-heading--lab .section-heading-side {
    align-self: flex-start !important;
    margin-top: 22px !important;
    padding: 0 !important;
  }
  #live-demo .section-heading--lab .section-index {
    position: absolute !important;
    right: 5px !important;
    top: auto !important;
    bottom: -0.16em !important;
    width: auto !important;
    height: auto !important;
    display: block !important;
    margin: 0 !important;
    border: 0 !important;
    background: transparent !important;
    font-size: clamp(116px, 31vw, 148px) !important;
    line-height: 0.76 !important;
  }
  #live-demo .section-heading--lab .section-description {
    display: none !important;
  }
}

/* v4.4 · Notes and About use the same restrained section signature. */
.section-heading--notes {
  position: relative;
  min-height: clamp(175px, 19vw, 225px);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
  gap: 0;
  margin: 0 0 30px;
  padding: 18px 0 28px;
  overflow: hidden;
  border-top: 1px solid color-mix(in srgb, var(--app-border-strong) 58%, transparent);
  isolation: isolate;
}
.section-heading--notes .section-heading__copy {
  position: relative;
  z-index: 1;
  max-width: calc(100% - 28px);
}
.section-heading--notes .section-kicker {
  margin-bottom: 14px;
  color: var(--accent);
  font-size: 10px;
  letter-spacing: 0.16em;
}
.section-heading--notes h2 {
  font-size: clamp(38px, 4.4vw, 58px);
  line-height: 1.02;
  letter-spacing: -0.055em;
}
.section-heading--notes .section-heading-side {
  position: relative;
  z-index: 1;
  align-self: flex-end;
  margin-top: 24px;
  padding: 0;
}
.section-heading--notes .section-link {
  min-height: 30px;
  font-size: 12px;
}
.section-heading--notes .section-index {
  position: absolute;
  z-index: 0;
  right: 6px;
  top: auto;
  bottom: -0.16em;
  width: auto;
  height: auto;
  display: block;
  margin: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  color: color-mix(in srgb, var(--accent) 8%, transparent);
  font-family: var(--font-display);
  font-size: clamp(122px, 15vw, 205px);
  font-weight: 760;
  letter-spacing: -0.12em;
  line-height: 0.76;
  opacity: 0.84;
  pointer-events: none;
  -webkit-mask-image: none;
  mask-image: none;
  -webkit-text-stroke: 1px color-mix(in srgb, var(--accent) 12%, transparent);
}

.about-profile {
  position: relative;
  min-height: clamp(280px, 24vw, 340px);
  padding: 18px 0 32px;
  overflow: hidden;
  border-top: 1px solid color-mix(in srgb, var(--app-border-strong) 58%, transparent);
  isolation: isolate;
}
.about-profile::after {
  display: none;
}
.about-profile__copy,
.about-avatar-stage {
  position: relative;
  z-index: 1;
}
.about-profile__copy {
  max-width: 430px;
}
.about-profile__copy .section-kicker {
  margin-bottom: 14px;
  font-size: 10px;
  letter-spacing: 0.16em;
}
.about-profile h2 {
  font-size: clamp(38px, 4.4vw, 58px);
  line-height: 1.02;
  letter-spacing: -0.055em;
}
.about-profile .about-lead {
  margin-top: 14px;
}
.about-profile .about-intro {
  max-width: 34ch;
  margin-top: 16px;
}
.about-profile .section-index--about {
  position: absolute;
  z-index: 0;
  top: auto;
  right: 6px;
  bottom: -0.16em;
  left: auto;
  width: auto;
  height: auto;
  display: block;
  margin: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  color: color-mix(in srgb, var(--accent) 8%, transparent);
  font-family: var(--font-display);
  font-size: clamp(122px, 15vw, 205px);
  font-weight: 760;
  letter-spacing: -0.12em;
  line-height: 0.76;
  opacity: 0.84;
  pointer-events: none;
  -webkit-mask-image: none;
  mask-image: none;
  -webkit-text-stroke: 1px color-mix(in srgb, var(--accent) 12%, transparent);
}
.about-panel::after {
  opacity: 0.22;
}

@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  #notes .section-heading--notes {
    min-height: 164px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    margin: 0 0 20px !important;
    padding: 16px 0 24px !important;
  }
  #notes .section-heading--notes .section-heading__copy {
    max-width: calc(100% - 18px) !important;
  }
  #notes .section-heading--notes .section-kicker {
    margin-bottom: 13px !important;
    font-size: 9px !important;
  }
  #notes .section-heading--notes h2 {
    font-size: clamp(42px, 12vw, 56px) !important;
    line-height: 1.04 !important;
  }
  #notes .section-heading--notes .section-heading-side {
    align-self: flex-end !important;
    margin-top: 22px !important;
    padding: 0 !important;
  }
  #notes .section-heading--notes .section-index {
    position: absolute !important;
    right: 5px !important;
    top: auto !important;
    bottom: -0.16em !important;
    width: auto !important;
    height: auto !important;
    display: block !important;
    margin: 0 !important;
    border: 0 !important;
    background: transparent !important;
    font-size: clamp(116px, 31vw, 148px) !important;
    line-height: 0.76 !important;
  }

  .about-profile {
    min-height: 226px !important;
    padding: 16px 0 24px !important;
  }
  .about-profile .section-index--about {
    position: absolute !important;
    top: auto !important;
    right: 5px !important;
    bottom: -0.16em !important;
    left: auto !important;
    width: auto !important;
    height: auto !important;
    display: block !important;
    margin: 0 !important;
    border: 0 !important;
    background: transparent !important;
    font-size: clamp(116px, 31vw, 148px) !important;
    line-height: 0.76 !important;
  }
  .about-profile__copy {
    max-width: calc(100% - 18px) !important;
  }
  .about-profile .section-kicker {
    margin-bottom: 13px !important;
    font-size: 9px !important;
  }
  .about-profile h2 {
    font-size: clamp(42px, 12vw, 56px) !important;
    line-height: 1.04 !important;
  }
  .about-profile .about-intro {
    max-width: 30ch !important;
  }
}

/* v4.5 · Slightly tighter rhythm between the four home chapters. */
.hero-section {
  margin-bottom: clamp(46px, 5.8vw, 76px);
}
.demo-lab-section {
  margin-bottom: clamp(44px, 5.4vw, 72px);
  padding-top: clamp(46px, 5.8vw, 70px);
  padding-bottom: clamp(54px, 6.6vw, 80px);
}
.blog-section {
  margin-bottom: clamp(44px, 5.4vw, 72px);
  padding-top: clamp(54px, 6.5vw, 82px);
  padding-bottom: clamp(58px, 7vw, 88px);
}
.about-panel {
  padding-top: clamp(58px, 6.8vw, 80px);
  padding-bottom: clamp(56px, 6.8vw, 80px);
}

@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .hero-section {
    margin-bottom: 30px !important;
    padding-bottom: 26px !important;
  }
  .blog-section {
    margin-bottom: 34px !important;
    padding: 38px 0 40px !important;
  }
  .demo-lab-section {
    margin-bottom: 34px !important;
    padding: 0 !important;
  }
  .about-panel {
    padding: 28px 0 8px !important;
  }
}

/* v4.6 · Chapter numbers belong to the heading flow instead of floating at a corner. */
.section-heading--lab,
.section-heading--notes,
.about-profile {
  min-height: 0;
  overflow: visible;
}
.section-heading--lab {
  padding-bottom: 0;
}
.section-heading--notes {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  grid-template-areas:
    "copy action"
    "index index";
  align-items: end;
  column-gap: 24px;
  padding-bottom: 0;
}
.section-heading--notes .section-heading__copy {
  grid-area: copy;
}
.section-heading--notes .section-heading-side {
  grid-area: action;
  align-self: end;
  margin: 0 0 4px;
}
.section-heading--lab .section-index,
.section-heading--notes .section-index,
.about-profile .section-index--about {
  position: static;
  right: auto;
  bottom: auto;
  left: auto;
  width: auto;
  height: auto;
  display: block;
  align-self: flex-start;
  margin: clamp(28px, 3.2vw, 42px) 0 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  color: color-mix(in srgb, var(--accent) 13%, var(--app-bg));
  font-family: var(--font-display);
  font-size: clamp(122px, 12vw, 180px);
  font-weight: 740;
  letter-spacing: -0.1em;
  line-height: 0.82;
  opacity: 1;
  -webkit-mask-image: none;
  mask-image: none;
  -webkit-text-stroke: 0;
}
.section-heading--notes .section-index {
  grid-area: index;
  justify-self: start;
}
.about-profile {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0;
  padding-bottom: 0;
}
.about-avatar-stage {
  margin-top: 24px;
}
.about-profile .section-index--about {
  margin-top: clamp(30px, 3.6vw, 48px);
}
.about-panel::after {
  display: none;
}

@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  #live-demo .section-heading--lab {
    min-height: 0 !important;
    padding-bottom: 0 !important;
    overflow: visible !important;
  }
  #live-demo .section-heading--lab .section-index,
  #notes .section-heading--notes .section-index,
  .about-profile .section-index--about {
    position: static !important;
    right: auto !important;
    top: auto !important;
    bottom: auto !important;
    left: auto !important;
    width: auto !important;
    height: auto !important;
    align-self: flex-start !important;
    margin: 28px 0 0 !important;
    font-size: clamp(112px, 31vw, 132px) !important;
    line-height: 0.82 !important;
  }
  #notes .section-heading--notes {
    min-height: 0 !important;
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) auto !important;
    grid-template-areas:
      "copy action"
      "index index" !important;
    align-items: end !important;
    column-gap: 14px !important;
    padding-bottom: 0 !important;
    overflow: visible !important;
  }
  #notes .section-heading--notes .section-heading__copy {
    grid-area: copy !important;
  }
  #notes .section-heading--notes .section-heading-side {
    grid-area: action !important;
    align-self: end !important;
    margin: 0 0 4px !important;
    padding: 0 !important;
  }
  #notes .section-heading--notes .section-index {
    grid-area: index !important;
    justify-self: start !important;
  }
  .about-profile {
    min-height: 0 !important;
    display: flex !important;
    padding-bottom: 0 !important;
    overflow: visible !important;
  }
}

@media (max-width: 390px) {
  #notes .section-heading--notes {
    grid-template-columns: 1fr !important;
    grid-template-areas:
      "copy"
      "action"
      "index" !important;
  }
  #notes .section-heading--notes .section-heading-side {
    justify-self: start !important;
    margin-top: 16px !important;
  }
}

/* v4.7 · Compact, task-oriented chapter headings with a handwritten accent. */
.section-heading--lab,
.section-heading--notes {
  min-height: 0;
  padding: 16px 0 0;
  overflow: visible;
  border-top: 1px solid color-mix(in srgb, var(--app-border-strong) 58%, transparent);
}
.section-heading--lab {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.section-heading--notes {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  grid-template-areas: "copy note action";
  align-items: end;
  column-gap: 24px;
  margin-bottom: 26px;
}
.section-heading--lab h2,
.section-heading--notes h2 {
  font-size: clamp(36px, 3.2vw, 48px);
  line-height: 1.05;
  letter-spacing: -0.05em;
}
.section-heading--lab .section-heading-side {
  margin-top: 20px;
}
.section-heading--notes .section-heading__copy {
  grid-area: copy;
  max-width: none;
}
.section-heading--notes .section-heading-side {
  grid-area: action;
  align-self: end;
  margin: 0 0 4px;
}
.section-handnote {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-top: 26px;
  color: color-mix(in srgb, var(--accent) 68%, var(--app-text-soft));
  font-family: Caveat, cursive;
  font-size: clamp(23px, 2vw, 29px);
  font-weight: 550;
  letter-spacing: 0.01em;
  line-height: 1;
  white-space: nowrap;
  transform: rotate(-2deg);
}
.section-handnote::after {
  content: "";
  width: 42px;
  height: 1px;
  background: linear-gradient(90deg, currentColor, transparent);
  opacity: 0.45;
  transform: rotate(-2deg);
}
.section-heading--notes .section-handnote {
  grid-area: note;
  justify-self: start;
  margin: 0 0 7px 2px;
}
.hero-description__mobile {
  display: none;
}
.about-profile {
  min-height: 0;
  padding-bottom: 0;
  overflow: visible;
}

@media (max-width: 1080px) {
  .section-heading--lab {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    grid-template-areas:
      "copy action"
      "note note";
    align-items: end;
    column-gap: 24px;
  }
  .section-heading--lab .section-heading__copy {
    grid-area: copy;
  }
  .section-heading--lab .section-heading-side {
    grid-area: action;
    align-self: end;
    margin: 0 0 4px;
  }
  .section-heading--lab .section-handnote {
    grid-area: note;
  }
}

@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .hero-description__desktop {
    display: none;
  }
  .hero-description__mobile {
    display: inline;
  }
  #live-demo .section-heading--lab,
  #notes .section-heading--notes {
    min-height: 0 !important;
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) auto !important;
    grid-template-areas:
      "copy action"
      "note note" !important;
    align-items: end !important;
    column-gap: 14px !important;
    margin: 0 0 18px !important;
    padding: 14px 0 0 !important;
    overflow: visible !important;
  }
  #live-demo .section-heading--lab .section-heading__copy,
  #notes .section-heading--notes .section-heading__copy {
    grid-area: copy !important;
    max-width: none !important;
  }
  #live-demo .section-heading--lab .section-heading-side,
  #notes .section-heading--notes .section-heading-side {
    grid-area: action !important;
    align-self: end !important;
    margin: 0 0 3px !important;
    padding: 0 !important;
  }
  #live-demo .section-heading--lab h2,
  #notes .section-heading--notes h2 {
    font-size: clamp(34px, 9vw, 44px) !important;
    line-height: 1.06 !important;
  }
  #live-demo .section-heading--lab .section-kicker,
  #notes .section-heading--notes .section-kicker {
    margin-bottom: 10px !important;
  }
  #live-demo .section-handnote,
  #notes .section-handnote {
    grid-area: note !important;
    justify-self: start !important;
    margin-top: 17px !important;
    font-size: 24px !important;
  }
  #live-demo,
  .hero-actions .hero-button:not(.hero-button--primary) {
    display: none !important;
  }
  #notes .section-heading--notes {
    grid-template-columns: auto minmax(0, 1fr) !important;
    grid-template-areas:
      "copy note"
      "action action" !important;
    row-gap: 0 !important;
  }
  #notes .section-heading--notes h2 {
    font-size: clamp(32px, 8.5vw, 38px) !important;
  }
  #notes .section-handnote {
    grid-area: note !important;
    align-self: end !important;
    justify-self: start !important;
    gap: 7px !important;
    margin: 0 0 5px !important;
    font-size: clamp(19px, 5.2vw, 22px) !important;
  }
  #notes .section-handnote::after {
    width: 26px;
  }
  #notes .section-heading--notes .section-heading-side {
    grid-area: action !important;
    justify-self: end !important;
    margin-top: 10px !important;
  }
}

@media (max-width: 390px) {
  #notes .section-heading--notes {
    grid-template-columns: auto minmax(0, 1fr) !important;
    grid-template-areas:
      "copy note"
      "action action" !important;
  }
  #notes .section-heading--notes .section-heading-side {
    justify-self: end !important;
    margin-top: 10px !important;
  }
  #notes .section-handnote {
    gap: 4px !important;
    font-size: 18px !important;
  }
  #notes .section-handnote::after {
    display: none;
  }
}

/* v4.8 · Keep brand marks sharp and give mobile social links room to breathe. */
.about-card,
.about-card__icon,
.about-card__icon img {
  transform-style: flat;
  backface-visibility: visible;
}
.about-card__icon img {
  image-rendering: auto;
}
@media (hover: hover) {
  .about-card:hover .about-card__icon {
    transform: translateY(-6px) !important;
    border-color: color-mix(in srgb, var(--accent) 24%, var(--app-border)) !important;
    box-shadow:
      0 16px 34px rgba(34, 46, 70, 0.12),
      0 0 0 4px color-mix(in srgb, var(--accent) 5%, transparent) !important;
  }
  .about-card:hover .about-card__icon img {
    transform: none !important;
  }
  .about-card:hover .about-card__copy strong {
    color: var(--accent);
  }
  .about-card__copy strong {
    transition: color 180ms ease;
  }
  .about-card__arrow {
    display: none;
  }
}

@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .about-card,
  .about-card:nth-child(4),
  .about-card:nth-child(5) {
    flex: 0 0 96px !important;
    min-height: 88px !important;
    padding: 8px 5px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 7px !important;
    border: 0 !important;
    border-radius: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
  }
  .about-card__icon {
    flex: 0 0 44px !important;
    width: 50px !important;
    min-width: 50px !important;
    height: 44px !important;
    padding: 6px 7px !important;
    margin: 0 !important;
    transform: none !important;
    border: 0 !important;
    border-radius: 14px !important;
    background: color-mix(in srgb, var(--app-surface) 88%, transparent) !important;
    box-shadow: 0 8px 22px rgba(34, 46, 70, 0.07) !important;
  }
  .about-card__icon img {
    max-width: 100% !important;
    max-height: 100% !important;
    transform: none !important;
  }
  .about-card__copy {
    width: 100% !important;
    min-width: 0 !important;
    display: grid !important;
    justify-items: center !important;
    text-align: center !important;
    gap: 1px !important;
  }
  .about-card__copy strong,
  .about-card__copy small {
    max-width: 100% !important;
  }
}

/* v5.0 · Hover stays local: no sibling dimming or large-surface lift. */
@media (hover: hover) and (pointer: fine) {
  .notes-stack:has(.note-row:hover) .note-row:not(:hover) {
    opacity: 1;
  }
  .note-row:hover {
    transform: none;
  }
  .note-row:hover .note-row__media img {
    transform: scale(1.008);
  }
  .note-row:hover .note-row__arrow {
    transform: translate(1px, -1px);
  }
  .roadmap-stop:hover .roadmap-stop__node {
    transform: none;
  }
  .roadmap-preview:hover::before {
    opacity: 0.42;
    transform: translateX(4%);
  }
  .roadmap-preview:hover .roadmap-preview__media img {
    transform: scale(1.006);
  }
  .roadmap-primary:hover {
    transform: none;
    box-shadow: 0 8px 20px color-mix(in srgb, var(--accent) 12%, transparent);
  }
  .about-card:hover {
    transform: none;
    box-shadow: none;
  }
  .about-card:hover::before {
    opacity: 0.42;
  }
  .about-card:hover .about-card__icon {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 18px rgba(34, 46, 70, 0.065) !important;
  }
}
</style>
