<template>
  <router-view v-slot="{ Component }">
    <keep-alive>
      <component :is="Component" @vue:mounted="onPageReady" @vue:updated="onPageReady" />
    </keep-alive>
  </router-view>
  <input type="file" id="global-image-upload-input" accept="image/*" style="display: none" />
  <input type="file" id="global-file-upload-input" accept="*/*" style="display: none" />
</template>

<script setup>
import { useRoute } from "vue-router";
import { enterContent } from "./utils/motion";

const route = useRoute();
let animatedPath;
function onPageReady() {
  if (animatedPath === route.path) return;
  // Vnode hooks also run after lazy loading and KeepAlive activation. Do not animate
  // fixed navigation or restart motion when data arrives on the same page.
  const content = document.querySelector(".home-main, .tutorials-main, .article-shell, .livedemo-shell, .whiteboard-main, .admin-content, .not-found");
  if (!content) return;
  animatedPath = route.path;
  enterContent(content);
}
</script>
