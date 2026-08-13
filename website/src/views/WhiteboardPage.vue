<template>
  <MobileDrawer v-model="isMobileMenuOpen" subtitle="临时白板 · 密钥 · 笔记">
    <p>输入密钥来匹配已有白板，或者新建一个。</p>
  </MobileDrawer>

  <HeaderBar :route-name="'白板'" :scroll="true" @toggle-mobile-menu="onToggleMobileMenu"></HeaderBar>

  <div class="whiteboard-page">
    <main class="main-container whiteboard-main">
      <section class="whiteboard-heading">
        <div class="hero-copy">
          <p class="page-description">临时白板</p>
        </div>
        <span class="board-count">{{ boards.length }} 个白板</span>
      </section>

      <section class="input-area" aria-label="白板匹配">
        <div class="input-wrapper">
          <input v-model="key" type="text" placeholder="输入密钥" @keyup.enter="handleClick" />
          <button v-if="key" class="clear-btn" type="button" @click="clearKey" aria-label="清除密钥">×</button>
        </div>
        <button @click="handleClick">匹配/新建</button>
      </section>

      <section v-if="boards.length" class="board-selector" aria-label="已关联白板">
        <span class="selector-label">已关联白板</span>
        <div class="key-list">
          <button v-for="item in boards" :key="item.key" class="key-chip" :class="{ active: item.key === key }" @click="selectBoard(item.key)">
            {{ item.key }}
          </button>
        </div>
      </section>

      <section class="board" aria-label="白板内容">
        <article class="card" :class="{ empty: !selectedBoard }">
          <div class="card-header">
            <div class="card-meta">
              <div class="card-key">密钥: {{ selectedBoard?.key || "-" }}</div>
              <div class="card-owner">创建者: {{ displayUsername }}</div>
            </div>
            <div class="card-actions">
              <button class="secondary" @click="openImageUpload" :disabled="!selectedBoard">上传图片</button>
              <button class="secondary" @click="startEditing" :disabled="!canEdit">编辑</button>
              <button class="primary" @click="updateRecord" :disabled="!canSave">保存</button>
              <button class="secondary" @click="openFullscreen" :disabled="!selectedBoard">全屏</button>
            </div>
          </div>
          <input ref="imageUploadRef" class="image-upload-input" type="file" accept="image/*" multiple @change="handleImageUpload" />
          <textarea
            v-if="isEditing"
            ref="editorRef"
            v-model="content"
            :disabled="!selectedBoard"
            placeholder="先匹配或创建一个白板吧"
            @paste="handlePaste"
          ></textarea>
          <div v-else class="content-preview" :class="{ empty: !selectedBoard || !content }">
            <template v-if="selectedBoard && content">
              <template v-for="(block, index) in contentBlocks" :key="`${block.type}-${index}`">
                <img v-if="block.type === 'image'" class="preview-image" :src="block.value" alt="白板图片" loading="lazy" decoding="async" />
                <pre v-else class="preview-text">{{ block.value }}</pre>
              </template>
            </template>
            <span v-else>先匹配或创建一个白板吧</span>
          </div>
          <div class="timestamp">上次更新: {{ formatTimestamp(created) }}</div>
        </article>
      </section>
    </main>

    <div v-if="showFullscreen" class="fullscreen-overlay" @click.self="closeFullscreen">
      <div class="fullscreen-panel" role="dialog" aria-modal="true">
        <div class="fullscreen-header">
          <span class="fullscreen-title">白板内容预览</span>
          <button class="close-btn" type="button" @click="closeFullscreen" aria-label="关闭全屏">×</button>
        </div>
        <div class="fullscreen-body">
          <template v-if="content">
            <template v-for="(block, index) in contentBlocks" :key="`fullscreen-${block.type}-${index}`">
              <img v-if="block.type === 'image'" class="preview-image" :src="block.value" alt="白板图片" loading="lazy" decoding="async" />
              <pre v-else class="preview-text">{{ block.value }}</pre>
            </template>
          </template>
          <pre v-else class="preview-text">（还没写内容）</pre>
        </div>
        <div class="fullscreen-footer">
          <button type="button" class="exit-btn" @click="closeFullscreen">退出全屏</button>
        </div>
      </div>
    </div>

    <FooterBar></FooterBar>
  </div>
</template>

<script setup>
import HeaderBar from "../components/HeaderBar.vue";
import FooterBar from "../components/FooterBar.vue";
import MobileDrawer from "../components/MobileDrawer.vue";
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useStore } from "vuex";
import Toast from "../utils/toast.js";
import { getWhiteboardByKey, getWhiteboardByUser, updateWhiteboardContent } from "../utils/apis";

const store = useStore();
const route = useRoute();
const router = useRouter();
const username = computed(() => store.state.authState.username || "");

const boards = ref([]);
const key = ref("");
const content = ref("");
const created = ref("");
const isEditing = ref(false);
const editorRef = ref(null);
const imageUploadRef = ref(null);
const showFullscreen = ref(false);
const isMobileMenuOpen = ref(false);
const originalBodyOverflow = ref("");
const ignoredRouteKey = ref(null);
const keydownHandler = (event) => {
  if (event.key === "Escape") {
    event.preventDefault();
    closeFullscreen();
  }
};

const selectedBoard = computed(() => boards.value.find((item) => item.key === key.value) || null);
const canEdit = computed(() => !!selectedBoard.value && !isEditing.value);
const canSave = computed(() => !!selectedBoard.value && isEditing.value);
const displayUsername = computed(() => {
  const owner = selectedBoard.value?.username || "";
  return owner || "匿名";
});
const contentBlocks = computed(() => {
  const value = content.value || "";
  const imagePattern = /data:image\/[a-zA-Z0-9.+-]+;base64,[a-zA-Z0-9+/=]+/g;
  const blocks = [];
  let lastIndex = 0;
  let match;

  while ((match = imagePattern.exec(value)) !== null) {
    if (match.index > lastIndex) {
      const text = value.slice(lastIndex, match.index);
      if (text) {
        blocks.push({ type: "text", value: text });
      }
    }

    blocks.push({ type: "image", value: match[0] });
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < value.length) {
    blocks.push({ type: "text", value: value.slice(lastIndex) });
  }

  return blocks.length ? blocks : [{ type: "text", value }];
});

const formatTimestamp = (ts) => (ts ? new Date(ts).toLocaleString() : "-");

const normalizeKey = (value) => (typeof value === "string" ? value.trim() : "");

const clearBoard = () => {
  key.value = "";
  content.value = "";
  created.value = "";
  boards.value = [];
  isEditing.value = false;
};

const syncRouteKey = async (boardKey) => {
  const normalizedKey = normalizeKey(boardKey);
  if (normalizeKey(route.query.key) === normalizedKey) return;

  const query = { ...route.query };
  if (normalizedKey) query.key = normalizedKey;
  else delete query.key;

  ignoredRouteKey.value = normalizedKey;
  await router.push({ query });
};

const selectBoardByKey = (boardKey) => {
  const match = boards.value.find((item) => item.key === boardKey);
  if (!match) {
    return;
  }
  key.value = match.key;
  content.value = match.content || "";
  created.value = match.created || "";
  isEditing.value = false;
};

const selectBoard = (boardKey) => {
  selectBoardByKey(boardKey);
  syncRouteKey(boardKey);
};

const startEditing = () => {
  if (!selectedBoard.value) {
    Toast.error("先匹配一个白板");
    return;
  }
  if (isEditing.value) {
    return;
  }
  isEditing.value = true;
  nextTick(() => {
    editorRef.value?.focus();
  });
};

const clearKey = () => {
  clearBoard();
  syncRouteKey("");
};

const openFullscreen = () => {
  if (!selectedBoard.value && !content.value) {
    Toast.info("还没有白板内容");
    return;
  }
  showFullscreen.value = true;
};

const closeFullscreen = () => {
  showFullscreen.value = false;
};

const onToggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

const insertAtCursor = (value) => {
  const editor = editorRef.value;
  if (!editor) {
    content.value += value;
    return;
  }

  const start = editor.selectionStart ?? content.value.length;
  const end = editor.selectionEnd ?? start;
  content.value = `${content.value.slice(0, start)}${value}${content.value.slice(end)}`;

  nextTick(() => {
    editor.focus();
    const cursor = start + value.length;
    editor.setSelectionRange(cursor, cursor);
  });
};

const readImageFile = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result || ""));
    reader.onerror = () => reject(reader.error || new Error("Failed to read image"));
    reader.readAsDataURL(file);
  });

const openImageUpload = () => {
  if (!selectedBoard.value) {
    Toast.error("请先匹配一个白板");
    return;
  }
  if (!isEditing.value) {
    isEditing.value = true;
  }
  nextTick(() => {
    editorRef.value?.focus();
    imageUploadRef.value?.click();
  });
};

const handleImageUpload = async (event) => {
  const files = Array.from(event.target.files || []).filter((file) => file.type.startsWith("image/"));
  event.target.value = "";
  if (!files.length) return;

  try {
    const images = await Promise.all(files.map(readImageFile));
    insertAtCursor(images.filter(Boolean).join("\n\n"));
    Toast.success("图片已放进去了");
  } catch (error) {
    console.error("上传图片失败:", error);
    Toast.error("图片读取出错了，再试一次");
  }
};

const handlePaste = async (event) => {
  if (!isEditing.value || !selectedBoard.value) {
    return;
  }

  const items = Array.from(event.clipboardData?.items || []);
  const imageItems = items.filter((item) => item.type.startsWith("image/"));

  if (!imageItems.length) {
    return;
  }

  event.preventDefault();

  const readImage = (item) =>
    new Promise((resolve, reject) => {
      const file = item.getAsFile();
      if (!file) {
        reject(new Error("无法读取剪贴板图片"));
        return;
      }

      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result || ""));
      reader.onerror = () => reject(reader.error || new Error("图片读取失败"));
      reader.readAsDataURL(file);
    });

  try {
    const images = await Promise.all(imageItems.map(readImage));
    const imageText = images.filter(Boolean).join("\n\n");
    if (imageText) {
      insertAtCursor(imageText);
      Toast.success("图片已放进去啦");
    }
  } catch (error) {
    console.error("粘贴图片失败:", error);
    Toast.error("图片读取出错了，再试一次");
  }
};

const handleClick = async () => {
  const trimmedKey = key.value.trim();
  isEditing.value = false;

  if (trimmedKey) {
    await syncRouteKey(trimmedKey);
    const res = await getWhiteboardByKey(trimmedKey);
    if (!res) {
      Toast.error("未找到对应的白板");
      boards.value = [];
      content.value = "";
      created.value = "";
      return;
    }
    boards.value = [res];
    selectBoardByKey(res.key);
    Toast.success("找到了");
    return;
  }

  const res = await getWhiteboardByUser(username.value, true);
  if (!res || !res.length) {
    Toast.error("白板创建没成功，再试一次");
    return;
  }
  boards.value = [...res];
  selectBoardByKey(boards.value[0].key);
  await syncRouteKey(boards.value[0].key);
  Toast.success("白板建好了");
};

watch(
  () => normalizeKey(route.query.key),
  async (routeKey) => {
    if (ignoredRouteKey.value === routeKey) {
      ignoredRouteKey.value = null;
      return;
    }
    if (!routeKey) {
      clearBoard();
      return;
    }
    key.value = routeKey;
    await handleClick();
  },
  { immediate: true }
);

const updateRecord = async () => {
  if (!selectedBoard.value) {
    Toast.error("请选择要更新的白板");
    return;
  }
  if (!isEditing.value) {
    Toast.error("请先点击编辑按钮");
    return;
  }
  const res = await updateWhiteboardContent(key.value, content.value);
  if (!res || res.flag === false) {
    Toast.error(res?.log || "存失败了，再试一次");
    return;
  }
  const timestamp = res.created || new Date().toISOString();
  created.value = timestamp;
  const target = boards.value.find((item) => item.key === key.value);
  if (target) {
    target.content = content.value;
    target.created = timestamp;
  }
  boards.value = [...boards.value].sort((a, b) => (b.created || "").localeCompare(a.created || ""));
  isEditing.value = false;
  Toast.success("存好了");
};

watch(
  showFullscreen,
  (value) => {
    if (typeof document !== "undefined") {
      if (value) {
        originalBodyOverflow.value = document.body.style.overflow;
        document.body.style.overflow = "hidden";
      } else {
        document.body.style.overflow = originalBodyOverflow.value || "";
      }
    }
    if (typeof window !== "undefined") {
      if (value) {
        window.addEventListener("keydown", keydownHandler);
      } else {
        window.removeEventListener("keydown", keydownHandler);
      }
    }
  },
  { flush: "post" }
);

onBeforeUnmount(() => {
  if (typeof document !== "undefined") {
    document.body.style.overflow = originalBodyOverflow.value || "";
  }
  if (typeof window !== "undefined") {
    window.removeEventListener("keydown", keydownHandler);
  }
});
</script>

<style scoped>
@import url("../assets/views/main-container.css");

.whiteboard-page {
  min-height: 100vh;
  background: var(--app-bg);
}

.main-container {
  width: min(1120px, calc(100% - 40px));
  max-width: 1120px;
  display: block;
  padding: 110px 0 72px;
  min-height: auto;
}

.whiteboard-main {
  display: grid;
  gap: 24px;
  min-width: 0;
}

.whiteboard-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--app-border);
}

.hero-copy {
  display: grid;
  gap: 6px;
}

.page-kicker {
  margin: 0 0 12px;
  color: var(--app-blue);
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.page-description {
  margin: 0;
  color: var(--app-text);
  font-size: 18px;
  line-height: 1.45;
  font-weight: 600;
}

.board-count {
  display: inline-flex;
  align-items: center;
  height: 38px;
  padding: 0 14px;
  border: 1px solid var(--app-border);
  border-radius: 999px;
  background: var(--app-surface);
  color: var(--app-text-muted);
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}

.input-area {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 18px;
  border: 1px solid var(--app-border);
  border-radius: 20px;
  background: var(--app-surface);
  box-shadow: var(--app-shadow-sm);
}

.input-wrapper {
  position: relative;
  flex: 1;
  display: flex;
  min-width: 0;
}

.input-area input {
  flex: 1;
  height: 42px;
  min-width: 0;
  padding: 0 42px 0 14px;
  font-size: 14px;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-md);
  background: var(--app-surface);
  color: var(--app-text);
  transition: background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.input-area input:focus {
  background: var(--app-surface);
  border-color: var(--accent-line);
  box-shadow: 0 0 0 4px var(--accent-weak);
  outline: none;
}

.input-area > button {
  height: 42px;
  padding: 0 18px;
  font-size: 14px;
  font-weight: 600;
  background-color: var(--app-blue);
  color: var(--app-surface);
  border: 1px solid var(--app-blue);
  border-radius: 999px;
  cursor: pointer;
  white-space: nowrap;
  transition: background-color 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
}

.input-area > button:hover {
  background-color: var(--app-blue-hover);
  border-color: var(--app-blue-hover);
  transform: translateY(-1px);
}

.clear-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  border: 1px solid transparent;
  border-radius: 999px;
  background: transparent;
  color: var(--app-text-soft);
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.clear-btn:hover {
  background: rgba(120, 105, 85, 0.08);
  color: var(--app-text-muted);
}

.board-selector {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.selector-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--app-text-muted);
}

.key-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.key-chip {
  height: 32px;
  padding: 0 13px;
  font-size: 13px;
  border-radius: 999px;
  border: 1px solid var(--app-border);
  background: var(--app-surface);
  color: var(--app-text-muted);
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.key-chip:hover {
  background: var(--app-surface);
  border-color: var(--accent-line);
  color: var(--app-blue);
}

.key-chip.active {
  background: var(--accent-weak);
  border-color: var(--accent-line);
  color: var(--app-blue);
}

.board {
  display: grid;
  grid-template-columns: 1fr;
}

.card {
  display: flex;
  flex-direction: column;
  min-height: 540px;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-xl);
  overflow: hidden;
  background: var(--app-surface);
  box-shadow: var(--app-shadow-sm);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 18px;
  background-color: var(--app-surface);
  border-bottom: 1px solid var(--app-border);
}

.card-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: var(--app-text-soft);
  font-size: 13px;
  min-width: 0;
}

.card-key {
  font-weight: 600;
  color: var(--app-text);
}

.card-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.image-upload-input {
  display: none;
}

.card-actions button {
  height: 36px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 999px;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.card-actions .primary {
  background-color: var(--app-blue);
  color: var(--app-surface);
  border: 1px solid var(--app-blue);
}

.card-actions .primary:disabled {
  background-color: var(--accent-weak);
  border-color: var(--accent-line);
  cursor: not-allowed;
}

.card-actions .primary:not(:disabled):hover {
  background-color: var(--app-blue-hover);
}

.card-actions .secondary {
  background-color: var(--app-surface);
  color: var(--app-text-muted);
  border: 1px solid var(--app-border);
}

.card-actions .secondary:disabled {
  color: var(--app-text-soft);
  border-color: var(--app-border);
  cursor: not-allowed;
}

.card-actions .secondary:not(:disabled):hover {
  border-color: var(--accent-line);
  color: var(--app-blue);
}

.card textarea {
  flex: 1;
  min-height: 420px;
  padding: 18px;
  font-size: 15px;
  line-height: 1.7;
  border: none;
  resize: none;
  outline: none;
  background-color: var(--app-surface);
  color: var(--app-text);
}

.card textarea:disabled {
  background-color: var(--app-surface-sunken);
  color: var(--app-text-soft);
}

.content-preview {
  flex: 1;
  min-height: 420px;
  padding: 18px;
  overflow: auto;
  background: var(--app-surface);
  color: var(--app-text);
}

.content-preview.empty {
  display: grid;
  place-items: center;
  color: var(--app-text-soft);
  background: var(--app-surface-sunken);
}

.preview-text {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: "SFMono-Regular", Menlo, Consolas, "Liberation Mono", Courier, monospace;
  font-size: 14px;
  line-height: 1.7;
  color: var(--app-text);
}

.preview-image {
  display: block;
  max-width: min(100%, 860px);
  max-height: 70vh;
  margin: 10px 0;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-md);
  background: var(--app-surface);
  object-fit: contain;
}

.timestamp {
  padding: 10px 18px;
  font-size: 13px;
  color: var(--app-text-soft);
  background-color: var(--app-surface);
  text-align: right;
  border-top: 1px solid var(--app-border);
}

.fullscreen-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(42, 36, 32, 0.45);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10006;
  padding: 24px;
}
.fullscreen-panel {
  width: min(1200px, 100%);
  max-height: 100%;
  background-color: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-xl);
  box-shadow: var(--app-shadow-popover);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.fullscreen-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--app-border);
  position: sticky;
  top: 0;
  background-color: var(--app-surface);
  z-index: 5;
}
.fullscreen-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--app-text);
}

.close-btn {
  line-height: 1;
  width: 36px;
  height: 36px;
  border: 1px solid var(--app-border);
  border-radius: 999px;
  background: var(--app-surface);
  font-size: 22px;
  cursor: pointer;
  color: var(--app-text-muted);
  padding: 0;
}

.close-btn:hover {
  border-color: var(--accent-line);
  color: var(--app-blue);
}

.fullscreen-body {
  padding: 20px;
  overflow: auto;
  flex: 1;
  background-color: var(--app-surface-sunken);
}

.fullscreen-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--app-border);
  background-color: var(--app-surface);
  display: flex;
  justify-content: flex-end;
}

.exit-btn {
  height: 38px;
  padding: 0 18px;
  background-color: var(--app-blue);
  color: var(--app-surface);
  border: 1px solid var(--app-blue);
  border-radius: 999px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: background-color 0.2s ease;
}

.exit-btn:hover {
  background-color: var(--app-blue-hover);
}

@media (max-width: 900px) {
  .main-container {
    width: min(100% - 28px, 980px);
    padding-top: 102px;
  }
}

@media (max-width: 640px) {
  .main-container {
    width: calc(100% - 24px);
    padding: 92px 0 54px;
  }

  .whiteboard-main {
    gap: 18px;
  }

  .whiteboard-heading {
    align-items: start;
    flex-direction: column;
    gap: 14px;
    padding-bottom: 14px;
  }

  .page-kicker {
    margin-bottom: 6px;
    font-size: 11px;
  }

  .page-description {
    font-size: 16px;
  }

  .input-area {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
    padding: 14px;
  }
  .input-wrapper {
    width: 100%;
  }
  .input-area > button {
    width: 100%;
  }

  .key-list {
    gap: 6px;
  }

  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
    padding: 14px;
  }

  .card {
    min-height: 460px;
  }

  .card textarea {
    min-height: 320px;
    padding: 14px;
    font-size: 14px;
  }

  .content-preview {
    min-height: 320px;
    padding: 14px;
  }

  .preview-image {
    max-width: 100%;
    max-height: 62vh;
  }

  .timestamp {
    padding: 8px 14px;
    font-size: 12px;
  }

  .card-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  .card-actions button {
    width: 100%;
  }

  .fullscreen-overlay {
    padding: 12px;
  }

  .fullscreen-panel {
    max-height: calc(100vh - 24px);
  }

  .fullscreen-header {
    padding: 12px 16px;
  }

  .fullscreen-body {
    padding: 16px;
  }

  .fullscreen-footer {
    padding: 12px 16px 16px;
    justify-content: center;
  }

  .exit-btn {
    width: 100%;
  }
}
</style>
