<template>
  <div class="comments-container">
    <!-- 评论提交表单 -->
    <div class="comment-submit-container">
      <label for="comment-input" class="sr-only">输入评论内容</label>
      <textarea
        id="comment-input"
        v-model="commentText"
        :placeholder="replyTo ? `回复 @${replyTo.username}:` : placeholder"
        @keyup.enter.ctrl="onSubmit"
        :disabled="isSubmitting"
        :aria-disabled="isSubmitting"
        ref="textareaRef"
      ></textarea>
      <div class="actions">
        <div class="left-actions">
          <span v-if="replyTo" class="reply-info">
            回复 @{{ replyTo.username }}
            <button @click="cancelReply" class="cancel-reply">✕</button>
          </span>
          <span class="char-count" :class="{ 'over-limit': charCount > maxLength }"> {{ charCount }}/{{ maxLength }} </span>
        </div>
        <button class="submit-btn" :disabled="!isValid || isSubmitting" @click="onSubmit">
          {{ isSubmitting ? "提交中..." : replyTo ? "回复" : buttonText }}
        </button>
      </div>
    </div>

    <!-- 评论列表 -->
    <div class="comments-list" v-if="comments.length > 0">
      <div class="comments-header">
        <h3>评论 ({{ comments.length }})</h3>
        <div class="sort-options">
          <button :class="{ active: sortBy === 'newest' }" @click="sortBy = 'newest'">最新</button>
          <button :class="{ active: sortBy === 'oldest' }" @click="sortBy = 'oldest'">最早</button>
        </div>
      </div>

      <div class="comment-item" v-for="comment in sortedComments" :key="comment.id">
        <div class="comment-avatar">
          <img :src="comment.avatar" />
        </div>
        <div class="comment-content">
          <div class="comment-header">
            <span class="username">{{ comment.username }}</span>
            <span class="time">{{ formatTime(comment.created) }}</span>
          </div>
          <div class="comment-text">{{ comment.content }}</div>
          <div class="comment-actions">
            <button @click="startReply(comment)" class="action-btn"><span class="icon">💬</span> 回复</button>
            <button v-if="canDelete(comment)" @click="onDeleteComment(comment.id)" class="action-btn delete-btn" :disabled="deletingIds.has(comment.id)">
              <span class="icon">🗑️</span>
              {{ deletingIds.has(comment.id) ? "删除中..." : "删除" }}
            </button>
          </div>

          <!-- 回复列表 -->
          <div class="replies" v-if="comment.replies && comment.replies.length > 0">
            <div class="reply-item" v-for="reply in comment.replies" :key="reply.id">
              <div class="reply-avatar">
                <img :src="reply.avatar || '/default-avatar.png'" :alt="reply.username" />
              </div>
              <div class="reply-content">
                <div class="reply-header">
                  <span class="username">{{ reply.username }}</span>
                  <span class="time">{{ formatTime(reply.created) }}</span>
                </div>
                <div class="reply-text">
                  <span v-if="reply.replyToUsername" class="reply-to"> @{{ reply.replyToUsername }} </span>
                  {{ reply.content }}
                </div>
                <div class="reply-actions">
                  <button @click="startReply(comment, reply)" class="action-btn"><span class="icon">💬</span> 回复</button>
                  <button
                    v-if="canDelete(reply)"
                    @click="onDeleteReply(comment.id, reply.id)"
                    class="action-btn delete-btn"
                    :disabled="deletingIds.has(reply.id)"
                  >
                    <span class="icon">🗑️</span>
                    {{ deletingIds.has(reply.id) ? "删除中..." : "删除" }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="empty-comments" v-else>
      <div class="empty-icon">💬</div>
      <p>还没有评论，来发表第一条评论吧！</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch } from "vue";
import { useStore } from "vuex";
import Toast from "../../utils/toast.js";

import { getAllComments, addComment, deleteComment } from "../../utils/apis";

// Props
const props = defineProps({
  articleId: { type: [String, Number], required: true },
  placeholder: { type: String, default: "输入评论内容..." },
  buttonText: { type: String, default: "发表评论" },
  maxLength: { type: Number, default: 500 },
});

// Emits
const emit = defineEmits(["comment-added", "comment-deleted", "reply-added", "reply-deleted"]);

const store = useStore();
const username = computed(() => store.state.authState.username);
const avatar = computed(() => store.state.authState.avatar);

// 状态
const commentText = ref("");
const isSubmitting = ref(false);
const replyTo = ref(null); // { id, username, isReply: boolean }
const comments = ref([]);
const deletingIds = ref(new Set());
const sortBy = ref("newest");
const textareaRef = ref(null);

// 计算属性
const charCount = computed(() => commentText.value.length);
const isValid = computed(() => {
  const text = commentText.value.trim();
  return text.length > 0 && text.length <= props.maxLength && username.value;
});

const sortedComments = computed(() => {
  const sorted = [...comments.value];
  if (sortBy.value === "newest") {
    return sorted.sort((a, b) => new Date(b.created) - new Date(a.created));
  } else {
    return sorted.sort((a, b) => new Date(a.created) - new Date(b.created));
  }
});

// 提交评论或回复
async function onSubmit() {
  if (isSubmitting.value) return;

  if (!username.value) {
    Toast.error("请先登录");
    return;
  }

  const text = commentText.value.trim();
  if (!text) {
    Toast.warning("评论内容不能为空");
    return;
  }

  if (text.length > props.maxLength) {
    Toast.warning(`评论不能超过${props.maxLength}个字`);
    return;
  }

  try {
    isSubmitting.value = true;

    if (replyTo.value) {
      const reply = {
        id: (Date.now() + Math.random()).toString().replace(".", ""),
        content: text,
        username: username.value,
        avatar: avatar.value,
        replies: [],
        replyToUsername: replyTo.value.username || "",
        created: new Date().toISOString(),
      };

      const flag = await addComment(props.articleId, reply, replyTo.value.id || "");
      if (!flag) {
        Toast.error("评论失败，请重试");
        return;
      }

      // 找到对应的评论并添加回复
      const comment = comments.value.find((c) => c.id === replyTo.value.id);
      if (comment) {
        if (!comment.replies) comment.replies = [];
        comment.replies.push(reply);
        emit("reply-added", reply);
      }

      Toast.success("回复成功");
    } else {
      // 添加评论
      const comment = {
        id: (Date.now() + Math.random()).toString().replace(".", ""),
        content: text,
        username: username.value,
        avatar: avatar.value,
        replies: [],
        replyToUsername: "",
        created: new Date().toISOString(),
      };

      const flag = await addComment(props.articleId, comment);
      if (flag) {
        comments.value.unshift(comment);
        Toast.success("评论成功");
      } else {
        Toast.error("评论失败，请重试");
        return;
      }
    }

    // 清空输入
    commentText.value = "";
    cancelReply();
  } catch (error) {
    Toast.error(replyTo.value ? "回复失败，请重试" : "评论失败，请重试");
    console.error("Submit error:", error);
  } finally {
    isSubmitting.value = false;
  }
}

// 开始回复
async function startReply(comment, reply = null) {
  if (reply) {
    // 回复某条回复
    replyTo.value = {
      id: comment.id,
      username: reply.username,
      isReply: true,
    };
  } else {
    // 回复某条评论
    replyTo.value = {
      id: comment.id,
      username: comment.username,
      isReply: false,
    };
  }

  // 聚焦到输入框
  await nextTick();
  textareaRef.value?.focus();
}

// 取消回复
function cancelReply() {
  replyTo.value = null;
}

// 删除评论
async function onDeleteComment(commentId) {
  if (deletingIds.value.has(commentId)) return;

  try {
    deletingIds.value.add(commentId);
    const flag = await deleteComment(props.articleId, commentId);
    if (!flag) {
      Toast.error("删除失败，请重试");
      return;
    }

    const index = comments.value.findIndex((c) => c.id === commentId);
    if (index !== -1) {
      const deletedComment = comments.value.splice(index, 1)[0];
      emit("comment-deleted", deletedComment);
      Toast.success("评论已删除");
    }
  } catch (error) {
    Toast.error("删除失败，请重试");
    console.error("Delete comment error:", error);
  } finally {
    deletingIds.value.delete(commentId);
  }
}

// 删除回复
async function onDeleteReply(commentId, replyId) {
  if (deletingIds.value.has(replyId)) return;

  try {
    deletingIds.value.add(replyId);

    const flag = await deleteComment(props.articleId, replyId);
    if (!flag) {
      Toast.error("删除失败，请重试");
      return;
    }

    const comment = comments.value.find((c) => c.id === commentId);
    if (comment && comment.replies) {
      const index = comment.replies.findIndex((r) => r.id === replyId);
      if (index !== -1) {
        const deletedReply = comment.replies.splice(index, 1)[0];
        emit("reply-deleted", deletedReply);
        Toast.success("回复已删除");
      }
    }
  } catch (error) {
    Toast.error("删除失败，请重试");
    console.error("Delete reply error:", error);
  } finally {
    deletingIds.value.delete(replyId);
  }
}

// 检查是否可以删除
function canDelete(item) {
  return username.value && item.username === username.value;
}

// 格式化时间
function formatTime(dateString) {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now - date;

  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return "刚刚";
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  if (days < 7) return `${days}天前`;

  return date.toLocaleDateString("zh-CN");
}

/**
 * 组件挂载时获取初始评论
 */
watch(
  () => props.articleId,
  async () => {
    if (!props.articleId) {
      return;
    }
    // 获取初始评论
    const data = await getAllComments(props.articleId);
    if (Array.isArray(data)) {
      comments.value = data;
    }
  }
);
</script>

<style scoped>
.comments-container {
  max-width: 100%;
  margin: 0 auto;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.comment-submit-container {
  margin-bottom: 24px;
  padding: 16px;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-md);
  background-color: var(--app-surface);
  box-shadow: var(--app-shadow-sm);
}

textarea {
  width: 100%;
  min-height: 120px;
  padding: 12px;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-sm);
  font-size: 14px;
  line-height: 1.5;
  transition: border-color var(--app-motion-duration) var(--app-ease);
  resize: vertical;
  box-sizing: border-box;
  font-family: inherit;
}

textarea:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(189, 88, 54, 0.2);
}

textarea:disabled {
  background-color: var(--app-surface-sunken);
  cursor: not-allowed;
}

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.left-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.reply-info {
  font-size: 12px;
  color: var(--accent);
  background: var(--accent-weak);
  padding: 4px 8px;
  border-radius: var(--app-radius-sm);
  display: flex;
  align-items: center;
  gap: 6px;
}

.cancel-reply {
  background: none;
  border: none;
  color: var(--app-text-soft);
  cursor: pointer;
  padding: 0;
  font-size: 12px;
}

.cancel-reply:hover {
  color: var(--app-text-muted);
}

.char-count {
  font-size: 12px;
  color: var(--app-text-soft);
  transition: color var(--app-motion-duration) var(--app-ease);
}

.char-count.over-limit {
  color: var(--app-red);
  font-weight: 500;
}

.submit-btn {
  padding: 8px 20px;
  font-size: 14px;
  font-weight: 500;
  color: var(--app-surface);
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%);
  border: none;
  border-radius: var(--app-radius-sm);
  cursor: pointer;
  transition: background var(--app-motion-duration) var(--app-ease), transform var(--app-motion-duration) var(--app-ease);
  min-width: 80px;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.submit-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--accent-hover) 0%, var(--accent) 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(189, 88, 54, 0.28);
}

.comments-list {
  margin-top: 24px;
}

.comments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.comments-header h3 {
  margin: 0;
  font-size: 18px;
  color: var(--app-text);
}

.sort-options {
  display: flex;
  gap: 8px;
}

.sort-options button {
  padding: 6px 12px;
  font-size: 12px;
  border: 1px solid var(--app-border);
  background: var(--app-surface);
  border-radius: var(--app-radius-sm);
  cursor: pointer;
  transition: background var(--app-motion-duration) var(--app-ease), color var(--app-motion-duration) var(--app-ease), border-color var(--app-motion-duration) var(--app-ease);
}

.sort-options button.active {
  background: var(--accent);
  color: var(--app-surface);
  border-color: var(--accent);
}

.comment-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-md);
  background: var(--app-surface);
  margin-bottom: 16px;
}

.comment-avatar,
.reply-avatar {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.comment-avatar img,
.reply-avatar img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.reply-avatar img {
  width: 32px;
  height: 32px;
}

.comment-content {
  flex: 1;
}

.comment-header,
.reply-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.username {
  font-weight: 500;
  color: var(--app-text);
}

.time {
  font-size: 12px;
  color: var(--app-text-soft);
}

.comment-text,
.reply-text {
  line-height: 1.6;
  color: var(--app-text);
  margin-bottom: 12px;
  word-break: break-word;
}

.reply-to {
  color: var(--accent);
  font-weight: 500;
}

.comment-actions,
.reply-actions {
  display: flex;
  gap: 16px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  font-size: 12px;
  color: var(--app-text-muted);
  background: none;
  border: none;
  border-radius: var(--app-radius-sm);
  cursor: pointer;
  transition: background var(--app-motion-duration) var(--app-ease), color var(--app-motion-duration) var(--app-ease);
}

.action-btn:hover {
  background: var(--app-surface-sunken);
  color: var(--app-text);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.delete-btn:hover {
  background: rgba(180, 71, 47, 0.12);
  color: var(--app-red);
}

.icon {
  font-size: 12px;
}

.replies {
  margin-top: 16px;
  padding-left: 16px;
  border-left: 2px solid var(--app-border);
}

.reply-item {
  display: flex;
  gap: 8px;
  padding: 12px 0;
  border-bottom: 1px solid var(--app-border);
}

.reply-item:last-child {
  border-bottom: none;
}

.reply-content {
  flex: 1;
}

.empty-comments {
  text-align: center;
  padding: 48px 16px;
  color: var(--app-text-soft);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-comments p {
  margin: 0;
  font-size: 14px;
}
</style>
