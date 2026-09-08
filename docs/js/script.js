const API_BASE_URL =
    "https://ai-exam-generator-backend.onrender.com";

let isGenerating = false;
let sectionCount = 0;

const QUESTION_TYPES = [
    "MCQ",
    "Very Short Answer",
    "Short Answer",
    "Long Answer",
    "Case Study",
    "Assertion-Reason",
    "Application-based",
    "HOTS",
    "True/False",
    "Fill in the Blanks",
    "Match the Following",
    "One Word Answer",
    "Source-Based Questions",
    "Diagram-Based Questions"
];

function handleCustom(selectId, inputId) {

    const select = document.getElementById(selectId);
    const input = document.getElementById(inputId);

    if (!select || !input) {
        return;
    }

    if (select.value === "custom") {

        input.style.display = "block";

    } else {

        input.style.display = "none";
        input.value = "";

    }
}

function getGuestId() {
    let guestId = localStorage.getItem("guest_id");

    if (!guestId) {
        guestId = crypto.randomUUID();
        localStorage.setItem("guest_id", guestId);
    }

    return guestId;
}

function getQuestionTypeOptions() {
    return QUESTION_TYPES.map(
        type => `<option value="${type}">${type}</option>`
    ).join("");
}

function addSection() {
    sectionCount++;

    const container = document.getElementById("sectionsContainer");

    if (!container) {
        return;
    }

    const currentSections =
        document.querySelectorAll(".section").length;

    const letter = String.fromCharCode(65 + currentSections);

    const newSection = document.createElement("div");
    newSection.className = "section";
    newSection.id = `section-${sectionCount}`;

    newSection.innerHTML = `
        <div class="section-header">
            <h4 class="sectionTitle">Section ${letter}</h4>
            ${
                currentSections === 0
                    ? ""
                    : `
                        <button
                            type="button"
                            class="remove-section-btn"
                            onclick="removeSection(${sectionCount})"
                        >
                            ❌ Remove Section
                        </button>
                    `
            }
        </div>

        <div class="question-groups"></div>

        <button
            type="button"
            class="add-question-type-btn"
            onclick="addQuestionType(${sectionCount})"
        >
            ➕ Add Question Type
        </button>
    `;

    container.appendChild(newSection);
    addQuestionType(sectionCount);
}

function addQuestionType(sectionId) {
    const section = document.getElementById(`section-${sectionId}`);

    if (!section) {
        return;
    }

    const groupsContainer =
        section.querySelector(".question-groups");

    if (!groupsContainer) {
        return;
    }

    const group = document.createElement("div");
    group.className = "question-group";

    group.innerHTML = `
        <div class="question-group-header">
            <strong>Question Type</strong>

            <button
                type="button"
                class="remove-question-type-btn"
                onclick="removeQuestionType(this)"
            >
                ✖
            </button>
        </div>

        <div class="question-group-fields">
            <div class="input-group">
                <label>Question Type</label>

                <select class="questionType">
                    ${getQuestionTypeOptions()}
                </select>
            </div>

            <div class="input-group">
                <label>Number of Questions</label>

                <input
                    type="number"
                    class="questions"
                    min="1"
                    step="1"
                    placeholder="e.g. 5"
                >
            </div>

            <div class="input-group">
                <label>Marks / Question</label>

                <input
                    type="number"
                    class="marksPerQuestion"
                    min="1"
                    step="1"
                    placeholder="e.g. 1"
                >
            </div>
        </div>

        <div class="group-total">
            Total Marks:
            <strong class="groupTotalMarks">0</strong>
        </div>
    `;

    groupsContainer.appendChild(group);

    const questionsInput =
        group.querySelector(".questions");

    const marksInput =
        group.querySelector(".marksPerQuestion");

    function updateGroupMarks() {
        const questions =
            parseInt(questionsInput.value, 10) || 0;

        const marksPerQuestion =
            parseInt(marksInput.value, 10) || 0;

        group.querySelector(".groupTotalMarks").innerText =
            questions * marksPerQuestion;
    }

    questionsInput.addEventListener(
        "input",
        updateGroupMarks
    );

    marksInput.addEventListener(
        "input",
        updateGroupMarks
    );
}

function removeQuestionType(button) {
    const group =
        button.closest(".question-group");

    if (!group) {
        return;
    }

    const section =
        group.closest(".section");

    if (!section) {
        return;
    }

    const groups =
        section.querySelectorAll(".question-group");

    if (groups.length <= 1) {
        alert(
            "Each section must contain at least one question type."
        );
        return;
    }

    group.remove();
}

function removeSection(id) {
    const section =
        document.getElementById(`section-${id}`);

    if (!section) {
        return;
    }

    section.remove();
    refreshSectionNames();
}

function refreshSectionNames() {
    const sections =
        document.querySelectorAll(".section");

    sections.forEach((section, index) => {
        const title =
            section.querySelector(".sectionTitle");

        if (title) {
            title.innerText =
                `Section ${String.fromCharCode(65 + index)}`;
        }
    });
}

function validateSections(sections, totalMarks) {
    if (!sections.length) {
        alert("Please add at least one section.");
        return false;
    }

    let calculatedTotal = 0;

    for (const section of sections) {
        if (!section.question_groups.length) {
            alert(
                `${section.section_name} must contain at least one question type.`
            );
            return false;
        }

        let sectionMarks = 0;
        let sectionQuestions = 0;
        const types = new Set();

        for (const group of section.question_groups) {
            if (types.has(group.question_type)) {
                alert(
                    `${section.section_name} contains the question type "${group.question_type}" more than once.`
                );
                return false;
            }

            types.add(group.question_type);

            if (
                !Number.isInteger(group.question_count) ||
                group.question_count <= 0
            ) {
                alert(
                    `Enter a valid number of questions for ${group.question_type} in ${section.section_name}.`
                );
                return false;
            }

            if (
                !Number.isInteger(group.marks_per_question) ||
                group.marks_per_question <= 0
            ) {
                alert(
                    `Enter valid marks per question for ${group.question_type} in ${section.section_name}.`
                );
                return false;
            }

            group.marks =
                group.question_count *
                group.marks_per_question;

            sectionMarks += group.marks;
            sectionQuestions += group.question_count;
        }

        section.marks = sectionMarks;
        section.question_count = sectionQuestions;
        calculatedTotal += sectionMarks;
    }

    if (
        !Number.isInteger(totalMarks) ||
        totalMarks <= 0
    ) {
        alert("Please enter valid total marks.");
        return false;
    }

    if (calculatedTotal !== totalMarks) {
        alert(
            `Total marks are ${totalMarks}, but your sections add up to ${calculatedTotal}.`
        );
        return false;
    }

    return true;
}

async function generatePDF() {
    if (isGenerating) {
        return;
    }

    isGenerating = true;

    const loading =
        document.getElementById("loading");

    const downloadLink =
        document.getElementById("downloadLink");

    if (loading) {
        loading.style.display = "block";
    }

    if (downloadLink) {
        downloadLink.innerText = "";
        downloadLink.removeAttribute("href");
    }

    try {
        const sections = [];

        document
            .querySelectorAll(".section")
            .forEach((section, sectionIndex) => {
                const sectionNameElement =
                    section.querySelector(".sectionTitle");

                const sectionName =
                    sectionNameElement
                        ? sectionNameElement.innerText.trim()
                        : `Section ${String.fromCharCode(65 + sectionIndex)}`;

                const questionGroups = [];

                section
                    .querySelectorAll(".question-group")
                    .forEach(group => {
                        const type =
                            group.querySelector(".questionType").value;

                        const questions =
                            parseInt(
                                group.querySelector(".questions").value,
                                10
                            ) || 0;

                        const marksPerQuestion =
                            parseInt(
                                group.querySelector(".marksPerQuestion").value,
                                10
                            ) || 0;

                        if (
                            questions <= 0 ||
                            marksPerQuestion <= 0
                        ) {
                            return;
                        }

                        questionGroups.push({
                            question_type: type,
                            question_count: questions,
                            marks_per_question: marksPerQuestion,
                            marks: questions * marksPerQuestion
                        });
                    });

                if (!questionGroups.length) {
                    return;
                }

                const sectionMarks =
                    questionGroups.reduce(
                        (total, group) =>
                            total + group.marks,
                        0
                    );

                const sectionQuestions =
                    questionGroups.reduce(
                        (total, group) =>
                            total + group.question_count,
                        0
                    );

                sections.push({
                    section_name: sectionName,
                    marks: sectionMarks,
                    question_count: sectionQuestions,
                    question_groups: questionGroups
                });
            });

        const totalMarks =
            parseInt(
                document.getElementById("total").value,
                10
            ) || 0;

        if (!validateSections(sections, totalMarks)) {
            return;
        }

        const selectedTime =
            document.getElementById("time_limit").value;

        const customTime =
            document.getElementById("custom_time");

        if (
            selectedTime === "custom" &&
            (!customTime || !customTime.value.trim())
        ) {
            alert("Please enter a custom time limit.");
            return;
        }

        const timeLimit =
            selectedTime === "custom" && customTime
                ? customTime.value.trim()
                : selectedTime;

        const includeAnswersElement =
            document.getElementById("includeAnswers");

        const includeAnswers =
            includeAnswersElement
                ? includeAnswersElement.checked
                : true;

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
                totalMarks,

            sections:
                sections,

            instructions:
                document.getElementById("instructions").value
        };

        const formData = new FormData();

        formData.append(
            "data",
            JSON.stringify(data)
        );

        formData.append(
            "include_answers",
            includeAnswers
        );

        const files =
            document.getElementById("pyq_files").files;

        for (let i = 0; i < files.length; i++) {
            formData.append(
                "files",
                files[i]
            );
        }

        const token =
            localStorage.getItem("access_token");

        const headers = {};

        if (token) {
            headers.Authorization =
                `Bearer ${token}`;
        } else {
            headers["X-Guest-ID"] =
                getGuestId();
        }

        const controller =
            new AbortController();

        const timeoutId =
            setTimeout(() => {
                controller.abort();
            }, 150000);

        let res;

        try {
            res = await fetch(
                `${API_BASE_URL}/generate-paper`,
                {
                    method: "POST",
                    headers: headers,
                    body: formData,
                    signal: controller.signal
                }
            );
        } finally {
            clearTimeout(timeoutId);
        }

        let result;

        try {
            result = await res.json();
        } catch {
            result = {};
        }

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

        if (
            res.status === 403 &&
            result.detail === "NO_CREDITS"
        ) {
            showNoCreditsMessage();
            return;
        }

        if (!res.ok) {
            const message =
                result.detail ||
                result.message ||
                result.error ||
                "Paper generation failed. Please try again.";

            alert(message);
            return;
        }

        if (result.download_url) {
            const link =
                document.getElementById("downloadLink");

            if (link) {
                link.href =
                    API_BASE_URL +
                    result.download_url;

                link.innerText =
                    "📥 Download PDF";

                link.target = "_blank";
            }

            if (token) {
                loadUserInfo();
            } else {
                loadGuestCredits();
            }
        } else {
            alert(
                "Paper generation failed. Please try again."
            );
        }
    } catch (error) {
        console.error(
            "Generation Error:",
            error
        );

        if (error.name === "AbortError") {
            alert(
                "Exam generation took too long. Please try again."
            );
        } else {
            alert(
                "Server error. Check the browser console and backend logs."
            );
        }
    } finally {
        if (loading) {
            loading.style.display = "none";
        }

        isGenerating = false;
    }
}

async function loadUserInfo() {
    const token =
        localStorage.getItem("access_token");

    if (!token) {
        return;
    }

    try {
        const response =
            await fetch(
                `${API_BASE_URL}/current-user`,
                {
                    headers: {
                        Authorization:
                            `Bearer ${token}`
                    }
                }
            );

        if (!response.ok) {
            localStorage.removeItem("access_token");
            return;
        }

        const user =
            await response.json();

        const loginButton =
            document.getElementById("loginBtn");

        const signupButton =
            document.getElementById("signupBtn");

        if (loginButton) {
            loginButton.style.display = "none";
        }

        if (signupButton) {
            signupButton.style.display = "none";
        }

        const userDisplay =
            document.getElementById("userDisplay");

        if (userDisplay) {
            userDisplay.textContent =
                `👤 ${user.name}`;
        }

        const creditsElement =
            document.getElementById("guestCredits");

        if (creditsElement && user.credits_remaining !== undefined) {
            creditsElement.innerText =
                `Credits: ${user.credits_remaining}`;
        }
    } catch (error) {
        console.error(
            "Failed to load user:",
            error
        );
    }
}

async function loadGuestCredits() {
    const guestId =
        localStorage.getItem("guest_id");

    const creditsElement =
        document.getElementById("guestCredits");

    if (!creditsElement) {
        return;
    }

    if (!guestId) {
        creditsElement.innerText =
            "Free Credits: 2";
        return;
    }

    try {
        const response =
            await fetch(
                `${API_BASE_URL}/guest-credits`,
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
            `Free Credits: ${data.credits}`;
    } catch (error) {
        console.error(
            "Failed to load guest credits:",
            error
        );

        creditsElement.innerText =
            "Unable to load credits.";
    }
}

function showNoCreditsMessage() {
    const existing =
        document.getElementById("noCreditsBox");

    if (existing) {
        existing.style.display = "block";
        return;
    }

    const box =
        document.createElement("div");

    box.id = "noCreditsBox";

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
                    <h3>PRO</h3>

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
                    <h3>PREMIUM</h3>

                    <p>
                        ₹399 / 6 months
                    </p>

                    <p>
                        500 credits
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

    const formCard =
        document.querySelector(".form-card");

    if (formCard) {
        formCard.appendChild(box);
    }
}

function buyPlan(plan) {
    localStorage.setItem(
        "selected_plan",
        plan
    );

    const token =
        localStorage.getItem("access_token");

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

function openMyPapers() {
    window.location.href =
        "mypapers.html";
}

document.addEventListener(
    "DOMContentLoaded",
    () => {
        if (
            document.getElementById("sectionsContainer") &&
            document.querySelectorAll(".section").length === 0
        ) {
            addSection();
        }

        loadUserInfo();
        loadGuestCredits();
    }
);