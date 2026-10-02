<template>
  <div class="content-container">
    <div class="content-header">
      <h1>账号安全</h1>
      <p>管理当前管理员账号的登录保护</p>
    </div>
    <div class="content-body">
      <div class="security-user">
        <img :src="avatar || '/api/v1/website/image/avatar/default.jpg'" alt="当前账号头像" />
        <div>
          <strong>{{ nickname || username || "当前账号" }}</strong>
          <p>{{ username }}</p>
        </div>
        <span class="account-label">管理员账号</span>
      </div>
      <section class="security-card">
        <div class="security-icon" :class="{ enabled: twoFactorEnabled }">
          <span class="material-symbols-rounded" aria-hidden="true">{{ twoFactorEnabled ? "verified_user" : "shield" }}</span>
        </div>
        <div class="security-copy">
          <div class="security-title">
            <h2>两步验证</h2>
            <span class="security-status" :class="{ active: twoFactorEnabled }">{{ twoFactorEnabled ? "已开启" : "未开启" }}</span>
          </div>
          <p>在密码之外，再为账号加一道保护。使用验证器应用生成动态码，验证每一次登录。</p>
        </div>
        <button class="security-action" :class="{ secondary: twoFactorEnabled }" type="button" @click="twoFactorEnabled ? onOpenDisable() : onSetupTwoFactor()">
          {{ twoFactorEnabled ? "管理验证" : "开启两步验证" }}<span class="material-symbols-rounded" aria-hidden="true">arrow_forward</span>
        </button>
      </section>
      <p class="security-note"><span class="material-symbols-rounded" aria-hidden="true">lock</span>动态验证码仅用于身份验证，请勿分享给他人。</p>
    </div>
    <AccountDialog
      :open="dialogOpen"
      :busy="isBusy"
      wide
      :title="dialogMode === 'setup' ? '开启两步验证' : '关闭两步验证'"
      :description="dialogMode === 'setup' ? '绑定验证器，为你的账号添加额外保护。' : '关闭后，登录将只使用账号和密码。'"
      icon="verified_user"
      @close="onCancelSetup"
    >
      <form :id="formId" class="dialog-form" @submit.prevent="dialogMode === 'setup' ? onConfirmTwoFactor() : onDisableTwoFactor()">
        <template v-if="dialogMode === 'setup'">
          <div v-if="!setupData" class="setup-loading" role="status">{{ isBusy ? "正在准备绑定二维码…" : "二维码生成失败，请重试。" }}</div>
          <template v-else>
            <div class="scan-panel">
              <div v-if="setupData.qr_code" class="qr-frame"><img :src="setupData.qr_code" alt="两步验证绑定二维码" /></div>
              <div class="scan-copy">
                <strong>使用验证器扫描二维码</strong>
                <p>打开 Microsoft Authenticator、Google Authenticator 等应用，添加账号。</p>

                <details class="manual-key">
                  <summary>无法扫码？使用手动密钥</summary>
                  <div class="secret-row">
                    <code>{{ setupData.secret }}</code
                    ><button type="button" :aria-label="copied ? '密钥已复制' : '复制密钥'" @click="onCopySecret">
                      <span class="material-symbols-rounded" aria-hidden="true">{{ copied ? "check" : "content_copy" }}</span>
                    </button>
                  </div>
                </details>
              </div>
            </div>
            <label class="dialog-field"
              >验证器中的 6 位动态码<input
                ref="codeInput"
                v-model="setupCode"
                class="dialog-input dialog-otp"
                inputmode="numeric"
                autocomplete="one-time-code"
                maxlength="6"
                pattern="[0-9]{6}"
                placeholder="000000"
                required
                :readonly="isBusy"
            /></label>
          </template>
        </template>
        <template v-else>
          <div class="disable-notice"><span class="material-symbols-rounded" aria-hidden="true">info</span>请先验证身份，确认由你本人关闭登录保护。</div>
          <label class="dialog-field"
            >验证器中的 6 位动态码<input
              ref="codeInput"
              v-model="disableCode"
              class="dialog-input dialog-otp"
              inputmode="numeric"
              autocomplete="one-time-code"
              maxlength="6"
              pattern="[0-9]{6}"
              placeholder="000000"
              required
              :readonly="isBusy"
          /></label>
        </template>
        <p v-if="errorMessage" class="dialog-error" role="alert">{{ errorMessage }}</p>
      </form>
      <template #footer>
        <button class="dialog-secondary" type="button" :disabled="isBusy" @click="onCancelSetup">取消</button
        ><button v-if="dialogMode === 'setup' && !setupData" class="dialog-primary" type="button" :disabled="isBusy" @click="onSetupTwoFactor">
          {{ isBusy ? "正在准备…" : "重新生成" }}</button
        ><button v-else :class="dialogMode === 'setup' ? 'dialog-primary' : 'dialog-danger'" type="submit" :form="formId" :disabled="isBusy">
          {{ isBusy ? "正在验证…" : dialogMode === "setup" ? "验证并开启" : "确认关闭" }}
        </button>
      </template>
    </AccountDialog>
  </div>
</template>

<script setup>
import { computed, ref, nextTick, watch, useId, onBeforeUnmount, onDeactivated } from "vue";
import { useStore } from "vuex";
import { setupTwoFactor, confirmTwoFactor, disableTwoFactor } from "../../utils/apis";
import Toast from "../../utils/toast.js";

import AccountDialog from "../AccountDialog.vue";

const store = useStore();
const formId = useId();

const username = computed(() => store.state.authState.username);
const nickname = computed(() => store.state.authState.nickname);
const avatar = computed(() => store.state.authState.avatar);
const twoFactorEnabled = computed(() => store.state.authState.twoFactorEnabled);

const errorMessage = ref("");
const setupData = ref(null);
const setupCode = ref("");
const disableCode = ref("");
const isBusy = ref(false);
const dialogOpen = ref(false);
const dialogMode = ref("setup");
const codeInput = ref(null);
const copied = ref(false);
let requestVersion = 0;

async function updateAuthState(res) {
  await store.dispatch("authState/update", {
    username: res.username || "",
    isadmin: res.isadmin || false,
    avatar: res.avatar || "",
    nickname: res.nickname || "",
    two_factor_enabled: res.two_factor_enabled || false,
  });
}

async function onSetupTwoFactor() {
  if (isBusy.value) return;
  const version = ++requestVersion;
  dialogMode.value = "setup";
  dialogOpen.value = true;
  copied.value = false;
  isBusy.value = true;
  errorMessage.value = "";
  try {
    const res = await setupTwoFactor();
    if (version !== requestVersion) return;
    if (!res?.flag) {
      throw new Error(res?.log || "生成绑定二维码失败");
    }
    setupData.value = res;
    setupCode.value = "";
    await nextTick();
    codeInput.value?.focus({ preventScroll: true });
  } catch (error) {
    if (version !== requestVersion) return;
    errorMessage.value = error.message || "生成绑定二维码失败";
    Toast.error(errorMessage.value);
  } finally {
    if (version === requestVersion) isBusy.value = false;
  }
}

function onCancelSetup() {
  requestVersion += 1;
  isBusy.value = false;
  dialogOpen.value = false;
  setupData.value = null;
  setupCode.value = "";
  disableCode.value = "";
  errorMessage.value = "";
  copied.value = false;
}
function onOpenDisable() {
  dialogMode.value = "disable";
  errorMessage.value = "";
  dialogOpen.value = true;
  nextTick(() => codeInput.value?.focus());
}
async function onCopySecret() {
  try {
    await navigator.clipboard.writeText(setupData.value.secret);
    copied.value = true;
  } catch {
    Toast.error("复制失败，请手动复制密钥");
  }
}
watch(username, () => onCancelSetup());
onBeforeUnmount(onCancelSetup);
onDeactivated(onCancelSetup);

async function onConfirmTwoFactor() {
  if (isBusy.value) return;
  if (!/^[0-9]{6}$/.test(setupCode.value)) {
    errorMessage.value = "请输入 6 位数字验证码";
    return;
  }

  isBusy.value = true;
  errorMessage.value = "";
  const version = ++requestVersion;
  try {
    const res = await confirmTwoFactor(setupCode.value);
    if (version !== requestVersion) return;
    if (!res?.flag) {
      throw new Error(res?.log || "开启两步验证失败");
    }
    await updateAuthState(res);
    setupData.value = null;
    setupCode.value = "";
    onCancelSetup();
    Toast.success("两步验证已开启");
  } catch (error) {
    if (version !== requestVersion) return;
    errorMessage.value = error.message || "开启两步验证失败";
    Toast.error(errorMessage.value);
  } finally {
    if (version === requestVersion) isBusy.value = false;
  }
}

async function onDisableTwoFactor() {
  if (isBusy.value) return;
  if (!/^[0-9]{6}$/.test(disableCode.value)) {
    errorMessage.value = "请输入 6 位数字验证码";
    return;
  }

  isBusy.value = true;
  errorMessage.value = "";
  const version = ++requestVersion;
  try {
    const res = await disableTwoFactor(disableCode.value);
    if (version !== requestVersion) return;
    if (!res?.flag) {
      throw new Error(res?.log || "关闭两步验证失败");
    }
    await updateAuthState(res);
    disableCode.value = "";
    onCancelSetup();
    Toast.success("两步验证已关闭");
  } catch (error) {
    if (version !== requestVersion) return;
    errorMessage.value = error.message || "关闭两步验证失败";
    Toast.error(errorMessage.value);
  } finally {
    if (version === requestVersion) isBusy.value = false;
  }
}
</script>

<style scoped>
@import url("../../assets/components/admin-content.css");
.security-user {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 0 0 24px;
}
.security-user img {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border: 1px solid var(--app-border);
  border-radius: 14px;
}
.security-user strong {
  font-size: 15px;
  color: var(--app-text);
}
.security-user p {
  margin: 5px 0 0;
  color: var(--app-text-muted);
  font-size: 13px;
  overflow-wrap: anywhere;
}
.account-label {
  margin-left: auto;
  font-size: 12px;
  color: var(--app-text-muted);
}
.security-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 26px;
  border: 1px solid var(--app-border);
  border-radius: 18px;
  background: var(--app-surface);
}
.security-icon {
  display: grid;
  place-items: center;
  flex: 0 0 52px;
  width: 52px;
  height: 52px;
  border-radius: 16px;
  background: var(--accent-weak);
  color: var(--app-blue);
}
.security-icon span {
  font-size: 28px;
}
.security-icon.enabled {
  color: var(--app-green);
  background: color-mix(in srgb, var(--app-green) 10%, transparent);
}
.security-copy {
  flex: 1;
}
.security-title {
  display: flex;
  align-items: center;
  gap: 12px;
}
.security-title h2 {
  margin: 0;
  font-size: 17px;
  color: var(--app-text);
}
.security-copy p {
  max-width: 520px;
  margin: 8px 0 0;
  color: var(--app-text-muted);
  font-size: 13px;
  line-height: 1.8;
}
.security-status {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 6px;
  color: var(--app-text-muted);
  background: var(--app-bg);
}
.security-status.active {
  color: var(--app-green);
  background: color-mix(in srgb, var(--app-green) 10%, transparent);
}
.security-action {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex-shrink: 0;
  min-height: 42px;
  padding: 0 16px;
  border: 1px solid transparent;
  border-radius: 10px;
  background: var(--app-blue);
  color: #fff;
  font: inherit;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}
.security-action span {
  font-size: 18px;
}
.security-action.secondary {
  border-color: var(--app-border);
  background: var(--app-surface);
  color: var(--app-text);
}
.security-note {
  display: flex;
  align-items: center;
  gap: 7px;
  margin: 16px 0;
  font-size: 12px;
  color: var(--app-text-muted);
}
.security-note span {
  font-size: 15px;
}
.scan-panel {
  display: grid;
  grid-template-columns: 152px minmax(0, 1fr);
  gap: 22px;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--app-border);
}
.scan-copy strong {
  font-size: 14px;
  color: var(--app-text);
}
.scan-copy p {
  margin: 8px 0 14px;
  font-size: 12px;
  color: var(--app-text-muted);
  line-height: 1.8;
}
.qr-frame {
  width: 132px;
  height: 132px;
  padding: 9px;
  margin: 0;
  box-sizing: content-box;
  border: 1px solid var(--app-border);
  border-radius: 14px;
  background: #fff;
}
.qr-frame img {
  display: block;
  width: 100%;
  height: 100%;
}
.manual-key {
  margin-top: 12px;
  font-size: 12px;
  color: var(--app-text-muted);
}
.manual-key summary {
  cursor: pointer;
  text-align: left;
  color: var(--app-blue);
}
.secret-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 10px;
  border-radius: 8px;
  background: var(--app-bg);
}
.secret-row code {
  flex: 1;
  min-width: 0;
  overflow-wrap: anywhere;
  color: var(--app-text);
  font-size: 12px;
  line-height: 1.6;
  user-select: all;
}
.secret-row button {
  flex-shrink: 0;
  border: 0;
  padding: 5px;
  background: transparent;
  color: var(--app-blue);
  cursor: pointer;
}
.secret-row button span {
  font-size: 18px;
}
.setup-loading {
  padding: 30px 0;
  text-align: center;
  font-size: 13px;
  color: var(--app-text-muted);
}
.disable-notice {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px;
  border-radius: 10px;
  background: var(--accent-weak);
  color: var(--app-text-muted);
  font-size: 13px;
  line-height: 1.7;
}
.disable-notice span {
  color: var(--app-blue);
  font-size: 20px;
}
@media (max-width: 480px) {
  .scan-panel {
    grid-template-columns: 1fr;
    gap: 14px;
  }
  .qr-frame {
    margin: 0 auto;
  }
  .scan-copy {
    text-align: center;
  }
  .manual-key summary {
    text-align: center;
  }
}
@media (max-width: 768px) {
  .security-card {
    flex-wrap: wrap;
    gap: 14px;
    padding: 20px;
  }
  .security-copy {
    flex-basis: calc(100% - 70px);
  }
  .security-action {
    width: 100%;
  }
  .account-label {
    display: none;
  }
}
</style>
