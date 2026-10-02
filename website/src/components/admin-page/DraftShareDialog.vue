<template>
  <AccountDialog :open="true" :busy="sharing" title="临时分享草稿" description="持有链接的人可在有效期内阅读，无需登录。" icon="link" @close="closeShare">
    <form :id="shareFormId" class="dialog-form" @submit.prevent="generateShare">
      <p class="share-title">{{ draft.title || "未命名草稿" }}</p>
      <label class="dialog-field"
        >有效时长
        <select v-model="duration" class="dialog-input" :disabled="sharing">
          <option value="1440">24 小时</option>
          <option value="60">1 小时</option>
          <option value="10080">7 天</option>
          <option value="custom">自定义</option>
        </select>
      </label>
      <label v-if="duration === 'custom'" class="dialog-field"
        >自定义时长（分钟，最多 365 天）<input
          v-model.number="customMinutes"
          class="dialog-input"
          type="number"
          min="1"
          max="525600"
          step="1"
          required
          :readonly="sharing"
      /></label>
      <p v-if="shareError" class="dialog-error" role="alert">{{ shareError }}</p>
      <div v-if="shareResult" class="share-result">
        <label class="dialog-field"
          >分享链接<input ref="shareInput" class="dialog-input" :value="shareResult.url" readonly @focus="$event.target.select()"
        /></label>
        <p>到期时间：{{ new Date(shareResult.expiresAt).toLocaleString() }}</p>
      </div>
    </form>
    <template #footer>
      <button class="dialog-secondary" type="button" :disabled="sharing" @click="closeShare">关闭</button>
      <button v-if="shareResult" class="dialog-primary" type="button" @click="copyShare">{{ copied ? "已复制" : "复制链接" }}</button>
      <button v-else class="dialog-primary" type="submit" :form="shareFormId" :disabled="sharing">{{ sharing ? "正在生成…" : "生成分享链接" }}</button>
    </template>
  </AccountDialog>
</template>

<script setup>
import { onBeforeUnmount, ref, useId, watch } from "vue";
import { createDraftShare } from "../../utils/apis/drafts.js";
import AccountDialog from "../AccountDialog.vue";

const props = defineProps({ draft: { type: Object, required: true } });
const emit = defineEmits(["close"]);
const duration = ref("1440");
const customMinutes = ref(1440);
const sharing = ref(false);
const shareResult = ref(null);
const shareError = ref("");
const copied = ref(false);
const shareInput = ref(null);
const shareFormId = useId();
let requestId = 0;

function closeShare() {
  emit("close");
}
watch([duration, customMinutes], () => {
  shareResult.value = null;
  copied.value = false;
  shareError.value = "";
});
async function generateShare() {
  if (sharing.value) return;
  const minutes = Number(duration.value === "custom" ? customMinutes.value : duration.value);
  if (!Number.isInteger(minutes) || minutes < 1 || minutes > 525600) {
    shareError.value = "请输入 1 至 525600 的整数分钟数";
    return;
  }
  const version = ++requestId;
  sharing.value = true;
  shareError.value = "";
  try {
    const result = await createDraftShare(props.draft.id, minutes);
    if (version !== requestId) return;
    if (!result?.url || !result.expiresAt) throw new Error("生成失败，请确认管理员登录状态后重试");
    shareResult.value = { ...result, url: new URL(result.url, window.location.origin).href };
  } catch (error) {
    if (version === requestId) shareError.value = error.message || "生成分享链接失败";
  } finally {
    if (version === requestId) sharing.value = false;
  }
}
async function copyShare() {
  try {
    await navigator.clipboard.writeText(shareResult.value.url);
    copied.value = true;
  } catch {
    shareInput.value?.focus();
    shareInput.value?.select();
    shareError.value = "请手动复制上方链接";
  }
}

onBeforeUnmount(() => {
  requestId += 1;
});
</script>

<style scoped>
.share-title {
  margin: 0;
  color: var(--app-text-muted);
  font-size: 13px;
  overflow-wrap: anywhere;
}
.share-result {
  display: grid;
  gap: 10px;
}
.share-result p {
  margin: 0;
  color: var(--app-text-muted);
  font-size: 12px;
}
</style>
