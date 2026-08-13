<template>
  <MobileDrawer v-model="isMobileMenuOpen" subtitle="Articles, notes, demos">
    <p>文章与教程</p>
    <p>{{ isSeriesView ? "这个专栏下的文章。" : "按专栏分门别类。" }}</p>
  </MobileDrawer>

  <HeaderBar :route-name="'教程'" :scroll="true" @toggle-mobile-menu="onToggleMobileMenu" />

  <div class="tutorials-page">
    <main class="tutorials-main">
      <section class="tutorials-hero">
        <div class="hero-copy">
          <p class="page-description">{{ pageTitle }}</p>
        </div>

        <div class="toolbar">
          <a v-if="isSeriesView" class="back-link" href="/articles">返回</a>
          <button
            v-for="option in sortOptions"
            :key="option.value"
            :class="['sort-chip', { active: sortBy === option.value }]"
            type="button"
            @click="sortBy = option.value"
          >
            {{ option.label }}
          </button>
        </div>
      </section>

      <section class="tutorials-summary">
        <span>共 {{ sortedArticles.length }} {{ isSeriesView ? "篇" : "个专栏" }}</span>
        <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
      </section>

      <section :class="['article-list', isSeriesView ? 'timeline-list' : 'category-grid']" :aria-label="isSeriesView ? '系列时间线' : '专栏列表'">
        <article v-for="article in pagedArticles" :key="article.id" :class="['article-row', isSeriesView ? 'timeline-item' : 'category-card']">
          <template v-if="isSeriesView">
            <div class="timeline-date">
              <span>{{ getDateParts(article.date).year }}</span>
              <strong>{{ getDateParts(article.date).day }}</strong>
            </div>

            <div class="timeline-node" aria-hidden="true"></div>

            <a class="timeline-cover" :href="getArticleLink(article)" :aria-label="article.title">
              <img :src="article.thumbnail || defaultCover" :alt="article.title" loading="lazy" decoding="async" />
            </a>

            <div class="article-copy">
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
                  <span v-for="tag in article.tags || []" :key="tag" class="tag-chip">{{ tag }}</span>
                </div>

                <a class="article-link" :href="getArticleLink(article)">去读读</a>
              </div>
            </div>
          </template>

          <template v-else>
            <a class="article-cover" :href="getArticleLink(article)" :aria-label="getCategoryTitle(article)">
              <img :src="article.thumbnail || defaultCover" :alt="getCategoryTitle(article)" loading="lazy" decoding="async" />
            </a>

            <div class="article-copy">
              <div class="article-meta">
                <span class="meta-pill">专栏</span>
                <span>{{ article.category || "others" }}</span>
              </div>

              <h2>
                <a :href="getArticleLink(article)">{{ getCategoryTitle(article) }}</a>
              </h2>

              <p>{{ article.summary || "还没写摘要" }}</p>

              <div class="article-footer">
                <div class="tag-list">
                  <span v-for="tag in article.tags || []" :key="tag" class="tag-chip">{{ tag }}</span>
                </div>

                <a class="article-link" :href="getArticleLink(article)">进专栏</a>
              </div>
            </div>
          </template>
        </article>
      </section>

      <nav v-if="totalPages > 1" class="pagination" aria-label="文章分页">
        <button class="page-button" type="button" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">上一页</button>
        <button v-for="page in visiblePages" :key="page" :class="['page-number', { active: page === currentPage }]" type="button" @click="goToPage(page)">
          {{ page }}
        </button>
        <button class="page-button" type="button" :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">下一页</button>
      </nav>
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
const pageSize = 8;

const activeCategory = computed(() => {
  const value = route.params.category;
  return Array.isArray(value) ? value[0] || "" : value || "";
});

const isSeriesView = computed(() => Boolean(activeCategory.value));
const pageTitle = computed(() => (isSeriesView.value ? `${activeCategory.value} 专栏时间线` : "教程专栏"));
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
};

onMounted(loadArticles);

watch(sortBy, () => {
  currentPage.value = 1;
});

watch(activeCategory, loadArticles);
</script>

<style scoped>
.tutorials-page {
  min-height: 100vh;
  background: var(--app-bg);
}

.tutorials-main {
  width: min(1120px, calc(100% - 40px));
  margin: 0 auto;
  padding: 118px 0 72px;
}

.tutorials-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--app-border);
}

.hero-copy {
  display: grid;
  gap: 6px;
}

.page-description {
  margin: 0;
  font-family: var(--font-display);
  font-weight: 600;
  color: var(--app-text);
  font-size: 26px;
  line-height: 1.3;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  height: 38px;
  padding: 0 14px;
  border: 1px solid var(--app-border);
  border-radius: 999px;
  background: var(--app-surface);
  color: var(--app-text);
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
}

.back-link:hover {
  border-color: var(--accent-line);
  color: var(--app-blue);
}

.sort-chip {
  height: 38px;
  padding: 0 16px;
  border: 1px solid var(--app-border);
  border-radius: 999px;
  background: var(--app-surface);
  color: var(--app-text-muted);
  font-size: 13px;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease, transform 0.2s ease;
}

.sort-chip:hover {
  background: var(--app-surface);
  border-color: var(--app-border-strong);
  color: var(--app-text);
  transform: translateY(-1px);
}

.sort-chip.active {
  background: var(--accent-weak);
  border-color: var(--accent-line);
  color: var(--app-blue);
}

.tutorials-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 0 8px;
  color: var(--app-text-soft);
  font-size: 14px;
}

.article-list {
  display: grid;
}

.category-grid {
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  padding-top: 14px;
}

.timeline-list {
  position: relative;
  gap: 0;
  padding-top: 10px;
}

.timeline-list::before {
  content: "";
  position: absolute;
  top: 28px;
  bottom: 26px;
  left: 118px;
  width: 1px;
  background: rgba(120, 105, 85, 0.22);
}

.category-card {
  display: grid;
  grid-template-rows: auto 1fr;
  overflow: hidden;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-xl);
  background: var(--app-surface);
  box-shadow: var(--app-shadow-sm);
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.category-card:hover {
  border-color: var(--app-border-strong);
  box-shadow: var(--app-shadow-md);
  transform: translateY(-2px);
}

.timeline-item {
  position: relative;
  display: grid;
  grid-template-columns: 92px 52px 180px minmax(0, 1fr);
  gap: 0 18px;
  padding: 18px 0 24px;
}

.timeline-date {
  display: grid;
  align-content: start;
  justify-items: end;
  gap: 2px;
  padding-top: 4px;
  color: var(--app-text-muted);
  font-size: 12px;
  line-height: 1.1;
}

.timeline-date strong {
  color: var(--app-text);
  font-size: 18px;
  line-height: 1.1;
}

.timeline-node {
  position: relative;
  z-index: 1;
  justify-self: center;
  width: 13px;
  height: 13px;
  margin-top: 10px;
  border: 3px solid var(--app-blue);
  border-radius: 999px;
  background: #ffffff;
}

.timeline-cover {
  display: grid;
  place-items: center;
  overflow: hidden;
  align-self: start;
  padding: 10px;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-sm);
  background: var(--app-surface);
}

.timeline-cover img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
  transition: transform 0.2s ease;
}

.timeline-cover:hover img {
  transform: scale(1.035);
}

.article-cover {
  display: block;
  overflow: hidden;
  border-bottom: 1px solid var(--app-border);
  background: var(--app-surface-sunken);
  aspect-ratio: 16 / 10;
}

.article-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.article-copy {
  min-width: 0;
}

.category-card .article-copy {
  display: grid;
  grid-template-rows: auto auto 1fr auto;
  gap: 0;
  padding: 18px;
}

.timeline-item .article-copy {
  padding: 0 0 22px;
  border-bottom: 1px solid var(--app-border);
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px 14px;
  color: var(--app-text-soft);
  font-size: 12px;
}

.meta-pill,
.tag-chip {
  display: inline-flex;
  align-items: center;
  height: 26px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid var(--app-border);
  background: var(--app-surface);
  color: var(--app-text-muted);
  font-size: 12px;
}

.article-copy h2 {
  margin: 10px 0 0;
  font-size: 21px;
  line-height: 1.28;
}

.article-copy h2 a {
  color: var(--app-text);
  text-decoration: none;
}

.article-copy h2 a:hover {
  color: var(--app-blue);
}

.article-copy p {
  margin: 10px 0 0;
  color: var(--app-text-muted);
  font-size: 14px;
  line-height: 1.72;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-footer {
  margin-top: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.article-link {
  color: var(--app-blue);
  text-decoration: none;
  font-weight: 600;
  white-space: nowrap;
  font-size: 14px;
}

.article-link:hover {
  color: var(--app-blue-hover);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  padding-top: 28px;
  border-top: 1px solid var(--app-border);
}

.page-button,
.page-number {
  height: 40px;
  min-width: 40px;
  padding: 0 14px;
  border: 1px solid var(--app-border);
  border-radius: 999px;
  background: var(--app-surface);
  color: var(--app-text-muted);
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.page-button:hover,
.page-number:hover {
  background: var(--app-surface);
  border-color: var(--app-border-strong);
  color: var(--app-text);
}

.page-button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.page-number.active {
  background: var(--accent-weak);
  border-color: var(--accent-line);
  color: var(--app-blue);
}

@media (max-width: 900px) {
  .tutorials-main {
    width: min(100% - 28px, 980px);
    padding-top: 102px;
  }

  .tutorials-hero {
    align-items: start;
    flex-direction: column;
  }

  .category-grid {
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 20px;
    padding: 4px 8px;
  }

  .timeline-list::before {
    left: 86px;
  }

  .timeline-item {
    grid-template-columns: 72px 30px 148px minmax(0, 1fr);
    gap: 0 14px;
  }
}

@media (max-width: 640px) {
  .tutorials-main {
    width: calc(100% - 24px);
    padding-top: 92px;
  }

  .tutorials-hero {
    gap: 14px;
    padding-bottom: 14px;
  }

  .page-kicker {
    margin-bottom: 6px;
    font-size: 11px;
  }

  .page-description {
    font-size: 16px;
  }

  .toolbar {
    width: 100%;
  }

  .sort-chip {
    flex: 1 1 calc(50% - 5px);
    justify-content: center;
  }

  .tutorials-summary,
  .article-footer {
    align-items: start;
    flex-direction: column;
  }

  .tutorials-summary {
    padding-top: 14px;
    gap: 6px;
    font-size: 13px;
  }

  .category-grid {
    grid-template-columns: 1fr;
    gap: 16px;
    padding: 4px 8px;
  }

  .timeline-list {
    padding-top: 2px;
  }

  .timeline-list::before {
    left: 10px;
  }

  .timeline-item {
    grid-template-columns: 22px minmax(0, 1fr);
    padding: 14px 0 18px;
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
    font-size: 14px;
  }

  .timeline-node {
    grid-column: 1;
    grid-row: 1 / span 3;
    width: 11px;
    height: 11px;
    margin-top: 4px;
  }

  .timeline-cover {
    grid-column: 2;
    grid-row: 2;
    width: min(100%, 240px);
    margin-bottom: 12px;
  }

  .timeline-item .article-copy {
    grid-column: 2;
    grid-row: 3;
    padding-bottom: 18px;
  }

  .category-card .article-copy {
    padding: 15px;
  }

  .article-cover {
    border-radius: 0;
  }

  .article-meta {
    gap: 8px 10px;
    font-size: 11px;
  }

  .meta-pill,
  .tag-chip {
    height: 24px;
    padding: 0 9px;
    font-size: 11px;
  }

  .article-copy h2 {
    font-size: 18px;
    line-height: 1.34;
  }

  .article-copy p {
    font-size: 13px;
    line-height: 1.7;
  }

  .article-link {
    font-size: 13px;
  }

  .pagination {
    gap: 8px;
    padding-top: 22px;
    justify-content: flex-start;
  }

  .page-button,
  .page-number {
    height: 36px;
    min-width: 36px;
    padding: 0 12px;
    font-size: 13px;
  }
}
</style>
