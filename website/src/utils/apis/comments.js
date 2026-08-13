import { apiPost, websitePrefix } from "./request.js";

const commentPrefix = `${websitePrefix}/comment`;

export function getAllComments(article_id) {
  return apiPost(`${commentPrefix}/all`, { article_id });
}

export function addComment(article_id, content, parent_id = "") {
  return apiPost(`${commentPrefix}/add`, { article_id, content, parent_id });
}

export function deleteComment(article_id, comment_id) {
  return apiPost(`${commentPrefix}/delete`, { article_id, comment_id });
}
