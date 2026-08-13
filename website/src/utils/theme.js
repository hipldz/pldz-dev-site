const THEME_KEY = "pldz-dev-theme";
const DEFAULT_THEME = "light";

export const themes = [
  { id: "light", label: "亮色", swatch: "#1a73e8" },
  { id: "lime", label: "青柠色", swatch: "#10a37f" },
  { id: "brown", label: "暖棕色", swatch: "#bd5836" },
];

const themeIds = new Set(themes.map((theme) => theme.id));

export function normalizeTheme(theme) {
  return themeIds.has(theme) ? theme : DEFAULT_THEME;
}

export function getStoredTheme() {
  if (typeof window === "undefined") return DEFAULT_THEME;

  try {
    return normalizeTheme(window.localStorage.getItem(THEME_KEY));
  } catch (_error) {
    return DEFAULT_THEME;
  }
}

export function applyTheme(theme) {
  const normalizedTheme = normalizeTheme(theme);

  if (typeof document !== "undefined") {
    document.documentElement.dataset.theme = normalizedTheme;
  }

  return normalizedTheme;
}

export function setStoredTheme(theme) {
  const normalizedTheme = applyTheme(theme);

  if (typeof window !== "undefined") {
    try {
      window.localStorage.setItem(THEME_KEY, normalizedTheme);
    } catch (_error) {
      // localStorage can be unavailable in private or embedded contexts.
    }
  }

  return normalizedTheme;
}

export function initTheme() {
  return applyTheme(getStoredTheme());
}
