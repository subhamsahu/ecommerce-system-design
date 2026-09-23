import { Provider } from "react-redux";
import { store } from "@/store";
import AppRouter from "@/routes";
import ErrorBoundary from "@/components/ErrorBoundary";
import { ThemeProvider } from "@/context/ThemeContext";
import { SettingsProvider } from "@/context/SettingsContext";

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <SettingsProvider>
          <Provider store={store}>
            <AppRouter />
          </Provider>
        </SettingsProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
