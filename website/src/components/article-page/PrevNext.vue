<template>
  <div class="prev-next-nav" aria-label="上一篇和下一篇">
    <div class="prev-next-item">
      <a v-if="prev" :href="prev.url" class="nav-link prev" :title="prev.title">
        <span class="nav-kicker">PREVIOUS</span>
        <strong>{{ prev.title }}</strong>
        <span class="nav-arrow" aria-hidden="true">←</span>
      </a>
    </div>
    <div class="prev-next-item">
      <a v-if="next" :href="next.url" class="nav-link next" :title="next.title">
        <span class="nav-kicker">NEXT</span>
        <strong>{{ next.title }}</strong>
        <span class="nav-arrow" aria-hidden="true">→</span>
      </a>
    </div>
  </div>
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
watch(
  [() => props.id, () => props.category],
  async () => {
    prev.value = null;
    next.value = null;

    if (props.category === "" || props.id === "") return;

    const res = await getArticlesByCategory(props.category);
    const currentIndex = res.findIndex((item) => item.id === props.id);
    if (currentIndex === -1) return;

    const prevArticle = currentIndex > 0 ? res[currentIndex - 1] : null;
    const nextArticle = currentIndex < res.length - 1 ? res[currentIndex + 1] : null;

    if (prevArticle) prev.value = { title: prevArticle.title, url: `/article/${prevArticle.id}` };
    if (nextArticle) next.value = { title: nextArticle.title, url: `/article/${nextArticle.id}` };
  },
  { immediate: true },
);
</script>

<style scoped>
.prev-next-nav {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 4px;
}
.prev-next-item {
  min-width: 0;
}
.nav-link {
  position: relative;
  min-height: 118px;
  padding: 18px 20px;
  display: grid;
  align-content: space-between;
  gap: 10px;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--app-border-strong) 72%, transparent);
  border-radius: 18px;
  background: color-mix(in srgb, var(--app-surface) 76%, transparent);
  color: var(--app-text);
  text-decoration: none;
  box-shadow: inset 0 1px 0 color-mix(in srgb, #fff 60%, transparent);
  transition:
    transform 240ms cubic-bezier(0.16, 1, 0.3, 1),
    border-color 180ms ease,
    background-color 180ms ease;
}
.nav-link::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(circle at 88% 16%, color-mix(in srgb, var(--accent) 7%, transparent), transparent 36%);
  opacity: 0;
  transition: opacity 180ms ease;
}
.nav-kicker {
  color: var(--app-text-soft);
  font-family: var(--font-mono);
  font-size: 8.5px;
  font-weight: 720;
  letter-spacing: 0.12em;
}
.nav-link strong {
  max-width: 26ch;
  color: var(--app-text);
  font-size: 14px;
  font-weight: 620;
  line-height: 1.5;
  text-wrap: pretty;
}
.nav-arrow {
  position: absolute;
  right: 18px;
  bottom: 17px;
  color: var(--accent);
  font-size: 16px;
  transition: transform 220ms cubic-bezier(0.16, 1, 0.3, 1);
}
.next {
  text-align: left;
}
.nav-link:hover {
  border-color: var(--accent-line);
  background: color-mix(in srgb, var(--app-surface) 90%, var(--accent) 1.5%);
  transform: translateY(-2px);
}
.nav-link:hover::after {
  opacity: 1;
}
.prev:hover .nav-arrow {
  transform: translateX(-3px);
}
.next:hover .nav-arrow {
  transform: translateX(3px);
}
@media (max-width: 640px) {
  .prev-next-nav {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  .nav-link {
    min-height: 96px;
    padding: 15px 16px;
    border-radius: 15px;
  }
  .nav-link strong {
    max-width: calc(100% - 34px);
    font-size: 13px;
  }
  .nav-arrow {
    right: 15px;
    bottom: 14px;
  }
}
</style>
