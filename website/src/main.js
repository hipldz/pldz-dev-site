import "./assets/index.css";
import App from "./App.vue";
import router from "./routers";
import store from "./store";

import { createApp } from "vue";
import { refresh } from "./utils/apis";
import { initAnalytics } from "./utils/analytics";
import { initTheme } from "./utils/theme";

const refreshAuthState = async () => {
  try {
    const res = await refresh();

    await store.dispatch("authState/update", {
      username: res?.username || "",
      avatar: res?.avatar || "",
      nickname: res?.nickname || "",
      isadmin: res?.isadmin || false,
      two_factor_enabled: res?.two_factor_enabled || false,
    });
  } catch (error) {
    console.error("refreshAuthState error:", error);
  } finally {
    await store.dispatch("authState/ready", true);
  }
};

initTheme();

const bootstrap = () => {
  try {
    window.loading?.set(98);

    const app = createApp(App);
    app.use(store);
    app.use(router);
    app.mount("#app");

    initAnalytics(router);
    refreshAuthState();
  } finally {
    window.loading?.done();
  }
};

// 等页面资源加载完后再启动
if (document.readyState === "complete") {
  bootstrap();
} else {
  window.addEventListener("load", bootstrap, { once: true });
}
