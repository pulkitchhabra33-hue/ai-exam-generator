// Backend URL
const BASE_URL = "https://ai-exam-generator-backend.onrender.com";

let sectionCount = 0;


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

    const sections = [];

    document
    .querySelectorAll(".section")
    .forEach(section => {

    const marks =
      section.querySelector(".marks").value;

    const questions =
      section.querySelector(".questions").value;

    const type =
      section.querySelector(".questionType").value;

    if (marks && questions) {

      sections.push({

        marks: parseInt(marks),

        questions: parseInt(questions),

        type: type

      });

    }

  });


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

      sections: sections,

      instructions:
        document.getElementById("instructions").value,

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
        result.detail ||
        result.error || 
        "Something went wrong"
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

async function loadUserInfo() {

  const token =
    localStorage.getItem("token");

  if (!token) return;

  const res = await fetch(
    `${BASE_URL}/current-user`,
    {

      headers: {
        Authorization:
          `Bearer ${token}`
      }

    }
  );

  const data =
    await res.json();

  document.getElementById(
    "userPlan"
  ).innerText =
    `Plan: ${data.plan}`;

  document.getElementById(
    "userCredits"
  ).innerText =
    `Credits: ${data.credits}`;

  document.getElementById(
    "userStatus"
).innerText =
  `Status: ${data.status}`;

  document.getElementById(
    "userExpiry"
).innerText =
  `Expires: ${
    data.subscription_end || "N/A"
  }`;

}

async function upgradePro() {

  const token =
    localStorage.getItem("token");

  const res = await fetch(
    `${BASE_URL}/upgrade-plan`,
    {

      method: "POST",

      headers: {

        "Content-Type":
          "application/json",

        "Authorization":
          `Bearer ${token}`

      },

      body: JSON.stringify({

        plan: "PRO"

      })

    }
  );

  const result =
    await res.json();

  alert(
    result.message
  );

  loadUserInfo();

}


async function upgradePremium() {

  const token =
    localStorage.getItem("token");

  const res = await fetch(
    `${BASE_URL}/upgrade-plan`,
    {

      method: "POST",

      headers: {

        "Content-Type":
          "application/json",

        "Authorization":
          `Bearer ${token}`

      },

      body: JSON.stringify({

        plan: "PREMIUM"

      })

    }
  );

  const result =
    await res.json();

  alert(
    result.message
  );

  loadUserInfo();

}

async function loadPaperHistory() {

  const token =
    localStorage.getItem(
      "token"
    );

  const res = await fetch(

    `${BASE_URL}/my-papers`,

    {

      headers: {

        Authorization:
          `Bearer ${token}`

      }

    }

  );

  const papers =
    await res.json();

  const container =
    document.getElementById(
      "paperHistory"
    );

  container.innerHTML = "";

  papers.forEach(
    paper => {

      container.innerHTML += `

      <div>

        <b>
        ${paper.exam_name}
        </b>

        -
        ${paper.subject}

        -
        ${paper.exam_type}

      </div>

      `;

    }
  );

}

window.onload = () => {

  loadUserInfo();

};

function openMyPapers() {

  window.location.href =
    "mypapers.html";

}

function addSection() {

  sectionCount++;

  const container =
    document.getElementById(
      "sectionsContainer"
    );

  const currentSections =
    document.querySelectorAll(
      ".section"
    ).length;
  
  const letter =
    String.fromCharCode(
      65 + currentSections
    );

  const removeButton =
    sectionCount === 1
      ? ""
      : `
      <button
        type="button"
        onclick="removeSection(${sectionCount})"
      >
        ❌ Remove Section
      </button>
      `;

  const newSection =
    document.createElement("div");

  newSection.className =
    "section";

  newSection.id =
    `section-${sectionCount}`;

  newSection.innerHTML = `

    <h4 class="sectionTitle">
      Section ${letter}
    </h4>

    ${removeButton}

    <input
      class="marks"
      placeholder="Marks"
    >

    <input
      class="questions"
      placeholder="Questions"
    >

    <select
      class="questionType"
    >

      <option>MCQ</option>
      <option>Very Short Answer</option>
      <option>Short Answer</option>
      <option>Long Answer</option>
      <option>Case Study</option>
      <option>Assertion-Reason</option>
      <option>Application-based</option>
      <option>HOTS</option>
      <option>True/False</option>
      <option>Fill in the Blanks</option>
      <option>Match the Following</option>
      <option>One Word Answer</option>
      <option>Source-Based Questions</option>
      <option>Diagram-Based Questions</option>

    </select>

  `;

  container.appendChild(
    newSection
  );
}

function removeSection(id) {

  const section =
    document.getElementById(
      `section-${id}`
    );

  section.remove();

  refreshSectionNames();

}

function refreshSectionNames() {

  const sections =
    document.querySelectorAll(
      ".section"
    );

  sections.forEach(
    (section, index) => {

      const title =
        section.querySelector(
          ".sectionTitle"
        );

      title.innerText =
        `Section ${
          String.fromCharCode(
            65 + index
          )
        }`;

    }
  );

}

addSection();