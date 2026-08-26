const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000";

export async function searchStartupIdea(idea) {
  const response = await fetch(`${API_BASE_URL}/api/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      idea,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to search startup idea");
  }

  return data;
}