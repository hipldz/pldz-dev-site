const THEME_KEY = "pldz-dev-theme";
const DEFAULT_THEME = "light";

export const themes = [
  { id: "light", label: "浅色", swatch: "#4f72bf" },
  { id: "dark", label: "深色", swatch: "#9db5e4" },
];

const themeIds = new Set(themes.map((theme) => theme.id));
const legacyLightThemes = new Set(["gemini", "lime", "gpt", "brown", "claude"]);

export function normalizeTheme(theme) {
  if (themeIds.has(theme)) return theme;
  if (legacyLightThemes.has(theme)) return "light";
  return DEFAULT_THEME;
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
