// Backend URL
const BASE_URL =
  "https://ai-exam-generator-backend.onrender.com";

let isgenerating= false;

function getGuestId() {

  let guestId =
    localStorage.getItem(
      "guest_id"
    );

  if (!guestId) {

    guestId =
      crypto.randomUUID();

    localStorage.setItem(
      "guest_id",
      guestId
    );

  }

  return guestId;

}

let sectionCount = 0;


// Handle custom dropdown logic
function handleCustom(selectId, inputId) {

  const select =
    document.getElementById(selectId);

  const input =
    document.getElementById(inputId);

  if (select.value === "custom") {

    input.style.display = "block";

  } else {

    input.style.display = "none";

  }

}

let isGenerating = false;

// GENERATE PDF
async function generatePDF() {

  if (isGenerating) {
        return;
    }

    isGenerating = true;

  document.getElementById(
    "loading"
  ).style.display = "block";

  document.getElementById(
    "downloadLink"
  ).innerText = "";

  try {

    const sections = [];

    document
      .querySelectorAll(".section")
      .forEach(section => {

        const marks =
          section.querySelector(
            ".marks"
          ).value;

        const questions =
          section.querySelector(
            ".questions"
          ).value;

        const type =
          section.querySelector(
            ".questionType"
          ).value;

        if (marks && questions) {

          const marksValue =
            parseInt(marks);

          const questionCountValue =
            parseInt(questions);

          sections.push({

            section_name:
              section.querySelector(
                ".sectionTitle"
              ).innerText,

            marks:
              marksValue,

            question_count:
              questionCountValue,

            marks_per_question:
              marksValue /
              questionCountValue,

            question_type:
              type

          });

        }

      });


    const totalMarks =
      parseInt(
        document.getElementById(
          "total"
        ).value
      ) || 0;


    const sectionTotal =
      sections.reduce(
        (sum, section) =>
          sum + section.marks,
        0
      );


    if (totalMarks !== sectionTotal) {

      alert(
        `Total marks are ${totalMarks}, but your sections add up to ${sectionTotal}.`
      );

      return;

    }


    const selectedTime =
      document.getElementById(
        "time_limit"
      ).value;


    const timeLimit =
      selectedTime === "custom"
        ? document.getElementById(
            "custom_time"
          ).value
        : selectedTime;


    console.log(
      "SELECTED TIME:",
      selectedTime
    );


    console.log(
      "TIME LIMIT SENT:",
      timeLimit
    );


    const includeAnswers =
      document.getElementById(
        "includeAnswers"
      ).checked;


    const data = {

      exam_type:
        document.getElementById(
          "exam_type"
        ).value,

      school_name:
        document.getElementById(
          "school_name"
        ).value,

      exam_name:
        document.getElementById(
          "exam_name"
        ).value,

      time_limit:
        timeLimit,

      class_name:
        document.getElementById(
          "class"
        ).value,

      subject:
        document.getElementById(
          "subject"
        ).value,

      topics:
        document.getElementById(
          "topics"
        ).value,

      difficulty:
        document.getElementById(
          "difficulty"
        ).value,

      total_marks:
        parseInt(
          document.getElementById(
            "total"
          ).value
        ) || 0,

      sections:
        sections,

      instructions:
        document.getElementById(
          "instructions"
        ).value

    };


    const formData =
      new FormData();


    formData.append(
      "data",
      JSON.stringify(data)
    );


    const files =
      document.getElementById(
        "pyq_files"
      ).files;


    for (
      let i = 0;
      i < files.length;
      i++
    ) {

      formData.append(
        "files",
        files[i]
      );

    }


    /*
     * Authentication / Guest Identity
     */

    const token =
      localStorage.getItem(
        "access_token"
      );


    const headers = {};


    if (token) {

      headers.Authorization =
        `Bearer ${token}`;

    } else {

      headers["X-Guest-ID"] =
        getGuestId();

    }


    /*
     * Generate Exam Paper
     */

    const controller =
      new AbortController();


    const timeoutId =
      setTimeout(() => {

        controller.abort();

      }, 150000);


    const res =
      await fetch(
        `${BASE_URL}/generate-paper?include_answers=${includeAnswers}`,
        {
          method: "POST",

          headers:
            headers,

          body:
            formData,

          signal:
            controller.signal

        }
      );


    const result =
      await res.json();


    clearTimeout(timeoutId);


    if (
      res.status === 401 &&
      result.detail === "AUTHENTICATION_REQUIRED"
    ) {

      localStorage.removeItem("access_token");

      alert(
        "Your session has expired. Please log in again to continue."
      );

      window.location.href = "login.html";

      return;
    }

    /*
     * No guest credits
     */

    if (
      res.status === 403 &&
      result.detail === "NO_CREDITS"
    ) {

      showNoCreditsMessage();

      return;

    }


    /*
     * Successful generation
     */

    if (
      result.download_url
    ) {

      const link =
        document.getElementById(
          "downloadLink"
        );


      link.href =
        BASE_URL +
        result.download_url;


      link.innerText =
        "📥 Download PDF";


      /*
       * Refresh guest credits
       */

      if (!token) {

        loadGuestCredits();

      }

    } else {

      alert(
        "Paper generation failed. Please try again."
      );

    }

  }

  catch (error) {

    console.error(
      "Generation Error:",
      error
    );


    if (
      error.name === "AbortError"
    ) {

      alert(
        "Exam generation took too long. Please try again."
      );

    } else {

      alert(
        "Server error. Check the browser console and backend logs."
      );

    }

  }

  finally {
    document.getElementById(
      "loading"
    ).style.display = "none";

    isGenerating= false;
  }

}


async function loadUserInfo() {

  const token =
    localStorage.getItem(
      "access_token"
    );

  if (!token) {

    return;

  }

  try {

    const response =
      await fetch(
        BASE_URL +
        "/current-user",
        {
          headers: {
            Authorization:
              `Bearer ${token}`
          }
        }
      );


    if (!response.ok) {

      localStorage.removeItem(
        "access_token"
      );

      return;

    }


    const user =
      await response.json();


    const loginButton =
      document.getElementById(
        "loginBtn"
      );


    const signupButton =
      document.getElementById(
        "signupBtn"
      );


    if (loginButton) {

      loginButton.style.display =
        "none";

    }


    if (signupButton) {

      signupButton.style.display =
        "none";

    }


    const userDisplay =
      document.getElementById(
        "userDisplay"
      );


    if (userDisplay) {

      userDisplay.textContent =
        `👤 ${user.name}`;

    }

  }

  catch (error) {

    console.error(
      "Failed to load user:",
      error
    );

  }

}


async function upgradePro() {

  const token =
    localStorage.getItem(
      "access_token"
    );


  const res =
    await fetch(
      `${BASE_URL}/upgrade-plan`,
      {
        method: "POST",

        headers: {

          "Content-Type":
            "application/json",

          "Authorization":
            `Bearer ${token}`

        },

        body:
          JSON.stringify({
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
    localStorage.getItem(
      "access_token"
    );


  const res =
    await fetch(
      `${BASE_URL}/upgrade-plan`,
      {
        method: "POST",

        headers: {

          "Content-Type":
            "application/json",

          "Authorization":
            `Bearer ${token}`

        },

        body:
          JSON.stringify({
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
      "access_token"
    );


  const res =
    await fetch(
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


  container.innerHTML =
    "";


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


async function loadGuestCredits() {

  const guestId =
    localStorage.getItem(
      "guest_id"
    );


  const creditsElement =
    document.getElementById(
      "guestCredits"
    );


  if (!creditsElement) return;


  if (!guestId) {

    creditsElement.innerText =
      "Free Credits: 2";

    return;

  }


  try {

    const response =
      await fetch(
        `${BASE_URL}/guest-credits`,
        {

          headers: {

            "X-Guest-ID":
              guestId

          }

        }
      );


    const data =
      await response.json();


    creditsElement.innerText =
      `Free Credits: ${
        data.credits
      }`;

  }

  catch (error) {

    console.error(
      "Failed to load guest credits:",
      error
    );


    creditsElement.innerText =
      "Unable to load credits.";

  }

}


window.onload = () => {

  loadUserInfo();

  loadGuestCredits();

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
    document.createElement(
      "div"
    );


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

      <option>
        Very Short Answer
      </option>

      <option>
        Short Answer
      </option>

      <option>
        Long Answer
      </option>

      <option>
        Case Study
      </option>

      <option>
        Assertion-Reason
      </option>

      <option>
        Application-based
      </option>

      <option>
        HOTS
      </option>

      <option>
        True/False
      </option>

      <option>
        Fill in the Blanks
      </option>

      <option>
        Match the Following
      </option>

      <option>
        One Word Answer
      </option>

      <option>
        Source-Based Questions
      </option>

      <option>
        Diagram-Based Questions
      </option>

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


function showNoCreditsMessage() {

  const existing =
    document.getElementById(
      "noCreditsBox"
    );


  if (existing) {

    existing.style.display =
      "block";

    return;

  }


  const box =
    document.createElement(
      "div"
    );


  box.id =
    "noCreditsBox";


  box.innerHTML = `

    <div class="no-credits-content">

      <h2>
        You've used all your free credits
      </h2>

      <p>
        You have 0 credits remaining.
      </p>

      <p>
        Choose a plan below to continue
        generating exam papers.
      </p>

      <div class="plan-options">

        <div class="plan-option">

          <h3>
            PRO
          </h3>

          <p>
            ₹99 / month
          </p>

          <p>
            75 credits
          </p>

          <button
            type="button"
            onclick="buyPlan('PRO')"
          >
            Buy PRO
          </button>

        </div>


        <div class="plan-option">

          <h3>
            PREMIUM
          </h3>

          <p>
            ₹399 / 6 months
          </p>

          <p>
            600 credits
          </p>

          <button
            type="button"
            onclick="buyPlan('PREMIUM')"
          >
            Buy PREMIUM
          </button>

        </div>

      </div>

    </div>

  `;


  document
    .querySelector(".form-card")
    .appendChild(box);

}


function buyPlan(plan) {

  localStorage.setItem(
    "selected_plan",
    plan
  );


  const token =
    localStorage.getItem(
      "access_token"
    );


  if (token) {

    window.location.href =
      "pricing.html";

    return;

  }


  alert(
    `Please login or create an account to purchase the ${plan} plan.`
  );

  localStorage.setItem(
    "auth_redirect",
    "pricing.html"
  );

  window.location.href =
    "login.html";

}