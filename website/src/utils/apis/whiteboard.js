import { apiPost, websitePrefix } from "./request.js";

const whiteboardPrefix = `${websitePrefix}/whiteboard`;

export function getWhiteboardByKey(key) {
  return apiPost(`${whiteboardPrefix}/key`, { key });
}

export function getWhiteboardByUser(username = "", createNew = true) {
  return apiPost(`${whiteboardPrefix}/authorized`, {
    username,
    create_new: createNew,
  });
}

export function updateWhiteboardContent(key, content) {
  return apiPost(`${whiteboardPrefix}/update`, { key, content });
}
