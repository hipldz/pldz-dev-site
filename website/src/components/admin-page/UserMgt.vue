<template>
  <div class="content-container user-container">
    <div class="content-header user-header">
      <div>
        <h1>用户管理</h1>
        <p>查看并维护后台账号、权限与基础资料</p>
      </div>
      <button class="btn btn-outline user-refresh" :class="{ 'is-loading': isLoading }" :disabled="isLoading" @click="refresh">刷新</button>
    </div>
    <div class="content-body">
      <div class="error-banner" v-if="errorMessage">{{ errorMessage }}</div>

      <div class="user-summary-grid">
        <article class="user-summary-card">
          <span>用户总数</span>
          <strong>{{ totalUsers }}</strong>
        </article>
        <article class="user-summary-card user-summary-card--admin">
          <span>管理员</span>
          <strong>{{ adminUsers }}</strong>
        </article>
        <article class="user-summary-card user-summary-card--secure">
          <span>已开启两步验证</span>
          <strong>{{ twoFactorUsers }}</strong>
        </article>
      </div>

      <div v-if="isLoading" class="loading-stack">
        <div v-for="n in 4" :key="`user-skeleton-${n}`" class="loading-card">
          <div class="skeleton-line w-25"></div>
          <div class="skeleton-line w-60" style="margin-top: 10px"></div>
          <div class="skeleton-line w-40" style="margin-top: 10px"></div>
        </div>
      </div>

      <div v-else-if="userMgt.users.length" class="user-list">
        <article class="user-card" v-for="(user, index) in userMgt.users" :key="user.username || index">
          <div class="user-card-main">
            <img class="user-avatar" :src="resolveAvatar(user.avatar)" :alt="`${displayName(user)} 的头像`" @error="onAvatarError" />
            <div class="user-identity">
              <div class="user-title-line">
                <span class="user-index">#{{ index + 1 }}</span>
                <strong>{{ displayName(user) }}</strong>
                <span class="status-pill" :class="user.isadmin ? 'status-pill--admin' : 'status-pill--normal'">
                  {{ user.isadmin ? "管理员" : "普通用户" }}
                </span>
              </div>
              <span class="user-email">{{ user.username || "-" }}</span>
            </div>
          </div>

          <div class="user-details">
            <div class="detail-item">
              <span>两步验证</span>
              <strong :class="user.two_factor_enabled ? 'text-success' : 'text-muted'">
                {{ user.two_factor_enabled ? "已开启" : "未开启" }}
              </strong>
            </div>
            <div class="detail-item detail-item--wide">
              <span>头像地址</span>
              <strong :title="user.avatar || '-'">{{ user.avatar || "-" }}</strong>
            </div>
          </div>

          <div class="user-card-actions">
            <button class="btn btn-danger user-delete" @click="onDeleteUserByUsername(user.username)">删除</button>
          </div>
        </article>
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">--</div>
        <p>暂无用户数据，稍后再试或刷新列表。</p>
        <button class="btn btn-outline" @click="refresh">重新加载</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from "vue";
import { getAllUsers, deleteUserByUsername } from "../../utils/apis";
import Toast from "../../utils/toast.js";
import { useLoading } from "../../utils/use-loading";

const DEFAULT_AVATAR = "/api/v1/website/image/avatar/default.jpg";

const errorMessage = ref("");
const userMgt = ref({ users: [] });
const { isLoading, start: startLoading, stop: stopLoading } = useLoading("admin.user.fetch");

const totalUsers = computed(() => userMgt.value.users.length);
const adminUsers = computed(() => userMgt.value.users.filter((user) => user.isadmin).length);
const twoFactorUsers = computed(() => userMgt.value.users.filter((user) => user.two_factor_enabled).length);

function displayName(user) {
  return user.nickname || user.username || "未命名用户";
}

function resolveAvatar(avatar) {
  return avatar || DEFAULT_AVATAR;
}

function onAvatarError(event) {
  if (event.target.src.endsWith(DEFAULT_AVATAR)) return;
  event.target.src = DEFAULT_AVATAR;
}

async function fetchUsers({ showSuccessToast = false } = {}) {
  startLoading();
  try {
    const res = await getAllUsers();
    if (res?.data) {
      userMgt.value.users = res.data;
      errorMessage.value = "";
      if (showSuccessToast) {
        Toast.success("用户数据加载成功");
      }
      return true;
    }
    userMgt.value.users = [];
    errorMessage.value = "获取用户数据失败，请稍后再试";
    Toast.error("获取用户数据失败，请稍后再试");
    return false;
  } catch (error) {
    console.error("获取用户数据失败:", error);
    userMgt.value.users = [];
    errorMessage.value = "获取用户数据失败，请稍后再试";
    Toast.error("获取用户数据失败，请稍后再试");
    return false;
  } finally {
    stopLoading();
  }
}

async function onDeleteUserByUsername(username) {
  if (!username) return;
  if (!confirm(`确定要删除用户 ${username} 吗？`)) return;

  const res = await deleteUserByUsername(username);
  if (res) {
    Toast.success(`用户 ${username} 已删除`);
    await fetchUsers();
  } else {
    errorMessage.value = "删除用户失败，请稍后再试";
    Toast.error("删除用户失败，请稍后再试");
  }
}

function refresh() {
  fetchUsers({ showSuccessToast: true });
}

onMounted(async () => {
  await fetchUsers({ showSuccessToast: true });
});
</script>

<style scoped>
@import url("../../assets/components/admin-content.css");

.user-container {
  gap: 18px;
}

.user-header {
  flex-direction: row;
  align-items: end;
  justify-content: space-between;
  gap: 18px;
}

.user-refresh {
  min-height: 38px;
  border-radius: 8px;
  white-space: nowrap;
}

.user-summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.user-summary-card {
  position: relative;
  overflow: hidden;
  display: grid;
  gap: 8px;
  padding: 16px 18px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  background: var(--app-surface);
  box-shadow: var(--app-shadow-sm);
}

.user-summary-card::before {
  content: "";
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: var(--app-blue);
}

.user-summary-card--admin::before {
  background: var(--app-green);
}

.user-summary-card--secure::before {
  background: var(--app-orange);
}

.user-summary-card span {
  color: var(--app-text-muted);
  font-size: 12px;
  font-weight: 700;
}

.user-summary-card strong {
  color: var(--app-text);
  font-size: 28px;
  line-height: 1;
}

.user-list {
  display: grid;
  gap: 12px;
}

.user-card {
  display: grid;
  grid-template-columns: minmax(280px, 1.1fr) minmax(360px, 1.6fr) auto;
  align-items: center;
  gap: 18px;
  padding: 16px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  background: var(--app-surface);
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.user-card:hover {
  border-color: var(--app-border-strong);
  box-shadow: var(--app-shadow-md);
  transform: none;
}

.user-card-main {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.user-avatar {
  width: 56px;
  height: 56px;
  flex: 0 0 56px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  background: var(--app-surface);
  object-fit: cover;
}

.user-identity {
  display: grid;
  gap: 6px;
  min-width: 0;
}

.user-title-line {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  min-width: 0;
}

.user-title-line strong {
  min-width: 0;
  color: var(--app-text);
  font-size: 16px;
  font-weight: 800;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-index {
  color: var(--app-text-soft);
  font-size: 13px;
  font-weight: 800;
}

.user-email {
  color: var(--app-text-muted);
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0 9px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.status-pill--admin {
  border: 1px solid rgba(93, 122, 74, 0.22);
  background: rgba(93, 122, 74, 0.1);
  color: var(--app-green);
}

.status-pill--normal {
  border: 1px solid var(--app-border);
  background: var(--app-surface-sunken);
  color: var(--app-text-muted);
}

.user-details {
  display: grid;
  grid-template-columns: minmax(120px, 0.7fr) minmax(120px, 0.7fr) minmax(180px, 1.3fr);
  gap: 10px;
  min-width: 0;
}

.detail-item {
  display: grid;
  gap: 5px;
  min-width: 0;
  padding: 10px 12px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  background: var(--app-surface-sunken);
}

.detail-item span {
  color: var(--app-text-muted);
  font-size: 12px;
  font-weight: 700;
}

.detail-item strong {
  min-width: 0;
  color: var(--app-text);
  font-size: 13px;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.text-success {
  color: var(--app-green) !important;
}

.text-muted {
  color: var(--app-text-muted) !important;
}

.user-card-actions {
  display: flex;
  justify-content: flex-end;
}

.user-delete {
  min-width: 70px;
  border-radius: 8px;
}

@media (max-width: 1120px) {
  .user-card {
    grid-template-columns: 1fr;
    align-items: stretch;
  }

  .user-card-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .user-header {
    align-items: stretch;
    flex-direction: column;
  }

  .user-refresh {
    width: 100%;
  }

  .user-summary-grid,
  .user-details {
    grid-template-columns: 1fr;
  }

  .user-card {
    padding: 14px;
  }

  .user-card-main {
    align-items: flex-start;
  }

  .user-avatar {
    width: 52px;
    height: 52px;
    flex-basis: 52px;
  }

  .user-delete {
    width: 100%;
  }
}
</style>
