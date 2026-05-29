// Backend URL
const BASE_URL = "https://ai-exam-generator-backend.onrender.com";


// SIGNUP
async function signup() {

  const email =
    document.getElementById("email").value;

  const password =
    document.getElementById("password").value;

  const res = await fetch(
    `${BASE_URL}/signup`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({
        email,
        password
      })

    }
  );

  const result = await res.json();

  alert(
    result.message || result.detail
  );

}


// LOGIN
async function login() {

  const email =
    document.getElementById("email").value;

  const password =
    document.getElementById("password").value;

  const res = await fetch(
    `${BASE_URL}/login`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({
        email,
        password
      })

    }
  );

  const result = await res.json();

  if (result.access_token) {

    localStorage.setItem(
      "token",
      result.access_token
    );

    alert("Login successful");

  }

  else {

    alert(
      result.detail || "Login failed"
    );

  }

}


// Handle custom dropdown logic
function handleCustom(selectId, inputId) {

  const select =
    document.getElementById(selectId);

  const input =
    document.getElementById(inputId);

  if (select.value === "custom") {

    input.style.display = "block";

  }

  else {

    input.style.display = "none";

  }

}


// GENERATE PDF
async function generatePDF() {

  document.getElementById("loading").style.display =
    "block";

  document.getElementById("downloadLink").innerText =
    "";

  try {

    const qa =
      document.getElementById("questions_a").value === "custom"
        ? document.getElementById("custom_a").value
        : document.getElementById("questions_a").value;


    const qb =
      document.getElementById("questions_b").value === "custom"
        ? document.getElementById("custom_b").value
        : document.getElementById("questions_b").value;


    const qc =
      document.getElementById("questions_c").value === "custom"
        ? document.getElementById("custom_c").value
        : document.getElementById("questions_c").value;


    const selectedTime =
      document.getElementById("time_limit").value;


    const timeLimit =
      selectedTime === "custom"
        ? document.getElementById("custom_time").value
        : selectedTime;


    const includeAnswers =
      document.getElementById("includeAnswers").checked;


    const data = {

      exam_type:
        document.getElementById("exam_type").value,

      school_name:
        document.getElementById("school_name").value,

      exam_name:
        document.getElementById("exam_name").value,

      time_limit:
        timeLimit,

      class_name:
        document.getElementById("class").value,

      subject:
        document.getElementById("subject").value,

      topics:
        document.getElementById("topics").value,

      difficulty:
        document.getElementById("difficulty").value,


      total_marks:
        parseInt(document.getElementById("total").value) || 0,


      section_a:
        parseInt(document.getElementById("section_a").value) || 0,

      section_b:
        parseInt(document.getElementById("section_b").value) || 0,

      section_c:
        parseInt(document.getElementById("section_c").value) || 0,


      type_a:
        document.getElementById("type_a").value,

      type_b:
        document.getElementById("type_b").value,

      type_c:
        document.getElementById("type_c").value,


      questions_a:
        parseInt(qa) || 1,

      questions_b:
        parseInt(qb) || 1,

      questions_c:
        parseInt(qc) || 1,


      instructions:
        document.getElementById("instructions").value

    };


    const formData = new FormData();


    formData.append(
      "data",
      JSON.stringify(data)
    );


    const files =
      document.getElementById("pyq_files").files;


    for (let i = 0; i < files.length; i++) {

      formData.append(
        "files",
        files[i]
      );

    }


    // 🔥 JWT TOKEN ADDED HERE
    const token =
      localStorage.getItem("token");


    const res = await fetch(
      `${BASE_URL}/generate-paper?include_answers=${includeAnswers}`,
      {
        method: "POST",

        headers: {
          "Authorization": `Bearer ${token}`
        },

        body: formData

      }
    );


    const result =
      await res.json();


    if (result.download_url) {

      const link =
        document.getElementById("downloadLink");


      link.href =
        BASE_URL + result.download_url;


      link.innerText =
        "📥 Download PDF";

    }

    else {

      alert(
        result.error || "Something went wrong"
      );

    }

  }


  catch (error) {

    console.error(
      "Error:",
      error
    );


    alert(
      "Server error. Check backend."
    );

  }


  finally {

    document.getElementById("loading").style.display =
      "none";

  }

}