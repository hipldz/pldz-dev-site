<template>
  <transition name="mobile-drawer-fade">
    <div v-show="modelValue" class="mobile-drawer-overlay" @click="onClose"></div>
  </transition>

  <transition name="mobile-drawer-slide">
    <aside v-show="modelValue" class="mobile-drawer">
      <div class="mobile-drawer__body">
        <div v-if="showNavPlaceholder" class="nav-placeholder"></div>
        <div v-if="$slots.default" class="mobile-drawer__extra">
          <slot></slot>
        </div>
      </div>
    </aside>
  </transition>
</template>

<script setup>
import { onBeforeUnmount, onMounted } from "vue";

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  title: {
    type: String,
    default: "Hi 爬楼的猪",
  },
  subtitle: {
    type: String,
    default: "",
  },
  showNavPlaceholder: {
    type: Boolean,
    default: true,
  },
  closeAtWidth: {
    type: Number,
    default: 840,
  },
});

const emit = defineEmits(["update:modelValue"]);

function onClose() {
  emit("update:modelValue", false);
}

function isDrawerViewport() {
  // Keep touch tablets in the mobile drawer mode, while a narrow desktop
  // window with a fine pointer keeps the desktop navigation contract.
  if (props.closeAtWidth !== 840) return window.innerWidth <= props.closeAtWidth;
  return Boolean(window.matchMedia?.("(max-width: 700px), (max-width: 840px) and (pointer: coarse)").matches);
}

function handleResize() {
  if (!isDrawerViewport() && props.modelValue) onClose();
}

onMounted(() => {
  window.addEventListener("resize", handleResize, { passive: true });
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);
});
</script>

<style scoped>
.mobile-drawer-overlay {
  position: fixed;
  inset: 0;
  z-index: 70;
  background: var(--app-overlay);
}

.mobile-drawer {
  position: fixed;
  top: 68px;
  right: auto;
  bottom: 0;
  left: 0;
  z-index: 80;
  width: min(312px, calc(100vw - 32px));
  background: var(--app-surface);
  border-right: 1px solid var(--app-border);
  box-shadow: var(--app-shadow-popover);
  overflow-y: auto;
  overflow-x: hidden;
  overscroll-behavior: contain;
  -webkit-overflow-scrolling: touch;
}

@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .mobile-drawer-overlay {
    top: 64px;
  }

  .mobile-drawer {
    top: 64px;
  }
}

@media (max-width: 640px) {
  .mobile-drawer-overlay {
    top: 58px;
  }

  .mobile-drawer {
    top: 58px;
  }
}

.mobile-drawer__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 18px 14px;
  border-bottom: 1px solid var(--app-border);
}

.mobile-drawer__brand {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.mobile-drawer__logo {
  width: 34px;
  height: 34px;
  flex: 0 0 34px;
  border-radius: 11px;
  background: var(--app-surface) url("../assets/svgs/logo-32.svg") no-repeat center / 22px;
  border: 1px solid var(--app-border);
}

.mobile-drawer__title {
  font-size: 16px;
  font-weight: 700;
  color: var(--app-text);
}

.mobile-drawer__subtitle {
  margin-top: 2px;
  font-size: 12px;
  color: var(--app-text-soft);
}

.mobile-drawer__close {
  width: 36px;
  height: 36px;
  border: 1px solid var(--app-border);
  border-radius: 999px;
  background: var(--app-surface);
  color: var(--app-text-muted);
  display: grid;
  place-items: center;
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
}
.mobile-drawer__close .material-symbols-rounded {
  font-size: 20px;
}
.mobile-drawer__close:hover {
  background: var(--app-surface-sunken);
  color: var(--app-text);
}

.mobile-drawer__body {
  padding: 14px 18px 24px;
}

.mobile-drawer__extra {
  margin-top: 18px;
  padding-top: 18px;
  border-top: 1px solid var(--app-border);
}

.mobile-drawer__extra :deep(p) {
  margin: 0;
  color: var(--app-text-muted);
  line-height: 1.7;
}

.mobile-drawer__extra :deep(p + p) {
  margin-top: 8px;
}

.mobile-drawer-fade-enter-active,
.mobile-drawer-fade-leave-active {
  transition: opacity 0.2s ease;
}

.mobile-drawer-fade-enter-from,
.mobile-drawer-fade-leave-to {
  opacity: 0;
}

.mobile-drawer-slide-enter-active,
.mobile-drawer-slide-leave-active {
  transition:
    opacity 0.22s ease,
    transform 0.22s ease;
}

.mobile-drawer-slide-enter-from,
.mobile-drawer-slide-leave-to {
  opacity: 0;
  transform: translateX(-18px);
}

/* v4.1 · mobile drawer as a proper navigation surface */
@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .mobile-drawer-overlay {
    top: 60px !important;
    z-index: 10001 !important;
  }
  .mobile-drawer {
    top: 60px !important;
    z-index: 10002 !important;
    width: min(88vw, 340px) !important;
  }
  .mobile-drawer__header {
    padding: 18px 16px 14px;
  }
  .mobile-drawer__close {
    width: 44px !important;
    height: 44px !important;
  }
  .mobile-drawer__body {
    padding: 8px 12px 24px;
  }
  .mobile-drawer__extra {
    font-size: 13px;
    line-height: 1.65;
  }
}
</style>
