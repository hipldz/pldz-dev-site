import { apiGet, websitePrefix } from "./request.js";

const articlePrefix = `${websitePrefix}/article`;

export function getAllArticles() {
  return apiGet(`${articlePrefix}/all/article`);
}

export function getArticleIntros() {
  return apiGet(`${articlePrefix}/all/intro`);
}

export function getAllCategories() {
  return apiGet(`${articlePrefix}/all/category`);
}

export function getTagCounts() {
  return apiGet(`${articlePrefix}/all/tag`);
}

export function getArticlesByCategory(categoryId) {
  return apiGet(`${articlePrefix}/category/${encodeURIComponent(categoryId)}`);
}

export function getArticle(articleId) {
  return apiGet(`${articlePrefix}/id/${encodeURIComponent(articleId)}`);
}

export function getArticlesByTag(tag) {
  return apiGet(`${articlePrefix}/tag/${encodeURIComponent(tag)}`);
}
