import { createRouter, createWebHistory } from "vue-router";
import HomePage from "../views/HomePage.vue";
import NotFound from "../views/NotFound.vue";

const ArticlePage = () => import("../views/ArticlePage.vue");
const TutorialsPage = () => import("../views/TutorialsPage.vue");
const AdminPage = () => import("../views/AdminPage.vue");
const WhiteboardPage = () => import("../views/WhiteboardPage.vue");
const LiveDemoPage = () => import("../views/LiveDemoPage.vue");

const router = createRouter({
  // 使用 HTML5 的 History 模式
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: HomePage,
    },
    {
      path: "/articles",
      component: TutorialsPage,
    },
    {
      path: "/articles/:category",
      component: TutorialsPage,
      props: true,
    },
    {
      path: "/admin/:id?",
      component: AdminPage,
      props: true,
    },
    {
      path: "/whiteboard",
      component: WhiteboardPage,
    },
    {
      path: "/livedemo",
      component: LiveDemoPage,
    },
    {
      // 动态路由，用 :id 捕获文章 ID
      path: "/article/:id",
      component: ArticlePage,
      // 将路由参数作为 props 传入组件
      props: true,
    },
    {
      path: "/404",
      component: NotFound,
    },
    {
      // 通配所有未匹配的路径
      path: "/:pathMatch(.*)*",
      redirect: "/",
    },
  ],
});

export default router;
