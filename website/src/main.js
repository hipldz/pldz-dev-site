import "./assets/index.css";
import App from "./App.vue";
import router from "./routers";
import store from "./store";

import { createApp } from "vue";
import { refresh } from "./utils/apis";
import { initAnalytics } from "./utils/analytics";
import { initTheme } from "./utils/theme";
import { cursor, depth, field, magnetic, reveal, spotlight } from "./utils/motion";

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
    app.directive("reveal", reveal);
    app.directive("spotlight", spotlight);
    app.directive("depth", depth);
    app.directive("field", field);
    app.directive("magnetic", magnetic);
    app.directive("cursor", cursor);
    app.use(store);
    app.use(router);
    app.mount("#app");

    initAnalytics(router);
    refreshAuthState();
  } finally {
    window.loading?.done();
  }
};

// Mount as soon as the DOM is ready. Images and embeds can continue loading lazily.
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", bootstrap, { once: true });
} else {
  bootstrap();
}
