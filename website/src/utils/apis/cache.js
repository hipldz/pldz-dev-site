import { apiGet, apiPost, apiPrefix } from "./request.js";

const cachePrefix = `${apiPrefix}/cache`;

export function getAllCache() {
  return apiGet(`${cachePrefix}/all`);
}

export function downloadCacheFile(filename) {
  return apiPost(`${cachePrefix}/download`, { filename }, true);
}

export function deleteCacheFile(filename) {
  return apiPost(`${cachePrefix}/delete`, { filename });
}
