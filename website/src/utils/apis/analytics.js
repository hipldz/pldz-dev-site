import { apiGet, apiPost, apiPrefix } from "./request.js";

const analyticsPrefix = `${apiPrefix}/analytics`;

export function trackAnalyticsEvent(payload) {
  return apiPost(`${analyticsPrefix}/track`, payload);
}

export function getAnalyticsOverview(rangeValue = "30d", granularity = "day") {
  const query = new URLSearchParams({ range_value: rangeValue, granularity });
  return apiGet(`${analyticsPrefix}/overview?${query}`);
}

export function getAnalyticsTopArticles(rangeValue = "30d", limit = 10) {
  const query = new URLSearchParams({ range_value: rangeValue, limit });
  return apiGet(`${analyticsPrefix}/articles/top?${query}`);
}

export function getAnalyticsCta(rangeValue = "30d", eventKey = "live_demo") {
  const query = new URLSearchParams({ range_value: rangeValue, event_key: eventKey });
  return apiGet(`${analyticsPrefix}/cta?${query}`);
}
