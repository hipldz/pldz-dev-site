<template>
  <Teleport to="body">
    <dialog
      ref="dialog"
      class="account-dialog"
      :class="{ 'account-dialog--wide': wide }"
      :aria-labelledby="titleId"
      :aria-describedby="description ? descriptionId : undefined"
      @cancel.prevent="requestClose"
      @click="onBackdrop"
    >
      <header class="dialog-heading">
        <div class="dialog-symbol">
          <span class="material-symbols-rounded" aria-hidden="true">{{ icon }}</span>
        </div>
        <button type="button" class="dialog-close" aria-label="关闭弹窗" :disabled="busy" @click="requestClose">
          <span class="material-symbols-rounded" aria-hidden="true">close</span>
        </button>
        <div class="dialog-heading-copy">
          <h2 :id="titleId">{{ title }}</h2>
          <p v-if="description" :id="descriptionId" class="dialog-description">{{ description }}</p>
        </div>
      </header>
      <div class="dialog-content"><slot /></div>
      <footer v-if="$slots.footer" class="dialog-actions"><slot name="footer" /></footer>
    </dialog>
  </Teleport>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, onDeactivated, useId } from "vue";
const props = defineProps({
  open: Boolean,
  busy: Boolean,
  title: String,
  description: String,
  wide: Boolean,
  icon: { type: String, default: "shield" },
});
const emit = defineEmits(["close"]);
const dialog = ref(null);
const titleId = useId();
const descriptionId = useId();
let previousOverflow;
let previousFocus;
function syncOpen() {
  if (!dialog.value) return;
  if (props.open && !dialog.value.open) {
    previousFocus = document.activeElement;
    previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    dialog.value.showModal();
  } else if (!props.open) closeDialog();
}
function closeDialog() {
  if (!dialog.value?.open) return;
  dialog.value.close();
  document.body.style.overflow = previousOverflow || "";
  if (previousFocus?.isConnected) previousFocus.focus();
}
function requestClose() {
  if (!props.busy) emit("close");
}
function onBackdrop(event) {
  if (event.target !== dialog.value) return;
  const bounds = dialog.value.getBoundingClientRect();
  if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) requestClose();
}
watch(() => props.open, syncOpen, { flush: "post" });
onMounted(syncOpen);
onBeforeUnmount(closeDialog);
onDeactivated(closeDialog);
</script>

<style scoped>
.account-dialog {
  box-sizing: border-box;
  width: min(460px, calc(100% - 32px));
  max-height: calc(100dvh - 32px);
  margin: auto;
  padding: 0;
  overflow: hidden;
  border: 1px solid var(--app-border);
  border-radius: 16px;
  background: var(--app-surface);
  color: var(--app-text);
  box-shadow: 0 24px 90px #0003;
}
.account-dialog[open] {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  animation: dialog-enter 0.2s ease-out;
}
.account-dialog::backdrop {
  background: #10182766;
  backdrop-filter: blur(6px);
}
.account-dialog--wide {
  width: min(560px, calc(100% - 32px));
}
.dialog-heading {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 22px 56px 20px 24px;
  border-bottom: 1px solid var(--app-border);
}
.dialog-heading-copy {
  min-width: 0;
}
.dialog-symbol {
  display: grid;
  place-items: center;
  flex: 0 0 36px;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--accent-weak);
  color: var(--app-blue);
}
.dialog-symbol span {
  font-size: 21px;
}
.dialog-close {
  position: absolute;
  top: 20px;
  right: 20px;
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: var(--app-text-muted);
  cursor: pointer;
}
.dialog-close:hover {
  background: var(--accent-weak);
}
.dialog-close span {
  font-size: 20px;
}
.dialog-heading h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 650;
  letter-spacing: -0.03em;
  line-height: 1.4;
}
.dialog-description {
  margin: 5px 0 0;
  font-size: 13px;
  color: var(--app-text-muted);
  line-height: 1.7;
}
.dialog-content {
  min-height: 0;
  overflow-y: auto;
  overscroll-behavior: contain;
  padding: 22px 24px;
  scrollbar-width: thin;
  scrollbar-color: var(--app-border) transparent;
}
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 24px;
  border-top: 1px solid var(--app-border);
  background: var(--app-surface);
}
.dialog-actions :deep(button) {
  min-height: 40px;
  padding: 8px 18px;
}

:deep(.dialog-form) {
  display: grid;
  gap: 16px;
}
:deep(.dialog-field) {
  display: grid;
  gap: 8px;
  color: var(--app-text);
  font-size: 13px;
  font-weight: 500;
}
:deep(.dialog-input) {
  box-sizing: border-box;
  width: 100%;
  min-width: 0;
  height: 46px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  padding: 0 14px;
  background: var(--app-bg);
  color: var(--app-text);
  font: inherit;
  font-size: 16px;
  transition:
    border-color 0.15s,
    box-shadow 0.15s;
}
:deep(.dialog-input:focus) {
  outline: none;
  border-color: var(--app-blue);
  box-shadow: none;
}
:deep(.dialog-input::placeholder) {
  color: var(--app-text-muted);
  font-size: 13px;
  font-weight: 400;
}
:deep(.dialog-otp) {
  text-align: center;
  letter-spacing: 0.25em;
  text-indent: 0.25em;
  font-family: var(--font-sans);
  font-variant-numeric: tabular-nums;
  font-size: 24px;
  font-weight: 500;
}
:deep(.dialog-otp::placeholder) {
  font-size: inherit;
  font-weight: inherit;
  opacity: 0.65;
}
:deep(.dialog-primary),
:deep(.dialog-secondary),
:deep(.dialog-danger) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 46px;
  padding: 10px 16px;
  border: 1px solid transparent;
  border-radius: 8px;
  font: inherit;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: filter 0.15s;
}
:deep(.dialog-primary) {
  background: var(--app-blue);
  color: #fff;
  box-shadow: 0 4px 10px color-mix(in srgb, var(--app-blue) 18%, transparent);
}
:deep(.dialog-secondary) {
  background: var(--app-surface);
  color: var(--app-text-muted);
  border-color: var(--app-border);
}
:deep(.dialog-danger) {
  background: var(--app-red);
  color: #fff;
}
:deep(button:disabled),
.dialog-close:disabled {
  opacity: 0.55;
  cursor: wait;
}
:deep(button:focus-visible),
.dialog-close:focus-visible {
  outline: 2px solid var(--app-blue);
  outline-offset: 3px;
}
:deep(.dialog-primary:hover:not(:disabled)),
:deep(.dialog-danger:hover:not(:disabled)) {
  filter: brightness(1.08);
}
:deep(.dialog-error) {
  margin: 0;
  padding: 10px 12px;
  background: color-mix(in srgb, var(--app-red) 8%, transparent);
  color: var(--app-red);
  border-radius: 10px;
  font-size: 13px;
  line-height: 1.6;
}
@keyframes dialog-enter {
  from {
    opacity: 0;
    transform: translateY(8px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: none;
  }
}
@media (max-width: 480px) {
  .dialog-heading {
    padding: 18px 48px 16px 18px;
  }
  .dialog-content {
    padding: 18px;
  }
  .dialog-actions {
    padding: 14px 18px;
  }
}
@media (prefers-reduced-motion: reduce) {
  .account-dialog[open] {
    animation: none;
  }
}
</style>
