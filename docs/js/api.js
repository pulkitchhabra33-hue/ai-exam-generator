const API_BASE_URL = "https://ai-exam-generator-backend.onrender.com";

async function apiRequest(endpoint, options = {}) {
    const response = await fetch(API_BASE_URL + endpoint, options);

    if (!response.ok) {
        let message = "Something went wrong. Please try again.";

        try {
            const errorData = await response.json();
            message = errorData.detail || message;
        } catch {
            // Keep the fallback message if the response isn't JSON.
        }

        throw new Error(message);
    }

    return response.json();
}