<template>
  <AccountDialog
    :open="true"
    :busy="showLoginCss"
    :title="username ? '我的账号' : showRegister ? '创建账号' : requiresTwoFactor ? '验证你的身份' : '欢迎回来'"
    :description="
      username
        ? '管理你的账号与登录保护'
        : showRegister
          ? '加入这里，记录想法，参与交流。'
          : requiresTwoFactor
            ? '输入验证器应用中的动态验证码，完成登录。'
            : '登录后参与评论与交流。'
    "
    :icon="username ? 'person' : requiresTwoFactor ? 'verified_user' : 'login'"
    @close="onCloseLoginForm"
  >
    <template v-if="username">
      <div class="profile-panel">
        <button class="profile-avatar" type="button" aria-label="上传头像" @click="onUploadAvatar">
          <img :src="avatar || '/api/v1/website/image/avatar/default.jpg'" alt="当前账号头像" /><span class="material-symbols-rounded" aria-hidden="true"
            >photo_camera</span
          >
        </button>
        <div class="profile-copy">
          <strong>{{ nickname || username }}</strong>
          <p>{{ username }}</p>
          <span class="role-badge">{{ isadmin ? "管理员" : "普通用户" }}</span>
        </div>
      </div>
      <div class="profile-security">
        <span class="material-symbols-rounded" aria-hidden="true">{{ twoFactorEnabled ? "verified_user" : "shield" }}</span>
        <div>
          <strong>两步验证</strong>
          <p>{{ twoFactorEnabled ? "已开启 · 登录时验证动态码" : isadmin ? "未开启 · 可前往账号安全设置" : "未开启" }}</p>
        </div>
        <span class="status-dot" :class="{ active: twoFactorEnabled }"></span>
      </div>
      <div v-if="isadmin" class="profile-actions">
        <button class="profile-link" type="button" @click="onOpenAdmin">
          <span class="material-symbols-rounded" aria-hidden="true">space_dashboard</span><span>进入后台<small>管理文章与网站内容</small></span
          ><span class="material-symbols-rounded arrow" aria-hidden="true">arrow_forward</span>
        </button>
        <button class="profile-link" type="button" @click="onOpenSecurity">
          <span class="material-symbols-rounded" aria-hidden="true">lock</span><span>账号安全<small>管理登录保护</small></span
          ><span class="material-symbols-rounded arrow" aria-hidden="true">chevron_right</span>
        </button>
      </div>
      <p v-if="error" class="dialog-error" role="alert">{{ error }}</p>
      <button class="logout-button" type="button" :disabled="showLoginCss" @click="onLogout">
        <span class="material-symbols-rounded" aria-hidden="true">logout</span>{{ showLoginCss ? "正在退出…" : "退出登录" }}
      </button>
    </template>
    <form v-else class="dialog-form" @submit.prevent="onLoginOrRegister">
      <label class="dialog-field"
        >{{ showRegister ? "邮箱地址" : "邮箱 / 用户名"
        }}<input
          v-model="name"
          class="dialog-input"
          :type="showRegister ? 'email' : 'text'"
          autocomplete="username"
          placeholder="输入你的账号"
          required
          autofocus
          :readonly="showLoginCss"
      /></label>
      <label class="dialog-field"
        >密码<input
          v-model="pwd"
          class="dialog-input"
          type="password"
          :autocomplete="showRegister ? 'new-password' : 'current-password'"
          placeholder="输入密码"
          required
          :readonly="showLoginCss"
      /></label>
      <label v-if="showRegister" class="dialog-field"
        >昵称<input v-model="nick" class="dialog-input" autocomplete="nickname" placeholder="希望大家如何称呼你" required :readonly="showLoginCss"
      /></label>
      <label v-if="requiresTwoFactor && !showRegister" class="dialog-field"
        >动态验证码<input
          ref="otpInput"
          v-model="otpCode"
          class="dialog-input dialog-otp"
          type="text"
          inputmode="numeric"
          autocomplete="one-time-code"
          maxlength="6"
          pattern="[0-9]{6}"
          placeholder="000000"
          required
          :readonly="showLoginCss"
      /></label>
      <p v-if="error" class="dialog-error" role="alert">{{ error }}</p>
      <button class="dialog-primary" type="submit" :disabled="showLoginCss">
        {{ showLoginCss ? "正在处理…" : showRegister ? "创建账号" : requiresTwoFactor ? "验证并登录" : "登录"
        }}<span v-if="!showLoginCss" class="material-symbols-rounded" aria-hidden="true">arrow_forward</span>
      </button>
      <p class="auth-switch">
        {{ showRegister ? "已经有账号？" : "还没有账号？" }}
        <button type="button" :disabled="showLoginCss" @click="onSwitchRegister">{{ showRegister ? "返回登录" : "注册账号" }}</button>
      </p>
      <p class="agreement">
        继续即表示同意 <a href="/api/v1/resource/website/legal/user-agreement" target="_blank" rel="noopener noreferrer">用户协议</a> 与
        <a href="/api/v1/resource/website/legal/privacy-policy" target="_blank" rel="noopener noreferrer">隐私政策</a>
      </p>
    </form>
  </AccountDialog>
</template>

<script setup>
import { useStore } from "vuex";
import { useRouter } from "vue-router";

import { ref, computed, nextTick, onDeactivated } from "vue";
import { login, register, logout, updateAvatar } from "../utils/apis";
import { uploadAvatar } from "../utils/file-upload.js";
import Toast from "../utils/toast.js";

import AccountDialog from "./AccountDialog.vue";

const emit = defineEmits(["close-login-form"]);

// 引入 Vuex store
const store = useStore();
// 引入 Vue Router
const router = useRouter();

// 取用户头像
const avatar = computed(() => store.state.authState.avatar);
const username = computed(() => store.state.authState.username);
const nickname = computed(() => store.state.authState.nickname);
const isadmin = computed(() => store.state.authState.isadmin);
const twoFactorEnabled = computed(() => store.state.authState.twoFactorEnabled);

// 用户名和密码的响应式引用
const name = ref("");
const pwd = ref("");
const nick = ref("");
const otpCode = ref("");
const error = ref("");
const requiresTwoFactor = ref(false);

// 显示是注册界面的状态
const showRegister = ref(false);

// 显示登陆css
const showLoginCss = ref(false);
const otpInput = ref(null);

/**
 * 检查用户名是否符合要求
 * @returns {boolean} 是否符合要求
 */
function onCheckName() {
  // 检查用户名是否符合要求
  const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  if (!emailPattern.test(name.value)) {
    error.value = "请输入合法的邮箱地址（示例：user@example.com）";
    return false;
  } else {
    error.value = "";
    return true;
  }
}

/**
 * 切换注册界面
 */
function onSwitchRegister() {
  error.value = "";
  showRegister.value = !showRegister.value;
  requiresTwoFactor.value = false;
  otpCode.value = "";
}

async function updateAuthState(res) {
  await store.dispatch("authState/update", {
    username: res.username || "",
    isadmin: res.isadmin || false,
    avatar: res.avatar || "",
    nickname: res.nickname || "",
    two_factor_enabled: res.two_factor_enabled || false,
  });
}

/**
 * 登录或注册操作
 */
async function onLoginOrRegister() {
  if (showLoginCss.value || (showRegister.value && !onCheckName())) return;
  showLoginCss.value = true;
  error.value = "";
  try {
    const res = showRegister.value ? await register(name.value, pwd.value, nick.value) : await login(name.value, pwd.value, otpCode.value);
    if (res?.flag) {
      await updateAuthState(res);
      onCloseLoginForm();
      Toast.success(showRegister.value ? "注册成功!" : "登录成功!");
    } else if (res?.requires_2fa) {
      if (requiresTwoFactor.value) error.value = res.log || "验证码错误或已过期";
      requiresTwoFactor.value = true;
      await nextTick();
      otpInput.value?.focus();
    } else {
      error.value = res?.log || "操作失败，请稍后再试";
    }
  } catch {
    error.value = "连接失败，请稍后重试";
  } finally {
    showLoginCss.value = false;
  }
}

async function onLogout() {
  if (showLoginCss.value) return;
  showLoginCss.value = true;
  error.value = "";
  try {
    if (!(await logout())) throw new Error("退出失败");
    await store.dispatch("authState/reset");
    onCloseLoginForm();
    Toast.success("退出成功!");
  } catch {
    error.value = "退出失败，请稍后重试";
  } finally {
    showLoginCss.value = false;
  }
}

/**
 * 关闭登录表单
 */
function onCloseLoginForm() {
  emit("close-login-form");
}

onDeactivated(onCloseLoginForm);

function onOpenAdmin() {
  if (isadmin.value) {
    router.push({ path: "/admin" });
    onCloseLoginForm();
  }
}

function onOpenSecurity() {
  if (isadmin.value) {
    router.push({ path: "/admin/security" });
    onCloseLoginForm();
  }
}

/**
 * 上传头像
 * @returns {Promise<void>}
 */
async function onUploadAvatar(event) {
  // 阻止事件冒泡，避免触发关闭登录表单
  event.stopPropagation();

  try {
    const res = await uploadAvatar(username.value);
    if (res?.data && res.data?.flag && res.data?.url) {
      // 更新 中的头像
      await store.dispatch("authState/avatar", res.data.url);
      await updateAvatar(res.data.url);
    } else {
      error.value = "头像上传失败，请稍后再试";
    }
  } catch {
    error.value = "头像上传失败，请稍后再试";
  }
}
</script>

<style scoped>
.profile-panel {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 22px;
}
.profile-avatar {
  position: relative;
  flex: 0 0 64px;
  width: 64px;
  height: 64px;
  padding: 0;
  border: 1px solid var(--app-border);
  border-radius: 18px;
  background: var(--app-bg);
  cursor: pointer;
  overflow: hidden;
}
.profile-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.profile-avatar > span {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  background: #0006;
  color: #fff;
  opacity: 0;
  transition: opacity 0.15s;
}
.profile-avatar:hover > span,
.profile-avatar:focus-visible > span {
  opacity: 1;
}
.profile-copy {
  min-width: 0;
}
.profile-copy strong {
  font-size: 18px;
  overflow-wrap: anywhere;
}
.profile-copy p {
  margin: 4px 0 8px;
  font-size: 13px;
  color: var(--app-text-muted);
  overflow-wrap: anywhere;
}
.role-badge {
  padding: 3px 8px;
  border-radius: 6px;
  background: var(--accent-weak);
  color: var(--app-blue);
  font-size: 11px;
}
.profile-security {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border: 1px solid var(--app-border);
  border-radius: 12px;
  background: var(--app-bg);
}
.profile-security > span:first-child {
  color: var(--app-blue);
  font-size: 22px;
}
.profile-security strong {
  font-size: 13px;
  font-weight: 600;
}
.profile-security p {
  margin: 4px 0 0;
  color: var(--app-text-muted);
  font-size: 12px;
  line-height: 1.6;
}
.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--app-text-muted);
  margin-left: auto;
  flex-shrink: 0;
}
.status-dot.active {
  background: var(--app-green);
}
.profile-actions {
  display: grid;
  gap: 6px;
  margin: 16px 0;
}
.profile-link {
  width: 100%;
  display: flex;
  align-items: center;
  text-align: left;
  gap: 12px;
  padding: 12px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: var(--app-text);
  cursor: pointer;
  font: inherit;
  font-size: 14px;
}
.profile-link:hover {
  background: var(--accent-weak);
}
.profile-link > span:first-child {
  color: var(--app-blue);
  font-size: 22px;
}
.profile-link small {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: var(--app-text-muted);
}
.profile-link .arrow {
  margin-left: auto;
  font-size: 18px;
  color: var(--app-text-muted);
}
.logout-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  margin-top: 16px;
  padding: 16px 0 0;
  border: 0;
  border-top: 1px solid var(--app-border);
  background: transparent;
  color: var(--app-red);
  cursor: pointer;
  font: inherit;
  font-size: 13px;
}
.logout-button span {
  font-size: 18px;
}
.auth-switch,
.agreement {
  margin: 0;
  text-align: center;
  font-size: 13px;
  color: var(--app-text-muted);
  line-height: 1.7;
}
.auth-switch button {
  border: 0;
  padding: 0;
  background: transparent;
  color: var(--app-blue);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}
.agreement {
  font-size: 11px;
  padding-top: 16px;
  border-top: 1px solid var(--app-border);
}
.agreement a {
  color: var(--app-text-muted);
  text-underline-offset: 3px;
}
</style>
