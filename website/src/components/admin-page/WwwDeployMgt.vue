<template>
  <div class="content-container">
    <div class="content-header">
      <h1>WWW 部署</h1>
      <p>查看 GitHub CI WWW 部署记录、错误日志和重试失败任务</p>
    </div>

    <div class="content-body">
      <div class="error-banner" v-if="errorMessage">{{ errorMessage }}</div>

      <div class="content-item">
        <span>部署记录</span>
        <button class="btn btn-outline" type="button" @click="loadDeployments" :disabled="isDeployLoading">刷新</button>
      </div>

      <div v-if="isDeployLoading" class="loading-stack">
        <div v-for="n in 5" :key="`deploy-skeleton-${n}`" class="loading-card">
          <div class="skeleton-line w-60"></div>
          <div class="skeleton-line w-40" style="margin-top: 12px"></div>
        </div>
      </div>

      <div v-else-if="deployments.length" class="list-block">
        <div class="list-row deploy-row" v-for="item in deployments" :key="item.id">
          <div class="deploy-main">
            <div class="deploy-title">
              <strong>{{ item.folder || "未匹配目录" }}</strong>
              <span :class="['status-pill', 'status-pill--' + item.status]">{{ formatStatus(item.status) }}</span>
            </div>
            <div class="deploy-meta">
              <span>{{ item.artifact_url }}</span>
              <span>{{ formatTime(item.created_at) }}</span>
            </div>
            <div v-if="item.error" class="deploy-error">{{ item.error }}</div>
            <details v-if="item.log_tail && item.log_tail.length" class="deploy-log">
              <summary>日志摘要</summary>
              <pre>{{ item.log_tail.join("\n") }}</pre>
            </details>
          </div>

          <div class="inline-actions">
            <button
              class="btn btn-info"
              type="button"
              @click="onRetry(item)"
              :disabled="isRetrying(item.id) || item.status === 'running' || item.status === 'queued'"
            >
              {{ isRetrying(item.id) ? "重试中" : "重试" }}
            </button>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <p>暂无 WWW 部署记录。</p>
        <button class="btn btn-outline" type="button" @click="loadDeployments">刷新</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { getWwwDeployments, retryWwwDeployment } from "../../utils/apis";
import Toast from "../../utils/toast.js";
import { useLoading } from "../../utils/use-loading";

const deployments = ref([]);
const errorMessage = ref("");
const retrying = reactive({});
const { isLoading: isDeployLoading, start: startDeployLoading, stop: stopDeployLoading } = useLoading("admin.www-deployment.list");

const retryingIds = computed(() => new Set(Object.keys(retrying).filter((id) => retrying[id])));

function isRetrying(id) {
  return retryingIds.value.has(id);
}

async function loadDeployments() {
  startDeployLoading();
  try {
    const res = await getWwwDeployments();
    if (!Array.isArray(res)) {
      throw new Error("Invalid deployment list response");
    }
    deployments.value = res;
    errorMessage.value = "";
  } catch (error) {
    console.error(error);
    errorMessage.value = "WWW 部署记录加载失败，请稍后再试";
    Toast.error("WWW 部署记录加载失败");
  } finally {
    stopDeployLoading();
  }
}

async function onRetry(item) {
  retrying[item.id] = true;
  try {
    const res = await retryWwwDeployment(item.id);
    if (!res) {
      throw new Error("Retry request failed");
    }
    Toast.success("已创建重试任务");
    await loadDeployments();
  } catch (error) {
    console.error(error);
    errorMessage.value = "重试任务创建失败，请稍后再试";
    Toast.error("重试任务创建失败");
  } finally {
    retrying[item.id] = false;
  }
}

function formatStatus(status) {
  const map = {
    queued: "排队中",
    running: "部署中",
    success: "成功",
    failed: "失败",
  };
  return map[status] || status || "-";
}

function formatTime(value) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

onMounted(loadDeployments);
</script>

<style scoped>
@import url("../../assets/components/admin-content.css");

.deploy-row {
  align-items: flex-start;
}

.deploy-main {
  flex: 1 1 480px;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.deploy-title {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.deploy-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  color: var(--app-text-muted);
  font-size: 13px;
  word-break: break-all;
}

.deploy-error {
  color: var(--app-red);
  font-size: 13px;
  line-height: 1.6;
  word-break: break-word;
}

.deploy-log {
  font-size: 13px;
  color: var(--app-text-muted);
}

.deploy-log summary {
  cursor: pointer;
  color: var(--app-blue);
}

.deploy-log pre {
  margin: 10px 0 0;
  padding: 12px;
  max-height: 220px;
  overflow: auto;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-md);
  background: var(--app-surface);
  color: var(--app-text-muted);
  white-space: pre-wrap;
  word-break: break-word;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  background: var(--app-surface);
  color: var(--app-text-muted);
  border: 1px solid var(--app-border);
}

.status-pill--success {
  color: #3f6f35;
  border-color: rgba(93, 122, 74, 0.28);
  background: rgba(93, 122, 74, 0.08);
}

.status-pill--failed {
  color: var(--app-red);
  border-color: rgba(180, 71, 47, 0.22);
  background: rgba(180, 71, 47, 0.08);
}

.status-pill--running,
.status-pill--queued {
  color: var(--app-blue);
  border-color: var(--accent-line);
  background: var(--accent-weak);
}
</style>
