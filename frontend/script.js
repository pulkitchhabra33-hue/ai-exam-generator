// Handle custom dropdown logic
function handleCustom(selectId, inputId) {
  const select = document.getElementById(selectId);
  const input = document.getElementById(inputId);

  if (select.value === "custom") {
    input.style.display = "block";
  } else {
    input.style.display = "none";
  }
}

// Main function
async function generatePDF() {

  // Show loading
  document.getElementById("loading").style.display = "block";

  try {

    // Handle question counts (dropdown + custom)
    const qa = document.getElementById("questions_a").value === "custom"
      ? document.getElementById("custom_a").value
      : document.getElementById("questions_a").value;

    const qb = document.getElementById("questions_b").value === "custom"
      ? document.getElementById("custom_b").value
      : document.getElementById("questions_b").value;

    const qc = document.getElementById("questions_c").value === "custom"
      ? document.getElementById("custom_c").value
      : document.getElementById("questions_c").value;

    // Instructions + toggle
    const instructions = document.getElementById("instructions").value;
    const includeAnswers = document.getElementById("includeAnswers").checked;

    // Build request body
    const data = {
      class_name: document.getElementById("class").value,
      subject: document.getElementById("subject").value,
      topics: document.getElementById("topics").value,
      difficulty: document.getElementById("difficulty").value,

      total_marks: parseInt(document.getElementById("total").value) || 0,

      section_a: parseInt(document.getElementById("section_a").value) || 0,
      section_b: parseInt(document.getElementById("section_b").value) || 0,
      section_c: parseInt(document.getElementById("section_c").value) || 0,

      questions_a: parseInt(qa) || 1,
      questions_b: parseInt(qb) || 1,
      questions_c: parseInt(qc) || 1,

      instructions: instructions
    };

    // API call
    const res = await fetch(
      `http://127.0.0.1:8000/generate-pdf?include_answers=${includeAnswers}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
      }
    );

    const result = await res.json();

    // Hide loading
    document.getElementById("loading").style.display = "none";

    // Success case
    if (result.download_url) {
      const link = document.getElementById("downloadLink");
      link.href = "http://127.0.0.1:8000" + result.download_url;
      link.innerText = "📥 Download PDF";
    } 
    // Error case
    else {
      alert(result.error || "Something went wrong");
    }

  } catch (error) {

    // Hide loading on error
    document.getElementById("loading").style.display = "none";

    console.error("Error:", error);
    alert("Server error. Check backend.");
  }
}