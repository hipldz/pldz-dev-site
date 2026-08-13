import { apiPost, websitePrefix } from "./request.js";

const imagePrefix = `${websitePrefix}/image`;

export function checkImageExists(category, name) {
  return apiPost(`${imagePrefix}/upload/check`, { category, name });
}

export function getImagesByCategory(category) {
  return apiPost(`${imagePrefix}/category/all`, { category });
}

export function renameImage(category, oldName, newName) {
  return apiPost(`${imagePrefix}/rename`, { category, oldName, newName });
}

export function deleteImage(category, name) {
  return apiPost(`${imagePrefix}/delete`, { category, name });
}
