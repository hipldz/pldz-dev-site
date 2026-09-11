<template>
  <MobileDrawer v-model="isMobileMenuOpen" subtitle="Articles, notes, demos">
    <p>文章与教程</p>
    <p>{{ isSeriesView ? "这个专栏下的文章。" : "按专栏分门别类。" }}</p>
  </MobileDrawer>

  <HeaderBar :route-name="'教程'" :scroll="true" @toggle-mobile-menu="onToggleMobileMenu" />

  <div class="tutorials-page">
    <main class="tutorials-main">
      <section v-reveal :class="['tutorials-hero', { 'tutorials-hero--series': isSeriesView }]">
        <div class="hero-copy" data-reveal-item>
          <p class="page-kicker"><span>Library</span><i aria-hidden="true">/</i><span>Articles</span></p>
          <h1 class="page-description">{{ pageTitle }}</h1>
          <p class="page-subtitle">持续记录我做过的事情、遇到的问题，以及感兴趣的工具与信息。</p>
        </div>

        <div class="hero-stat" data-reveal-item data-motion-layer="0.65" :aria-label="`${sortedArticles.length} ${isSeriesView ? '篇文章' : '个专栏'}`">
          <strong>{{ formatCount(sortedArticles.length) }}</strong>
          <small>{{ isSeriesView ? "篇文章" : "个专栏" }}</small>
        </div>
      </section>

      <section class="archive-controls" aria-label="列表排序">
        <div class="toolbar" data-reveal-item>
          <span class="toolbar-label">Sort by</span>
          <a v-if="isSeriesView" class="back-link" href="/articles"
            ><span class="material-symbols-rounded" aria-hidden="true">arrow_back</span><span>返回</span></a
          >
          <button
            v-for="option in sortOptions"
            :key="option.value"
            :class="['sort-chip', { active: sortBy === option.value }]"
            type="button"
            @click="sortBy = option.value"
          >
            <span>{{ option.label }}</span>
          </button>
        </div>
      </section>

      <section v-if="isSeriesView" class="article-list timeline-list" aria-label="系列时间线">
        <article v-reveal v-for="article in pagedArticles" :key="article.id" class="article-row timeline-item">
          <div class="timeline-date">
            <span>{{ getDateParts(article.date).year }}</span>
            <strong>{{ getDateParts(article.date).day }}</strong>
          </div>

          <div class="timeline-node" aria-hidden="true"></div>

          <a v-cursor="'READ'" data-reveal-media class="timeline-cover" :href="getArticleLink(article)" :aria-label="article.title">
            <img data-depth-layer="0.75" :src="article.thumbnail || defaultCover" :alt="article.title" loading="lazy" decoding="async" />
          </a>

          <div class="article-copy" data-reveal-item>
            <div class="article-meta">
              <span class="meta-pill">第 {{ article.serialNo }} 篇</span>
              <span>{{ article.date || "未注明日期" }}</span>
              <span>{{ article.views || 0 }} 次浏览</span>
            </div>

            <h2>
              <a :href="getArticleLink(article)">{{ article.title }}</a>
            </h2>
            <p>{{ article.summary || "还没写摘要" }}</p>

            <div class="article-footer">
              <div class="tag-list">
                <span v-for="tag in (article.tags || []).slice(0, 2)" :key="tag" class="tag-chip">{{ tag }}</span>
              </div>
              <a class="article-link" :href="getArticleLink(article)"
                ><span>去读读</span><span class="material-symbols-rounded" aria-hidden="true">arrow_forward</span></a
              >
            </div>
          </div>
        </article>
      </section>

      <section v-else class="portfolio-archive" aria-label="文章专栏列表">
        <div class="portfolio-archive__list">
          <a
            v-for="(article, index) in pagedArticles"
            :key="article.id"
            :class="['portfolio-row', { 'is-active': activeCollectionIndex === index }]"
            :href="getArticleLink(article)"
            @mouseenter="setActiveCollection(index)"
            @focus="setActiveCollection(index)"
          >
            <span class="portfolio-row__number">{{ formatCount(index + 1) }}</span>
            <span class="portfolio-row__title">
              <small>{{ article.category || "collection" }}</small>
              <strong>{{ getCategoryTitle(article) }}</strong>
            </span>
            <span class="portfolio-row__summary">{{ article.summary || "还没写摘要" }}</span>
            <span class="portfolio-row__tags">
              <span v-for="tag in (article.tags || []).slice(0, 1)" :key="tag">{{ tag }}</span>
            </span>
            <span class="portfolio-row__arrow material-symbols-rounded" aria-hidden="true">north_east</span>
          </a>
        </div>

        <aside v-if="activeCollection" class="portfolio-preview" aria-live="polite">
          <div class="portfolio-preview__topline">
            <span>专栏预览</span>
            <span>{{ formatCount(activeCollectionIndex + 1) }} / {{ formatCount(pagedArticles.length) }}</span>
          </div>

          <a
            v-cursor="'OPEN'"
            class="portfolio-preview__media"
            :href="getArticleLink(activeCollection)"
            :aria-label="`打开 ${getCategoryTitle(activeCollection)}`"
          >
            <Transition name="collection-media" mode="out-in">
              <img
                :key="activeCollection.id || activeCollection.category"
                :src="activeCollection.thumbnail || defaultCover"
                :alt="getCategoryTitle(activeCollection)"
                loading="eager"
                decoding="async"
              />
            </Transition>
            <span class="portfolio-preview__index" aria-hidden="true">{{ formatCount(activeCollectionIndex + 1) }}</span>
            <span class="portfolio-preview__open material-symbols-rounded" aria-hidden="true">arrow_outward</span>
          </a>

          <div class="portfolio-preview__caption">
            <div class="portfolio-preview__identity">
              <span>文章专栏</span>
              <span>{{ activeCollection.category || "未分类" }}</span>
            </div>
            <h2>
              <a :href="getArticleLink(activeCollection)">{{ getCategoryTitle(activeCollection) }}</a>
            </h2>
            <p>{{ activeCollection.summary || "还没写摘要" }}</p>
            <a class="portfolio-preview__cta" :href="getArticleLink(activeCollection)"
              >进入专栏<span class="material-symbols-rounded" aria-hidden="true">arrow_forward</span></a
            >
          </div>
        </aside>
      </section>

      <footer class="tutorials-footer" aria-label="列表汇总">
        <div class="tutorials-summary">
          <span v-if="totalPages > 1">本页 {{ pagedArticles.length }} {{ isSeriesView ? "篇文章" : "个专栏" }} · 共 {{ sortedArticles.length }}</span>
          <span v-else>已展示全部 {{ sortedArticles.length }} {{ isSeriesView ? "篇文章" : "个专栏" }}</span>
          <span v-if="totalPages > 1">第 {{ currentPage }} / {{ totalPages }} 页</span>
        </div>

        <nav v-if="totalPages > 1" class="pagination" aria-label="文章分页">
          <button class="page-button" type="button" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">上一页</button>
          <button v-for="page in visiblePages" :key="page" :class="['page-number', { active: page === currentPage }]" type="button" @click="goToPage(page)">
            {{ page }}
          </button>
          <button class="page-button" type="button" :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">下一页</button>
        </nav>
      </footer>
    </main>

    <FooterBar />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import FooterBar from "../components/FooterBar.vue";
import HeaderBar from "../components/HeaderBar.vue";
import MobileDrawer from "../components/MobileDrawer.vue";
import { getArticleIntros, getArticlesByCategory } from "../utils/apis";

const defaultCover = "/404.jpg";
const isMobileMenuOpen = ref(false);
const route = useRoute();

const sortBy = ref("date");
const articles = ref([]);
const currentPage = ref(1);
const activeCollectionIndex = ref(0);
const pageSize = 8;

const activeCategory = computed(() => {
  const value = route.params.category;
  return Array.isArray(value) ? value[0] || "" : value || "";
});

const isSeriesView = computed(() => Boolean(activeCategory.value));
const pageTitle = computed(() => (isSeriesView.value ? `${activeCategory.value} 专栏` : "全部专栏"));
const formatCount = (value) => String(value || 0).padStart(2, "0");
const sortOptions = computed(() => {
  const options = [
    { label: "按时间", value: "date" },
    { label: "按浏览", value: "views" },
  ];

  if (isSeriesView.value) {
    return [...options, { label: "按序号", value: "serial" }];
  }

  return options;
});

const parseDate = (value) => {
  const time = new Date(value || "").getTime();
  return Number.isNaN(time) ? 0 : time;
};

const sortedArticles = computed(() => {
  const cloned = [...articles.value];

  if (sortBy.value === "views") {
    return cloned.sort((a, b) => (b.views || 0) - (a.views || 0) || parseDate(b.date) - parseDate(a.date));
  }

  if (sortBy.value === "serial") {
    return cloned.sort((a, b) => (a.serialNo || 0) - (b.serialNo || 0) || parseDate(b.date) - parseDate(a.date));
  }

  return cloned.sort((a, b) => parseDate(b.date) - parseDate(a.date) || (b.views || 0) - (a.views || 0));
});

const totalPages = computed(() => Math.max(1, Math.ceil(sortedArticles.value.length / pageSize)));

const pagedArticles = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  return sortedArticles.value.slice(start, start + pageSize);
});

const activeCollection = computed(() => pagedArticles.value[activeCollectionIndex.value] || pagedArticles.value[0] || null);

const setActiveCollection = (index) => {
  if (index < 0 || index >= pagedArticles.value.length) return;
  activeCollectionIndex.value = index;
};

const visiblePages = computed(() => {
  const pages = [];
  const start = Math.max(1, currentPage.value - 2);
  const end = Math.min(totalPages.value, start + 4);

  for (let page = start; page <= end; page += 1) {
    pages.push(page);
  }

  return pages;
});

const getArticleLink = (article) => {
  if (isSeriesView.value) {
    return `/article/${article.id}`;
  }

  return `/articles/${encodeURIComponent(article.category || "")}`;
};

const getCategoryTitle = (article) => {
  return article.category || article.title || "未命名专栏";
};

const getDateParts = (value) => {
  if (!value) {
    return { year: "----", day: "--.--" };
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return { year: String(value).slice(0, 4) || "----", day: String(value).slice(5, 10) || "--.--" };
  }

  return {
    year: String(date.getFullYear()),
    day: `${String(date.getMonth() + 1).padStart(2, "0")}.${String(date.getDate()).padStart(2, "0")}`,
  };
};

const goToPage = (page) => {
  currentPage.value = Math.min(totalPages.value, Math.max(1, page));
  activeCollectionIndex.value = 0;
  window.scrollTo({ top: 0, behavior: "smooth" });
};

const onToggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

const loadArticles = async () => {
  sortBy.value = sortBy.value === "serial" && !isSeriesView.value ? "date" : sortBy.value;
  const res = isSeriesView.value ? await getArticlesByCategory(activeCategory.value) : await getArticleIntros();
  articles.value = Array.isArray(res) ? res : [];
  currentPage.value = 1;
  activeCollectionIndex.value = 0;
};

onMounted(loadArticles);

watch(sortBy, () => {
  currentPage.value = 1;
  activeCollectionIndex.value = 0;
});

watch(activeCategory, loadArticles);
</script>

<style scoped>
.tutorials-page {
  min-height: 100vh;
  background: var(--app-bg);
}

.tutorials-main {
  width: min(1240px, calc(100% - 2 * var(--app-page-gutter)));
  margin: 0 auto;
  padding: 96px 0 72px;
}

.tutorials-hero {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  align-items: center;
  gap: clamp(18px, 2.6vw, 34px);
  min-height: 0;
  padding: 18px 4px 24px;
  border-bottom: 1px solid var(--app-border);
}

.tutorials-hero::before {
  content: "";
  position: absolute;
  left: 4px;
  bottom: -1px;
  width: 52px;
  height: 2px;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--accent), color-mix(in srgb, var(--accent) 15%, transparent));
}

.tutorials-hero::after {
  content: "";
  position: absolute;
  z-index: -1;
  right: 12%;
  top: -18px;
  width: 160px;
  height: 80px;
  opacity: 0.22;
  background-image: radial-gradient(circle, color-mix(in srgb, var(--accent) 34%, transparent) 1px, transparent 1.2px);
  background-size: 12px 12px;
  pointer-events: none;
}

.hero-copy {
  display: grid;
  gap: 6px;
  max-width: 650px;
}
.page-kicker {
  margin: 0 0 1px;
  color: var(--accent);
  font-size: 9.75px;
  font-weight: 760;
  letter-spacing: 0.19em;
  text-transform: uppercase;
}
.page-description {
  margin: 0;
  color: var(--app-text);
  font-family: var(--font-display);
  font-weight: 670;
  font-size: clamp(34px, 3.5vw, 44px);
  line-height: 1.14;
  letter-spacing: -0.045em;
}
.page-subtitle {
  max-width: 590px;
  margin: 3px 0 0;
  color: var(--app-text-muted);
  font-size: 13px;
  line-height: 1.68;
}

.hero-stat {
  position: relative;
  min-width: 102px;
  padding: 2px 22px 3px;
  display: grid;
  grid-template-columns: auto auto;
  align-items: end;
  justify-content: center;
  gap: 0 7px;
  border-left: 1px solid var(--app-border);
  border-right: 1px solid var(--app-border);
  color: var(--app-text-soft);
  text-align: left;
}
.hero-stat::after {
  content: "";
  position: absolute;
  right: 8px;
  top: -4px;
  width: 8px;
  height: 8px;
  opacity: 0.36;
  background: var(--accent);
  clip-path: polygon(50% 0, 62% 38%, 100% 50%, 62% 62%, 50% 100%, 38% 62%, 0 50%, 38% 38%);
}
.hero-stat > span {
  grid-column: 1 / -1;
  margin-bottom: 2px;
  color: var(--app-text-soft);
  font-size: 8.5px;
  font-weight: 740;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.hero-stat strong {
  color: var(--app-text);
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 660;
  line-height: 1;
  letter-spacing: -0.04em;
}
.hero-stat small {
  padding-bottom: 1px;
  font-size: 10px;
  line-height: 1.2;
  white-space: nowrap;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
}

.back-link,
.sort-chip {
  min-height: 36px;
  padding: 0 11px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 1px solid var(--app-border);
  border-radius: 12px;
  background: color-mix(in srgb, var(--app-surface) 90%, transparent);
  color: var(--app-text-muted);
  font-size: 11.5px;
  font-weight: 620;
  text-decoration: none;
  cursor: pointer;
  transition:
    border-color 180ms var(--app-ease),
    background-color 180ms var(--app-ease),
    color 180ms var(--app-ease),
    transform 180ms var(--app-ease);
}
.back-link .material-symbols-rounded,
.sort-chip .material-symbols-rounded {
  font-size: 15px;
}
.back-link:hover,
.sort-chip:hover {
  border-color: var(--app-border-strong);
  background: var(--app-surface);
  color: var(--app-text);
}
.sort-chip.active {
  border-color: var(--accent-line);
  background: var(--accent-weak);
  color: var(--accent);
}

.tutorials-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 4px 14px;
  color: var(--app-text-soft);
  font-size: 12px;
  font-weight: 560;
}

.article-list {
  display: grid;
}
.category-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  padding-top: 4px;
}
.timeline-list {
  position: relative;
  gap: 0;
  padding-top: 8px;
}
.timeline-list::before {
  content: "";
  position: absolute;
  top: 26px;
  bottom: 28px;
  left: 122px;
  width: 1px;
  transform: translateX(-50%);
  background: var(--app-border);
}

/* Media-first editorial cards: the cover keeps its composition instead of being hard-cropped. */
.category-card {
  min-width: 0;
  min-height: 246px;
  overflow: hidden;
  display: grid;
  grid-template-columns: minmax(0, 0.49fr) minmax(0, 0.51fr);
  border: 1px solid var(--app-border);
  border-radius: 22px;
  background: var(--app-surface);
  box-shadow: 0 1px 0 rgba(30, 40, 58, 0.015);
  transition:
    transform 220ms var(--app-ease),
    border-color 180ms var(--app-ease),
    box-shadow 220ms var(--app-ease);
}

.article-cover {
  position: relative;
  min-width: 0;
  min-height: 246px;
  padding: 9px;
  display: grid;
  place-items: center;
  overflow: hidden;
  border-right: 1px solid var(--app-border);
  background: color-mix(in srgb, var(--app-surface-sunken) 66%, var(--brand-tint));
}
.article-cover::after {
  content: "";
  position: absolute;
  inset: 9px;
  border-radius: 16px;
  background: linear-gradient(180deg, transparent 74%, rgba(17, 29, 48, 0.07));
  opacity: 0;
  pointer-events: none;
  transition: opacity 220ms var(--app-ease);
}
.article-cover img {
  width: 100%;
  height: 100%;
  max-height: 228px;
  display: block;
  border-radius: 16px;
  object-fit: contain;
  object-position: center;
  transition: transform 360ms var(--app-ease);
}
.article-cover__action {
  position: absolute;
  z-index: 2;
  right: 16px;
  top: 16px;
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.91);
  color: #3c4655;
  font-size: 17px;
  box-shadow: 0 7px 18px rgba(22, 31, 46, 0.075);
  transition:
    transform 200ms var(--app-ease),
    background-color 200ms var(--app-ease);
}

.article-copy {
  min-width: 0;
}
.category-card .article-copy {
  min-height: 246px;
  padding: 22px 20px 19px;
  display: flex;
  flex-direction: column;
}
.article-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 7px 10px;
  color: var(--app-text-soft);
  font-size: 10.75px;
}
.meta-pill,
.tag-chip {
  min-height: 24px;
  padding: 0 8px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  border: 0;
  border-radius: 999px;
  background: var(--app-surface-sunken);
  color: var(--app-text-muted);
  font-size: 10px;
  font-weight: 620;
}
.meta-pill {
  background: var(--accent-weak);
  color: var(--accent);
}
.meta-pill .material-symbols-rounded {
  font-size: 13px;
}
.article-copy h2 {
  margin: 11px 0 0;
  color: var(--app-text);
  font-size: clamp(18px, 1.7vw, 21px);
  font-weight: 660;
  letter-spacing: -0.03em;
  line-height: 1.36;
}
.article-copy h2 a {
  color: inherit;
  text-decoration: none;
}
.article-copy h2 a:hover {
  color: var(--accent);
}
.article-copy p {
  margin: 8px 0 0;
  color: var(--app-text-muted);
  font-size: 12.5px;
  line-height: 1.72;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.article-footer {
  margin-top: auto;
  padding-top: 17px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
}
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  max-height: 54px;
  overflow: hidden;
}
.article-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--app-text);
  text-decoration: none;
  font-size: 12px;
  font-weight: 680;
  white-space: nowrap;
}
.article-link .material-symbols-rounded {
  font-size: 16px;
  transition: transform 180ms var(--app-ease);
}
.article-link:hover {
  color: var(--accent);
}
.article-link:hover .material-symbols-rounded {
  transform: translateX(2px);
}

@media (hover: hover) and (prefers-reduced-motion: no-preference) {
  .category-card:hover {
    transform: translateY(-3px);
    border-color: var(--accent-line);
    box-shadow: 0 16px 38px rgba(31, 40, 58, 0.055);
  }
  .category-card:hover .article-cover img {
    transform: scale(1.012);
  }
  .category-card:hover .article-cover::after {
    opacity: 1;
  }
  .category-card:hover .article-cover__action {
    transform: translate(2px, -2px);
    background: #fff;
  }
}

.timeline-item {
  position: relative;
  display: grid;
  grid-template-columns: 82px 44px 168px minmax(0, 1fr);
  gap: 0 18px;
  padding: 20px 0 28px;
}
.timeline-date {
  display: grid;
  align-content: start;
  justify-items: end;
  gap: 4px;
  padding-top: 4px;
  color: var(--app-text-soft);
  font-size: 10.5px;
  line-height: 1.1;
}
.timeline-date strong {
  color: var(--app-text);
  font-size: 16px;
  font-weight: 650;
}
.timeline-node {
  position: relative;
  z-index: 1;
  justify-self: center;
  width: 11px;
  height: 11px;
  margin-top: 8px;
  border: 3px solid var(--accent);
  border-radius: 50%;
  background: var(--app-bg);
}
.timeline-cover {
  align-self: start;
  overflow: hidden;
  aspect-ratio: 16/10;
  border: 1px solid var(--app-border);
  border-radius: 16px;
  background: var(--app-surface);
}
.timeline-cover img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
  transition: transform 240ms var(--app-ease);
}
.timeline-cover:hover img {
  transform: scale(1.025);
}
.timeline-item .article-copy {
  padding: 0 0 26px;
  border-bottom: 1px solid var(--app-border);
}
.timeline-item .article-copy h2 {
  margin-top: 9px;
}
.timeline-item .article-footer {
  padding-top: 14px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  padding-top: 30px;
  margin-top: 12px;
  border-top: 1px solid var(--app-border);
}
.page-button,
.page-number {
  height: 38px;
  min-width: 38px;
  padding: 0 13px;
  border: 1px solid var(--app-border);
  border-radius: 999px;
  background: var(--app-surface);
  color: var(--app-text-muted);
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
}
.page-button:hover,
.page-number:hover {
  border-color: var(--app-border-strong);
  color: var(--app-text);
}
.page-button:disabled {
  opacity: 0.42;
  cursor: not-allowed;
}
.page-number.active {
  border-color: var(--accent-line);
  background: var(--accent-weak);
  color: var(--accent);
}

@media (max-width: 1080px) {
  .category-grid {
    grid-template-columns: 1fr;
  }
  .category-card {
    grid-template-columns: minmax(280px, 0.42fr) minmax(0, 0.58fr);
  }
}

@media (max-width: 980px) {
  .tutorials-main {
    padding-top: 88px;
  }
  .tutorials-hero {
    grid-template-columns: 1fr auto;
    align-items: end;
    gap: 18px;
    padding-top: 18px;
  }
  .hero-copy {
    grid-column: 1 / -1;
  }
  .hero-stat {
    justify-self: start;
    border-left: 0;
    padding-left: 0;
  }
  .toolbar {
    justify-content: flex-start;
  }
  .timeline-list::before {
    left: 97px;
  }
  .timeline-item {
    grid-template-columns: 66px 30px 146px minmax(0, 1fr);
    gap: 0 14px;
  }
}

@media (max-width: 680px) {
  .tutorials-main {
    padding-top: 78px;
    padding-bottom: 54px;
  }
  .tutorials-hero {
    grid-template-columns: 1fr;
    gap: 14px;
    padding: 14px 2px 20px;
  }
  .hero-stat {
    display: none;
  }
  .page-description {
    font-size: 30px;
  }
  .page-subtitle {
    font-size: 12.5px;
  }
  .toolbar {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .sort-chip,
  .back-link {
    min-width: 0;
    padding-inline: 8px;
  }
  .tutorials-summary {
    padding-top: 17px;
    font-size: 11.5px;
  }
  .category-grid {
    grid-template-columns: 1fr;
    gap: 14px;
  }
  .category-card {
    grid-template-columns: 1fr;
    min-height: 0;
    border-radius: 20px;
  }
  .article-cover {
    min-height: 0;
    aspect-ratio: 16 / 9;
    padding: 7px;
    border-right: 0;
    border-bottom: 1px solid var(--app-border);
  }
  .article-cover::after {
    inset: 7px;
    border-radius: 15px;
  }
  .article-cover img {
    max-height: none;
    border-radius: 15px;
  }
  .category-card .article-copy {
    min-height: 205px;
    padding: 19px 18px 17px;
  }
  .article-footer {
    align-items: center;
  }
  .timeline-list {
    padding-top: 2px;
  }
  .timeline-list::before {
    left: 8px;
  }
  .timeline-item {
    grid-template-columns: 20px minmax(0, 1fr);
    padding: 14px 0 20px;
    gap: 0;
  }
  .timeline-date {
    grid-column: 2;
    grid-row: 1;
    justify-items: start;
    display: flex;
    align-items: baseline;
    gap: 6px;
    padding: 0 0 8px;
  }
  .timeline-date strong {
    font-size: 13px;
  }
  .timeline-node {
    grid-column: 1;
    grid-row: 1 / span 3;
    width: 9px;
    height: 9px;
    margin-top: 4px;
    border-width: 2px;
  }
  .timeline-cover {
    grid-column: 2;
    grid-row: 2;
    width: min(100%, 280px);
    margin-bottom: 12px;
  }
  .timeline-item .article-copy {
    grid-column: 2;
    grid-row: 3;
    padding-bottom: 28px;
  }
  .pagination {
    justify-content: flex-start;
  }
}

@media (max-width: 420px) {
  .toolbar {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .sort-chip .material-symbols-rounded {
    display: none;
  }
  .tutorials-summary {
    align-items: flex-start;
    flex-direction: column;
    gap: 3px;
  }
  .article-footer {
    align-items: flex-start;
    flex-direction: column;
  }
}

/* ============================================================
   v3.1 · collection gallery — covers lead, chrome recedes
   ============================================================ */
.tutorials-main {
  max-width: var(--app-page-width);
}
.tutorials-hero {
  grid-template-columns: minmax(0, 1fr) auto;
  gap: clamp(24px, 4vw, 54px);
  padding: 32px 4px 30px;
  border-bottom-color: color-mix(in srgb, var(--app-border-strong) 58%, transparent);
}
.tutorials-hero::before {
  width: 66px;
  background: linear-gradient(90deg, var(--accent), transparent);
}
.tutorials-hero::after {
  right: 3%;
  top: -8px;
  width: 210px;
  height: 110px;
  opacity: 0.11;
  background-size: 14px 14px;
}
.hero-copy {
  max-width: 720px;
}
.page-description {
  font-size: clamp(38px, 4.1vw, 52px);
}
.page-subtitle {
  max-width: 650px;
  font-size: 13.5px;
}
.hero-stat {
  min-width: 138px;
  padding: 10px 0 10px 24px;
  border-left: 1px solid var(--app-border);
  border-right: 0;
  justify-content: start;
}
.hero-stat::after {
  right: auto;
  left: -4px;
  top: 8px;
  width: 7px;
  height: 7px;
}
.hero-stat strong {
  font-size: 34px;
}
.toolbar {
  grid-column: 1 / -1;
  justify-content: flex-start;
  gap: 7px;
  padding-top: 2px;
}
.back-link,
.sort-chip {
  min-height: 34px;
  border-color: transparent;
  border-radius: 999px;
  background: var(--app-surface-sunken);
}
.back-link:hover,
.sort-chip:hover {
  border-color: transparent;
  background: var(--app-surface);
  box-shadow: 0 4px 14px rgba(34, 45, 65, 0.04);
}
.sort-chip.active {
  border-color: transparent;
  background: var(--accent-weak);
  box-shadow: inset 0 0 0 1px var(--accent-line);
}
.tutorials-summary {
  padding: 24px 4px 18px;
}

.category-grid {
  gap: clamp(28px, 3vw, 38px) clamp(20px, 2.4vw, 30px);
  padding-top: 8px;
}
.category-card {
  position: relative;
  min-height: 0;
  overflow: visible;
  grid-template-columns: 1fr;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}
.category-card::before {
  content: "";
  position: absolute;
  z-index: -1;
  left: 8%;
  right: 8%;
  top: 34%;
  height: 48%;
  border-radius: 42px;
  background: radial-gradient(ellipse at 50% 10%, color-mix(in srgb, var(--accent) 5%, transparent), transparent 72%);
  opacity: 0;
  transform: translateY(8px);
  transition:
    opacity 260ms ease,
    transform 420ms cubic-bezier(0.16, 1, 0.3, 1);
}
.article-cover {
  min-height: 0;
  aspect-ratio: 16 / 8.8;
  padding: 10px;
  border: 1px solid color-mix(in srgb, var(--app-border-strong) 62%, transparent);
  border-radius: 25px;
  background: linear-gradient(145deg, color-mix(in srgb, var(--brand-tint) 70%, var(--app-surface-sunken)), var(--app-surface-sunken));
  box-shadow: 0 18px 46px rgba(32, 44, 68, 0.055);
  transition:
    transform 360ms cubic-bezier(0.16, 1, 0.3, 1),
    box-shadow 360ms ease,
    border-color 220ms ease;
}
.article-cover::after {
  inset: 10px;
  border-radius: 17px;
}
.article-cover img {
  max-height: none;
  border-radius: 17px;
  object-fit: contain;
}
.article-cover__action {
  right: 18px;
  top: 18px;
  width: 36px;
  height: 36px;
  border-color: rgba(255, 255, 255, 0.58);
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(9px);
}
.category-card .article-copy {
  min-height: 176px;
  padding: 17px 5px 0;
}
.article-copy h2 {
  margin-top: 9px;
  font-size: clamp(19px, 1.8vw, 23px);
}
.article-copy p {
  max-width: 92%;
  -webkit-line-clamp: 2;
}
.article-footer {
  padding-top: 14px;
}
.article-footer .tag-list .tag-chip:nth-child(n + 2) {
  display: none;
}
.article-link {
  color: var(--accent);
  font-size: 11.5px;
  letter-spacing: 0.01em;
}
@media (hover: hover) and (prefers-reduced-motion: no-preference) {
  .category-card:hover {
    transform: none;
    border-color: transparent;
    box-shadow: none;
  }
  .category-card:hover::before {
    opacity: 1;
    transform: none;
  }
  .category-card:hover .article-cover {
    transform: translateY(-5px);
    border-color: color-mix(in srgb, var(--accent-line) 80%, var(--app-border));
    box-shadow: 0 28px 64px rgba(35, 48, 75, 0.105);
  }
  .category-card:hover .article-cover img {
    transform: scale(1.008);
  }
}

/* Series view stays reading-first, but gets cleaner nodes and spacing. */
.timeline-list::before {
  background: color-mix(in srgb, var(--app-border-strong) 68%, transparent);
}
.timeline-node {
  border-width: 2px;
  box-shadow: 0 0 0 5px color-mix(in srgb, var(--accent) 5%, transparent);
}
.timeline-cover {
  border-radius: 18px;
  box-shadow: 0 10px 30px rgba(33, 45, 68, 0.045);
}
.timeline-item .article-copy {
  border-bottom-color: color-mix(in srgb, var(--app-border) 78%, transparent);
}

@media (max-width: 980px) {
  .tutorials-hero {
    grid-template-columns: 1fr auto;
    padding-top: 24px;
  }
  .hero-copy {
    grid-column: auto;
  }
  .hero-stat {
    justify-self: end;
  }
  .toolbar {
    grid-column: 1 / -1;
  }
}
@media (max-width: 680px) {
  .tutorials-hero {
    grid-template-columns: 1fr;
    padding: 18px 2px 22px;
  }
  .page-description {
    font-size: 32px;
  }
  .hero-stat {
    display: none;
  }
  .toolbar {
    grid-column: auto;
    display: flex;
    overflow-x: auto;
    scrollbar-width: none;
  }
  .toolbar::-webkit-scrollbar {
    display: none;
  }
  .sort-chip,
  .back-link {
    flex: 0 0 auto;
  }
  .category-grid {
    gap: 30px;
  }
  .category-card {
    grid-template-columns: 1fr;
    border-radius: 0;
  }
  .article-cover {
    aspect-ratio: 16 / 9;
    padding: 7px;
    border-right: 1px solid color-mix(in srgb, var(--app-border-strong) 62%, transparent);
    border-bottom: 1px solid color-mix(in srgb, var(--app-border-strong) 62%, transparent);
  }
  .article-cover::after {
    inset: 7px;
  }
  .category-card .article-copy {
    min-height: 0;
    padding: 15px 3px 0;
  }
  .article-copy p {
    max-width: 100%;
  }
}

/* ============================================================
   v3.2 · Collection gallery — editorial rhythm without giant cards
   ============================================================ */
.category-grid {
  counter-reset: collection;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: clamp(36px, 4vw, 54px) clamp(20px, 2.5vw, 32px);
  align-items: start;
}
.category-card {
  counter-increment: collection;
  grid-column: span 6;
}
.category-card:nth-child(4n + 1) {
  grid-column: span 7;
}
.category-card:nth-child(4n + 2) {
  grid-column: span 5;
}
.category-card:nth-child(4n + 3) {
  grid-column: span 5;
}
.category-card:nth-child(4n + 4) {
  grid-column: span 7;
}
.category-card:nth-child(4n + 2) .article-cover,
.category-card:nth-child(4n + 3) .article-cover {
  aspect-ratio: 4 / 3;
}
.category-card .article-cover {
  position: relative;
  border-radius: 28px;
  box-shadow: 0 20px 54px rgba(32, 44, 68, 0.06);
}
.category-card .article-cover::before {
  content: "COLLECTION  " counter(collection, decimal-leading-zero);
  position: absolute;
  z-index: 5;
  left: 15px;
  bottom: 14px;
  min-height: 26px;
  padding: 0 9px;
  display: inline-flex;
  align-items: center;
  border: 1px solid rgba(255, 255, 255, 0.58);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.82);
  color: #586574;
  font-family: var(--font-mono);
  font-size: 7.5px;
  font-weight: 760;
  letter-spacing: 0.1em;
  box-shadow: 0 8px 22px rgba(31, 42, 64, 0.055);
  backdrop-filter: blur(8px);
}
.category-card .article-copy {
  padding-top: 16px;
}
.category-card .article-copy h2 {
  font-size: clamp(18px, 1.8vw, 23px);
}
.category-card .article-copy p {
  -webkit-line-clamp: 2;
  opacity: 0.78;
}
.category-card .article-footer {
  opacity: 0.66;
  transition: opacity 220ms ease;
}
@media (hover: hover) and (prefers-reduced-motion: no-preference) {
  .category-card {
    transition: opacity 260ms ease;
  }
  .category-grid:has(.category-card:hover) .category-card:not(:hover) {
    opacity: 0.66;
  }
  .category-card:hover .article-footer {
    opacity: 1;
  }
}
@media (max-width: 1040px) {
  .category-card,
  .category-card:nth-child(4n + 1),
  .category-card:nth-child(4n + 2),
  .category-card:nth-child(4n + 3),
  .category-card:nth-child(4n + 4) {
    grid-column: span 6;
  }
  .category-card:nth-child(4n + 2) .article-cover,
  .category-card:nth-child(4n + 3) .article-cover {
    aspect-ratio: 16 / 9;
  }
}
@media (max-width: 720px) {
  .category-grid {
    grid-template-columns: 1fr;
  }
  .category-card,
  .category-card:nth-child(4n + 1),
  .category-card:nth-child(4n + 2),
  .category-card:nth-child(4n + 3),
  .category-card:nth-child(4n + 4) {
    grid-column: auto;
  }
  .category-card .article-cover::before {
    left: 12px;
    bottom: 11px;
  }
  .category-card .article-footer {
    opacity: 1;
  }
}

/* ============================================================
   v3.3 · Collection density — three-up gallery on wide screens
   ============================================================ */
.category-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: clamp(34px, 3.4vw, 46px) clamp(18px, 2vw, 24px);
}
.category-card,
.category-card:nth-child(4n + 1),
.category-card:nth-child(4n + 2),
.category-card:nth-child(4n + 3),
.category-card:nth-child(4n + 4) {
  grid-column: auto;
}
.category-card:nth-child(4n + 2) .article-cover,
.category-card:nth-child(4n + 3) .article-cover,
.category-card .article-cover {
  aspect-ratio: 16 / 10;
  padding: 8px;
  border-radius: 22px;
  box-shadow: 0 14px 38px rgba(32, 44, 68, 0.052);
}
.category-card .article-cover::after {
  inset: 8px;
  border-radius: 15px;
}
.category-card .article-cover img {
  border-radius: 15px;
}
.category-card .article-cover::before {
  left: 12px;
  bottom: 11px;
  min-height: 23px;
  padding-inline: 8px;
  font-size: 6.8px;
}
.article-cover__action {
  right: 13px;
  top: 13px;
  width: 31px;
  height: 31px;
}
.category-card .article-copy {
  min-height: 0;
  padding: 13px 3px 0;
}
.category-card .article-copy h2 {
  margin-top: 6px;
  font-size: clamp(16.5px, 1.45vw, 19px);
}
.category-card .article-copy p {
  margin-top: 6px;
  font-size: 11.75px;
  line-height: 1.62;
  -webkit-line-clamp: 2;
}
.category-card .article-footer {
  padding-top: 8px;
  opacity: 0.58;
}
@media (hover: hover) and (prefers-reduced-motion: no-preference) {
  .category-grid:has(.category-card:hover) .category-card:not(:hover) {
    opacity: 0.77;
  }
  .category-card:hover .article-cover {
    transform: translateY(-4px);
    box-shadow: 0 22px 50px rgba(35, 48, 75, 0.09);
  }
}
@media (max-width: 1000px) {
  .category-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 720px) {
  .category-grid {
    grid-template-columns: 1fr;
    gap: 31px;
  }
  .category-card .article-footer {
    opacity: 1;
  }
}

/* ============================================================
   v3.4 · Collection portfolio finish — soft frame + caption shelf
   ============================================================ */
.category-grid {
  gap: clamp(42px, 4.2vw, 58px) clamp(20px, 2.2vw, 28px);
}
.category-card {
  isolation: isolate;
}
.category-card:nth-child(3n + 2) {
  padding-top: 18px;
}
.category-card::before {
  left: 7%;
  right: 7%;
  top: 18px;
  height: 48%;
  border-radius: 44px;
  background: radial-gradient(ellipse at 50% 16%, color-mix(in srgb, var(--accent) 8%, transparent), transparent 72%);
  opacity: 0.55;
  transform: translateY(8px) scale(0.96);
}
.category-card:nth-child(4n + 2) .article-cover,
.category-card:nth-child(4n + 3) .article-cover,
.category-card .article-cover {
  box-sizing: border-box;
  padding: 7px;
  border-radius: 30px;
  border-color: color-mix(in srgb, var(--app-border-strong) 54%, transparent);
  background:
    radial-gradient(circle at 18% 8%, color-mix(in srgb, var(--accent) 6%, transparent), transparent 38%),
    linear-gradient(145deg, color-mix(in srgb, var(--app-surface) 72%, var(--brand-tint)), var(--app-surface-sunken));
  box-shadow:
    0 18px 44px rgba(35, 47, 70, 0.065),
    0 2px 8px rgba(35, 47, 70, 0.025),
    inset 0 1px 0 rgba(255, 255, 255, 0.72);
}
.category-card .article-cover::after {
  inset: 7px;
  border-radius: 22px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.04), transparent 50%, rgba(18, 29, 45, 0.1)),
    radial-gradient(420px circle at var(--spot-x, 50%) var(--spot-y, 40%), color-mix(in srgb, var(--accent) 7%, transparent), transparent 68%);
  opacity: 0.42;
}
.category-card .article-cover img {
  border-radius: 22px;
}
.category-card .article-cover::before {
  left: 15px;
  bottom: 14px;
  min-height: 24px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 9px 24px rgba(24, 35, 54, 0.075);
}
.article-cover__action {
  right: 15px;
  top: 15px;
  width: 33px;
  height: 33px;
  border-radius: 13px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow:
    0 9px 24px rgba(24, 35, 54, 0.075),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
}
.category-card .article-copy {
  position: relative;
  z-index: 4;
  min-height: 0;
  margin: -15px 11px 0;
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
.category-card .article-copy::before {
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
.category-card .article-footer {
  opacity: 0.66;
}
@media (hover: hover) and (prefers-reduced-motion: no-preference) {
  .category-card:hover::before {
    opacity: 0.95;
    transform: translateY(0) scale(1);
  }
  .category-card:hover .article-cover {
    transform: translateY(-6px) scale(1.006);
    box-shadow:
      0 29px 68px rgba(35, 48, 75, 0.115),
      0 4px 14px rgba(35, 48, 75, 0.04);
  }
  .category-card:hover .article-copy {
    transform: translateY(-3px);
    border-color: color-mix(in srgb, var(--accent-line) 72%, var(--app-border));
    box-shadow:
      0 21px 46px rgba(31, 43, 65, 0.09),
      inset 0 1px 0 rgba(255, 255, 255, 0.82);
  }
}
@media (max-width: 1000px) {
  .category-card:nth-child(3n + 2) {
    padding-top: 0;
  }
  .category-card:nth-child(2n + 2) {
    padding-top: 14px;
  }
}
@media (max-width: 720px) {
  .category-card:nth-child(2n + 2) {
    padding-top: 0;
  }
  .category-card:nth-child(4n + 2) .article-cover,
  .category-card:nth-child(4n + 3) .article-cover,
  .category-card .article-cover {
    padding: 6px;
    border-radius: 25px;
  }
  .category-card .article-cover::after {
    inset: 6px;
    border-radius: 18px;
  }
  .category-card .article-cover img {
    border-radius: 18px;
  }
  .category-card .article-copy {
    margin: -11px 8px 0;
    padding: 15px 14px 14px;
    border-radius: 19px;
  }
}

/* ============================================================
   v3.5 · Folio archive — strict grid, selective asymmetry
   ============================================================ */
.category-grid {
  counter-reset: collection;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: clamp(50px, 5vw, 72px) clamp(22px, 2.5vw, 34px);
  align-items: start;
  padding-top: 10px;
}
.category-card,
.category-card:nth-child(4n + 1),
.category-card:nth-child(4n + 2),
.category-card:nth-child(4n + 3),
.category-card:nth-child(4n + 4) {
  counter-increment: collection;
  grid-column: span 4;
  padding-top: 0;
  display: block;
  overflow: visible;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}
.category-card:nth-child(4) {
  grid-column: span 7;
}
.category-card:nth-child(5) {
  grid-column: span 5;
}
.category-card::before {
  display: none;
}

.category-card .article-cover,
.category-card:nth-child(4n + 2) .article-cover,
.category-card:nth-child(4n + 3) .article-cover {
  aspect-ratio: 16 / 10;
  padding: 6px;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--app-border-strong) 50%, transparent);
  border-radius: 28px;
  background: linear-gradient(145deg, color-mix(in srgb, var(--app-surface) 76%, var(--brand-tint)), var(--app-surface-sunken));
  box-shadow:
    0 22px 58px rgba(31, 43, 65, 0.07),
    0 1px 0 rgba(255, 255, 255, 0.8) inset;
  transform-origin: 50% 88%;
}
.category-card:nth-child(4) .article-cover {
  aspect-ratio: 16 / 9;
}
.category-card:nth-child(5) .article-cover {
  aspect-ratio: 5 / 4;
}
.category-card .article-cover::before {
  content: none;
}
.category-card .article-cover::after {
  inset: 6px;
  border-radius: 21px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.03), transparent 54%, rgba(17, 29, 46, 0.09)),
    radial-gradient(360px circle at var(--spot-x, 50%) var(--spot-y, 42%), color-mix(in srgb, var(--accent) 6%, transparent), transparent 70%);
  opacity: 0.44;
}
.category-card .article-cover img {
  border-radius: 21px;
  object-fit: contain;
}
.category-card .article-cover__action {
  right: 15px;
  top: 15px;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  opacity: 0.64;
  transform: translate3d(0, 3px, 0) scale(0.92);
  box-shadow: 0 10px 26px rgba(24, 35, 54, 0.08);
}

.category-card .article-copy {
  position: relative;
  z-index: 2;
  min-height: 0;
  margin: 0;
  padding: 17px 4px 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  transition: transform 320ms cubic-bezier(0.16, 1, 0.3, 1);
}
.category-card .article-copy::before {
  display: none;
}
.category-card .article-meta {
  min-height: 20px;
  gap: 8px;
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.category-card .article-meta::before {
  content: counter(collection, decimal-leading-zero) "  /  COLLECTION";
  color: color-mix(in srgb, var(--accent) 72%, var(--app-text-soft));
}
.category-card .article-meta .meta-pill {
  display: none;
}
.category-card .article-meta > span:last-child {
  position: relative;
  padding-left: 11px;
}
.category-card .article-meta > span:last-child::before {
  content: "";
  position: absolute;
  left: 1px;
  top: 50%;
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--app-border-strong);
  transform: translateY(-50%);
}
.category-card .article-copy h2 {
  margin-top: 8px;
  max-width: 95%;
  font-size: clamp(18px, 1.65vw, 22px);
  line-height: 1.28;
  letter-spacing: -0.035em;
}
.category-card:nth-child(4) .article-copy h2 {
  max-width: 82%;
  font-size: clamp(20px, 1.85vw, 25px);
}
.category-card .article-copy p {
  max-width: 88%;
  margin-top: 7px;
  color: var(--app-text-muted);
  font-size: 11.75px;
  line-height: 1.65;
  opacity: 0.78;
}
.category-card .article-footer {
  margin-top: 13px;
  padding-top: 0;
  align-items: center;
  border-top: 0;
  opacity: 0.78;
}
.category-card .tag-list {
  min-width: 0;
}
.category-card .tag-list .tag-chip {
  min-height: 21px;
  padding-inline: 7px;
  background: transparent;
  border: 1px solid color-mix(in srgb, var(--app-border-strong) 58%, transparent);
  font-size: 8.5px;
}
.category-card .article-link {
  position: relative;
  gap: 5px;
  color: var(--app-text-muted);
  font-size: 10.5px;
  font-weight: 680;
  letter-spacing: 0.02em;
}
.category-card .article-link::before {
  content: "";
  position: absolute;
  left: 0;
  right: 100%;
  bottom: -4px;
  height: 1px;
  background: var(--accent);
  transition: right 280ms cubic-bezier(0.16, 1, 0.3, 1);
}

@media (hover: hover) and (prefers-reduced-motion: no-preference) {
  .category-grid:has(.category-card:hover) .category-card:not(:hover) {
    opacity: 0.84;
  }
  .category-card:hover {
    transform: none;
  }
  .category-card:hover .article-cover {
    transform: translateY(-6px) rotate(0.18deg) scale(1.004);
    border-color: color-mix(in srgb, var(--accent-line) 72%, var(--app-border));
    box-shadow:
      0 30px 72px rgba(31, 43, 65, 0.115),
      0 1px 0 rgba(255, 255, 255, 0.86) inset;
  }
  .category-card:nth-child(even):hover .article-cover {
    transform: translateY(-6px) rotate(-0.18deg) scale(1.004);
  }
  .category-card:hover .article-cover__action {
    opacity: 1;
    transform: none;
  }
  .category-card:hover .article-copy {
    transform: translateX(3px);
  }
  .category-card:hover .article-link {
    color: var(--accent);
  }
  .category-card:hover .article-link::before {
    right: 0;
  }
}

@media (max-width: 1060px) {
  .category-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .category-card,
  .category-card:nth-child(4),
  .category-card:nth-child(5),
  .category-card:nth-child(4n + 1),
  .category-card:nth-child(4n + 2),
  .category-card:nth-child(4n + 3),
  .category-card:nth-child(4n + 4) {
    grid-column: auto;
  }
  .category-card:nth-child(4) .article-cover,
  .category-card:nth-child(5) .article-cover {
    aspect-ratio: 16 / 10;
  }
  .category-card:nth-child(4) .article-copy h2 {
    max-width: 94%;
    font-size: clamp(18px, 2.2vw, 23px);
  }
}
@media (max-width: 700px) {
  .category-grid {
    grid-template-columns: 1fr;
    gap: 38px;
  }
  .category-card .article-cover,
  .category-card:nth-child(4) .article-cover,
  .category-card:nth-child(5) .article-cover {
    aspect-ratio: 16 / 9;
    border-radius: 24px;
    padding: 5px;
  }
  .category-card .article-cover::after {
    inset: 5px;
    border-radius: 18px;
  }
  .category-card .article-cover img {
    border-radius: 18px;
  }
  .category-card .article-copy {
    padding: 14px 3px 0;
  }
  .category-card .article-copy p {
    max-width: 100%;
  }
  .category-card .article-footer {
    opacity: 1;
  }
}

/* ============================================================
   v3.6 · Curated collection index — preview + archive, not cards
   ============================================================ */
.collection-showcase {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(330px, 0.72fr);
  gap: clamp(44px, 6vw, 86px);
  align-items: start;
  padding: clamp(18px, 2.2vw, 28px) 0 54px;
}

.collection-stage {
  position: sticky;
  top: 112px;
  min-width: 0;
}

.collection-stage__topline,
.collection-index__heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 28px;
  margin-bottom: 14px;
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 8.5px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.collection-stage__topline::before {
  content: "";
  width: 26px;
  height: 1px;
  margin-right: 3px;
  flex: 0 0 26px;
  background: linear-gradient(90deg, var(--accent), color-mix(in srgb, var(--accent) 8%, transparent));
}
.collection-stage__topline > span:first-child {
  margin-right: auto;
}

.collection-stage__media {
  --stage-radius: 27px;
  position: relative;
  isolation: isolate;
  width: 100%;
  aspect-ratio: 16 / 10;
  display: block;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--app-border-strong) 62%, transparent);
  border-radius: var(--stage-radius);
  background:
    radial-gradient(circle at 16% 10%, color-mix(in srgb, var(--accent) 7%, transparent), transparent 34%),
    color-mix(in srgb, var(--app-surface-sunken) 92%, var(--brand-tint));
  box-shadow:
    0 32px 80px rgba(28, 42, 64, 0.085),
    0 3px 12px rgba(28, 42, 64, 0.035),
    inset 0 1px 0 rgba(255, 255, 255, 0.72);
  text-decoration: none;
  transform-origin: 50% 78%;
}

.collection-stage__media::before {
  content: "";
  position: absolute;
  z-index: 2;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.03), transparent 54%, rgba(19, 29, 45, 0.1)),
    radial-gradient(520px circle at var(--spot-x, 50%) var(--spot-y, 45%), color-mix(in srgb, var(--accent) 7%, transparent), transparent 68%);
}

.collection-stage__media::after {
  content: "";
  position: absolute;
  z-index: 3;
  pointer-events: none;
  inset: 1px;
  border: 1px solid rgba(255, 255, 255, 0.46);
  border-radius: calc(var(--stage-radius) - 1px);
  opacity: 0.55;
}

.collection-stage__media img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: contain;
  object-position: center;
  background: color-mix(in srgb, var(--app-surface-sunken) 94%, var(--brand-tint));
}

.collection-stage__number {
  position: absolute;
  z-index: 4;
  left: clamp(18px, 2vw, 26px);
  bottom: 14px;
  color: rgba(255, 255, 255, 0.86);
  font-family: var(--font-display);
  font-size: clamp(50px, 7vw, 86px);
  font-weight: 650;
  letter-spacing: -0.08em;
  line-height: 0.82;
  text-shadow: 0 8px 26px rgba(17, 28, 45, 0.12);
  mix-blend-mode: soft-light;
  pointer-events: none;
}

.collection-stage__open {
  position: absolute;
  z-index: 5;
  right: 16px;
  top: 16px;
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.86);
  color: #58677a;
  font-size: 18px;
  box-shadow: 0 12px 30px rgba(21, 34, 53, 0.08);
  backdrop-filter: blur(10px);
  transition:
    transform 260ms cubic-bezier(0.16, 1, 0.3, 1),
    background-color 200ms ease,
    color 200ms ease;
}

.collection-stage__caption {
  padding: 22px 3px 0;
}
.collection-stage__identity {
  display: flex;
  align-items: center;
  gap: 9px;
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 8.5px;
  font-weight: 700;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}
.collection-stage__kind {
  color: color-mix(in srgb, var(--accent) 72%, var(--app-text-soft));
}
.collection-stage__identity > span + span::before {
  content: "";
  width: 3px;
  height: 3px;
  margin: 0 9px 1px 0;
  display: inline-block;
  border-radius: 50%;
  background: var(--app-border-strong);
}
.collection-stage__caption h2 {
  max-width: 88%;
  margin: 8px 0 0;
  color: var(--app-text);
  font-family: var(--font-display);
  font-size: clamp(28px, 3vw, 42px);
  font-weight: 650;
  letter-spacing: -0.052em;
  line-height: 1.08;
}
.collection-stage__caption h2 a {
  color: inherit;
  text-decoration: none;
}
.collection-stage__caption > p {
  max-width: 620px;
  margin: 10px 0 0;
  color: var(--app-text-muted);
  font-size: 13px;
  line-height: 1.72;
}
.collection-stage__footer {
  margin-top: 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}
.collection-stage__footer .tag-chip {
  min-height: 24px;
  padding-inline: 9px;
  border: 1px solid color-mix(in srgb, var(--app-border-strong) 58%, transparent);
  background: transparent;
  font-size: 9px;
}
.collection-stage__cta {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: var(--app-text);
  font-size: 11px;
  font-weight: 700;
  text-decoration: none;
  white-space: nowrap;
}
.collection-stage__cta .material-symbols-rounded {
  color: var(--accent);
  font-size: 16px;
  transition: transform 220ms cubic-bezier(0.16, 1, 0.3, 1);
}

.collection-index {
  min-width: 0;
  border-top: 1px solid color-mix(in srgb, var(--app-border-strong) 70%, transparent);
}
.collection-index__heading {
  margin: 0;
  min-height: 54px;
  border-bottom: 1px solid var(--app-border);
}
.collection-index__heading small {
  color: var(--app-text-soft);
  font: inherit;
  letter-spacing: 0.04em;
  text-transform: none;
}
.collection-index__item {
  position: relative;
  min-height: 104px;
  padding: 17px 0;
  display: grid;
  grid-template-columns: 34px minmax(120px, 0.88fr) minmax(0, 1fr) 26px;
  align-items: center;
  gap: 14px;
  border-bottom: 1px solid var(--app-border);
  color: var(--app-text);
  text-decoration: none;
  transition:
    padding 320ms cubic-bezier(0.16, 1, 0.3, 1),
    color 180ms ease,
    opacity 180ms ease;
}
.collection-index__item::before {
  content: "";
  position: absolute;
  left: -16px;
  top: 50%;
  width: 2px;
  height: 0;
  border-radius: 999px;
  background: var(--accent);
  transform: translateY(-50%);
  transition: height 300ms cubic-bezier(0.16, 1, 0.3, 1);
}
.collection-index__item::after {
  content: "";
  position: absolute;
  inset: 7px -14px;
  z-index: -1;
  border-radius: 16px;
  background: linear-gradient(90deg, color-mix(in srgb, var(--accent) 5%, transparent), transparent 75%);
  opacity: 0;
  transition: opacity 220ms ease;
}
.collection-index__item.is-active::before {
  height: 44px;
}
.collection-index__item.is-active::after {
  opacity: 1;
}
.collection-index__number {
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 8.5px;
  font-weight: 700;
  letter-spacing: 0.08em;
}
.collection-index__copy {
  min-width: 0;
  display: grid;
  gap: 4px;
}
.collection-index__copy small {
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
.collection-index__copy strong {
  overflow: hidden;
  font-family: var(--font-display);
  font-size: clamp(15px, 1.35vw, 18px);
  font-weight: 640;
  letter-spacing: -0.03em;
  line-height: 1.25;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.collection-index__summary {
  display: -webkit-box;
  overflow: hidden;
  color: var(--app-text-muted);
  font-size: 10.5px;
  line-height: 1.55;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}
.collection-index__arrow {
  width: 26px;
  height: 26px;
  display: grid;
  place-items: center;
  color: var(--app-text-soft);
  font-size: 16px;
  transition:
    transform 260ms cubic-bezier(0.16, 1, 0.3, 1),
    color 180ms ease;
}
.collection-index__item.is-active .collection-index__number,
.collection-index__item.is-active .collection-index__arrow {
  color: var(--accent);
}

.collection-media-enter-active,
.collection-media-leave-active {
  transition:
    opacity 230ms ease,
    transform 330ms cubic-bezier(0.16, 1, 0.3, 1),
    filter 230ms ease;
}
.collection-media-enter-from {
  opacity: 0;
  transform: scale(1.025);
  filter: blur(5px);
}
.collection-media-leave-to {
  opacity: 0;
  transform: scale(0.985);
  filter: blur(3px);
}

@media (hover: hover) and (pointer: fine) {
  .collection-stage__media:hover .collection-stage__open {
    transform: translate(2px, -2px) rotate(4deg);
    color: var(--accent);
    background: #fff;
  }
  .collection-stage__cta:hover .material-symbols-rounded {
    transform: translateX(3px);
  }
  .collection-index__item:hover {
    padding-left: 6px;
  }
  .collection-index__item:hover::before {
    height: 44px;
  }
  .collection-index__item:hover::after {
    opacity: 1;
  }
  .collection-index__item:hover .collection-index__arrow {
    color: var(--accent);
    transform: translate(2px, -2px);
  }
}

@media (max-width: 980px) {
  .collection-showcase {
    grid-template-columns: 1fr;
    gap: 34px;
  }
  .collection-stage {
    position: relative;
    top: auto;
  }
  .collection-stage__media {
    aspect-ratio: 16 / 9;
  }
  .collection-index__item {
    grid-template-columns: 34px minmax(170px, 0.8fr) minmax(0, 1fr) 26px;
  }
}

@media (max-width: 640px) {
  .collection-showcase {
    gap: 27px;
    padding-top: 4px;
  }
  .collection-stage__topline {
    margin-bottom: 10px;
  }
  .collection-stage__media {
    --stage-radius: 22px;
    aspect-ratio: 16 / 10;
  }
  .collection-stage__number {
    font-size: 48px;
  }
  .collection-stage__open {
    width: 38px;
    height: 38px;
    right: 12px;
    top: 12px;
  }
  .collection-stage__caption {
    padding-top: 17px;
  }
  .collection-stage__caption h2 {
    max-width: 100%;
    font-size: 28px;
  }
  .collection-stage__caption > p {
    font-size: 12px;
  }
  .collection-stage__footer {
    align-items: flex-end;
  }
  .collection-index__heading small {
    display: none;
  }
  .collection-index__item {
    min-height: 82px;
    padding: 14px 0;
    grid-template-columns: 28px minmax(0, 1fr) 26px;
    gap: 11px;
  }
  .collection-index__summary {
    display: none;
  }
  .collection-index__item::before {
    left: -8px;
  }
  .collection-index__copy strong {
    font-size: 15px;
  }
}

/* ============================================================
   v3.7 · Portfolio archive — typographic index + selected preview
   ============================================================ */
.portfolio-archive {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(340px, 0.72fr);
  gap: clamp(44px, 6vw, 84px);
  align-items: start;
  padding: clamp(20px, 2.4vw, 30px) 0 58px;
}
.portfolio-archive__list {
  min-width: 0;
}
.portfolio-archive__head,
.portfolio-preview__topline {
  min-height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  border-bottom: 1px solid var(--app-border);
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.11em;
  text-transform: uppercase;
}
.portfolio-archive__head small {
  font: inherit;
  letter-spacing: 0.04em;
  text-transform: none;
}
.portfolio-row {
  position: relative;
  min-height: 104px;
  display: grid;
  grid-template-columns: 34px minmax(150px, 0.8fr) minmax(180px, 1fr) auto 26px;
  align-items: center;
  gap: clamp(12px, 1.6vw, 20px);
  padding: 16px 0;
  border-bottom: 1px solid var(--app-border);
  color: var(--app-text);
  text-decoration: none;
  transition:
    color 180ms ease,
    opacity 180ms ease,
    transform 300ms cubic-bezier(0.16, 1, 0.3, 1);
}
.portfolio-row::before {
  content: "";
  position: absolute;
  left: -15px;
  top: 50%;
  width: 2px;
  height: 0;
  border-radius: 999px;
  background: var(--accent);
  transform: translateY(-50%);
  transition: height 300ms cubic-bezier(0.16, 1, 0.3, 1);
}
.portfolio-row__number {
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.08em;
}
.portfolio-row__title {
  min-width: 0;
  display: grid;
  gap: 5px;
}
.portfolio-row__title small {
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
.portfolio-row__title strong {
  overflow: hidden;
  font-family: var(--font-display);
  font-size: clamp(19px, 1.9vw, 26px);
  font-weight: 630;
  letter-spacing: -0.035em;
  line-height: 1.14;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.portfolio-row__summary {
  display: -webkit-box;
  overflow: hidden;
  color: var(--app-text-muted);
  font-size: 10.5px;
  line-height: 1.58;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}
.portfolio-row__tags {
  min-width: 0;
  display: flex;
  justify-content: flex-end;
}
.portfolio-row__tags span {
  min-height: 23px;
  padding: 0 8px;
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--app-border);
  border-radius: 999px;
  color: var(--app-text-soft);
  font-size: 8.5px;
  white-space: nowrap;
}
.portfolio-row__arrow {
  color: var(--app-text-soft);
  font-size: 16px;
  transition:
    color 180ms ease,
    transform 260ms cubic-bezier(0.16, 1, 0.3, 1);
}
.portfolio-row.is-active {
  color: color-mix(in srgb, var(--app-text) 84%, var(--accent));
}
.portfolio-row.is-active::before {
  height: 42px;
}
.portfolio-row.is-active .portfolio-row__number,
.portfolio-row.is-active .portfolio-row__arrow {
  color: var(--accent);
}

.portfolio-preview {
  position: sticky;
  top: 108px;
  min-width: 0;
}
.portfolio-preview__topline {
  min-height: 36px;
  margin-bottom: 14px;
  border-bottom: 0;
}
.portfolio-preview__media {
  position: relative;
  isolation: isolate;
  display: block;
  width: 100%;
  aspect-ratio: 4 / 3;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--app-border-strong) 58%, transparent);
  border-radius: 25px;
  background: color-mix(in srgb, var(--app-surface-sunken) 94%, var(--brand-tint));
  box-shadow:
    0 28px 68px rgba(29, 42, 64, 0.072),
    inset 0 1px 0 rgba(255, 255, 255, 0.72);
  text-decoration: none;
}
.portfolio-preview__media::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.02), transparent 62%, rgba(15, 26, 42, 0.12));
}
.portfolio-preview__media img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: contain;
  object-position: center;
  background: color-mix(in srgb, var(--app-surface-sunken) 94%, var(--brand-tint));
}
.portfolio-preview__index {
  position: absolute;
  z-index: 2;
  left: 15px;
  bottom: 10px;
  color: rgba(255, 255, 255, 0.78);
  font-family: var(--font-display);
  font-size: clamp(46px, 5.8vw, 72px);
  font-weight: 650;
  letter-spacing: -0.08em;
  line-height: 0.84;
  mix-blend-mode: soft-light;
}
.portfolio-preview__open {
  position: absolute;
  z-index: 3;
  right: 13px;
  top: 13px;
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border: 1px solid rgba(255, 255, 255, 0.68);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.86);
  color: #59677a;
  font-size: 17px;
  box-shadow: 0 10px 26px rgba(20, 33, 51, 0.07);
  backdrop-filter: blur(8px);
  transition:
    color 180ms ease,
    transform 260ms cubic-bezier(0.16, 1, 0.3, 1);
}
.portfolio-preview__caption {
  padding: 18px 2px 0;
}
.portfolio-preview__identity {
  display: flex;
  gap: 9px;
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.portfolio-preview__identity > span + span::before {
  content: "·";
  margin-right: 9px;
  color: var(--app-border-strong);
}
.portfolio-preview__caption h2 {
  margin: 7px 0 0;
  font-family: var(--font-display);
  font-size: clamp(25px, 2.6vw, 36px);
  font-weight: 640;
  letter-spacing: -0.048em;
  line-height: 1.08;
}
.portfolio-preview__caption h2 a {
  color: inherit;
  text-decoration: none;
}
.portfolio-preview__caption p {
  max-width: 520px;
  margin: 9px 0 0;
  color: var(--app-text-muted);
  font-size: 11.5px;
  line-height: 1.68;
}
.portfolio-preview__cta {
  margin-top: 14px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--app-text);
  font-size: 10.5px;
  font-weight: 700;
  text-decoration: none;
}
.portfolio-preview__cta .material-symbols-rounded {
  color: var(--accent);
  font-size: 15px;
  transition: transform 220ms cubic-bezier(0.16, 1, 0.3, 1);
}

@media (hover: hover) and (pointer: fine) {
  .portfolio-archive__list:has(.portfolio-row:hover) .portfolio-row:not(:hover) {
    opacity: 0.55;
  }
  .portfolio-row:hover {
    transform: translateX(4px);
  }
  .portfolio-row:hover::before {
    height: 42px;
  }
  .portfolio-row:hover .portfolio-row__arrow {
    color: var(--accent);
    transform: translate(2px, -2px);
  }
  .portfolio-preview__media:hover .portfolio-preview__open {
    color: var(--accent);
    transform: translate(2px, -2px) rotate(4deg);
  }
  .portfolio-preview__cta:hover .material-symbols-rounded {
    transform: translateX(3px);
  }
}

@media (max-width: 1020px) {
  .portfolio-archive {
    grid-template-columns: 1fr;
    gap: 32px;
  }
  .portfolio-preview {
    position: relative;
    top: auto;
    order: -1;
    max-width: 760px;
  }
  .portfolio-preview__media {
    aspect-ratio: 16 / 9;
  }
  .portfolio-row {
    grid-template-columns: 34px minmax(190px, 0.85fr) minmax(0, 1fr) auto 26px;
  }
}

@media (max-width: 700px) {
  .portfolio-archive {
    gap: 24px;
    padding-top: 8px;
  }
  .portfolio-archive__head small {
    display: none;
  }
  .portfolio-preview__topline {
    margin-bottom: 10px;
  }
  .portfolio-preview__media {
    aspect-ratio: 16 / 10;
    border-radius: 21px;
  }
  .portfolio-preview__caption h2 {
    font-size: 27px;
  }
  .portfolio-row {
    min-height: 82px;
    grid-template-columns: 28px minmax(0, 1fr) 24px;
    gap: 11px;
    padding: 13px 0;
  }
  .portfolio-row__summary,
  .portfolio-row__tags {
    display: none;
  }
  .portfolio-row__title strong {
    font-size: 18px;
  }
  .portfolio-row::before {
    left: -8px;
  }
}

/* ============================================================
   v4.0 · Archive precision pass — readable index, aligned preview
   ============================================================ */
.tutorials-main {
  padding-top: 104px;
}
.tutorials-hero h1,
.portfolio-row__title strong,
.portfolio-preview__caption h2 {
  overflow: visible;
  text-wrap: balance;
}

.portfolio-archive {
  gap: clamp(42px, 5vw, 70px);
  padding-top: 18px;
}
.portfolio-archive__head,
.portfolio-preview__topline {
  font-size: 9.5px;
  line-height: 1.3;
}
.portfolio-archive__head {
  min-height: 48px;
}
.portfolio-row {
  min-height: 108px;
  grid-template-columns: 36px minmax(180px, 0.88fr) minmax(190px, 1fr) auto 28px;
  gap: clamp(14px, 1.8vw, 22px);
  padding-block: 18px;
}
.portfolio-row__number {
  font-size: 9.5px;
  line-height: 1.25;
}
.portfolio-row__title small {
  font-size: 9px;
  line-height: 1.35;
}
.portfolio-row__title strong {
  display: -webkit-box;
  overflow: hidden;
  white-space: normal;
  text-overflow: clip;
  font-size: clamp(19px, 1.8vw, 25px);
  line-height: 1.2;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}
.portfolio-row__summary {
  font-size: 12px;
  line-height: 1.6;
}
.portfolio-row__tags span {
  min-height: 25px;
  padding-inline: 9px;
  font-size: 9.5px;
}
.portfolio-row__arrow {
  font-size: 17px;
}
.portfolio-preview {
  top: 92px;
}
.portfolio-preview__topline {
  min-height: 38px;
  margin-bottom: 12px;
}
.portfolio-preview__media {
  border-radius: 24px;
}
.portfolio-preview__identity {
  font-size: 9.5px;
  line-height: 1.35;
}
.portfolio-preview__caption {
  padding-top: 17px;
}
.portfolio-preview__caption h2 {
  margin-top: 8px;
  line-height: 1.1;
  padding-bottom: 0.04em;
}
.portfolio-preview__caption p {
  max-width: 54ch;
  margin-top: 10px;
  font-size: 13px;
  line-height: 1.68;
}
.portfolio-preview__cta {
  margin-top: 13px;
  font-size: 11.5px;
}

@media (max-width: 1020px) {
  .tutorials-main {
    padding-top: 92px;
  }
  .portfolio-archive {
    gap: 28px;
  }
  .portfolio-preview {
    top: auto;
  }
}
@media (max-width: 700px) {
  .tutorials-main {
    padding-top: 78px;
  }
  .portfolio-row {
    min-height: 86px;
    grid-template-columns: 30px minmax(0, 1fr) 26px;
    padding-block: 15px;
  }
  .portfolio-row__title small {
    font-size: 8.5px;
  }
  .portfolio-row__title strong {
    font-size: 18px;
  }
  .portfolio-preview__caption p {
    font-size: 12.5px;
  }
}

/* ============================================================
   v4.1 · Articles / collections mobile rebuild
   ============================================================ */
@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .tutorials-main {
    width: 100% !important;
    max-width: 100% !important;
    padding: 78px 16px 50px !important;
  }
  .tutorials-hero {
    display: grid !important;
    grid-template-columns: 1fr !important;
    gap: 14px !important;
    padding: 18px 0 20px !important;
  }
  .tutorials-hero::after {
    right: -40px !important;
    opacity: 0.08 !important;
  }
  .hero-copy {
    grid-column: auto !important;
    max-width: none !important;
  }
  .page-kicker {
    font-size: 9px !important;
  }
  .page-description {
    font-size: clamp(31px, 8.8vw, 42px) !important;
    line-height: 1.1 !important;
  }
  .page-subtitle {
    max-width: none !important;
    font-size: 13px !important;
    line-height: 1.68 !important;
  }
  .hero-stat {
    display: none !important;
  }
  .toolbar {
    width: calc(100% + 32px) !important;
    margin-inline: -16px !important;
    padding: 2px 16px 4px !important;
    display: flex !important;
    flex-wrap: nowrap !important;
    justify-content: flex-start !important;
    gap: 7px !important;
    overflow-x: auto !important;
    scrollbar-width: none;
  }
  .toolbar::-webkit-scrollbar {
    display: none;
  }
  .sort-chip,
  .back-link {
    flex: 0 0 auto !important;
    min-height: 40px !important;
    padding-inline: 12px !important;
  }
  .tutorials-summary {
    padding: 16px 0 12px !important;
    font-size: 11.5px !important;
  }

  .category-grid {
    grid-template-columns: 1fr !important;
    gap: 24px !important;
  }
  .category-card {
    grid-template-columns: 1fr !important;
    min-height: 0 !important;
  }
  .category-card .article-cover {
    width: 100% !important;
    min-height: 0 !important;
    aspect-ratio: 16 / 9 !important;
    border-right: 0 !important;
  }
  .category-card .article-copy {
    min-height: 0 !important;
    padding: 16px 4px 6px !important;
  }

  .timeline-list::before {
    left: 10px !important;
  }
  .timeline-item {
    grid-template-columns: 20px minmax(0, 1fr) !important;
    gap: 0 !important;
  }
  .timeline-date,
  .timeline-cover,
  .timeline-item .article-copy {
    grid-column: 2 !important;
  }
  .timeline-node {
    grid-column: 1 !important;
  }
  .timeline-cover {
    width: 100% !important;
    max-width: 420px !important;
  }

  .portfolio-archive {
    display: grid !important;
    grid-template-columns: 1fr !important;
    gap: 22px !important;
    padding: 8px 0 38px !important;
  }
  .portfolio-preview {
    position: static !important;
    top: auto !important;
    order: -1 !important;
    width: 100% !important;
    max-width: none !important;
  }
  .portfolio-preview__topline {
    min-height: 34px !important;
    margin-bottom: 8px !important;
  }
  .portfolio-preview__media {
    width: 100% !important;
    aspect-ratio: 16 / 10 !important;
    border-radius: 20px !important;
  }
  .portfolio-preview__index {
    font-size: 44px !important;
  }
  .portfolio-preview__caption {
    padding: 14px 2px 0 !important;
  }
  .portfolio-preview__caption h2 {
    font-size: 27px !important;
  }
  .portfolio-preview__caption p {
    font-size: 12.5px !important;
  }
  .portfolio-archive__head {
    min-height: 42px !important;
  }
  .portfolio-row {
    min-height: 78px !important;
    grid-template-columns: 28px minmax(0, 1fr) 28px !important;
    gap: 10px !important;
    padding: 13px 0 !important;
    transform: none !important;
  }
  .portfolio-row__summary,
  .portfolio-row__tags {
    display: none !important;
  }
  .portfolio-row__title strong {
    font-size: 18px !important;
    line-height: 1.2 !important;
  }
  .portfolio-row__title small {
    font-size: 9.5px !important;
    line-height: 1.3 !important;
  }
  .pagination {
    max-width: 100% !important;
    flex-wrap: wrap !important;
    gap: 6px !important;
  }
}
@media (max-width: 430px) {
  .tutorials-main {
    padding-inline: 13px !important;
  }
  .toolbar {
    width: calc(100% + 26px) !important;
    margin-inline: -13px !important;
    padding-inline: 13px !important;
  }
  .tutorials-summary {
    align-items: flex-start !important;
    flex-direction: column !important;
    gap: 4px !important;
  }
}

/* ============================================================
   v5.0 · Editorial archive masthead
   ============================================================ */
.tutorials-main {
  width: min(1180px, calc(100% - 2 * var(--app-page-gutter)));
  max-width: 1180px;
  padding-top: 104px;
}

.tutorials-hero {
  min-height: 184px;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: clamp(42px, 8vw, 120px);
  padding: 24px 4px 28px;
  border-bottom: 1px solid color-mix(in srgb, var(--app-border-strong) 66%, transparent);
}
.tutorials-hero::before,
.tutorials-hero::after {
  display: none;
}
.hero-copy {
  max-width: 760px;
  gap: 7px;
}
.page-kicker {
  margin: 0 0 3px;
  display: flex;
  align-items: center;
  gap: 9px;
  color: var(--accent);
  font-family: var(--font-mono);
  font-size: 9.5px;
  font-weight: 740;
  letter-spacing: 0.13em;
  line-height: 1.4;
}
.page-kicker i {
  color: var(--app-border-strong);
  font-style: normal;
}
.page-description {
  font-family: var(--font-display);
  font-size: clamp(42px, 4.2vw, 52px);
  font-weight: 610;
  line-height: 1;
  letter-spacing: -0.042em;
}
.page-subtitle {
  max-width: 690px;
  margin-top: 4px;
  font-size: 13.5px;
  line-height: 1.7;
}
.hero-stat {
  min-width: 160px;
  padding: 11px 4px 11px 28px;
  display: flex;
  grid-template-columns: none;
  align-items: baseline;
  justify-content: flex-start;
  gap: 10px;
  border: 0;
  border-left: 1px solid color-mix(in srgb, var(--app-border-strong) 68%, transparent);
}
.hero-stat::after {
  display: none;
}
.hero-stat strong {
  font-size: 42px;
  font-weight: 620;
  line-height: 1;
}
.hero-stat small {
  color: var(--app-text-soft);
  font-size: 11px;
}

.archive-controls {
  min-height: 76px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid var(--app-border);
}
.toolbar {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 34px;
  padding: 0 4px;
}
.toolbar-label {
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 9.5px;
  font-weight: 720;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}
.back-link,
.sort-chip {
  position: relative;
  min-height: 38px;
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  color: var(--app-text-muted);
  font-size: 12px;
  font-weight: 580;
  box-shadow: none;
}
.back-link:hover,
.sort-chip:hover,
.sort-chip.active {
  border: 0;
  background: transparent;
  color: var(--app-text);
  box-shadow: none;
}
.sort-chip::after {
  content: "";
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  height: 2px;
  background: var(--accent);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 180ms var(--app-ease);
}
.sort-chip.active::after {
  transform: scaleX(1);
}
.tutorials-summary {
  padding: 25px 4px 18px;
}

@media (max-width: 980px) {
  .tutorials-main {
    padding-top: 90px;
  }
  .tutorials-hero {
    min-height: 168px;
    grid-template-columns: minmax(0, 1fr) auto;
    padding-top: 20px;
  }
  .hero-copy {
    grid-column: auto;
  }
}

@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .tutorials-main {
    padding-top: 76px !important;
  }
  .tutorials-hero {
    min-height: 0 !important;
    gap: 0 !important;
    padding: 22px 0 25px !important;
  }
  .page-kicker {
    font-size: 8.5px !important;
  }
  .page-description {
    font-size: clamp(34px, 10.5vw, 46px) !important;
  }
  .page-subtitle {
    font-size: 12.5px !important;
  }
  .archive-controls {
    width: calc(100% + 32px);
    min-height: 62px;
    margin-inline: -16px;
    overflow: hidden;
  }
  .toolbar {
    width: 100% !important;
    margin: 0 !important;
    padding: 0 16px !important;
    gap: 26px !important;
  }
  .sort-chip,
  .back-link {
    min-height: 40px !important;
    padding: 0 !important;
  }
}

/* v5.1 · Archive hover contract: local feedback without dimming the list. */
@media (hover: hover) and (pointer: fine) {
  .portfolio-archive__list:has(.portfolio-row:hover) .portfolio-row:not(:hover) {
    opacity: 1;
  }
  .portfolio-row:hover {
    background: color-mix(in srgb, var(--app-surface) 84%, transparent);
    transform: none;
  }
  .portfolio-row:hover::before {
    height: 28px;
  }
  .portfolio-row:hover .portfolio-row__arrow {
    transform: translate(1px, -1px);
  }
  .portfolio-preview__media:hover .portfolio-preview__open {
    transform: translate(1px, -1px);
  }
  .timeline-cover:hover img {
    transform: scale(1.008);
  }
}

/* v5.2 · Keep counts as a quiet closing note instead of repeating them above the archive. */
.portfolio-archive {
  padding-bottom: 0;
}
.tutorials-footer {
  margin-top: clamp(28px, 4vw, 48px);
  padding: 20px 4px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  border-top: 1px solid var(--app-border);
}
.tutorials-footer .tutorials-summary {
  flex: 1 1 auto;
  padding: 0;
}
.tutorials-footer .pagination {
  flex: 0 0 auto;
  justify-content: flex-end;
  margin: 0;
  padding: 0;
  border-top: 0;
}

@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .portfolio-archive {
    padding-bottom: 0 !important;
  }
  .tutorials-footer {
    margin-top: 30px;
    padding-inline: 0;
    align-items: flex-start;
    flex-direction: column;
    gap: 16px;
  }
  .tutorials-footer .tutorials-summary {
    padding: 0 !important;
  }
  .tutorials-footer .pagination {
    justify-content: flex-start !important;
  }
}
</style>
