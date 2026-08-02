const API_BASE_URL = "https://ai-exam-generator-backend.onrender.com";

async function apiRequest(
    endpoint,
    options = {}
) {
    const response = await fetch(

        API_BASE_URL + endpoint,

        options

    );

    if (!response.ok) {

        throw new Error(

            await response.text()

        );

    }

    return response.json();
}