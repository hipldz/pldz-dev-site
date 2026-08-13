import { apiGet, apiPost, apiPrefix } from "./request.js";

const authPrefix = `${apiPrefix}/authorization`;

export function getPrivacyPolicy() {
  return apiGet(`${authPrefix}/privacy`);
}

export function getAllUsers() {
  return apiGet(`${authPrefix}/usermanagement/all`);
}

export function login(username, password, otp_code = "") {
  return apiPost(`${authPrefix}/login`, { username, password, otp_code });
}

export function register(username, password, nickname) {
  return apiPost(`${authPrefix}/register`, { username, password, nickname });
}

export function refresh() {
  return apiPost(`${authPrefix}/refresh`);
}

export function logout() {
  return apiGet(`${authPrefix}/logout`);
}

export function updateAvatar(avatar) {
  return apiPost(`${authPrefix}/update/avatar`, { avatar });
}

export function setupTwoFactor() {
  return apiPost(`${authPrefix}/2fa/setup`);
}

export function confirmTwoFactor(code) {
  return apiPost(`${authPrefix}/2fa/confirm`, { code });
}

export function disableTwoFactor(code) {
  return apiPost(`${authPrefix}/2fa/disable`, { code });
}

export function deleteUserByUsername(username) {
  return apiPost(`${authPrefix}/usermanagement/delete`, { username });
}
