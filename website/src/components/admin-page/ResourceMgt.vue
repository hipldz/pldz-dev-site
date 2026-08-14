<template>
  <div class="content-container">
    <div class="content-header">
      <h1>资源文件</h1>
      <p>浏览 data/resources 中的公开文件，并复制可直接访问的 URL</p>
    </div>

    <div class="content-body">
      <div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div>

      <div class="content-item filter-bar">
        <span>筛选文件</span>
        <select v-model="selectedCategory" :disabled="isLoading">
          <option value="">全部分类</option>
          <option v-for="category in categories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
        <input v-model.trim="keyword" type="search" placeholder="搜索路径或文件名" />
        <button class="btn btn-outline" type="button" :disabled="isLoading" @click="loadResources">
          刷新
        </button>
      </div>

      <div v-if="isLoading" class="loading-stack">
        <div v-for="n in 6" :key="n" class="loading-card"></div>
      </div>

      <div v-else-if="filteredFiles.length" class="list-block">
        <div v-for="file in filteredFiles" :key="file.path" class="list-row file-row">
          <div class="file-primary">
            <span class="category-badge">{{ file.category || "根目录" }}</span>
            <strong>{{ file.filename }}</strong>
            <code>{{ file.path }}</code>
          </div>
          <div class="field">
            <span class="field-label">大小</span>
            <span class="field-value field-value--muted">{{ formatFileSize(file.size) }}</span>
          </div>
          <div class="field">
            <span class="field-label">更新</span>
            <span class="field-value field-value--muted">{{ formatTime(file.modified_time) }}</span>
          </div>
          <div class="inline-actions">
            <button class="btn btn-outline" type="button" @click="copyUrl(file)">复制 URL</button>
            <a class="btn btn-info" :href="resourceUrl(file)" target="_blank" rel="noopener">打开</a>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">📁</div>
        <p>{{ files.length ? "没有符合筛选条件的资源文件。" : "暂无资源文件。" }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getAllResources } from "../../utils/apis";
import { buildPublicFileUrl, copyText } from "../../utils/clipboard.js";
import Toast from "../../utils/toast.js";
import { useLoading } from "../../utils/use-loading";

const files = ref([]);
const keyword = ref("");
const route = useRoute();
const router = useRouter();
const selectedCategory = ref(typeof route.query.category === "string" ? route.query.category : "");
const errorMessage = ref("");
const { isLoading, start, stop } = useLoading("admin.resource.list");

const categories = computed(() =>
  [...new Set(files.value.map((file) => file.category).filter(Boolean))].sort((a, b) =>
    a.localeCompare(b)
  )
);

const filteredFiles = computed(() => {
  const query = keyword.value.toLocaleLowerCase();
  return files.value.filter((file) => {
    if (selectedCategory.value && file.category !== selectedCategory.value) return false;
    return !query || file.path.toLocaleLowerCase().includes(query);
  });
});

watch(selectedCategory, (category) => {
  const currentCategory = typeof route.query.category === "string" ? route.query.category : "";
  if (category === currentCategory) return;
  const query = { ...route.query };
  if (category) query.category = category;
  else delete query.category;
  router.replace({ query });
});

watch(
  () => route.query.category,
  (category) => {
    const nextCategory = typeof category === "string" ? category : "";
    if (nextCategory !== selectedCategory.value) selectedCategory.value = nextCategory;
  }
);

function resourceUrl(file) {
  return buildPublicFileUrl("resource", file.path);
}

async function copyUrl(file) {
  try {
    await copyText(resourceUrl(file));
    Toast.success("资源 URL 已复制");
  } catch (error) {
    console.error("复制资源 URL 失败:", error);
    Toast.error("复制失败，请手动复制");
  }
}

async function loadResources() {
  start();
  try {
    const result = await getAllResources();
    if (!Array.isArray(result)) throw new Error("Invalid resource list");
    files.value = result;
    errorMessage.value = "";
  } catch (error) {
    console.error("加载资源文件失败:", error);
    files.value = [];
    errorMessage.value = "资源文件加载失败，请稍后再试";
  } finally {
    stop();
  }
}

function formatTime(timestamp) {
  const value = Number(timestamp);
  if (!Number.isFinite(value)) return "-";
  return new Date(value * 1000).toLocaleString();
}

function formatFileSize(bytes) {
  const value = Number(bytes);
  if (!Number.isFinite(value) || value < 0) return "-";
  if (value === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let size = value;
  let unit = 0;
  while (size >= 1024 && unit < units.length - 1) {
    size /= 1024;
    unit += 1;
  }
  return size.toFixed(size >= 10 || unit === 0 ? 0 : 1) + " " + units[unit];
}

onMounted(loadResources);
</script>

<style scoped>
@import url("../../assets/components/admin-content.css");

.filter-bar input,
.filter-bar select {
  min-width: min(220px, 100%);
}

.file-row {
  align-items: center;
}

.file-primary {
  min-width: 280px;
  flex: 1 1 360px;
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: center;
  gap: 6px 10px;
}

.file-primary strong {
  min-width: 0;
  overflow-wrap: anywhere;
}

.file-primary code {
  grid-column: 1 / -1;
  color: var(--app-text-muted);
  font-size: 12px;
  overflow-wrap: anywhere;
}

.category-badge {
  width: fit-content;
  padding: 3px 8px;
  border-radius: 999px;
  background: var(--accent-weak);
  color: var(--app-blue);
  font-size: 11px;
  font-weight: 700;
}

@media (max-width: 768px) {
  .filter-bar input,
  .filter-bar select {
    width: 100%;
  }
}
</style>
