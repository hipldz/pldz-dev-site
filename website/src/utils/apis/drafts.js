import { apiGet, apiPost, websitePrefix } from "./request.js";

const articlePrefix = `${websitePrefix}/article`;

export function getDraftArticles() {
  return apiGet(`${articlePrefix}/drafts`);
}

export function getDraftArticle(articleId) {
  return apiGet(`${articlePrefix}/draft/${encodeURIComponent(articleId)}`);
}

export function createDraftShare(articleId, durationMinutes = 1440) {
  return apiPost(`${articlePrefix}/draft/${encodeURIComponent(articleId)}/share`, { duration_minutes: durationMinutes });
}

export async function getSharedDraft(articleId, token) {
  const response = await fetch(`${articlePrefix}/shared/${encodeURIComponent(articleId)}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!response.ok) throw new Error(response.status === 410 ? "分享链接已过期" : "分享链接无效，或文章已不可用");
  return (await response.json()).data;
}
