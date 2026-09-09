
const API_BASE_URL = "https://nexus-server-staging.onrender.com";

export async function validateIdea(idea, domain, targetCustomer) {
  const response = await fetch(`${API_BASE_URL}/api/validate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      idea,
      domain: domain || undefined,
      target_customer: targetCustomer || undefined,
    }),
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    const message = errorBody.detail || `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return response.json();
}