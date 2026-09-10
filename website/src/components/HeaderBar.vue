<template>
  <header :class="['header', { 'header--hidden': !isHeaderVisible, 'header--scrolled': hasScrolled }]">
    <div class="header-inner">
      <div class="header-left">
        <button v-if="showMobileMenu" v-burst="'soft'" class="mobile-menu-btn" type="button" aria-label="打开导航菜单" @click="toggleMobileMenu()">
          <span class="material-symbols-rounded" aria-hidden="true">menu</span>
        </button>
        <a v-magnetic="6" v-burst class="brand-link" href="/">
          <span class="app-logo"></span>
          <span class="brand-copy">
            <span class="brand-name">Hi 爬楼的猪</span>
            <span class="brand-subtitle">项目 · 教程 · Demo</span>
          </span>
        </a>
      </div>

      <nav class="header-nav" aria-label="主导航">
        <ul ref="navAllRef" class="nav-menu">
          <li v-for="item in navItems" :key="item.label" :class="['nav-item', { active: isActive(item) }]">
            <a v-burst="'soft'" :href="item.href" :aria-current="isActive(item) ? 'page' : undefined">{{ item.label }}</a>
          </li>
          <li v-for="nav in navs" :key="nav.title" class="nav-item nav-item--external">
            <a v-burst="'soft'" :href="nav.url" target="_blank" rel="noopener noreferrer">
              {{ nav.title }}
              <span v-if="nav.new" class="nav-badge">new</span>
            </a>
          </li>
        </ul>
      </nav>

      <div class="header-right">
        <div class="theme-picker">
          <button v-burst="'soft'" class="theme-trigger" type="button" aria-label="切换主题" :aria-pressed="currentTheme === 'dark'" @click="onToggleTheme">
            <span class="material-symbols-rounded theme-trigger__icon" aria-hidden="true">{{ currentTheme === "dark" ? "dark_mode" : "light_mode" }}</span>
          </button>
        </div>

        <button v-magnetic="6" v-burst class="search-trigger" type="button" aria-label="打开全局搜索与命令面板" title="搜索 / 快速前往" @click="onOpenSearch">
          <span class="material-symbols-rounded search-trigger__icon" aria-hidden="true">search</span>
          <span class="search-trigger__text">搜索</span>
          <kbd class="search-trigger__kbd" aria-hidden="true">{{ shortcutLabel }}</kbd>
        </button>

        <div v-if="avatar" v-burst="'soft'" class="user-avatar" @click="onToggleLoginForm">
          <img :src="avatar" alt="avatar" />
        </div>
        <button v-else v-burst="'soft'" class="login-register-btn" @click="onToggleLoginForm">
          <span class="material-symbols-rounded" aria-hidden="true">person</span><span>登录 / 注册</span>
        </button>
      </div>
    </div>
  </header>

  <LoginCard v-if="showLoginForm" @close-login-form="onCloseLoginForm" />
  <SearchOverlay v-model="searchOpen" />
</template>

<script setup>
import { computed, onActivated, onBeforeUnmount, onDeactivated, onMounted, ref, watch } from "vue";
import { useStore } from "vuex";
import { useRoute } from "vue-router";
import Toast from "../utils/toast.js";
import { getStoredTheme, setStoredTheme } from "../utils/theme";
import LoginCard from "./LoginCard.vue";
import SearchOverlay from "./SearchOverlay.vue";

const props = defineProps({
  routeName: {
    type: String,
    required: false,
    default: "",
  },
  showMobileMenu: {
    type: Boolean,
    required: false,
    default: true,
  },
  scroll: {
    type: Boolean,
    required: false,
    default: true,
  },
});

const emit = defineEmits(["toggle-mobile-menu"]);

const store = useStore();
const route = useRoute();
const avatar = computed(() => store.state.authState.avatar);
const username = computed(() => store.state.authState.username);

const navAllRef = ref(null);
const navs = ref([]);
const showLoginForm = ref(false);
const searchOpen = ref(false);
const isHeaderVisible = ref(true);
const hasScrolled = ref(false);
const currentTheme = ref(getStoredTheme());
const shortcutLabel = ref("Ctrl K");

const navItems = [
  { label: "首页", href: "/", anchor: "" },
  { label: "文章/教程", href: "/articles", anchor: "/articles" },
  { label: "白板", href: "/whiteboard", anchor: "/whiteboard" },
  { label: "Demos", href: "/livedemo", anchor: "/livedemo" },
];

let lastScrollY = 0;
let scrollFrame = 0;
let accumulatedUp = 0;
let accumulatedDown = 0;
let scrollListenerActive = false;
let isActivePage = true;

function isActive(item) {
  if (item.href === "/") return route.path === "/";
  if (item.href === "/articles" && route.path.startsWith("/article/")) return true;
  return route.path === item.href || route.path.startsWith(`${item.href}/`);
}

function handleScroll() {
  const currentY = window.scrollY;
  hasScrolled.value = currentY > 16;
  const diff = currentY - lastScrollY;

  if (Math.abs(diff) < 1) {
    lastScrollY = currentY;
    return;
  }

  if (diff > 0) {
    accumulatedDown += diff;
    accumulatedUp = 0;
    if (accumulatedDown > 10 && currentY > 80 && isHeaderVisible.value) {
      isHeaderVisible.value = false;
      accumulatedDown = 0;
    }
  } else {
    accumulatedUp += -diff;
    accumulatedDown = 0;
    if (accumulatedUp > 40 && !isHeaderVisible.value) {
      isHeaderVisible.value = true;
      accumulatedUp = 0;
    }
  }

  lastScrollY = currentY;
}

function onScrollThrottled() {
  if (scrollFrame) return;
  scrollFrame = window.requestAnimationFrame(() => {
    handleScroll();
    scrollFrame = 0;
  });
}

function isMobileNavigationViewport() {
  return Boolean(window.matchMedia?.("(max-width: 700px), (max-width: 840px) and (pointer: coarse)").matches);
}

function enableScrollHide() {
  // On touch/mobile layouts the header stays stable; hiding it during short swipes
  // made navigation feel broken and caused visible layout jitter.
  if (isMobileNavigationViewport()) {
    disableScrollHide();
    hasScrolled.value = window.scrollY > 16;
    return;
  }
  if (scrollListenerActive) return;
  lastScrollY = window.scrollY;
  hasScrolled.value = lastScrollY > 16;
  window.addEventListener("scroll", onScrollThrottled, { passive: true });
  scrollListenerActive = true;
}

function disableScrollHide() {
  window.cancelAnimationFrame(scrollFrame);
  scrollFrame = 0;
  window.removeEventListener("scroll", onScrollThrottled);
  scrollListenerActive = false;
  isHeaderVisible.value = true;
  accumulatedUp = 0;
  accumulatedDown = 0;
}

function toggleMobileMenu() {
  const placeholders = document.querySelectorAll(".nav-placeholder");
  if (placeholders.length && navAllRef.value) {
    placeholders.forEach((item) => {
      item.innerHTML = "";
      item.appendChild(navAllRef.value.cloneNode(true));
    });
  }
  emit("toggle-mobile-menu");
}

function onToggleLoginForm() {
  showLoginForm.value = true;
  if (username.value) return;

  Toast.info("登录后可以注册aigc账号, 评论文章, 缓存白板内容");
}

function onCloseLoginForm() {
  showLoginForm.value = false;
}

function onOpenSearch() {
  searchOpen.value = true;
}

function onToggleTheme() {
  const nextTheme = currentTheme.value === "dark" ? "light" : "dark";
  currentTheme.value = setStoredTheme(nextTheme);
}

function onViewportResize() {
  if (!isActivePage || !props.scroll) return;
  if (isMobileNavigationViewport()) disableScrollHide();
  else enableScrollHide();
  hasScrolled.value = window.scrollY > 16;
}

function onDocumentKeydown(event) {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    onOpenSearch();
    return;
  }
}

function activateHeader() {
  isActivePage = true;
  shortcutLabel.value = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent || "") ? "⌘ K" : "Ctrl K";
  currentTheme.value = getStoredTheme();
  if (props.scroll) enableScrollHide();
  document.addEventListener("keydown", onDocumentKeydown);
  window.addEventListener("resize", onViewportResize, { passive: true });
}

function deactivateHeader() {
  isActivePage = false;
  disableScrollHide();
  document.removeEventListener("keydown", onDocumentKeydown);
  window.removeEventListener("resize", onViewportResize);
}

watch(
  () => props.scroll,
  (shouldScroll) => {
    if (shouldScroll && isActivePage) enableScrollHide();
    else disableScrollHide();
  },
);

onMounted(activateHeader);
onActivated(activateHeader);
onDeactivated(deactivateHeader);
onBeforeUnmount(deactivateHeader);
</script>

<style scoped>
.header {
  position: fixed;
  inset: 0 0 auto;
  z-index: 10005;
  background: var(--app-header-bg);
  border-bottom: 1px solid transparent;
  transition:
    transform 180ms var(--app-ease),
    background-color 180ms var(--app-ease),
    border-color 180ms var(--app-ease),
    box-shadow 180ms var(--app-ease);
}

.header--scrolled {
  border-bottom-color: color-mix(in srgb, var(--app-border) 80%, transparent);
  background: color-mix(in srgb, var(--app-surface) 92%, transparent);
  box-shadow: 0 8px 30px rgba(31, 36, 52, 0.055);
}

.header--hidden {
  transform: translateY(-100%);
  pointer-events: none;
}

.header-inner {
  width: min(var(--app-page-width), calc(100% - 2 * var(--app-page-gutter)));
  height: 72px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 28px;
}

.header-left,
.header-right,
.brand-link {
  display: flex;
  align-items: center;
}

.header-left {
  min-width: 0;
}
.header-right {
  justify-content: flex-end;
  gap: 8px;
}

.brand-link {
  min-width: 0;
  gap: 11px;
  color: inherit;
  text-decoration: none;
}

.app-logo {
  position: relative;
  width: 34px;
  height: 34px;
  flex: 0 0 34px;
  border-radius: 12px;
  background: var(--app-surface) url("../assets/svgs/logo-32.svg") no-repeat center / 22px;
  border: 1px solid color-mix(in srgb, var(--accent-line) 72%, var(--app-border));
  box-shadow: 0 5px 16px color-mix(in srgb, var(--accent) 11%, transparent);
  transition:
    transform 220ms var(--app-ease),
    border-color 180ms var(--app-ease),
    box-shadow 220ms var(--app-ease);
}
.app-logo::after {
  content: "";
  position: absolute;
  width: 9px;
  height: 9px;
  right: -4px;
  top: -4px;
  opacity: 0;
  background: var(--accent);
  clip-path: polygon(50% 0, 62% 38%, 100% 50%, 62% 62%, 50% 100%, 38% 62%, 0 50%, 38% 38%);
  transform: rotate(-18deg) scale(0.55);
  transition:
    opacity 180ms var(--app-ease),
    transform 220ms var(--app-ease);
}
@media (hover: hover) and (prefers-reduced-motion: no-preference) {
  .brand-link:hover .app-logo {
    transform: translateY(-1px) rotate(-2deg);
    border-color: var(--accent-line);
    box-shadow: 0 8px 20px color-mix(in srgb, var(--accent) 13%, transparent);
  }
  .brand-link:hover .app-logo::after {
    opacity: 0.75;
    transform: rotate(0) scale(1);
  }
}

.brand-copy {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 4px;
}

.brand-name {
  overflow: hidden;
  color: var(--app-text);
  font-size: 15px;
  font-weight: 650;
  letter-spacing: -0.015em;
  line-height: 1.1;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.brand-subtitle {
  color: var(--app-text-soft);
  font-size: 11px;
  letter-spacing: 0.02em;
  line-height: 1;
  white-space: nowrap;
}

.header-nav {
  min-width: 0;
}
.nav-menu {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.nav-item {
  position: relative;
}
.nav-item a {
  display: inline-flex;
  height: 38px;
  align-items: center;
  gap: 6px;
  padding: 0 13px;
  border-radius: 999px;
  color: var(--app-text-muted);
  font-size: 13.5px;
  font-weight: 520;
  text-decoration: none;
  transition:
    color 160ms var(--app-ease),
    background-color 160ms var(--app-ease),
    transform 160ms var(--app-ease);
}

.nav-item a:hover {
  background: var(--app-hover-bg);
  color: var(--app-text);
}

.nav-item.active a {
  background: var(--accent-weak);
  color: var(--accent);
  font-weight: 620;
}
.nav-item.active a::before {
  content: "";
  width: 7px;
  height: 7px;
  flex: 0 0 7px;
  background: currentColor;
  opacity: 0.72;
  clip-path: polygon(50% 0, 62% 38%, 100% 50%, 62% 62%, 50% 100%, 38% 62%, 0 50%, 38% 38%);
}

.nav-item--external a {
  color: var(--app-text-muted);
}
.nav-badge {
  padding: 3px 6px;
  border-radius: 999px;
  background: var(--accent-weak);
  color: var(--accent);
  font-size: 9px;
  line-height: 1;
}

.theme-picker {
  display: inline-flex;
  gap: 4px;
  position: relative;
  flex: 0 0 auto;
}
.theme-trigger,
.search-trigger,
.login-register-btn {
  height: 38px;
  border: 1px solid var(--app-border);
  background: color-mix(in srgb, var(--app-surface) 92%, transparent);
  color: var(--app-text-muted);
  cursor: pointer;
  box-shadow: none;
}

.theme-trigger {
  width: 38px;
  padding: 0;
  border-radius: 11px;
  display: inline-grid;
  place-items: center;
}

.theme-trigger:hover,
.search-trigger:hover {
  border-color: var(--app-border-strong);
  background: var(--app-surface);
  color: var(--app-text);
}

.theme-trigger__icon {
  font-size: 18px;
  color: var(--accent);
}

.search-trigger {
  padding: 0 12px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  gap: 7px;
}
.search-trigger__icon {
  width: auto;
  height: auto;
  font-size: 18px;
  color: currentColor;
}

.search-trigger__text {
  font-size: 13px;
}
.search-trigger__kbd {
  margin-left: 2px;
  padding: 3px 6px;
  border: 1px solid var(--app-border);
  border-radius: 6px;
  background: var(--app-surface-sunken);
  color: var(--app-text-soft);
  font-family: var(--font-sans);
  font-size: 8.5px;
  font-weight: 700;
  line-height: 1;
  box-shadow: inset 0 -1px 0 color-mix(in srgb, var(--app-border-strong) 45%, transparent);
}

.login-register-btn {
  padding: 0 15px;
  border-color: transparent;
  border-radius: 999px;
  background: var(--accent-weak);
  color: var(--accent);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 620;
}
.login-register-btn .material-symbols-rounded {
  font-size: 17px;
}
.login-register-btn:hover {
  background: var(--accent-weak-hover);
  color: var(--accent-hover);
}

.user-avatar {
  width: 38px;
  height: 38px;
  overflow: hidden;
  border: 1px solid var(--app-border);
  border-radius: 50%;
  cursor: pointer;
  box-shadow:
    0 0 0 3px var(--app-surface),
    0 0 0 4px var(--app-border);
}
.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.mobile-menu-btn {
  display: none;
  width: 38px;
  height: 38px;
  margin-right: 8px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--app-text-muted);
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.mobile-menu-btn .material-symbols-rounded {
  font-size: 23px;
}
.mobile-menu-btn:hover {
  background-color: var(--app-hover-bg);
  color: var(--app-text);
}

@media (max-width: 1080px) {
  .header-inner {
    gap: 18px;
  }
  .nav-menu {
    gap: 0;
  }
  .nav-item a {
    padding: 0 10px;
  }
  .nav-item--external {
    display: none;
  }
}

@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .header-inner {
    width: min(100%, calc(100% - 24px));
    height: 64px;
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 12px;
  }
  .header-left,
  .brand-link,
  .brand-copy {
    overflow: hidden;
  }
  .brand-link {
    gap: 9px;
  }
  .header-nav {
    display: none;
  }
  .mobile-menu-btn {
    display: inline-flex;
    flex-shrink: 0;
  }
  .brand-subtitle {
    display: none;
  }
}

@media (max-width: 640px) {
  .header-inner {
    width: min(100%, calc(100% - 16px));
    height: 58px;
    gap: 7px;
  }
  .header-right {
    gap: 6px;
  }
  .app-logo {
    width: 30px;
    height: 30px;
    flex-basis: 30px;
    background-size: 20px;
    border-radius: 10px;
  }
  .brand-name {
    max-width: 94px;
    font-size: 13.5px;
  }
  .mobile-menu-btn {
    width: 36px;
    height: 36px;
    margin-right: 4px;
  }
  .theme-trigger {
    width: 36px;
    height: 36px;
  }
  .search-trigger {
    width: 36px;
    height: 36px;
    padding: 0;
    justify-content: center;
  }
  .search-trigger__text,
  .search-trigger__kbd {
    display: none;
  }
  .login-register-btn {
    height: 36px;
    padding: 0 11px;
    font-size: 12.5px;
  }
}

@media (max-width: 480px) {
  .brand-name {
    max-width: 76px;
  }
  .login-register-btn {
    padding: 0 10px;
  }
}

@media (max-width: 380px) {
  .brand-name {
    max-width: 58px;
  }
  .app-logo {
    display: none;
  }
}

/* v2.9 · stronger navigation signature */
.header--scrolled {
  background: color-mix(in srgb, var(--app-surface) 90%, transparent);
  box-shadow:
    0 12px 36px rgba(31, 42, 64, 0.065),
    inset 0 1px 0 rgba(255, 255, 255, 0.52);
  backdrop-filter: blur(12px) saturate(0.9);
}
.app-logo::before {
  content: "";
  position: absolute;
  inset: -6px;
  border: 1px solid color-mix(in srgb, var(--accent) 18%, transparent);
  border-radius: 16px;
  opacity: 0;
  transform: scale(0.78) rotate(-8deg);
  transition:
    opacity 220ms ease,
    transform 420ms cubic-bezier(0.16, 1, 0.3, 1);
}
.brand-link:hover .app-logo::before {
  opacity: 1;
  transform: scale(1) rotate(3deg);
}
.search-trigger {
  position: relative;
  overflow: hidden;
}
.search-trigger::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0;
  background: linear-gradient(110deg, transparent 15%, rgba(255, 255, 255, 0.72) 48%, transparent 76%);
  transform: translateX(-130%);
  transition:
    transform 620ms cubic-bezier(0.16, 1, 0.3, 1),
    opacity 180ms ease;
}
.search-trigger:hover::after {
  opacity: 0.58;
  transform: translateX(130%);
}
@media (prefers-reduced-motion: reduce) {
  .search-trigger::after {
    display: none;
  }
}

/* ============================================================
   v3.1 · floating header — calm, tactile, no progress indicator
   ============================================================ */
.header {
  padding-top: 0;
  background: transparent;
  border-bottom: 0;
  pointer-events: none;
}
.header-inner {
  pointer-events: auto;
  transition:
    height 320ms cubic-bezier(0.16, 1, 0.3, 1),
    margin-top 320ms cubic-bezier(0.16, 1, 0.3, 1),
    padding 320ms cubic-bezier(0.16, 1, 0.3, 1),
    border-color 260ms ease,
    background-color 260ms ease,
    border-radius 320ms cubic-bezier(0.16, 1, 0.3, 1),
    box-shadow 320ms ease;
}
.header--scrolled {
  background: transparent;
  box-shadow: none;
  backdrop-filter: none;
}
.header--scrolled .header-inner {
  height: 60px;
  margin-top: 10px;
  padding: 0 12px 0 14px;
  border: 1px solid color-mix(in srgb, var(--app-border-strong) 66%, transparent);
  border-radius: 20px;
  background: color-mix(in srgb, var(--app-surface) 87%, transparent);
  box-shadow:
    0 14px 42px rgba(34, 46, 70, 0.085),
    inset 0 1px 0 rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(16px) saturate(0.92);
}
.app-logo {
  border-color: transparent;
  background-color: transparent;
  box-shadow: none;
}
.app-logo::before {
  inset: -4px;
  border-radius: 14px;
}
.brand-link:hover .app-logo {
  box-shadow: none;
}
.brand-name {
  font-weight: 690;
}

.header-nav {
  justify-self: center;
  padding: 3px;
  border: 1px solid color-mix(in srgb, var(--app-border) 68%, transparent);
  border-radius: 999px;
  background: color-mix(in srgb, var(--app-surface) 58%, transparent);
}
.nav-menu {
  gap: 1px;
}
.nav-item a {
  height: 34px;
  padding: 0 14px;
  border-radius: 999px;
  font-size: 13px;
}
.nav-item.active a {
  background: var(--app-surface);
  color: var(--app-text);
  box-shadow:
    0 2px 10px rgba(32, 41, 60, 0.055),
    inset 0 0 0 1px color-mix(in srgb, var(--app-border) 78%, transparent);
}
.nav-item.active a::before {
  width: 5px;
  height: 5px;
  flex-basis: 5px;
  border-radius: 50%;
  background: var(--accent);
  clip-path: none;
  opacity: 0.9;
}
.header-right {
  padding: 3px;
  border: 1px solid color-mix(in srgb, var(--app-border) 58%, transparent);
  border-radius: 999px;
  background: color-mix(in srgb, var(--app-surface) 52%, transparent);
}
.theme-trigger,
.search-trigger,
.login-register-btn {
  height: 34px;
  border-color: transparent;
  background: transparent;
}
.theme-trigger:hover,
.search-trigger:hover {
  border-color: transparent;
  background: var(--app-surface);
  box-shadow: 0 2px 10px rgba(35, 44, 64, 0.05);
}
.login-register-btn {
  background: var(--accent-weak);
}
.search-trigger__kbd {
  border-color: color-mix(in srgb, var(--app-border) 75%, transparent);
  background: color-mix(in srgb, var(--app-surface-sunken) 72%, transparent);
}
.search-trigger::after {
  opacity: 0 !important;
  display: none;
}

@media (max-width: 1080px) {
  .header-nav {
    padding: 2px;
  }
  .nav-item a {
    padding: 0 10px;
  }
}
@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .header {
    background: color-mix(in srgb, var(--app-bg) 86%, transparent);
    backdrop-filter: blur(14px);
  }
  .header--scrolled .header-inner {
    height: 54px;
    margin-top: 5px;
    border-radius: 17px;
  }
  .header-right {
    border-color: transparent;
    background: transparent;
    padding: 0;
  }
}
@media (max-width: 640px) {
  .header--scrolled .header-inner {
    height: 50px;
    margin-top: 4px;
    padding-inline: 8px;
  }
  .theme-trigger,
  .search-trigger,
  .login-register-btn {
    height: 34px;
  }
}

/* ============================================================
   v3.2 · Header as one calm instrument, not three pill groups
   ============================================================ */
.header-inner {
  grid-template-columns: minmax(190px, 1fr) auto minmax(190px, 1fr);
}
.header--scrolled .header-inner {
  border-radius: 18px;
  background: color-mix(in srgb, var(--app-surface) 91%, transparent);
  box-shadow:
    0 18px 50px rgba(34, 46, 70, 0.075),
    inset 0 1px 0 rgba(255, 255, 255, 0.78);
}
.header--scrolled .brand-subtitle {
  max-height: 0;
  opacity: 0;
  transform: translateY(-4px);
}
.brand-subtitle {
  max-height: 18px;
  transition:
    opacity 220ms ease,
    transform 260ms cubic-bezier(0.16, 1, 0.3, 1),
    max-height 260ms cubic-bezier(0.16, 1, 0.3, 1);
}
.header-nav {
  border: 0;
  border-radius: 0;
  background: transparent;
  padding: 0;
}
.nav-menu {
  gap: 4px;
}
.nav-item a {
  position: relative;
  padding: 0 13px;
  background: transparent;
}
.nav-item a::after {
  content: "";
  position: absolute;
  left: 50%;
  bottom: 1px;
  width: 14px;
  height: 1px;
  border-radius: 99px;
  background: var(--accent);
  opacity: 0;
  transform: translateX(-50%) scaleX(0.25);
  transition:
    opacity 180ms ease,
    transform 300ms cubic-bezier(0.16, 1, 0.3, 1);
}
.nav-item.active a {
  background: transparent;
  box-shadow: none;
  color: var(--app-text);
}
.nav-item.active a::before {
  width: 7px;
  height: 7px;
  flex-basis: 7px;
  clip-path: polygon(50% 0, 62% 38%, 100% 50%, 62% 62%, 50% 100%, 38% 62%, 0 50%, 38% 38%);
  border-radius: 0;
}
.nav-item.active a::after {
  opacity: 0.7;
  transform: translateX(-50%) scaleX(1);
}
.header-right {
  border: 0;
  border-radius: 0;
  background: transparent;
  padding: 0;
}
.theme-trigger,
.search-trigger,
.login-register-btn {
  border-radius: 11px;
}
.login-register-btn {
  background: color-mix(in srgb, var(--accent-weak) 72%, var(--app-surface));
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--accent-line) 62%, transparent);
}
.search-trigger__kbd {
  opacity: 0.72;
}
.app-logo::before {
  inset: -6px;
  border-radius: 15px;
  border-color: color-mix(in srgb, var(--accent) 14%, transparent);
}
.brand-link:hover .app-logo::before {
  transform: scale(1) rotate(5deg);
}
@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .header-inner {
    grid-template-columns: minmax(0, 1fr) auto;
  }
}

/* ============================================================
   v4.0 · Header optical centering and spacing QA
   ============================================================ */
.header-inner {
  height: 70px;
  gap: 20px;
}
.header-left {
  min-width: 0;
}
.header-right {
  gap: 8px;
}
.brand-link {
  gap: 10px;
}
.brand-name {
  line-height: 1.18;
}
.brand-subtitle {
  line-height: 1.25;
}
.nav-item a {
  min-height: 38px;
  line-height: 1;
}
.theme-trigger,
.search-trigger,
.login-register-btn,
.user-avatar {
  flex: 0 0 auto;
}

@media (min-width: 1081px) {
  .header-inner {
    position: relative;
    grid-template-columns: auto minmax(0, 1fr) auto;
  }
  .header-nav {
    position: absolute;
    left: 50%;
    top: 50%;
    width: max-content;
    max-width: min(48vw, 620px);
    transform: translate(-50%, -50%);
  }
  .header-left {
    min-width: 210px;
  }
  .header-right {
    min-width: 310px;
    justify-content: flex-end;
  }
  .header--scrolled .header-inner {
    height: 58px;
  }
}

@media (max-width: 1080px) {
  .header-nav {
    position: static;
    width: auto;
    max-width: none;
    transform: none;
  }
}

@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .header-inner {
    height: 62px;
  }
  .header-right {
    gap: 5px;
  }
}

@media (max-width: 640px) {
  .header-inner {
    height: 58px;
  }
  .brand-name {
    line-height: 1.15;
  }
}
</style>

<style>
.nav-placeholder {
  width: 100%;
}

.nav-placeholder .nav-menu {
  display: flex !important;
  flex-direction: column !important;
  align-items: stretch !important;
  gap: 6px !important;
  padding: 8px 0 !important;
}

.nav-placeholder .nav-item {
  width: 100%;
}

.nav-placeholder .nav-item a {
  display: flex !important;
  width: 100%;
  justify-content: space-between;
  box-sizing: border-box;
}

.nav-placeholder .nav-item--external {
  display: block !important;
}

/* ============================================================
   v4.1 · Mobile header contract — stable, reachable, never crowded
   ============================================================ */
@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .header,
  .header--scrolled {
    background: color-mix(in srgb, var(--app-bg) 94%, transparent) !important;
    border-bottom: 1px solid color-mix(in srgb, var(--app-border) 78%, transparent) !important;
    box-shadow: none !important;
    backdrop-filter: blur(14px) saturate(0.92) !important;
  }
  .header--hidden {
    transform: none !important;
    pointer-events: auto !important;
  }
  .header-inner,
  .header--scrolled .header-inner {
    width: calc(100% - 24px) !important;
    height: 60px !important;
    margin: 0 auto !important;
    padding: 0 !important;
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) auto !important;
    gap: 8px !important;
    border: 0 !important;
    border-radius: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
  }
  .header-left {
    min-width: 0;
    gap: 2px;
  }
  .mobile-menu-btn {
    display: inline-grid !important;
    width: 44px !important;
    height: 44px !important;
    margin: 0 3px 0 -7px !important;
    place-items: center;
  }
  .brand-link {
    min-width: 0;
    gap: 8px !important;
  }
  .app-logo {
    display: block !important;
    width: 32px !important;
    height: 32px !important;
    flex: 0 0 32px !important;
    border-radius: 10px !important;
    background-size: 21px !important;
  }
  .app-logo::before,
  .app-logo::after {
    display: none !important;
  }
  .brand-copy {
    min-width: 0;
  }
  .brand-name {
    max-width: min(31vw, 132px) !important;
    font-size: 13.5px !important;
    line-height: 1.2 !important;
  }
  .brand-subtitle,
  .header-nav {
    display: none !important;
  }
  .header-right {
    min-width: 0 !important;
    gap: 3px !important;
    padding: 0 !important;
  }
  .theme-trigger,
  .search-trigger,
  .login-register-btn,
  .user-avatar {
    width: 44px !important;
    height: 44px !important;
    min-height: 44px !important;
    padding: 0 !important;
    border-radius: 12px !important;
    display: inline-grid !important;
    place-items: center !important;
  }
  .search-trigger__text,
  .search-trigger__kbd,
  .login-register-btn > span:last-child {
    display: none !important;
  }
  .theme-trigger__icon,
  .search-trigger__icon,
  .login-register-btn .material-symbols-rounded {
    font-size: 20px !important;
  }
  .mobile-menu-btn .material-symbols-rounded,
  .theme-trigger__icon,
  .search-trigger__icon,
  .login-register-btn .material-symbols-rounded {
    width: 1.15em !important;
    max-width: 1.15em !important;
    overflow: hidden !important;
  }
  .user-avatar {
    overflow: hidden;
  }
}
@media (max-width: 430px) {
  .header-inner,
  .header--scrolled .header-inner {
    width: calc(100% - 18px) !important;
  }
  .theme-picker {
    display: none !important;
  }
  .brand-name {
    max-width: 34vw !important;
  }
}
@media (max-width: 350px) {
  .brand-copy {
    display: none !important;
  }
}
</style>
