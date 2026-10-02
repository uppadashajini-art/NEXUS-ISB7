import React, { useState, useEffect } from "react";
import { AuthProvider } from "./context/AuthContext";
import StartupValidator from "./pages/StartupValidator";
import Styleguide from "./pages/Styleguide";
import "./styles/tokens.css";
import "./styles/primitives.css";
import "./styles/shell.css";
import "./styles/studio.css";
import "./styles/suite.css";
import "./styles/results.css";
import "./styles/activity-log.css";
import "./styles/advisory.css";
import "./styles/compliance.css";
import "./App.css";
import "./components/LegendaryUI.css";

function App() {
  const [currentPath, setCurrentPath] = useState(
    window.location.pathname === "/styleguide" ||
    window.location.hash === "#styleguide"
      ? "/styleguide"
      : "/"
  );

  // =========================================================
  // LIGHT / DARK THEME
  // =========================================================

  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("nexus-theme") || "dark";
  });

  useEffect(() => {
    // Apply theme to the HTML element
    document.documentElement.setAttribute("data-theme", theme);

    // Remember user's theme choice
    localStorage.setItem("nexus-theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((currentTheme) =>
      currentTheme === "dark" ? "light" : "dark"
    );
  };

  // =========================================================
  // ROUTING
  // =========================================================

  useEffect(() => {
    const handleLocationChange = () => {
      if (
        window.location.pathname === "/styleguide" ||
        window.location.hash === "#styleguide"
      ) {
        setCurrentPath("/styleguide");
      } else {
        setCurrentPath("/");
      }
    };

    window.addEventListener("popstate", handleLocationChange);
    window.addEventListener("hashchange", handleLocationChange);

    return () => {
      window.removeEventListener("popstate", handleLocationChange);
      window.removeEventListener("hashchange", handleLocationChange);
    };
  }, []);

  const navigateTo = (path) => {
    window.history.pushState({}, "", path);
    setCurrentPath(path);
  };

  // =========================================================
  // STYLEGUIDE
  // =========================================================

  if (currentPath === "/styleguide") {
    return (
      <Styleguide
        onNavigateToApp={() => navigateTo("/")}
      />
    );
  }

  // =========================================================
  // MAIN NEXUS APPLICATION
  // =========================================================

  return (
    <AuthProvider>
      <StartupValidator
        onNavigateToStyleguide={() => navigateTo("/styleguide")}
        theme={theme}
        onToggleTheme={toggleTheme}
      />
    </AuthProvider>
  );
}

export default App;