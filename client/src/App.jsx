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
    window.location.pathname === "/styleguide" || window.location.hash === "#styleguide"
      ? "/styleguide"
      : "/"
  );

  useEffect(() => {
    const handleLocationChange = () => {
      if (window.location.pathname === "/styleguide" || window.location.hash === "#styleguide") {
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

  if (currentPath === "/styleguide") {
    return <Styleguide onNavigateToApp={() => navigateTo("/")} />;
  }

  return (
    <AuthProvider>
      <StartupValidator onNavigateToStyleguide={() => navigateTo("/styleguide")} />
    </AuthProvider>
  );
}

export default App;