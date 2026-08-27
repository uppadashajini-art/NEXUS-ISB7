const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "https://nexus-server-staging.onrender.com";

export async function searchStartupIdea(
  idea,
  targetCustomer = ""
) {
  const trimmedIdea = idea?.trim() || "";
  const trimmedTargetCustomer =
    targetCustomer?.trim() || "";

  // =========================================
  // STARTUP IDEA VALIDATION
  // =========================================

  if (!trimmedIdea) {
    throw new Error(
      "Please enter your startup idea."
    );
  }

  if (trimmedIdea.length < 3) {
    throw new Error(
      "Startup idea must contain at least 3 characters."
    );
  }

  // =========================================
  // API REQUEST
  // =========================================

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

          // Optional field
          target_customer:
            trimmedTargetCustomer,
        }),
      }
    );

    // =========================================
    // RESPONSE
    // =========================================

    let data;

    try {
      data = await response.json();
    } catch {
      throw new Error(
        "The backend returned an invalid response."
      );
    }

    // =========================================
    // ERROR
    // =========================================

    if (!response.ok) {
      throw new Error(
        data?.detail ||
          data?.message ||
          "Failed to validate startup idea."
      );
    }

    return data;

  } catch (error) {

    console.error(
      "API request failed:",
      error
    );

    if (error instanceof TypeError) {
      throw new Error(
        "Unable to connect to the backend. Please check the server."
      );
    }

    throw error;
  }
}