import React, { createContext, useContext, useEffect, useState } from "react";

export type Theme =
  "light" | "dark" | "system" | "blue-light" | "crimson-dark" | "violet-dark";

const CUSTOM_DARK_THEMES: Theme[] = ["crimson-dark", "violet-dark"];
const CUSTOM_LIGHT_THEMES: Theme[] = ["blue-light"];
const THEME_CLASSES = [
  "theme-blue-light",
  "theme-crimson-dark",
  "theme-violet-dark",
];

interface ThemeContextValue {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextValue>({
  theme: "system",
  setTheme: () => {},
});

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(() => {
    return (localStorage.getItem("theme") as Theme) || "system";
  });

  useEffect(() => {
    const root = document.documentElement;
    const mq = window.matchMedia("(prefers-color-scheme: dark)");

    const applyTheme = (t: Theme) => {
      // Always clear previous theme classes first
      root.classList.remove("dark", ...THEME_CLASSES);

      if (CUSTOM_DARK_THEMES.includes(t)) {
        root.classList.add("dark", `theme-${t}`);
      } else if (CUSTOM_LIGHT_THEMES.includes(t)) {
        root.classList.add(`theme-${t}`);
      } else if (t === "dark") {
        root.classList.add("dark");
      } else if (t === "system") {
        if (mq.matches) root.classList.add("dark");
      }
      // 'light' → no class added
    };

    applyTheme(theme);

    const handler = () => {
      if (theme === "system") applyTheme("system");
    };
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, [theme]);

  const setTheme = (t: Theme) => {
    localStorage.setItem("theme", t);
    setThemeState(t);
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}
