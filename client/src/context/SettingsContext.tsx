import React, { createContext, useContext, useState } from "react";

interface UISettings {
  compactMode: boolean;
  setCompactMode: (v: boolean) => void;
}

const SettingsContext = createContext<UISettings>({
  compactMode: false,
  setCompactMode: () => {},
});

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const [compactMode, setCompactModeState] = useState<boolean>(() => {
    return localStorage.getItem("compactMode") === "true";
  });

  const setCompactMode = (v: boolean) => {
    localStorage.setItem("compactMode", String(v));
    setCompactModeState(v);
  };

  return (
    <SettingsContext.Provider value={{ compactMode, setCompactMode }}>
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings() {
  return useContext(SettingsContext);
}
