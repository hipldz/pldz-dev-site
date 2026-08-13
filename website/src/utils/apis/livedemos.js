import { apiGet, websitePrefix } from "./request.js";

export function getAllLiveDemos() {
  return apiGet(`${websitePrefix}/livedemo/all`);
}
