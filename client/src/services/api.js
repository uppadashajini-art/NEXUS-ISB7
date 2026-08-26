const API_BASE_URL = "https://nexus-server-staging.onrender.com";

export async function searchStartupIdea(idea) {
  const response = await fetch(`${API_BASE_URL}/api/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      idea: idea,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Failed to validate startup idea."
    );
  }

  return data;
}