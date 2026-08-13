<template>
  <header :class="['header', { 'header--hidden': !isHeaderVisible }]">
    <div class="header-inner">
      <div class="header-left">
        <button v-if="showMobileMenu" class="mobile-menu-btn" type="button" aria-label="打开导航菜单" @click="toggleMobileMenu()"></button>
        <a class="brand-link" href="/">
          <span class="app-logo"></span>
          <span class="brand-copy">
            <span class="brand-name">爬楼的猪 Dev</span>
            <span class="brand-subtitle">项目 · 教程 · Demo</span>
          </span>
        </a>
      </div>

      <nav class="header-nav" aria-label="主导航">
        <ul ref="navAllRef" class="nav-menu">
          <li v-for="item in navItems" :key="item.label" :class="['nav-item', { active: isActive(item) }]">
            <a :href="item.href">{{ item.label }}</a>
          </li>
          <li v-for="nav in navs" :key="nav.title" class="nav-item nav-item--external">
            <a :href="nav.url" target="_blank" rel="noopener noreferrer">
              {{ nav.title }}
              <span v-if="nav.new" class="nav-badge">new</span>
            </a>
          </li>
        </ul>
      </nav>

      <div class="header-right">
        <div ref="themePickerRef" :class="['theme-picker', { 'theme-picker--open': isThemeMenuOpen }]">
          <button
            class="theme-trigger"
            type="button"
            aria-label="切换主题"
            :aria-expanded="isThemeMenuOpen"
            :style="{ '--theme-swatch': currentThemeOption.swatch }"
            @click="onToggleThemeMenu"
          >
            <span class="theme-trigger__dot" aria-hidden="true"></span>
            <span class="theme-trigger__label">{{ currentThemeOption.label }}</span>
            <span class="theme-trigger__chevron" aria-hidden="true"></span>
          </button>

          <div v-if="isThemeMenuOpen" class="theme-menu" role="menu">
            <button
              v-for="theme in themes"
              :key="theme.id"
              :class="['theme-option', { 'theme-option--active': theme.id === currentTheme }]"
              type="button"
              role="menuitemradio"
              :aria-checked="theme.id === currentTheme"
              :style="{ '--theme-swatch': theme.swatch }"
              @click="onSelectTheme(theme.id)"
            >
              <span class="theme-option__dot" aria-hidden="true"></span>
              <span class="theme-option__label">{{ theme.label }}</span>
            </button>
          </div>
        </div>

        <button class="search-trigger" type="button" aria-label="打开搜索" title="搜索" @click="onOpenSearch">
          <span class="search-trigger__icon"></span>
          <span class="search-trigger__text">搜索</span>
        </button>

        <div v-if="avatar" class="user-avatar" @click="onToggleLoginForm">
          <img :src="avatar" alt="avatar" />
        </div>
        <button v-else class="login-register-btn" @click="onToggleLoginForm">登录 / 注册</button>
      </div>
    </div>
  </header>

  <LoginCard v-if="showLoginForm" @close-login-form="onCloseLoginForm" />
  <SearchOverlay v-model="searchOpen" />
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useStore } from "vuex";
import Toast from "../utils/toast.js";
import { getStoredTheme, setStoredTheme, themes } from "../utils/theme";
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
const avatar = computed(() => store.state.authState.avatar);
const username = computed(() => store.state.authState.username);

const navAllRef = ref(null);
const navs = ref([]);
const showLoginForm = ref(false);
const searchOpen = ref(false);
const isHeaderVisible = ref(true);
const activeAnchor = ref("");
const currentTheme = ref(getStoredTheme());
const themePickerRef = ref(null);
const isThemeMenuOpen = ref(false);
const currentThemeOption = computed(() => themes.find((theme) => theme.id === currentTheme.value) || themes[0]);

const navItems = [
  { label: "首页", href: "/", anchor: "" },
  { label: "文章/教程", href: "/articles", anchor: "/articles" },
  { label: "白板", href: "/whiteboard", anchor: "/whiteboard" },
  { label: "Demos", href: "/livedemo", anchor: "/livedemo" },
];

let lastScrollY = 0;
let ticking = false;
let accumulatedUp = 0;
let accumulatedDown = 0;
let scrollListenerActive = false;
let hashchangeHandler = null;

function isActive(item) {
  if (props.routeName !== "首页") {
    return item.label === routeNameToNavLabel[props.routeName];
  }

  if (!activeAnchor.value) {
    return item.label === "首页";
  }

  return item.anchor === activeAnchor.value;
}

const routeNameToNavLabel = {
  首页: "首页",
  教程: "教程",
  "Code Space": "Demos",
  白板: "白板",
};

function handleScroll() {
  const currentY = window.scrollY;
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
  if (ticking) return;
  ticking = true;
  window.requestAnimationFrame(() => {
    handleScroll();
    ticking = false;
  });
}

function enableScrollHide() {
  if (scrollListenerActive) return;
  lastScrollY = window.scrollY;
  window.addEventListener("scroll", onScrollThrottled, { passive: true });
  scrollListenerActive = true;
}

function disableScrollHide() {
  if (!scrollListenerActive) return;
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
  isThemeMenuOpen.value = false;
  searchOpen.value = true;
}

function onToggleThemeMenu() {
  isThemeMenuOpen.value = !isThemeMenuOpen.value;
}

function onSelectTheme(theme) {
  currentTheme.value = setStoredTheme(theme);
  isThemeMenuOpen.value = false;
}

function onDocumentClick(event) {
  if (!themePickerRef.value?.contains(event.target)) {
    isThemeMenuOpen.value = false;
  }
}

function onDocumentKeydown(event) {
  if (event.key === "Escape") {
    isThemeMenuOpen.value = false;
  }
}

function syncActiveAnchor() {
  activeAnchor.value = window.location.hash || "";
}

onMounted(async () => {
  if (props.scroll) {
    enableScrollHide();
  }

  watch(
    () => props.scroll,
    (shouldScroll) => {
      if (shouldScroll) {
        enableScrollHide();
      } else {
        disableScrollHide();
      }
    }
  );
  hashchangeHandler = () => syncActiveAnchor();
  window.addEventListener("hashchange", hashchangeHandler);
  document.addEventListener("click", onDocumentClick);
  document.addEventListener("keydown", onDocumentKeydown);
  syncActiveAnchor();
});

onBeforeUnmount(() => {
  disableScrollHide();
  if (hashchangeHandler) {
    window.removeEventListener("hashchange", hashchangeHandler);
  }
  document.removeEventListener("click", onDocumentClick);
  document.removeEventListener("keydown", onDocumentKeydown);
});
</script>

<style scoped>
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10005;
  background: var(--app-header-bg);
  border-bottom: 1px solid var(--app-border);
  transition:
    transform var(--app-motion-duration) ease-out,
    border-color var(--app-motion-duration) ease-out,
    background-color var(--app-motion-duration) ease-out;
}

.header--hidden {
  transform: translateY(-100%);
  pointer-events: none;
}

.header-inner {
  width: min(1180px, calc(100% - 32px));
  height: 68px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 28px;
}

.header-left {
  display: flex;
  align-items: center;
  min-width: 0;
}

.brand-link {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: inherit;
  text-decoration: none;
  min-width: 0;
}

.app-logo {
  width: 34px;
  height: 34px;
  border-radius: 11px;
  background: transparent url("../assets/svgs/logo-32.svg") no-repeat center;
  background-size: 22px;
  flex-shrink: 0;
}

.brand-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.brand-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--app-text);
  line-height: 1.1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.brand-subtitle {
  font-size: 12px;
  color: var(--app-text-soft);
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
  gap: 8px;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-item {
  position: relative;
}

.nav-item a {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 38px;
  padding: 0 12px;
  border-radius: 999px;
  color: var(--app-text-muted);
  text-decoration: none;
  font-size: 14px;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.nav-item a:hover {
  color: var(--app-text);
  background: var(--app-hover-bg);
}

.nav-item.active a {
  color: var(--app-blue);
  background: var(--accent-weak);
}

.nav-item--external a {
  color: var(--app-text-muted);
}

.nav-badge {
  font-size: 10px;
  line-height: 1;
  color: var(--app-blue);
  background: var(--accent-weak);
  border-radius: 999px;
  padding: 3px 6px;
}


.theme-picker {
  position: relative;
  flex: 0 0 auto;
}

.theme-trigger {
  width: 96px;
  height: 38px;
  padding: 0 9px;
  border: 1px solid var(--app-border);
  border-radius: 999px;
  background: linear-gradient(180deg, var(--app-surface), var(--app-bg-elevated));
  color: var(--app-text);
  display: inline-grid;
  grid-template-columns: 12px minmax(0, 1fr) 10px;
  align-items: center;
  gap: 6px;
  box-shadow: var(--app-shadow-sm);
  cursor: pointer;
}

.theme-trigger:hover,
.theme-picker--open .theme-trigger {
  border-color: var(--accent-line);
  background: var(--app-surface);
  box-shadow: 0 0 0 4px var(--accent-weak);
}

.theme-trigger__dot,
.theme-option__dot {
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: var(--theme-swatch, var(--accent));
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--theme-swatch, var(--accent)) 18%, transparent);
  flex: 0 0 auto;
}

.theme-trigger__label {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  font-weight: 700;
  line-height: 1;
  text-align: left;
}

.theme-trigger__chevron {
  width: 7px;
  height: 7px;
  justify-self: center;
  border-right: 1.5px solid var(--app-text-soft);
  border-bottom: 1.5px solid var(--app-text-soft);
  transform: translateY(-2px) rotate(45deg);
  transition: transform var(--app-motion-duration) var(--app-ease), border-color var(--app-motion-duration) var(--app-ease);
}

.theme-picker--open .theme-trigger__chevron {
  border-color: var(--accent);
  transform: translateY(2px) rotate(225deg);
}

.theme-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  z-index: 2;
  width: 136px;
  padding: 6px;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-md);
  background: var(--app-surface);
  box-shadow: var(--app-shadow-popover);
}

.theme-option {
  width: 100%;
  height: 34px;
  padding: 0 10px;
  border: 1px solid transparent;
  border-radius: var(--app-radius-sm);
  background: transparent;
  color: var(--app-text-muted);
  display: grid;
  grid-template-columns: 12px minmax(0, 1fr);
  align-items: center;
  gap: 9px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 650;
  text-align: left;
}

.theme-option:hover {
  background: var(--app-hover-bg);
  color: var(--app-text);
}

.theme-option--active {
  border-color: var(--accent-line);
  background: var(--accent-weak);
  color: var(--accent);
}

.theme-option__label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.header-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}

.search-trigger {
  height: 38px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid var(--app-border);
  background: var(--app-surface);
  color: var(--app-text-muted);
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: border-color 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
}

.search-trigger:hover {
  border-color: var(--app-border-strong);
  color: var(--app-text);
  box-shadow: var(--app-shadow-sm);
}

.search-trigger__icon {
  width: 16px;
  height: 16px;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%236b6359' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='7'/%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'/%3E%3C/svg%3E")
    no-repeat center / contain;
}

.search-trigger__text {
  font-size: 14px;
}

.login-register-btn {
  height: 38px;
  padding: 0 14px;
  border-radius: 999px;
  border: 1px solid var(--accent-line);
  background: var(--accent-weak);
  color: var(--app-blue);
  font-size: 14px;
  cursor: pointer;
  transition: border-color 0.2s ease, background-color 0.2s ease, transform 0.2s ease;
}

.login-register-btn:hover {
  border-color: var(--accent-line);
  background: var(--accent-weak-hover);
  transform: translateY(-1px);
}

.user-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid var(--app-border);
  box-shadow: var(--app-shadow-sm);
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
  margin-right: 10px;
  background: transparent url("../assets/svgs/menu-32.svg") no-repeat center;
  cursor: pointer;
  border: none;
}

@media (max-width: 1080px) {
  .header-inner {
    grid-template-columns: auto 1fr auto;
    gap: 18px;
  }

  .nav-menu {
    gap: 2px;
  }

  .nav-item a {
    padding: 0 10px;
  }

  .nav-item--external {
    display: none;
  }
}

@media (max-width: 840px) {
  .header-inner {
    width: min(100%, calc(100% - 24px));
    height: 64px;
    grid-template-columns: minmax(0, 1fr) auto;
    justify-content: stretch;
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
    margin-right: 8px;
  }

  .brand-subtitle {
    display: none;
  }
}

@media (max-width: 640px) {
  .header-inner {
    width: min(100%, calc(100% - 16px));
    height: 58px;
    gap: 8px;
  }

  .header-right {
    gap: 8px;
  }

  .app-logo {
    width: 30px;
    height: 30px;
    border-radius: 9px;
    background-size: 20px;
  }

  .brand-name {
    max-width: 92px;
    font-size: 14px;
  }

  .mobile-menu-btn {
    width: 36px;
    height: 36px;
    margin-right: 6px;
    background-size: 28px;
  }

  .theme-trigger {
    width: 38px;
    height: 38px;
    padding: 0;
    display: inline-flex;
    justify-content: center;
    gap: 0;
  }

  .theme-trigger__label,
  .theme-trigger__chevron {
    display: none;
  }

  .theme-trigger__dot {
    width: 12px;
    height: 12px;
  }

  .theme-menu {
    width: 128px;
  }

  .search-trigger {
    width: 38px;
    padding: 0;
    justify-content: center;
  }

  .search-trigger__text,
  .search-trigger__key {
    display: none;
  }

  .login-register-btn {
    padding: 0 12px;
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .header-inner {
    width: min(100%, calc(100% - 16px));
  }

  .brand-name {
    max-width: 82px;
    font-size: 13px;
  }

  .login-register-btn {
    height: 38px;
    padding: 0 10px;
    font-size: 12.5px;
  }

  .github-link {
    display: none;
  }
}

@media (max-width: 380px) {
  .brand-name {
    max-width: 64px;
  }

  .app-logo {
    display: none;
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
</style>
