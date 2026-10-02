<template>
  <div class="content-container">
    <div class="content-header">
      <h1>文章草稿</h1>
      <p>未发布的文章仅管理员可查看，点击预览会在新窗口打开文章阅读页。</p>
    </div>
    <div class="content-body">
      <div class="content-item">
        <input v-model.trim="keyword" type="search" placeholder="搜索草稿标题、分类或路径" aria-label="搜索草稿" />
        <button class="btn btn-outline" type="button" :disabled="loading" @click="loadDrafts">刷新</button>
      </div>
      <div v-if="error" class="error-banner" role="alert">{{ error }}</div>
      <p v-if="loading" role="status">草稿加载中…</p>
      <div v-else-if="filteredDrafts.length" class="list-block">
        <div v-for="draft in filteredDrafts" :key="draft.id" class="list-row draft-row">
          <div class="draft-info">
            <span class="draft-badge">草稿 · DRAFT</span>
            <strong>{{ draft.title || "未命名草稿" }}</strong>
            <p>{{ draft.summary || "暂无摘要" }}</p>
            <small>{{ draft.category || "未分类" }} · {{ draft.date || "未注明日期" }}</small>
            <code>{{ draft.path }}</code>
          </div>
          <div class="draft-actions">
            <a class="btn btn-info" :href="`/admin/drafts/${encodeURIComponent(draft.id)}/preview`" target="_blank" rel="noopener noreferrer">在新窗口预览</a>
            <button class="btn btn-outline" type="button" @click="shareDraft = draft">临时分享</button>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <p>{{ drafts.length ? "没有匹配的草稿。" : "暂无文章草稿。" }}</p>
      </div>
    </div>
    <DraftShareDialog v-if="shareDraft" :draft="shareDraft" @close="shareDraft = null" />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onDeactivated, onMounted, ref } from "vue";
import { getDraftArticles } from "../../utils/apis/drafts.js";
import DraftShareDialog from "./DraftShareDialog.vue";

const drafts = ref([]);
const keyword = ref("");
const loading = ref(false);
const error = ref("");
let requestId = 0;
const shareDraft = ref(null);
const filteredDrafts = computed(() => {
  const query = keyword.value.toLocaleLowerCase();
  return drafts.value.filter((draft) => `${draft.title} ${draft.category} ${draft.path}`.toLocaleLowerCase().includes(query));
});

async function loadDrafts() {
  const version = ++requestId;
  loading.value = true;
  error.value = "";
  try {
    const result = await getDraftArticles();
    if (version !== requestId) return;
    if (!Array.isArray(result)) throw new Error("草稿列表加载失败，请确认管理员登录状态后重试。");
    drafts.value = result;
  } catch (err) {
    if (version === requestId) {
      drafts.value = [];
      error.value = err.message;
    }
  } finally {
    if (version === requestId) loading.value = false;
  }
}

onMounted(loadDrafts);
onBeforeUnmount(() => {
  requestId += 1;
  shareDraft.value = null;
});
onDeactivated(() => {
  shareDraft.value = null;
});
</script>

<style scoped>
@import url("../../assets/components/admin-content.css");
.draft-row {
  align-items: center;
  gap: 16px;
}
.draft-info {
  min-width: 0;
  flex: 1;
  display: grid;
  gap: 8px;
}
.draft-info p {
  margin: 0;
  color: var(--app-text-muted);
}
.draft-info small,
.draft-info code {
  color: var(--app-text-soft);
}
.draft-info code {
  overflow-wrap: anywhere;
}
.draft-badge {
  width: fit-content;
  padding: 4px 8px;
  border: 1px solid var(--accent-line);
  border-radius: 999px;
  background: var(--accent-weak);
  color: var(--accent);
  font-size: 11px;
  font-weight: 700;
}
.draft-row a {
  text-decoration: none;
}
.draft-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
