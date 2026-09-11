<template>
  <MobileDrawer v-model="isMobileMenuOpen" subtitle="临时缓存 · 文本 · 图片">
    <p>输入密钥打开已有白板，或者直接新建一个临时内容板。</p>
  </MobileDrawer>

  <HeaderBar :route-name="'白板'" :scroll="true" @toggle-mobile-menu="onToggleMobileMenu" />

  <div class="whiteboard-page">
    <main class="main-container whiteboard-main">
      <section v-reveal class="workspace-masthead" aria-labelledby="whiteboard-title">
        <div class="workspace-masthead__copy" data-reveal-item>
          <p class="workspace-kicker"><span aria-hidden="true"></span> Scratchpad / temporary</p>
          <h1 id="whiteboard-title" class="page-description">白板</h1>
          <p>用一个密钥暂存文字与图片，随时回来继续。</p>
        </div>
        <p class="layout-handnote workspace-signature" data-reveal-item>Scratch, save, return.</p>
      </section>

      <section v-reveal class="board-entry" aria-label="打开或新建白板">
        <div class="board-entry__label">
          <span class="material-symbols-rounded" aria-hidden="true">link</span>
          <span>
            <strong>打开 / 新建</strong>
            <small>有密钥就打开，没有就创建</small>
          </span>
        </div>

        <div class="input-area">
          <div class="input-wrapper">
            <span class="material-symbols-rounded input-icon" aria-hidden="true">key</span>
            <input ref="keyInputRef" v-model="key" type="text" placeholder="输入密钥，打开已有白板" autocomplete="off" @keyup.enter="handleClick" />
            <button v-if="key" class="clear-btn" type="button" @click="clearKey" aria-label="清除密钥">
              <span class="material-symbols-rounded" aria-hidden="true">close</span>
            </button>
          </div>
          <button class="entry-action" type="button" @click="handleClick">
            <span>{{ key.trim() ? "打开" : "新建" }}</span>
            <span class="material-symbols-rounded" aria-hidden="true">arrow_forward</span>
          </button>
        </div>
      </section>

      <section v-if="boards.length" class="board-selector" aria-label="已关联白板">
        <span class="selector-label">最近打开</span>
        <div class="key-list">
          <button v-for="item in boards" :key="item.key" class="key-chip" :class="{ active: item.key === key }" type="button" @click="selectBoard(item.key)">
            <span class="material-symbols-rounded" aria-hidden="true">description</span>
            <span>{{ item.key }}</span>
          </button>
        </div>
      </section>

      <section class="board" aria-label="白板内容">
        <article class="board-card" :class="{ 'board-card--empty': !selectedBoard }">
          <header class="card-header">
            <div class="card-meta">
              <p class="card-eyebrow">Current scratchpad</p>
              <div class="card-key-row">
                <strong>{{ selectedBoard?.key || "还没有打开白板" }}</strong>
                <span v-if="selectedBoard">{{ displayUsername }} 创建</span>
              </div>
            </div>

            <div class="card-actions" aria-label="白板操作">
              <button class="tool-button" type="button" @click="openImageUpload" :disabled="!selectedBoard">
                <span class="material-symbols-rounded" aria-hidden="true">add_photo_alternate</span><span>图片</span>
              </button>
              <button v-if="!isEditing" class="tool-button" type="button" @click="startEditing" :disabled="!canEdit">
                <span class="material-symbols-rounded" aria-hidden="true">edit_note</span><span>编辑</span>
              </button>
              <button v-else class="tool-button" type="button" @click="cancelEditing">
                <span class="material-symbols-rounded" aria-hidden="true">close</span><span>取消</span>
              </button>
              <button class="tool-button tool-button--primary" type="button" @click="updateRecord" :disabled="!canSave">
                <span class="material-symbols-rounded" aria-hidden="true">save</span><span>保存</span>
              </button>
              <button class="tool-button" type="button" @click="openFullscreen" :disabled="!selectedBoard || !content">
                <span class="material-symbols-rounded" aria-hidden="true">open_in_full</span><span>预览</span>
              </button>
            </div>
          </header>

          <input ref="imageUploadRef" class="image-upload-input" type="file" accept="image/*" multiple @change="handleImageUpload" />

          <div v-if="isEditing" class="composer">
            <div class="composer-text">
              <label for="scratchpad-editor">文字</label>
              <textarea
                id="scratchpad-editor"
                ref="editorRef"
                v-model="draftText"
                placeholder="写点临时笔记，或者直接粘贴截图…"
                @paste="handlePaste"
              ></textarea>
              <p><span class="material-symbols-rounded" aria-hidden="true">content_paste</span>可以直接粘贴文本；粘贴截图会自动加入图片附件。</p>
            </div>

            <aside class="composer-media" aria-label="图片附件">
              <div class="composer-media__heading">
                <span>图片</span>
                <small>{{ draftImages.length }} 张</small>
              </div>
              <div class="attachment-grid">
                <div v-for="(image, index) in draftImages" :key="`draft-image-${index}`" class="attachment-item">
                  <img :src="image" :alt="`白板图片 ${index + 1}`" />
                  <button type="button" @click="removeDraftImage(index)" :aria-label="`移除第 ${index + 1} 张图片`">
                    <span class="material-symbols-rounded" aria-hidden="true">close</span>
                  </button>
                </div>
                <button class="attachment-add" type="button" @click="imageUploadRef?.click()">
                  <span class="material-symbols-rounded" aria-hidden="true">add_photo_alternate</span>
                  <span>添加图片</span>
                </button>
              </div>
            </aside>
          </div>

          <div v-else class="content-preview" :class="{ empty: !selectedBoard || !content }">
            <template v-if="selectedBoard && content">
              <template v-for="(block, index) in contentBlocks" :key="`${block.type}-${index}`">
                <img v-if="block.type === 'image'" class="preview-image" :src="block.value" alt="白板图片" loading="lazy" decoding="async" />
                <pre v-else-if="block.value.trim()" class="preview-text">{{ block.value }}</pre>
              </template>
            </template>

            <div v-else-if="selectedBoard" class="empty-state">
              <div class="empty-visual" aria-hidden="true">
                <span class="empty-sheet empty-sheet--back"></span>
                <span class="empty-sheet empty-sheet--front"><span class="material-symbols-rounded">note_add</span></span>
              </div>
              <p class="empty-kicker">Ready when you are</p>
              <h2>这个白板还是空的</h2>
              <p>写一段临时文本，放几张截图，之后用密钥随时回来继续。</p>
            </div>

            <div v-else class="empty-state">
              <div class="empty-visual" aria-hidden="true">
                <span class="empty-sheet empty-sheet--back"></span>
                <span class="empty-sheet empty-sheet--front"><span class="material-symbols-rounded">inventory_2</span></span>
              </div>
              <p class="empty-kicker">Temporary & lightweight</p>
              <h2>共享临时内容</h2>
              <p>新建一个白板缓存文字和图片，或者输入密钥打开之前的内容。</p>
            </div>
          </div>

          <footer class="card-footer">
            <div class="content-stats" aria-label="内容统计">
              <span><span class="material-symbols-rounded" aria-hidden="true">notes</span>{{ currentTextLength }} 字</span>
              <span><span class="material-symbols-rounded" aria-hidden="true">image</span>{{ currentImageCount }} 张图片</span>
            </div>
            <span>上次更新 {{ formatTimestamp(created) }}</span>
          </footer>
        </article>
      </section>
    </main>

    <div v-if="showFullscreen" class="fullscreen-overlay" @click.self="closeFullscreen">
      <div class="fullscreen-panel" role="dialog" aria-modal="true" aria-labelledby="fullscreen-title">
        <div class="fullscreen-header">
          <div>
            <span class="fullscreen-eyebrow">Preview</span>
            <strong id="fullscreen-title" class="fullscreen-title">{{ selectedBoard?.key || "白板内容" }}</strong>
          </div>
          <button class="close-btn" type="button" @click="closeFullscreen" aria-label="关闭预览">
            <span class="material-symbols-rounded" aria-hidden="true">close</span>
          </button>
        </div>
        <div class="fullscreen-body">
          <template v-if="content">
            <template v-for="(block, index) in contentBlocks" :key="`fullscreen-${block.type}-${index}`">
              <img v-if="block.type === 'image'" class="preview-image" :src="block.value" alt="白板图片" loading="lazy" decoding="async" />
              <pre v-else-if="block.value.trim()" class="preview-text">{{ block.value }}</pre>
            </template>
          </template>
          <pre v-else class="preview-text">（还没有内容）</pre>
        </div>
      </div>
    </div>

    <FooterBar />
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
const draftText = ref("");
const draftImages = ref([]);
const editorRef = ref(null);
const imageUploadRef = ref(null);
const keyInputRef = ref(null);
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

const parseContentBlocks = (value = "") => {
  const imagePattern = /data:image\/[a-zA-Z0-9.+-]+;base64,[a-zA-Z0-9+/=]+/g;
  const blocks = [];
  let lastIndex = 0;
  let match;

  while ((match = imagePattern.exec(value)) !== null) {
    if (match.index > lastIndex) {
      blocks.push({ type: "text", value: value.slice(lastIndex, match.index) });
    }
    blocks.push({ type: "image", value: match[0] });
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < value.length) {
    blocks.push({ type: "text", value: value.slice(lastIndex) });
  }

  return blocks.length ? blocks : [{ type: "text", value }];
};

const selectedBoard = computed(() => boards.value.find((item) => item.key === key.value) || null);
const canEdit = computed(() => !!selectedBoard.value && !isEditing.value);
const canSave = computed(() => !!selectedBoard.value && isEditing.value);
const displayUsername = computed(() => selectedBoard.value?.username || "匿名");
const contentBlocks = computed(() => parseContentBlocks(content.value || ""));
const currentTextLength = computed(() => {
  if (isEditing.value) return draftText.value.trim().length;
  return contentBlocks.value.filter((block) => block.type === "text").reduce((sum, block) => sum + block.value.trim().length, 0);
});
const currentImageCount = computed(() => {
  if (isEditing.value) return draftImages.value.length;
  return contentBlocks.value.filter((block) => block.type === "image").length;
});

const formatTimestamp = (ts) => (ts ? new Date(ts).toLocaleString() : "尚未保存");
const normalizeKey = (value) => (typeof value === "string" ? value.trim() : "");

const syncDraftFromContent = () => {
  const blocks = parseContentBlocks(content.value || "");
  draftText.value = blocks
    .filter((block) => block.type === "text")
    .map((block) => block.value)
    .join("")
    .trim();
  draftImages.value = blocks.filter((block) => block.type === "image").map((block) => block.value);
};

const composeDraftContent = () => {
  const parts = [];
  if (draftText.value.trim()) parts.push(draftText.value.trim());
  parts.push(...draftImages.value.filter(Boolean));
  return parts.join("\n\n");
};

const clearBoard = () => {
  key.value = "";
  content.value = "";
  created.value = "";
  boards.value = [];
  draftText.value = "";
  draftImages.value = [];
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
  if (!match) return;

  key.value = match.key;
  content.value = match.content || "";
  created.value = match.created || "";
  draftText.value = "";
  draftImages.value = [];
  isEditing.value = false;
};

const selectBoard = (boardKey) => {
  selectBoardByKey(boardKey);
  syncRouteKey(boardKey);
};

const startEditing = () => {
  if (!selectedBoard.value) {
    Toast.error("先打开或新建一个白板");
    return;
  }
  if (isEditing.value) return;

  syncDraftFromContent();
  isEditing.value = true;
  nextTick(() => editorRef.value?.focus());
};

const cancelEditing = () => {
  syncDraftFromContent();
  isEditing.value = false;
};

const clearKey = () => {
  clearBoard();
  syncRouteKey("");
};

const focusKeyInput = () => {
  keyInputRef.value?.focus();
};

const openFullscreen = () => {
  if (!selectedBoard.value || !content.value) {
    Toast.info("还没有可以预览的内容");
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

const readImageFile = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result || ""));
    reader.onerror = () => reject(reader.error || new Error("Failed to read image"));
    reader.readAsDataURL(file);
  });

const openImageUpload = () => {
  if (!selectedBoard.value) {
    Toast.error("请先打开或新建一个白板");
    return;
  }

  if (!isEditing.value) startEditing();
  nextTick(() => imageUploadRef.value?.click());
};

const handleImageUpload = async (event) => {
  const files = Array.from(event.target.files || []).filter((file) => file.type.startsWith("image/"));
  event.target.value = "";
  if (!files.length) return;

  try {
    const images = await Promise.all(files.map(readImageFile));
    draftImages.value.push(...images.filter(Boolean));
    Toast.success(`${images.length} 张图片已加入`);
  } catch (error) {
    console.error("上传图片失败:", error);
    Toast.error("图片读取出错了，再试一次");
  }
};

const removeDraftImage = (index) => {
  draftImages.value.splice(index, 1);
};

const handlePaste = async (event) => {
  if (!isEditing.value || !selectedBoard.value) return;

  const items = Array.from(event.clipboardData?.items || []);
  const imageItems = items.filter((item) => item.type.startsWith("image/"));
  if (!imageItems.length) return;

  event.preventDefault();

  try {
    const images = await Promise.all(
      imageItems.map((item) => {
        const file = item.getAsFile();
        if (!file) return Promise.reject(new Error("无法读取剪贴板图片"));
        return readImageFile(file);
      }),
    );
    draftImages.value.push(...images.filter(Boolean));
    Toast.success("截图已加入白板");
  } catch (error) {
    console.error("粘贴图片失败:", error);
    Toast.error("图片读取出错了，再试一次");
  }
};

const createBoard = async () => {
  key.value = "";
  await syncRouteKey("");
  await handleClick();
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
    Toast.success("白板已打开");
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
  { immediate: true },
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

  const nextContent = composeDraftContent();
  const res = await updateWhiteboardContent(key.value, nextContent);
  if (!res || res.flag === false) {
    Toast.error(res?.log || "保存失败了，再试一次");
    return;
  }

  content.value = nextContent;
  const timestamp = res.created || new Date().toISOString();
  created.value = timestamp;
  const target = boards.value.find((item) => item.key === key.value);
  if (target) {
    target.content = nextContent;
    target.created = timestamp;
  }
  boards.value = [...boards.value].sort((a, b) => (b.created || "").localeCompare(a.created || ""));
  isEditing.value = false;
  Toast.success("已经保存");
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
      if (value) window.addEventListener("keydown", keydownHandler);
      else window.removeEventListener("keydown", keydownHandler);
    }
  },
  { flush: "post" },
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
  background: radial-gradient(circle at 84% 9%, color-mix(in srgb, var(--accent) 4.5%, transparent), transparent 27rem), var(--app-bg);
}

.main-container {
  width: min(1160px, calc(100% - 2 * var(--app-page-gutter)));
  display: block;
  padding: var(--app-page-top) 0 72px;
  min-height: auto;
}

.whiteboard-main {
  display: grid;
  gap: 20px;
  min-width: 0;
}

.whiteboard-heading {
  position: relative;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 28px;
  padding: 28px 4px 30px;
  border-bottom: 1px solid var(--app-border);
}

.whiteboard-heading::before {
  content: "";
  position: absolute;
  left: 4px;
  bottom: -1px;
  width: 52px;
  height: 2px;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--accent), color-mix(in srgb, var(--accent) 15%, transparent));
}

.hero-copy {
  display: grid;
  gap: 7px;
  max-width: 680px;
}
.page-kicker {
  margin: 0;
  color: var(--accent);
  font-size: 10.5px;
  font-weight: 760;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}
.page-description {
  margin: 0;
  color: var(--app-text);
  font-family: var(--font-display);
  font-size: clamp(32px, 4vw, 46px);
  line-height: 1.16;
  font-weight: 670;
  letter-spacing: -0.045em;
}
.page-subtitle {
  max-width: 620px;
  margin: 4px 0 0;
  color: var(--app-text-muted);
  font-size: 13.5px;
  line-height: 1.75;
}

.board-count {
  min-height: 38px;
  padding: 0 13px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--app-border);
  border-radius: 999px;
  background: color-mix(in srgb, var(--app-surface) 88%, transparent);
  color: var(--app-text-muted);
  font-size: 12px;
  white-space: nowrap;
}
.board-count .material-symbols-rounded {
  color: var(--accent);
  font-size: 17px;
}
.board-count strong {
  color: var(--app-text);
  font-size: 13px;
}

.board-entry {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: center;
  gap: 18px;
  padding: 12px;
  border: 1px solid var(--app-border);
  border-radius: 20px;
  background: var(--app-surface);
  box-shadow: 0 10px 30px rgba(31, 40, 58, 0.025);
}

.board-entry__label {
  padding: 0 8px 0 4px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--app-text-muted);
}
.board-entry__label > .material-symbols-rounded {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  background: var(--accent-weak);
  color: var(--accent);
  font-size: 19px;
}
.board-entry__label > span:last-child {
  display: grid;
  gap: 1px;
}
.board-entry__label strong {
  color: var(--app-text);
  font-size: 12.5px;
  font-weight: 680;
}
.board-entry__label small {
  color: var(--app-text-soft);
  font-size: 10.5px;
}

.input-area {
  min-width: 0;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 8px;
}
.input-wrapper {
  position: relative;
  min-width: 0;
}
.input-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  color: var(--app-text-soft);
  font-size: 18px;
  transform: translateY(-50%);
  pointer-events: none;
}
.input-area input {
  width: 100%;
  height: 46px;
  min-width: 0;
  padding: 0 44px 0 42px;
  border: 1px solid var(--app-border);
  border-radius: 14px;
  background: var(--app-surface-sunken);
  color: var(--app-text);
  font-size: 13.5px;
  outline: none;
  transition:
    border-color 180ms var(--app-ease),
    box-shadow 180ms var(--app-ease),
    background-color 180ms var(--app-ease);
}
.input-area input::placeholder {
  color: var(--app-text-soft);
}
.input-area input:focus {
  border-color: var(--accent-line);
  background: var(--app-surface);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent-weak) 76%, transparent);
}
.clear-btn {
  position: absolute;
  right: 10px;
  top: 50%;
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  border: 0;
  border-radius: 50%;
  background: transparent;
  color: var(--app-text-soft);
  transform: translateY(-50%);
  cursor: pointer;
}
.clear-btn .material-symbols-rounded {
  font-size: 17px;
}
.clear-btn:hover {
  background: var(--app-hover-bg);
  color: var(--app-text);
}
.entry-action {
  min-width: 102px;
  height: 46px;
  padding: 0 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  border: 1px solid var(--accent);
  border-radius: 14px;
  background: var(--accent);
  color: var(--app-on-accent);
  font-size: 12.5px;
  font-weight: 680;
  cursor: pointer;
}
.entry-action:hover {
  background: var(--accent-hover);
  border-color: var(--accent-hover);
}
.entry-action .material-symbols-rounded {
  font-size: 16px;
}

.board-selector {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 2px;
}
.selector-label {
  flex: 0 0 auto;
  color: var(--app-text-soft);
  font-size: 10.5px;
  font-weight: 680;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.key-list {
  min-width: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}
.key-chip {
  min-width: 0;
  height: 32px;
  padding: 0 10px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  border: 1px solid var(--app-border);
  border-radius: 999px;
  background: var(--app-surface);
  color: var(--app-text-muted);
  font-size: 11px;
  cursor: pointer;
}
.key-chip .material-symbols-rounded {
  color: var(--app-text-soft);
  font-size: 14px;
}
.key-chip:hover {
  border-color: var(--app-border-strong);
  color: var(--app-text);
}
.key-chip.active {
  border-color: var(--accent-line);
  background: var(--accent-weak);
  color: var(--accent);
}
.key-chip.active .material-symbols-rounded {
  color: var(--accent);
}

.board {
  min-width: 0;
}
.board-card {
  min-width: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 500px;
  border: 1px solid var(--app-border);
  border-radius: 24px;
  background: var(--app-surface);
  box-shadow: 0 18px 52px rgba(31, 40, 58, 0.035);
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 15px 16px 15px 20px;
  border-bottom: 1px solid var(--app-border);
  background: color-mix(in srgb, var(--app-surface) 95%, var(--app-surface-sunken));
}
.card-meta {
  min-width: 0;
  display: grid;
  gap: 3px;
}
.card-eyebrow {
  margin: 0;
  color: var(--app-text-soft);
  font-size: 9.5px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.card-key-row {
  min-width: 0;
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 5px 10px;
}
.card-key-row strong {
  max-width: min(440px, 52vw);
  overflow: hidden;
  color: var(--app-text);
  font-family: var(--font-mono);
  font-size: 12.5px;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.card-key-row span {
  color: var(--app-text-soft);
  font-size: 10.5px;
}
.card-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}
.tool-button {
  min-width: 0;
  height: 38px;
  padding: 0 11px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  border: 1px solid var(--app-border);
  border-radius: 12px;
  background: var(--app-surface);
  color: var(--app-text-muted);
  font-size: 11.5px;
  font-weight: 620;
  cursor: pointer;
}
.tool-button .material-symbols-rounded {
  font-size: 17px;
}
.tool-button:hover:not(:disabled) {
  border-color: var(--app-border-strong);
  background: var(--app-surface-sunken);
  color: var(--app-text);
}
.tool-button--primary {
  border-color: var(--accent);
  background: var(--accent);
  color: var(--app-on-accent);
}
.tool-button--primary:hover:not(:disabled) {
  border-color: var(--accent-hover);
  background: var(--accent-hover);
  color: var(--app-on-accent);
}
.tool-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.image-upload-input {
  display: none;
}

.composer {
  flex: 1;
  min-height: 390px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  background: var(--app-surface);
}
.composer-text {
  min-width: 0;
  padding: 24px;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--app-border);
}
.composer-text label,
.composer-media__heading > span {
  color: var(--app-text-soft);
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.composer-text textarea {
  flex: 1;
  width: 100%;
  min-height: 300px;
  margin-top: 10px;
  padding: 0;
  resize: none;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--app-text);
  font-family: var(--font-sans);
  font-size: 15px;
  line-height: 1.85;
}
.composer-text textarea::placeholder {
  color: var(--app-text-soft);
}
.composer-text > p {
  margin: 16px 0 0;
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--app-text-soft);
  font-size: 10.5px;
}
.composer-text > p .material-symbols-rounded {
  font-size: 15px;
}
.composer-media {
  min-width: 0;
  padding: 22px 18px;
  background: color-mix(in srgb, var(--app-surface-sunken) 66%, var(--app-surface));
}
.composer-media__heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 12px;
}
.composer-media__heading small {
  color: var(--app-text-soft);
  font-size: 10.5px;
}
.attachment-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}
.attachment-item,
.attachment-add {
  position: relative;
  overflow: hidden;
  aspect-ratio: 1;
  border: 1px solid var(--app-border);
  border-radius: 14px;
  background: var(--app-surface);
}
.attachment-item img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}
.attachment-item > button {
  position: absolute;
  right: 6px;
  top: 6px;
  width: 26px;
  height: 26px;
  display: grid;
  place-items: center;
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: 50%;
  background: rgba(24, 31, 42, 0.64);
  color: #fff;
  cursor: pointer;
}
.attachment-item > button .material-symbols-rounded {
  font-size: 15px;
}
.attachment-add {
  display: grid;
  place-items: center;
  align-content: center;
  gap: 4px;
  color: var(--app-text-soft);
  font-size: 10.5px;
  cursor: pointer;
}
.attachment-add .material-symbols-rounded {
  color: var(--accent);
  font-size: 22px;
}
.attachment-add:hover {
  border-color: var(--accent-line);
  background: var(--accent-weak);
  color: var(--accent);
}

.content-preview {
  flex: 1;
  min-height: 390px;
  padding: clamp(24px, 4vw, 46px);
  overflow: auto;
  background:
    linear-gradient(var(--app-surface), var(--app-surface)) padding-box,
    radial-gradient(circle at 14% 8%, color-mix(in srgb, var(--accent) 3%, transparent), transparent 20rem);
  color: var(--app-text);
}
.content-preview.empty {
  display: grid;
  place-items: center;
  overflow: hidden;
  background: color-mix(in srgb, var(--app-surface) 93%, var(--app-surface-sunken));
}
.preview-text {
  max-width: 820px;
  margin: 0 auto 24px;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: var(--font-sans);
  font-size: 14.5px;
  line-height: 1.9;
  color: var(--app-text);
}
.preview-image {
  display: block;
  max-width: min(100%, 860px);
  max-height: 70vh;
  margin: 14px auto 26px;
  border: 1px solid var(--app-border);
  border-radius: 18px;
  background: var(--app-surface-sunken);
  box-shadow: 0 12px 34px rgba(31, 40, 58, 0.055);
  object-fit: contain;
}

.empty-state {
  width: min(100%, 480px);
  display: grid;
  justify-items: center;
  text-align: center;
}
.empty-visual {
  position: relative;
  width: 92px;
  height: 74px;
  margin-bottom: 18px;
}
.empty-sheet {
  position: absolute;
  width: 60px;
  height: 48px;
  left: 16px;
  top: 10px;
  border: 1px solid var(--accent-line);
  border-radius: 15px;
  background: color-mix(in srgb, var(--app-surface) 74%, var(--accent-weak));
  box-shadow: 0 12px 28px rgba(46, 65, 92, 0.07);
}
.empty-sheet--back {
  transform: translate(10px, -7px) rotate(7deg);
  opacity: 0.62;
}
.empty-sheet--front {
  display: grid;
  place-items: center;
  transform: rotate(-4deg);
}
.empty-sheet--front .material-symbols-rounded {
  color: var(--accent);
  font-size: 25px;
}
.empty-kicker {
  margin: 0 0 6px;
  color: var(--accent);
  font-size: 9.5px;
  font-weight: 720;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.empty-state h2 {
  margin: 0;
  color: var(--app-text);
  font-family: var(--font-display);
  font-size: clamp(21px, 3vw, 28px);
  font-weight: 650;
  letter-spacing: -0.035em;
}
.empty-state > p:not(.empty-kicker) {
  max-width: 390px;
  margin: 10px 0 0;
  color: var(--app-text-muted);
  font-size: 12.5px;
  line-height: 1.75;
}
.empty-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
}
.empty-primary,
.empty-secondary {
  min-height: 40px;
  padding: 0 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border-radius: 999px;
  font-size: 11.5px;
  font-weight: 650;
  cursor: pointer;
}
.empty-primary {
  border: 1px solid var(--accent);
  background: var(--accent);
  color: var(--app-on-accent);
}
.empty-secondary {
  border: 1px solid var(--app-border);
  background: var(--app-surface);
  color: var(--app-text-muted);
}
.empty-primary .material-symbols-rounded,
.empty-secondary .material-symbols-rounded {
  font-size: 16px;
}
.empty-primary:hover {
  background: var(--accent-hover);
  border-color: var(--accent-hover);
}
.empty-secondary:hover {
  border-color: var(--app-border-strong);
  color: var(--app-text);
}

.card-footer {
  min-height: 44px;
  padding: 0 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  border-top: 1px solid var(--app-border);
  background: color-mix(in srgb, var(--app-surface) 95%, var(--app-surface-sunken));
  color: var(--app-text-soft);
  font-size: 10.5px;
}
.content-stats {
  display: flex;
  align-items: center;
  gap: 12px;
}
.content-stats > span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.content-stats .material-symbols-rounded {
  font-size: 14px;
}

.fullscreen-overlay {
  position: fixed;
  inset: 0;
  z-index: 10006;
  padding: 24px;
  display: grid;
  place-items: center;
  background: var(--app-overlay);
}
.fullscreen-panel {
  width: min(1080px, 100%);
  max-height: calc(100vh - 48px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--app-border);
  border-radius: 24px;
  background: var(--app-surface);
  box-shadow: var(--app-shadow-popover);
}
.fullscreen-header {
  padding: 15px 16px 15px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border-bottom: 1px solid var(--app-border);
}
.fullscreen-header > div {
  min-width: 0;
  display: grid;
  gap: 1px;
}
.fullscreen-eyebrow {
  color: var(--app-text-soft);
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.fullscreen-title {
  overflow: hidden;
  color: var(--app-text);
  font-family: var(--font-mono);
  font-size: 12.5px;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.close-btn {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  border: 1px solid var(--app-border);
  border-radius: 50%;
  background: var(--app-surface);
  color: var(--app-text-muted);
  cursor: pointer;
}
.close-btn .material-symbols-rounded {
  font-size: 18px;
}
.close-btn:hover {
  border-color: var(--app-border-strong);
  color: var(--app-text);
}
.fullscreen-body {
  flex: 1;
  min-height: 0;
  padding: clamp(24px, 4vw, 46px);
  overflow: auto;
  background: var(--app-surface);
}

@media (max-width: 900px) {
  .main-container {
    padding-top: 102px;
  }
  .board-entry {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  .board-entry__label {
    display: none;
  }
  .composer {
    grid-template-columns: 1fr;
  }
  .composer-text {
    border-right: 0;
    border-bottom: 1px solid var(--app-border);
  }
  .composer-media {
    padding: 18px 20px;
  }
  .attachment-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .main-container {
    padding: 84px 0 54px;
  }
  .whiteboard-main {
    gap: 15px;
  }
  .whiteboard-heading {
    align-items: flex-start;
    gap: 14px;
    padding: 18px 2px 24px;
  }
  .page-description {
    font-size: 30px;
  }
  .page-subtitle {
    font-size: 12.25px;
    line-height: 1.65;
  }
  .board-count {
    min-height: 34px;
    padding-inline: 10px;
    font-size: 10.5px;
  }
  .board-count > span:last-child {
    display: none;
  }
  .board-entry {
    padding: 8px;
    border-radius: 17px;
  }
  .input-area {
    gap: 7px;
  }
  .input-area input {
    height: 44px;
    padding-left: 39px;
    font-size: 12px;
  }
  .entry-action {
    min-width: 82px;
    height: 44px;
    padding-inline: 12px;
  }
  .entry-action .material-symbols-rounded {
    display: none;
  }
  .board-selector {
    align-items: flex-start;
    flex-direction: column;
    gap: 7px;
  }
  .key-list {
    width: 100%;
    flex-wrap: nowrap;
    overflow-x: auto;
    padding-bottom: 2px;
    scrollbar-width: none;
  }
  .key-list::-webkit-scrollbar {
    display: none;
  }
  .key-chip {
    flex: 0 0 auto;
  }
  .board-card {
    min-height: 430px;
    border-radius: 20px;
  }
  .card-header {
    align-items: flex-start;
    flex-direction: column;
    gap: 12px;
    padding: 14px;
  }
  .card-key-row strong {
    max-width: 82vw;
  }
  .card-actions {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 6px;
  }
  .tool-button {
    width: 100%;
    height: 42px;
    padding: 0 6px;
    flex-direction: column;
    gap: 1px;
    border-radius: 11px;
    font-size: 9.5px;
  }
  .tool-button .material-symbols-rounded {
    font-size: 17px;
  }
  .composer {
    min-height: 350px;
  }
  .composer-text {
    padding: 20px 16px;
  }
  .composer-text textarea {
    min-height: 250px;
    font-size: 14px;
  }
  .composer-text > p {
    align-items: flex-start;
    line-height: 1.5;
  }
  .composer-media {
    padding: 16px;
  }
  .attachment-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  .content-preview {
    min-height: 340px;
    padding: 24px 16px;
  }
  .preview-text {
    font-size: 14px;
    line-height: 1.82;
  }
  .preview-image {
    max-height: 58vh;
    margin-bottom: 18px;
    border-radius: 15px;
  }
  .empty-state > p:not(.empty-kicker) {
    max-width: 320px;
  }
  .empty-actions {
    width: 100%;
  }
  .empty-primary,
  .empty-secondary {
    flex: 1 1 0;
    min-width: 0;
  }
  .card-footer {
    min-height: 48px;
    padding: 0 14px;
  }
  .card-footer > span:last-child {
    display: none;
  }
  .fullscreen-overlay {
    padding: 10px;
  }
  .fullscreen-panel {
    max-height: calc(100vh - 20px);
    border-radius: 18px;
  }
  .fullscreen-body {
    padding: 22px 14px;
  }
}

@media (max-width: 390px) {
  .page-subtitle {
    max-width: 270px;
  }
  .board-count {
    padding-inline: 9px;
  }
  .input-icon {
    left: 11px;
  }
  .input-area input {
    padding-left: 35px;
    padding-right: 34px;
  }
  .entry-action {
    min-width: 72px;
    padding-inline: 9px;
    font-size: 11.5px;
  }
  .attachment-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .tool-button {
    font-size: 9px;
  }
  .empty-actions {
    flex-direction: column;
  }
  .content-stats {
    gap: 8px;
  }
}

/* ============================================================
   v3.1 · scratchpad as a document surface, not a dashboard card
   ============================================================ */
.whiteboard-main {
  gap: 18px;
}
.whiteboard-heading {
  padding: 34px 4px 32px;
  border-bottom-color: color-mix(in srgb, var(--app-border-strong) 58%, transparent);
}
.whiteboard-heading::before {
  width: 66px;
  background: linear-gradient(90deg, var(--accent), transparent);
}
.board-count {
  min-height: 34px;
  padding: 0 5px 0 10px;
  border-color: transparent;
  background: transparent;
}
.board-count .material-symbols-rounded {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  border-radius: 9px;
  background: var(--accent-weak);
}
.board-entry {
  position: relative;
  padding: 9px;
  border-color: color-mix(in srgb, var(--app-border-strong) 60%, transparent);
  border-radius: 18px;
  background: linear-gradient(105deg, color-mix(in srgb, var(--brand-tint) 54%, var(--app-surface)), var(--app-surface) 42%);
  box-shadow:
    0 12px 32px rgba(34, 46, 70, 0.035),
    inset 0 1px 0 rgba(255, 255, 255, 0.62);
}
.board-entry::before {
  content: "";
  position: absolute;
  left: 18px;
  top: -1px;
  width: 54px;
  height: 2px;
  border-radius: 999px;
  background: linear-gradient(90deg, color-mix(in srgb, var(--accent) 70%, #fff), transparent);
}
.board-entry__label > .material-symbols-rounded {
  background: color-mix(in srgb, var(--app-surface) 76%, transparent);
}
.input-area input {
  background: color-mix(in srgb, var(--app-surface) 92%, transparent);
}
.entry-action {
  border-radius: 12px;
}
.board-selector {
  padding-block: 2px;
}
.key-chip {
  border-color: transparent;
  background: var(--app-surface-sunken);
}
.key-chip.active {
  box-shadow: inset 0 0 0 1px var(--accent-line);
}

.board {
  position: relative;
  isolation: isolate;
  padding-top: 4px;
}
.board::before {
  content: "";
  position: absolute;
  z-index: -1;
  left: 7%;
  right: 7%;
  top: 3%;
  bottom: -4%;
  border-radius: 48px;
  background: radial-gradient(ellipse at 50% 8%, color-mix(in srgb, var(--accent) 5%, transparent), transparent 66%);
  pointer-events: none;
}
.board-card {
  overflow: hidden;
  border-color: color-mix(in srgb, var(--app-border-strong) 64%, transparent);
  border-radius: 26px;
  background: var(--app-surface);
  box-shadow:
    0 24px 68px rgba(34, 46, 70, 0.065),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
}
.card-header {
  border-bottom-color: color-mix(in srgb, var(--app-border) 76%, transparent);
  background: color-mix(in srgb, var(--app-surface) 95%, var(--brand-tint));
}
.tool-button {
  border-color: transparent;
  background: var(--app-surface-sunken);
}
.tool-button:hover {
  border-color: transparent;
}
.tool-button--primary {
  background: var(--accent);
}
.content-preview.empty {
  background:
    radial-gradient(circle at 1px 1px, color-mix(in srgb, var(--accent) 9%, transparent) 1px, transparent 1.2px) 0 0 / 22px 22px,
    radial-gradient(circle at 50% 46%, color-mix(in srgb, var(--accent) 4%, transparent), transparent 40%),
    var(--app-surface);
}
.empty-visual {
  transform: rotate(-2deg);
}
.card-footer {
  background: color-mix(in srgb, var(--app-surface-sunken) 62%, var(--app-surface));
}

@media (max-width: 680px) {
  .whiteboard-heading {
    padding: 22px 2px 24px;
  }
  .board-entry {
    padding: 7px;
  }
  .board {
    padding-top: 0;
  }
  .board-card {
    border-radius: 20px;
    box-shadow: 0 16px 44px rgba(34, 46, 70, 0.05);
  }
}

/* ============================================================
   v3.2 · Scratchpad identity — quiet paper, clearer working state
   ============================================================ */
.board-card {
  position: relative;
  box-shadow:
    0 28px 78px rgba(34, 46, 70, 0.07),
    inset 0 1px 0 rgba(255, 255, 255, 0.78);
}
.board-card::before {
  content: "";
  position: absolute;
  z-index: 4;
  left: 28px;
  top: 0;
  width: 82px;
  height: 2px;
  border-radius: 0 0 999px 999px;
  background: linear-gradient(90deg, color-mix(in srgb, var(--accent) 78%, #fff), color-mix(in srgb, var(--accent) 8%, transparent));
  pointer-events: none;
}
.card-header {
  min-height: 76px;
  background: color-mix(in srgb, var(--app-surface) 97%, var(--brand-tint));
}
.content-preview:not(.empty) {
  background: linear-gradient(90deg, transparent 0 48px, color-mix(in srgb, var(--accent) 7%, transparent) 48px 49px, transparent 49px), var(--app-surface);
}
.preview-text {
  padding-left: 18px;
}
.composer-text {
  background: linear-gradient(90deg, transparent 0 48px, color-mix(in srgb, var(--accent) 6%, transparent) 48px 49px, transparent 49px), var(--app-surface);
}
.composer-text textarea {
  background: transparent;
}
@media (max-width: 680px) {
  .board-card::before {
    left: 18px;
    width: 58px;
  }
  .content-preview:not(.empty),
  .composer-text {
    background: var(--app-surface);
  }
  .preview-text {
    padding-left: 0;
  }
}

/* ============================================================
   v4.0 · Whiteboard detail QA — stable baselines and mobile density
   ============================================================ */
.main-container {
  padding-top: 102px;
}
.whiteboard-heading {
  align-items: center;
}
.page-description {
  line-height: 1.08;
  padding-bottom: 0.04em;
}
.page-subtitle {
  max-width: 62ch;
  font-size: 13px;
  line-height: 1.7;
}
.board-entry {
  align-items: center;
}
.board-entry__label strong {
  font-size: 13px;
  line-height: 1.3;
}
.board-entry__label small {
  font-size: 11px;
  line-height: 1.4;
}
.tool-button {
  font-size: 11px;
  line-height: 1.2;
}
.card-key-row strong {
  line-height: 1.3;
}
.composer-text textarea,
.preview-text {
  line-height: 1.72;
}
.card-footer {
  font-size: 10.5px;
}

@media (max-width: 640px) {
  .main-container {
    padding-top: 76px;
  }
  .whiteboard-heading {
    align-items: flex-start;
  }
  .page-description {
    font-size: 29px;
  }
  .page-subtitle {
    font-size: 12.5px;
  }
  .tool-button {
    font-size: 10px;
  }
}

/* ============================================================
   v4.1 · Whiteboard mobile rebuild — thumb-friendly scratchpad
   ============================================================ */
@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .main-container {
    width: 100% !important;
    padding: 76px 14px 48px !important;
  }
  .whiteboard-main {
    gap: 16px !important;
  }
  .whiteboard-heading {
    display: grid !important;
    grid-template-columns: 1fr !important;
    gap: 12px !important;
    padding: 18px 0 22px !important;
  }
  .page-description {
    font-size: clamp(30px, 9vw, 40px) !important;
  }
  .page-subtitle {
    max-width: none !important;
    font-size: 13px !important;
  }
  .board-count {
    justify-self: start !important;
  }
  .board-entry {
    grid-template-columns: 1fr !important;
    gap: 9px !important;
    padding: 9px !important;
  }
  .board-entry__label {
    display: none !important;
  }
  .input-area {
    grid-template-columns: 1fr !important;
    gap: 8px !important;
  }
  .input-area input {
    height: 48px !important;
    font-size: 16px !important;
  }
  .entry-action {
    width: 100% !important;
    min-height: 46px !important;
  }
  .board-selector {
    align-items: flex-start !important;
    flex-direction: column !important;
    gap: 7px !important;
  }
  .key-list {
    width: calc(100% + 28px) !important;
    margin-inline: -14px !important;
    padding: 0 14px 4px !important;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    scrollbar-width: none;
  }
  .key-list::-webkit-scrollbar {
    display: none;
  }
  .key-chip {
    flex: 0 0 auto !important;
    min-height: 38px !important;
  }
  .board {
    padding-top: 0 !important;
  }
  .board::before {
    display: none !important;
  }
  .board-card {
    min-height: 0 !important;
    border-radius: 20px !important;
  }
  .card-header {
    align-items: stretch !important;
    flex-direction: column !important;
    gap: 12px !important;
    padding: 14px !important;
  }
  .card-key-row {
    min-width: 0 !important;
  }
  .card-key-row strong {
    max-width: 100% !important;
    overflow-wrap: anywhere !important;
  }
  .card-actions {
    width: 100% !important;
    display: grid !important;
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    gap: 7px !important;
  }
  .tool-button {
    width: 100% !important;
    min-height: 44px !important;
    padding: 0 10px !important;
    flex-direction: row !important;
    justify-content: center !important;
    gap: 6px !important;
    font-size: 11px !important;
  }
  .composer {
    grid-template-columns: 1fr !important;
    min-height: 0 !important;
  }
  .composer-text {
    padding: 16px !important;
    border-right: 0 !important;
    border-bottom: 1px solid var(--app-border) !important;
  }
  .composer-text textarea {
    min-height: 220px !important;
    font-size: 16px !important;
    line-height: 1.7 !important;
  }
  .composer-media {
    padding: 15px !important;
  }
  .attachment-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    gap: 8px !important;
  }
  .content-preview {
    min-height: 300px !important;
    padding: 22px 15px !important;
  }
  .preview-image {
    width: 100% !important;
    max-height: none !important;
    object-fit: contain !important;
  }
  .empty-actions {
    width: 100% !important;
    display: grid !important;
    grid-template-columns: 1fr !important;
    gap: 8px !important;
  }
  .empty-primary,
  .empty-secondary {
    width: 100% !important;
    min-height: 44px !important;
  }
  .card-footer {
    padding-inline: 13px !important;
  }
}
@media (max-width: 420px) {
  .main-container {
    padding-inline: 12px !important;
  }
  .key-list {
    width: calc(100% + 24px) !important;
    margin-inline: -12px !important;
    padding-inline: 12px !important;
  }
  .attachment-grid {
    grid-template-columns: 1fr !important;
  }
}

/* ============================================================
   v5.0 · Shared workspace masthead language
   ============================================================ */
.main-container {
  width: min(1180px, calc(100% - 2 * var(--app-page-gutter)));
  padding-top: 104px;
}
.whiteboard-main {
  gap: 18px;
}
.workspace-masthead {
  position: relative;
  min-height: 128px;
  padding: 13px 4px 23px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: clamp(38px, 7vw, 100px);
  border-bottom: 1px solid color-mix(in srgb, var(--app-border-strong) 68%, transparent);
}
.workspace-masthead__copy {
  min-width: 0;
}
.workspace-kicker {
  margin: 0 0 8px;
  display: flex;
  align-items: center;
  gap: 9px;
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 8.5px;
  font-weight: 720;
  letter-spacing: 0.14em;
  line-height: 1.4;
  text-transform: uppercase;
}
.workspace-kicker span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent) 7%, transparent);
}
.workspace-masthead h1 {
  margin: 0;
  color: var(--app-text);
  font-family: var(--font-display);
  font-size: clamp(40px, 4.2vw, 52px);
  font-weight: 610;
  letter-spacing: -0.042em;
  line-height: 1;
}
.workspace-masthead__copy > p:last-child {
  margin: 9px 0 0;
  color: var(--app-text-muted);
  font-size: 13px;
  line-height: 1.65;
}
.workspace-signature {
  justify-self: end;
  margin-right: 8px;
}

@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .main-container {
    padding-top: 76px !important;
  }
  .whiteboard-main {
    gap: 15px !important;
  }
  .workspace-masthead {
    min-height: 0;
    display: block;
    padding: 12px 0 16px;
  }
  .workspace-kicker {
    display: none;
  }
  .workspace-masthead h1 {
    font-size: clamp(33px, 10vw, 42px);
  }
  .workspace-masthead__copy > p:last-child {
    margin-top: 7px;
    font-size: 12.5px;
  }
}

/* v5.1 · Workspace controls use restrained, local state changes. */
.clear-btn,
.entry-action,
.key-chip,
.tool-button,
.attachment-add,
.empty-primary,
.empty-secondary,
.close-btn {
  transition:
    color 160ms ease,
    background-color 160ms ease,
    border-color 160ms ease,
    box-shadow 180ms ease;
}
@media (hover: hover) and (pointer: fine) {
  .entry-action:hover,
  .tool-button--primary:hover:not(:disabled),
  .empty-primary:hover {
    box-shadow: 0 7px 18px color-mix(in srgb, var(--accent) 12%, transparent);
  }
}
</style>
