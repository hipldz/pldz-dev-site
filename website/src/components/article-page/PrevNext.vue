<template>
  <!-- 上一篇/下一篇导航 -->
  <div class="prev-next-nav">
    <div class="prev-next-item">
      <a v-if="prev" :href="prev.url" class="nav-link prev" :title="prev.title"> &laquo; 上一篇：{{ prev.title }} </a>
    </div>
    <div class="prev-next-item">
      <a v-if="next" :href="next.url" class="nav-link next" :title="next.title"> 下一篇：{{ next.title }} &raquo; </a>
    </div>
  </div>
  <!-- 分割线 -->
  <div class="divider"></div>
</template>

<script setup>
import { ref, watch } from "vue";
import { getArticlesByCategory } from "../../utils/apis";

// 定义 props 接收文章信息
const props = defineProps({
  id: {
    type: String,
    required: true,
    default: "",
  },
  category: {
    type: String,
    required: true,
    default: "",
  },
});

// 定义响应式变量来存储上一篇和下一篇文章的信息
const prev = ref(null);
const next = ref(null);

/**
 * 获取上一篇和下一篇文章
 * @param {Object} article 当前文章对象
 */
watch([() => props.id, () => props.category], async () => {
  if (props.category === "" || props.id === "") {
    console.warn("没有分类或ID, 无法获取文章.");
    return;
  }

  const res = await getArticlesByCategory(props.category);
  const currentIndex = res.findIndex((item) => item.id === props.id);
  if (currentIndex === -1) {
    console.warn("当前文章未找到.");
    return;
  }

  // 获取上一篇和下一篇文章
  const prevArticle = currentIndex > 0 ? res[currentIndex - 1] : null;
  const nextArticle = currentIndex < res.length - 1 ? res[currentIndex + 1] : null;

  if (prevArticle) {
    prev.value = { title: prevArticle.title, url: `/article/${prevArticle.id}` };
  }

  if (nextArticle) {
    next.value = { title: nextArticle.title, url: `/article/${nextArticle.id}` };
  }
});
</script>

<style scoped>
/* 分割线样式 */
.divider {
  width: 100%;
  height: 1px;
  margin: 20px 0;
  background: linear-gradient(to right, rgba(189, 88, 54, 0) 0%, rgba(189, 88, 54, 0.4) 50%, rgba(189, 88, 54, 0) 100%);
}

.prev-next-nav {
  display: flex;
  justify-content: space-between;
  margin: 32px auto;
  flex: 1;
}

.prev-next-item {
  width: 50%;
}

.nav-link {
  flex: 1;
  margin: 0 10px;
  display: block;
  text-decoration: none;
  color: var(--accent);
  font-size: 15px;
  padding: 12px 14px;
  transition: background-color var(--app-motion-duration) var(--app-ease), color var(--app-motion-duration) var(--app-ease),
    border-color var(--app-motion-duration) var(--app-ease);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.prev,
.next {
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-md);
  height: 100%;
}

.prev {
  text-align: left;
}

.next {
  text-align: right;
}

.nav-link:hover {
  background-color: var(--accent);
  border-color: var(--accent);
  color: #fffdf8;
}
</style>
