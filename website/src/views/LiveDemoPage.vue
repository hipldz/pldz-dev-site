<template>
  <!-- 顶部导航栏 -->
  <HeaderBar @toggle-mobile-menu="onToggleMobileMenu" :route-name="'Code Space'" :scroll="true" :show-mobile-menu="false" />

  <div class="main-container">
    <main class="livedemo-shell">
      <section class="livedemo-heading">
        <div class="hero-copy">
          <p class="page-description">能上手玩的 Demo</p>
        </div>
        <span class="project-count">共 {{ mockData.length }} 个</span>
      </section>

      <section class="home-content" aria-label="项目列表">
        <!-- 卡片 -->
        <article v-for="c in mockData" :key="c.title || c.url || c.previewgif" class="live-demo-card">
          <!-- 标题 -->
          <header class="preview-title" :title="c.title">
            <span>{{ c.title || "未命名" }}</span>
          </header>

          <!-- 媒体：缩略图 / 悬停切换 GIF（CSS-only，不触发 JS 重渲染） -->
          <figure class="preview-gif">
            <img v-if="hasThumb(c)" class="preview-gif__thumb" :src="c.thumbnail" :alt="c.title || '预览图'" loading="lazy" decoding="async" @error="(e) => handleImgError(e, c)" />
            <img v-if="c.previewgif" class="preview-gif__gif" :src="c.previewgif" :alt="c.title || 'GIF 预览'" loading="lazy" decoding="async" @error="(e) => handleImgError(e, c)" />
            <img v-if="!hasThumb(c) && !c.previewgif" :src="'/404.jpg'" :alt="c.title || '暂无预览'" loading="lazy" decoding="async" />
          </figure>

          <!-- 元信息：日期 + 目录 -->
          <div class="card-meta">
            <time v-if="c.date" class="chip" :datetime="c.date">{{ fmtDate(c.date) }}</time>
            <span v-if="c.folder" class="chip chip-muted" :title="c.folder">{{ c.folder }}</span>
          </div>

          <!-- 描述 -->
          <p v-if="c.description" class="preview-description" :title="c.description">
            {{ c.description }}
          </p>

          <!-- 操作 -->
          <div class="actions">
            <button
              class="btn"
              :aria-label="`在线打开：${c.title}`"
              @click="onGoPreview(c.url)"
              :disabled="!c.url"
              :title="c.url ? '在线打开' : '还没放预览地址'"
              data-analytics-cta="live_demo"
              :data-analytics-source="`livedemo.list.${c.folder || c.title || 'unknown'}`"
              :data-analytics-label="c.title || 'Live Demo'"
            >
              在线打开
            </button>

            <a
              v-if="c.sourcelink"
              class="btn btn-secondary"
              :href="c.sourcelink"
              target="_blank"
              rel="noopener noreferrer"
              :aria-label="`看源码：${c.title}`"
              title="看源码"
            >
              看源码
            </a>
            <button v-else class="btn btn-secondary" disabled title="还没放源码">看源码</button>
          </div>
        </article>
      </section>
    </main>
  </div>

  <!-- 底部 -->
  <FooterBar />
</template>

<script setup>
import HeaderBar from "../components/HeaderBar.vue";
import FooterBar from "../components/FooterBar.vue";

import { ref, onMounted } from "vue";
import { getAllLiveDemos } from "../utils/apis";

/**
 * 单个配置项
 * title: 标题
 * folder: 文件夹名称
 * url: 访问链接
 * thumbnail: 缩略图链接
 * previewgif: 预览GIF链接
 * sourcelink: 源代码链接
 * description: 描述
 */
const mockData = ref([]);

const hasThumb = (c) => Boolean(c.thumbnail);

const onGoPreview = (url) => {
  if (!url) return;
  const final = /^https?:\/\//i.test(url) ? url : `${location.origin.replace(/\/$/, "")}/${url.replace(/^\//, "")}`;
  window.open(final, "_blank");
};

const fmtDate = (dateStr) => {
  // 兼容 YYYY-MM-DD / ISO
  const d = new Date(dateStr);
  if (isNaN(d)) return dateStr;
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const d2 = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${d2}`;
};

const handleImgError = (e, c) => {
  // 优先尝试另一个资源，最终回退 404
  const el = e.target;
  if (el.dataset.fallbackTried === "1") {
    el.src = "/404.jpg";
    return;
  }
  el.dataset.fallbackTried = "1";
  el.src = c.thumbnail && el.src !== c.thumbnail ? c.thumbnail : c.previewgif || "/404.jpg";
};

const onToggleMobileMenu = () => {
  // 保留原逻辑/事件透传
};

/**
 * 获取所有的livedemo配置项
 * @returns {Promise<Array>} 返回livedemo配置项数组
 */
onMounted(async () => {
  const res = await getAllLiveDemos();
  mockData.value = res || [];
});
</script>

<style scoped>
@import url("../assets/views/main-container.css");

.main-container {
  width: min(1180px, calc(100% - 40px));
  max-width: 1180px;
  display: block;
  padding: 110px 0 72px;
}

.livedemo-shell {
  display: grid;
  gap: 26px;
}

.livedemo-heading {
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
  color: var(--app-text);
  font-family: var(--font-display);
  font-size: 26px;
  line-height: 1.25;
  font-weight: 600;
}

.project-count {
  display: inline-flex;
  align-items: center;
  height: 38px;
  padding: 0 14px;
  border: 1px solid var(--app-border);
  border-radius: 999px;
  background: var(--app-surface);
  color: var(--app-text-muted);
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}

.home-content {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 34px;
}

.live-demo-card {
  position: relative;
  display: grid;
  grid-template-rows: auto auto auto auto 1fr auto;
  min-height: 100%;
  padding: 0;
  overflow: hidden;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-lg);
  background: var(--app-surface);
  box-shadow: var(--app-shadow-sm);
  transition: transform var(--app-motion-duration) var(--app-ease), border-color var(--app-motion-duration) var(--app-ease);
}

.live-demo-card:hover {
  transform: translateY(-3px);
  border-color: var(--app-border-strong);
  box-shadow: var(--app-shadow-md);
}

.preview-title {
  min-height: 70px;
  padding: 16px 16px 12px;
  color: var(--app-text);
  font-size: 18px;
  font-weight: 700;
  line-height: 1.24;
  border-bottom: 1px solid var(--app-border);
}

.preview-title span {
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.preview-gif {
  position: relative;
  width: 100%;
  margin: 0;
  padding: 12px;
  aspect-ratio: 16 / 10;
  overflow: hidden;
  border-bottom: 1px solid var(--app-border);
  background: linear-gradient(180deg, var(--app-surface), var(--app-surface-sunken));
}

.preview-gif img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-lg);
  background: var(--app-surface);
}

.preview-gif__thumb {
  position: relative;
  z-index: 1;
}

.preview-gif__gif {
  position: absolute;
  inset: 12px;
  z-index: 2;
  opacity: 0;
  transition: opacity var(--app-motion-duration) var(--app-ease);
  pointer-events: none;
}

.live-demo-card:hover .preview-gif__gif {
  opacity: 1;
}

.live-demo-card:hover .preview-gif__thumb {
  opacity: 0;
}

.card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  min-height: 42px;
  padding: 12px 16px 0;
}

.chip {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  min-height: 24px;
  padding: 0 8px;
  overflow: hidden;
  border: 1px solid var(--accent-line);
  border-radius: 999px;
  background: var(--accent-weak);
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
  line-height: 1.2;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chip-muted {
  background: rgba(120, 105, 85, 0.08);
  color: var(--app-text-muted);
}

.preview-description {
  min-height: 78px;
  margin: 0;
  padding: 12px 16px 0;
  color: var(--app-text-muted);
  font-size: 14px;
  line-height: 1.55;
  text-align: left;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  -webkit-line-clamp: 3;
}

.actions {
  display: flex;
  align-items: stretch;
  gap: 10px;
  padding: 16px;
}

.btn,
.btn-secondary {
  flex: 1 1 0;
  min-width: 0;
  min-height: 40px;
  padding: 0 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  border-radius: var(--app-radius-lg);
  color: var(--app-surface);
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
  box-shadow: var(--app-shadow-sm);
  transition: transform var(--app-motion-duration) var(--app-ease), background-color var(--app-motion-duration) var(--app-ease), border-color var(--app-motion-duration) var(--app-ease), opacity var(--app-motion-duration) var(--app-ease);
}

.btn {
  background: var(--app-blue);
}

.btn:hover {
  background: var(--app-blue-hover);
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(80, 55, 35, 0.16);
}

.btn:active {
  transform: translateY(0);
  box-shadow: 0 6px 16px rgba(80, 55, 35, 0.12);
}

.btn:focus-visible {
  outline: none;
  box-shadow: 0 0 0 4px rgba(189, 88, 54, 0.14), 0 8px 20px rgba(80, 55, 35, 0.12);
}

.btn[disabled] {
  cursor: not-allowed;
  opacity: 0.55;
  transform: none;
  box-shadow: none;
}

.btn-secondary {
  background: var(--app-surface);
  border-color: var(--app-border);
  color: var(--app-text);
  box-shadow: none;
}

.btn-secondary:hover {
  background: var(--app-surface);
  box-shadow: var(--app-shadow-sm);
}

@media (prefers-reduced-motion: reduce) {
  .live-demo-card,
  .btn {
    transition: none;
  }
}

@media (max-width: 768px) {
  .main-container {
    width: calc(100% - 28px);
    padding-top: 92px;
    padding-bottom: 48px;
  }

  .livedemo-shell {
    gap: 18px;
  }

  .livedemo-heading {
    align-items: start;
    flex-direction: column;
    gap: 14px;
    padding-bottom: 14px;
  }

  .home-content {
    grid-template-columns: 1fr;
    gap: 28px;
  }

  .live-demo-card {
    box-shadow: var(--app-shadow-sm);
  }

  .live-demo-card:hover {
    transform: none;
    box-shadow: var(--app-shadow-sm);
  }

  .preview-title {
    min-height: auto;
    font-size: 17px;
  }

  .preview-gif {
    padding: 10px;
    aspect-ratio: 4 / 3;
  }

  .actions {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .main-container {
    width: calc(100% - 22px);
  }

  .live-demo-card {
    border-radius: var(--app-radius-lg);
  }

  .preview-title {
    font-size: 15px;
  }

  .preview-description {
    min-height: auto;
    font-size: 13px;
    line-height: 1.5;
  }

  .page-kicker {
    margin-bottom: 6px;
    font-size: 11px;
  }

  .page-description {
    font-size: 16px;
  }

  .project-count {
    width: 100%;
    justify-content: center;
  }
}
</style>
