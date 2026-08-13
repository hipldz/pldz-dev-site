import { apiGet, apiPost, apiPrefix } from "./request.js";

export async function getWwwDeployments() {
  return apiGet(`${apiPrefix}/deploy/www/all`);
}

export async function retryWwwDeployment(id) {
  return apiPost(`${apiPrefix}/deploy/www/retry`, { id });
}
