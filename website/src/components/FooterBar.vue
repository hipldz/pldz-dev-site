<template>
  <footer class="footer">
    <div class="footer-inner">
      <div class="footer-copy">
        <span>{{ privacyData.copyright }}</span>
        <span class="footer-divider"></span>
        <span>Hi 爬楼的猪</span>
      </div>

      <div class="footer-links">
        <a href="https://beian.miit.gov.cn/?spm=5176.28426678.J_9220772140.59.30965181t5PJph#/Integrated/index" rel="noreferrer" target="_blank">
          {{ privacyData.ps }}
        </a>
        <a href="https://beian.miit.gov.cn/" target="_blank">{{ privacyData.icp }}</a>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { getPrivacyPolicy } from "../utils/apis";

const privacyData = ref({ icp: "", copyright: "", ps: "" });

onMounted(async () => {
  const res = await getPrivacyPolicy();
  Object.assign(privacyData.value, res);
});
</script>

<style scoped>
.footer {
  padding: 16px 0 32px;
}

.footer-inner {
  width: min(var(--app-page-width), calc(100% - 2 * var(--app-page-gutter)));
  margin: 0 auto;
  padding: 24px 0 0;
  border-top: 1px solid var(--app-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  color: var(--app-text-soft);
  font-size: 12px;
}

.footer-copy,
.footer-links {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.footer-divider {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--app-border-strong);
}

.footer-links a {
  color: var(--app-text-muted);
  text-decoration: none;
}

.footer-links a:hover {
  color: var(--app-blue);
}

@media (max-width: 700px), (max-width: 840px) and (pointer: coarse) {
  .footer-inner {
    width: min(var(--app-page-width), calc(100% - 2 * var(--app-page-gutter)));
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 640px) {
  .footer-inner {
    width: min(var(--app-page-width), calc(100% - 2 * var(--app-page-gutter)));
  }
}

/* v4.0 · Footer alignment */
.footer-inner {
  min-height: 58px;
  padding-top: 20px;
  line-height: 1.5;
}
.footer-copy,
.footer-links {
  gap: 10px 12px;
}

/* v4.1 · mobile footer */
@media (max-width: 640px) {
  .footer {
    padding: 8px 0 24px;
  }
  .footer-inner {
    width: calc(100% - 28px) !important;
    min-height: 0 !important;
    padding-top: 18px !important;
    gap: 10px !important;
    font-size: 11px !important;
  }
  .footer-copy,
  .footer-links {
    width: 100%;
    gap: 7px 10px !important;
  }
  .footer-links {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
