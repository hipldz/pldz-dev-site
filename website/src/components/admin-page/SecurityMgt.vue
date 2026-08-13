<template>
  <div class="content-container">
    <div class="content-header">
      <h1>账号安全</h1>
      <p>管理当前管理员账号的登录保护</p>
    </div>

    <div class="content-body">
      <div class="error-banner" v-if="errorMessage">{{ errorMessage }}</div>

      <section class="security-section">
        <div class="security-user">
          <img :src="avatar || '/api/v1/website/image/avatar/default.jpg'" alt="当前账号头像" />
          <div class="security-user-copy">
            <strong>{{ nickname || username || "当前账号" }}</strong>
            <span>{{ username || "-" }}</span>
          </div>
        </div>
        <div class="security-status" :class="{ active: twoFactorEnabled }">
          <span>两步验证</span>
          <strong>{{ twoFactorEnabled ? "已开启" : "未开启" }}</strong>
        </div>
      </section>

      <section class="security-section security-section--stack">
        <div class="section-heading">
          <h2>{{ twoFactorEnabled ? "关闭两步验证" : "开启两步验证" }}</h2>
          <p>{{ twoFactorEnabled ? "关闭前需要输入验证器应用里的 6 位动态码。" : "使用验证器应用扫码绑定，登录后台时会多一步动态码校验。" }}</p>
        </div>

        <template v-if="twoFactorEnabled">
          <div class="security-form-row">
            <input class="field-input" type="text" inputmode="numeric" autocomplete="one-time-code" placeholder="输入 6 位验证码" v-model="disableCode" />
            <button class="btn btn-danger" :disabled="isBusy" @click="onDisableTwoFactor">关闭两步验证</button>
          </div>
        </template>

        <template v-else>
          <button v-if="!setupData" class="btn btn-primary security-primary-action" :disabled="isBusy" @click="onSetupTwoFactor">生成绑定二维码</button>

          <div v-else class="setup-grid">
            <div v-if="setupData.qr_code" class="qr-frame">
              <img :src="setupData.qr_code" alt="两步验证绑定二维码" />
            </div>

            <div class="setup-details">
              <div>
                <span class="label-sm">手动密钥</span>
                <code>{{ setupData.secret }}</code>
              </div>
              <div class="security-form-row">
                <input class="field-input" type="text" inputmode="numeric" autocomplete="one-time-code" placeholder="输入应用中的 6 位验证码" v-model="setupCode" />
                <button class="btn btn-primary" :disabled="isBusy" @click="onConfirmTwoFactor">确认开启</button>
              </div>
              <button class="btn btn-outline" :disabled="isBusy" @click="onCancelSetup">取消绑定</button>
            </div>
          </div>
        </template>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { useStore } from "vuex";
import { setupTwoFactor, confirmTwoFactor, disableTwoFactor } from "../../utils/apis";
import Toast from "../../utils/toast.js";

const store = useStore();

const username = computed(() => store.state.authState.username);
const nickname = computed(() => store.state.authState.nickname);
const avatar = computed(() => store.state.authState.avatar);
const twoFactorEnabled = computed(() => store.state.authState.twoFactorEnabled);

const errorMessage = ref("");
const setupData = ref(null);
const setupCode = ref("");
const disableCode = ref("");
const isBusy = ref(false);

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
  isBusy.value = true;
  errorMessage.value = "";
  try {
    const res = await setupTwoFactor();
    if (!res?.flag) {
      throw new Error(res?.log || "生成绑定二维码失败");
    }
    setupData.value = res;
    setupCode.value = "";
    Toast.success("绑定二维码已生成");
  } catch (error) {
    errorMessage.value = error.message || "生成绑定二维码失败";
    Toast.error(errorMessage.value);
  } finally {
    isBusy.value = false;
  }
}

function onCancelSetup() {
  setupData.value = null;
  setupCode.value = "";
}

async function onConfirmTwoFactor() {
  if (!setupCode.value) {
    errorMessage.value = "请输入验证码";
    return;
  }

  isBusy.value = true;
  errorMessage.value = "";
  try {
    const res = await confirmTwoFactor(setupCode.value);
    if (!res?.flag) {
      throw new Error(res?.log || "开启两步验证失败");
    }
    await updateAuthState(res);
    setupData.value = null;
    setupCode.value = "";
    Toast.success("两步验证已开启");
  } catch (error) {
    errorMessage.value = error.message || "开启两步验证失败";
    Toast.error(errorMessage.value);
  } finally {
    isBusy.value = false;
  }
}

async function onDisableTwoFactor() {
  if (!disableCode.value) {
    errorMessage.value = "请输入验证码";
    return;
  }

  isBusy.value = true;
  errorMessage.value = "";
  try {
    const res = await disableTwoFactor(disableCode.value);
    if (!res?.flag) {
      throw new Error(res?.log || "关闭两步验证失败");
    }
    await updateAuthState(res);
    disableCode.value = "";
    Toast.success("两步验证已关闭");
  } catch (error) {
    errorMessage.value = error.message || "关闭两步验证失败";
    Toast.error(errorMessage.value);
  } finally {
    isBusy.value = false;
  }
}
</script>

<style scoped>
@import url("../../assets/components/admin-content.css");

.security-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 18px 0;
  border-bottom: 1px solid var(--app-border);
}

.security-section--stack {
  align-items: stretch;
  flex-direction: column;
}

.security-user {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.security-user img {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  object-fit: cover;
  border: 1px solid var(--app-border);
  background: var(--app-surface);
}

.security-user-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.security-user-copy strong {
  color: var(--app-text);
  font-size: 16px;
  font-weight: 700;
}

.security-user-copy span {
  color: var(--app-text-muted);
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.security-status {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 999px;
  border: 1px solid var(--app-border);
  background: var(--app-surface);
  color: var(--app-text-muted);
  white-space: nowrap;
}

.security-status.active {
  border-color: rgba(93, 122, 74, 0.28);
  background: rgba(93, 122, 74, 0.1);
  color: var(--app-green);
}

.security-status span,
.security-status strong {
  font-size: 13px;
}

.security-status strong {
  font-weight: 700;
}

.section-heading {
  display: grid;
  gap: 6px;
}

.section-heading h2 {
  margin: 0;
  color: var(--app-text);
  font-size: 17px;
  font-weight: 700;
}

.section-heading p {
  margin: 0;
  color: var(--app-text-muted);
  font-size: 14px;
  line-height: 1.7;
}

.security-form-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.security-form-row .field-input {
  max-width: 280px;
}

.security-primary-action {
  align-self: flex-start;
}

.setup-grid {
  display: grid;
  grid-template-columns: 180px minmax(0, 1fr);
  gap: 22px;
  align-items: start;
}

.qr-frame {
  width: 180px;
  height: 180px;
  padding: 12px;
  border: 1px solid var(--app-border);
  border-radius: 16px;
  background: var(--app-surface);
}

.qr-frame img {
  display: block;
  width: 100%;
  height: 100%;
}

.setup-details {
  display: grid;
  gap: 14px;
}

.setup-details code {
  display: block;
  width: 100%;
  padding: 12px;
  overflow-wrap: anywhere;
  border: 1px solid var(--app-border);
  border-radius: 12px;
  background: var(--app-surface);
  color: var(--app-text);
  font-size: 13px;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .security-section {
    align-items: stretch;
    flex-direction: column;
  }

  .security-status {
    align-self: flex-start;
  }

  .setup-grid {
    grid-template-columns: 1fr;
  }

  .qr-frame {
    width: 176px;
    height: 176px;
  }

  .security-form-row {
    align-items: stretch;
    flex-direction: column;
  }

  .security-form-row .field-input {
    max-width: none;
  }
}
</style>
