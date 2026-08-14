import { apiGet, apiPrefix } from "./request.js";

export function getAllResources() {
  return apiGet(apiPrefix + "/resource/all");
}
