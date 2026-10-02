import { computed, onActivated, onBeforeUnmount, onDeactivated, onMounted, ref, watch } from "vue";
import { useStore } from "vuex";
import { useRouter } from "vue-router";
import { getArticle } from "./apis/articles.js";
import { getDraftArticle, getSharedDraft } from "./apis/drafts.js";

const emptyArticle = () => ({ id: "", content: "", meta: {}, views: 0 });

// Reading access and its lifetime belong here; ArticlePage only renders the result.
export function useArticleReader(props) {
  const store = useStore();
  const router = useRouter();
  const article = ref(emptyArticle());
  const error = ref("");
  const expiresAt = ref("");
  const isDraft = computed(() => props.mode !== "published");
  const isShared = computed(() => props.mode === "shared");
  let active = true;
  let requestId = 0;
  let expiryTimer;

  function clearArticle() {
    article.value = emptyArticle();
    expiresAt.value = "";
    clearTimeout(expiryTimer);
  }

  function scheduleExpiry() {
    clearTimeout(expiryTimer);
    if (!active || !isShared.value || !expiresAt.value) return;
    const remaining = new Date(expiresAt.value).getTime() - Date.now();
    if (remaining <= 0) {
      clearArticle();
      error.value = "分享链接已过期";
      return;
    }
    expiryTimer = setTimeout(scheduleExpiry, Math.min(remaining, 2147483647));
  }

  async function load() {
    if (!active) return;
    const version = ++requestId;
    clearArticle();
    error.value = "";

    if (props.mode === "draft") {
      if (!store.state.authState.ready) return;
      if (!store.state.authState.isadmin) {
        router.replace("/404");
        return;
      }
    }

    try {
      let result;
      switch (props.mode) {
        case "draft":
          result = await getDraftArticle(props.id);
          break;
        case "shared":
          result = await getSharedDraft(props.id, props.shareToken);
          break;
        default:
          result = await getArticle(props.id);
      }
      if (version !== requestId) return;
      if (!result || (isDraft.value && !result.isDraft)) throw new Error(isShared.value ? "分享链接无效，或文章已不可用" : "文章不存在或暂时无法访问");

      // Expiry describes access to an article; it is not part of the article itself.
      const { shareExpiresAt, ...document } = result;
      article.value = document;
      expiresAt.value = isShared.value ? shareExpiresAt || "" : "";
      scheduleExpiry();
    } catch (err) {
      if (version !== requestId) return;
      if (props.mode === "draft") router.replace("/404");
      else error.value = err.message || "文章暂时无法访问，请稍后重试";
    }
  }

  function deactivate() {
    active = false;
    requestId += 1;
    clearTimeout(expiryTimer);
    if (isDraft.value || article.value.isDraft) clearArticle();
  }

  watch(() => [props.id, props.mode, props.shareToken], load);
  watch([() => store.state.authState.ready, () => store.state.authState.isadmin], () => {
    if (props.mode === "draft") void load();
  });
  onMounted(load);
  onActivated(() => {
    if (active) return;
    active = true;
    void load();
  });
  onDeactivated(deactivate);
  onBeforeUnmount(deactivate);

  return { article, error, expiresAt, isDraft, isShared };
}
