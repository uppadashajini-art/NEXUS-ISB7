const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "https://nexus-server-staging.onrender.com";

export async function searchStartupIdea(idea) {
  const trimmedIdea = idea.trim();

  // Frontend validation
  if (!trimmedIdea) {
    throw new Error("Please enter a startup idea.");
  }

  if (trimmedIdea.length < 3) {
    throw new Error(
      "Startup idea must contain at least 3 characters."
    );
  }

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/search`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          idea: trimmedIdea,
        }),
      }
    );

    let data;

    try {
      data = await response.json();
    } catch {
      throw new Error(
        "The backend returned an invalid response."
      );
    }

    if (!response.ok) {
      throw new Error(
        data.detail ||
          "Failed to validate startup idea."
      );
    }

    return data;
  } catch (error) {
    console.error("API request failed:", error);

    if (error instanceof TypeError) {
      throw new Error(
        "Unable to connect to the backend. Please check the server."
      );
    }

    throw error;
  }
}