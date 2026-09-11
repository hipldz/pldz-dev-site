<template>
  <div class="content-container">
    <div class="content-header">
      <h1>缓存文件</h1>
      <p>浏览 data/cache 下的分类文件，复制公开 URL 或执行维护操作</p>
    </div>

    <div class="progress-toast-container" v-if="activeTransfers.length">
      <div v-for="item in activeTransfers" :key="item.name" :class="['progress-toast', 'progress-toast--' + item.state]">
        <div class="progress-toast-title">{{ item.name }}</div>
        <div class="progress-toast-bar">
          <div class="progress-toast-bar-inner" :style="{ width: item.state === 'error' ? '100%' : (item.percent || 0) + '%' }"></div>
        </div>
        <div class="progress-toast-percent">{{ formatProgressText(item) }}</div>
      </div>
    </div>

    <div class="content-body">
      <div class="error-banner" v-if="errorMessage">{{ errorMessage }}</div>

      <div class="content-item">
        <span>上传缓存资源</span>
        <button class="btn btn-primary" @click="onUploadCacheFile" :disabled="isCacheLoading">上传</button>
      </div>

      <div class="content-item filter-bar">
        <span>筛选文件</span>
        <select v-model="selectedCategory" :disabled="isCacheLoading">
          <option value="">全部分类</option>
          <option v-for="category in categories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
        <input v-model.trim="keyword" type="search" placeholder="搜索路径或文件名" />
        <button class="btn btn-outline" type="button" @click="onSelectCacheManagement" :disabled="isCacheLoading">刷新</button>
      </div>

      <div v-if="isCacheLoading" class="loading-stack">
        <div v-for="n in 5" :key="`cache-skeleton-${n}`" class="loading-card">
          <div class="skeleton-line w-60"></div>
          <div class="skeleton-line w-40" style="margin-top: 12px"></div>
        </div>
      </div>

      <div v-else-if="filteredCache.length" class="list-block">
        <div class="list-row" v-for="cache in filteredCache" :key="cache.filename">
          <div class="file-title">
            <span class="category-badge">{{ cache.category || "根目录" }}</span>
            <strong>{{ cache.filename }}</strong>
          </div>
          <div class="field">
            <span class="field-label">更新时间</span>
            <span class="field-value field-value--muted">{{ cache.modified_time }}</span>
          </div>
          <div class="field">
            <span class="field-label">文件大小</span>
            <span class="field-value field-value--muted">{{ formatFileSize(cache.size) }}</span>
          </div>
          <div class="inline-actions">
            <button class="btn btn-outline" @click="onCopyCacheLink(cache)">复制 URL</button>
            <button class="btn btn-info" @click="onDownloadCacheFile(cache)">下载</button>
            <button class="btn btn-danger" @click="onDeleteCacheFile(cache)">删除</button>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">📂</div>
        <p>{{ cacheMgt.length ? "没有符合筛选条件的缓存文件。" : "暂无缓存文件。" }}</p>
        <button class="btn btn-outline" @click="onSelectCacheManagement" :disabled="isCacheLoading">刷新</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getAllCache, deleteCacheFile } from "../../utils/apis";
import { uploadCacheFile } from "../../utils/file-upload.js";
import { buildPublicFileUrl, copyText } from "../../utils/clipboard.js";
import Toast from "../../utils/toast.js";
import { useLoading } from "../../utils/use-loading";

const errorMessage = ref("");
const cacheMgt = ref([]);
const route = useRoute();
const router = useRouter();
const selectedCategory = ref(typeof route.query.category === "string" ? route.query.category : "");
const keyword = ref("");
const transferProgress = reactive({});
const { isLoading: isCacheLoading, start: startCacheLoading, stop: stopCacheLoading } = useLoading("admin.cache.list");

const activeTransfers = computed(() =>
  Object.entries(transferProgress)
    .filter(([, item]) => item.state !== "hidden")
    .map(([name, item]) => ({ name, ...item })),
);

const categories = computed(() => [...new Set(cacheMgt.value.map((file) => file.category).filter(Boolean))].sort((a, b) => a.localeCompare(b)));

const filteredCache = computed(() => {
  const query = keyword.value.toLocaleLowerCase();
  return cacheMgt.value.filter((file) => {
    if (selectedCategory.value && file.category !== selectedCategory.value) return false;
    return !query || file.filename.toLocaleLowerCase().includes(query);
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
  },
);

async function onDeleteCacheFile(file) {
  if (!confirm(`确定要删除 ${file.filename} 吗？`)) return;
  startCacheLoading();
  try {
    const res = await deleteCacheFile(file.filename);
    if (res) {
      await onSelectCacheManagement();
      Toast.success("缓存文件删除成功");
    } else {
      throw new Error("删除缓存文件失败");
    }
  } catch (error) {
    console.error(error);
    errorMessage.value = "删除缓存文件失败，请稍后再试";
    Toast.error("删除缓存文件失败，请稍后再试");
  } finally {
    stopCacheLoading();
  }
}

async function onDownloadCacheFile(fileObj) {
  const fname = fileObj.filename;
  transferProgress[fname] = { percent: 0, loaded: 0, total: 0, state: "downloading", mode: "download" };

  try {
    const res = await fetch("/api/v1/cache/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filename: fname }),
    });
    if (!res.ok) {
      throw new Error(`${res.status} ${res.statusText}`);
    }

    const total = Number(res.headers.get("content-length")) || 0;
    transferProgress[fname].total = total;

    if (!res.body || !res.body.getReader) {
      const blob = await res.blob();
      triggerDownload(blob, fname);
      completeTransfer(fname, total);
      Toast.success("缓存文件下载成功");
      errorMessage.value = "";
      return;
    }

    const reader = res.body.getReader();
    const chunks = [];
    let loaded = 0;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
      loaded += value.length;
      transferProgress[fname].loaded = loaded;
      if (total > 0) {
        transferProgress[fname].percent = Math.min(100, (loaded / total) * 100);
      } else {
        transferProgress[fname].percent = 0;
      }
    }

    const blob = new Blob(chunks, { type: "application/octet-stream" });
    triggerDownload(blob, fname);
    completeTransfer(fname, total || loaded);
    Toast.success("缓存文件下载成功");
    errorMessage.value = "";
  } catch (err) {
    console.error("下载缓存文件失败:", err);
    markTransferFailed(fname);
    errorMessage.value = "下载缓存文件失败，请稍后再试";
    Toast.error("下载缓存文件失败，请稍后再试");
  }
}

async function onCopyCacheLink(fileObj) {
  const link = buildPublicFileUrl("cache", fileObj.filename);
  try {
    await copyText(link);
    Toast.success("缓存 URL 已复制");
    errorMessage.value = "";
  } catch (err) {
    console.error("复制缓存 URL 失败:", err);
    errorMessage.value = "复制缓存 URL 失败，请手动复制";
    Toast.error("复制缓存 URL 失败");
  }
}

function triggerDownload(blob, fname) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = fname;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function completeTransfer(fname, total) {
  if (!transferProgress[fname]) return;
  const entry = transferProgress[fname];
  const finalTotal = total || entry.total || entry.loaded || 0;
  entry.total = finalTotal;
  entry.loaded = finalTotal;
  entry.percent = 100;
  entry.state = "done";
  setTimeout(() => {
    if (transferProgress[fname]) {
      transferProgress[fname].state = "hidden";
    }
    setTimeout(() => {
      delete transferProgress[fname];
    }, 200);
  }, 800);
}

function markTransferFailed(fname) {
  if (!transferProgress[fname]) return;
  transferProgress[fname].state = "error";
  setTimeout(() => {
    if (transferProgress[fname]) {
      transferProgress[fname].state = "hidden";
    }
    setTimeout(() => {
      delete transferProgress[fname];
    }, 200);
  }, 1600);
}

async function onUploadCacheFile() {
  let uploadStarted = false;
  let uploadName = "";
  try {
    const res = await uploadCacheFile({
      onSelected(file) {
        uploadStarted = true;
        uploadName = file.name;
        startCacheLoading();
        transferProgress[uploadName] = {
          percent: 0,
          loaded: 0,
          total: file.size || 0,
          state: "uploading",
          mode: "upload",
        };
      },
      onProgress({ loaded, total }, file) {
        if (!file || !transferProgress[file.name]) return;
        const entry = transferProgress[file.name];
        entry.loaded = loaded;
        entry.total = total || entry.total || file.size || 0;
        if (entry.total > 0) {
          entry.percent = Math.min(100, (entry.loaded / entry.total) * 100);
        } else {
          entry.percent = 0;
        }
      },
      onError(_, file) {
        if (file) {
          markTransferFailed(file.name);
        }
      },
    });

    if (!uploadStarted) {
      return;
    }

    if (res) {
      completeTransfer(uploadName, transferProgress[uploadName]?.total || 0);
      await onSelectCacheManagement();
      Toast.success("缓存文件上传成功");
      errorMessage.value = "";
    } else {
      throw new Error("上传缓存文件失败");
    }
  } catch (error) {
    console.error(error);
    if (uploadName) {
      markTransferFailed(uploadName);
    }
    errorMessage.value = "上传缓存文件失败，请稍后再试";
    Toast.error("上传缓存文件失败，请稍后再试");
  } finally {
    if (uploadStarted) {
      stopCacheLoading();
    }
  }
}

async function onSelectCacheManagement() {
  startCacheLoading();
  try {
    const res = await getAllCache();
    if (Array.isArray(res)) {
      res
        .sort((a, b) => b.modified_time - a.modified_time)
        .forEach((item) => {
          const d = new Date(item.modified_time * 1000);
          item.modified_time = d.toISOString().replace("T", " ").split(".")[0];
          const size = Number(item.size);
          item.size = Number.isFinite(size) ? size : 0;
        });
      cacheMgt.value = res;
      Toast.success("缓存数据加载成功");
      errorMessage.value = "";
    } else {
      throw new Error("获取缓存数据失败");
    }
  } catch (error) {
    console.error(error);
    errorMessage.value = "获取缓存数据失败，请稍后再试";
    Toast.error("获取缓存数据失败，请稍后再试");
    cacheMgt.value = [];
  } finally {
    stopCacheLoading();
  }
}

onMounted(async () => {
  await onSelectCacheManagement();
});

function formatProgressText(item) {
  if (!item) return "";
  if (item.state === "error") {
    return item.mode === "upload" ? "上传失败" : "下载失败";
  }
  if (item.state === "done") {
    return "100%";
  }
  if (item.total > 0) {
    const percent = item.percent || 0;
    return `${Math.min(100, percent).toFixed(0)}%`;
  }

  const loaded = item.loaded || 0;
  if (!loaded) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let size = loaded;
  let unitIndex = 0;
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  const precision = size >= 10 || unitIndex === 0 ? 0 : 1;
  return `${size.toFixed(precision)} ${units[unitIndex]}`;
}

function formatFileSize(bytes) {
  const value = Number(bytes);
  if (!Number.isFinite(value) || value < 0) return "-";
  if (value === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  let size = value;
  let unitIndex = 0;
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  const precision = size >= 10 || unitIndex === 0 ? 0 : 1;
  return `${size.toFixed(precision)} ${units[unitIndex]}`;
}
</script>

<style scoped>
@import url("../../assets/components/admin-content.css");

.progress-toast-container {
  position: fixed;
  top: 88px;
  right: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 1000;
}

.progress-toast {
  min-width: 220px;
  max-width: 280px;
  background: #2a2420;
  color: #ece4d8;
  box-shadow: var(--app-shadow-md);
  border-radius: var(--app-radius-lg);
  padding: 14px 16px;
  border: 1px solid color-mix(in srgb, var(--app-text-soft) 22%, transparent);
}

.progress-toast-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
  word-break: break-all;
}

.progress-toast-bar {
  position: relative;
  width: 100%;
  height: 6px;
  background: rgba(236, 228, 216, 0.16);
  border-radius: 4px;
  overflow: hidden;
}

.progress-toast-bar-inner {
  height: 100%;
  background: var(--accent);
  transition: width 0.2s ease;
}

.progress-toast-percent {
  margin-top: 8px;
  text-align: right;
  font-size: 12px;
  color: rgba(236, 228, 216, 0.8);
  font-weight: 500;
}

.progress-toast--done {
  border-color: rgba(93, 122, 74, 0.4);
}

.progress-toast--done .progress-toast-bar-inner {
  background: var(--app-green);
}

.progress-toast--error {
  border-color: rgba(180, 71, 47, 0.5);
}

.progress-toast--error .progress-toast-bar-inner {
  background: var(--app-red);
}

.file-title {
  min-width: 280px;
  flex: 1 1 340px;
  display: flex;
  align-items: center;
  gap: 10px;
  overflow-wrap: anywhere;
}

.category-badge {
  flex: 0 0 auto;
  padding: 3px 8px;
  border-radius: 999px;
  background: var(--accent-weak);
  color: var(--app-blue);
  font-size: 11px;
  font-weight: 700;
}

.inline-actions {
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 768px) {
  .filter-bar input,
  .filter-bar select {
    width: 100%;
  }

  .progress-toast-container {
    top: auto;
    bottom: 24px;
    right: 16px;
  }

  .inline-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
