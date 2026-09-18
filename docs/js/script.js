const API_BASE_URL = "https://ai-exam-generator-backend.onrender.com";

let isGenerating = false;
let generationTimer = null;
let generationStartedAt = null;

function getGuestId() {
    let guestId = localStorage.getItem("guest_id");

    if (!guestId) {
        guestId =
            "guest_" +
            crypto.randomUUID();

        localStorage.setItem(
            "guest_id",
            guestId
        );
    }

    return guestId;
}

function setGenerationUI(active) {
    const loading =
        document.getElementById("loading");

    const generateBtn =
        document.getElementById("generateBtn");

    const myPapersBtn =
        document.getElementById("myPapersBtn");

    const generationElapsed =
        document.getElementById("generationElapsed");

    if (active) {
        if (loading) {
            loading.style.display = "flex";
        }

        if (generateBtn) {
            generateBtn.disabled = true;
            generateBtn.innerText =
                "⏳ Generating...";
        }

        if (myPapersBtn) {
            myPapersBtn.disabled = true;
        }

        generationStartedAt =
            Date.now();

        if (generationElapsed) {
            generationElapsed.innerText =
                "Elapsed: 0s";
        }

        if (generationTimer) {
            clearInterval(
                generationTimer
            );
        }

        generationTimer =
            setInterval(() => {
                if (!generationStartedAt) {
                    return;
                }

                const elapsed =
                    Math.floor(
                        (
                            Date.now() -
                            generationStartedAt
                        ) / 1000
                    );

                if (generationElapsed) {
                    generationElapsed.innerText =
                        `Elapsed: ${elapsed}s`;
                }
            }, 1000);
    } else {
        if (generationTimer) {
            clearInterval(
                generationTimer
            );

            generationTimer = null;
        }

        generationStartedAt = null;

        if (loading) {
            loading.style.display = "none";
        }

        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.innerText =
                "Generate Exam Paper";
        }

        if (myPapersBtn) {
            myPapersBtn.disabled = false;
        }
    }
}

function showGenerationResult(
    message,
    success = true
) {
    const result =
        document.getElementById("result");

    if (!result) {
        return;
    }

    result.innerHTML = `
        <div class="${success ? "success-message" : "error-message"}">
            ${message}
        </div>
    `;
}

function addQuestionGroup() {
    const container =
        document.getElementById(
            "sectionsContainer"
        );

    const sectionCount =
        container.children.length + 1;

    const section =
        document.createElement("div");

    section.className =
        "section-block";

    section.innerHTML = `
        <div class="section-header">
            <h3>Section ${String.fromCharCode(64 + sectionCount)}</h3>
            <button
                type="button"
                class="remove-section-btn"
                onclick="removeSection(this)"
            >
                Remove
            </button>
        </div>

        <div class="row">
            <div>
                <label>Section Name</label>
                <input
                    type="text"
                    class="section-name"
                    value="Section ${String.fromCharCode(64 + sectionCount)}"
                >
            </div>

            <div>
                <label>Total Questions</label>
                <input
                    type="number"
                    class="section-total-questions"
                    min="1"
                    value="3"
                >
            </div>
        </div>

        <div class="question-groups">
            <div class="question-group">
                <div class="row">
                    <div>
                        <label>Question Type</label>
                        <select class="question-type">
                            <option value="MCQ">MCQ</option>
                            <option value="Short Answer">Short Answer</option>
                            <option value="Long Answer">Long Answer</option>
                            <option value="Case Study">Case Study</option>
                            <option value="Assertion-Reason">Assertion-Reason</option>
                            <option value="Application-based">Application-based</option>
                            <option value="HOTS">HOTS</option>
                            <option value="True/False">True/False</option>
                            <option value="Fill in Blanks">Fill in Blanks</option>
                            <option value="Match Following">Match Following</option>
                            <option value="One Word Answer">One Word Answer</option>
                            <option value="Source-Based">Source-Based</option>
                        </select>
                    </div>

                    <div>
                        <label>Number of Questions</label>
                        <input
                            type="number"
                            class="question-count"
                            min="1"
                            value="3"
                        >
                    </div>

                    <div>
                        <label>Marks Each</label>
                        <input
                            type="number"
                            class="marks-each"
                            min="1"
                            value="1"
                        >
                    </div>
                </div>
            </div>
        </div>

        <button
            type="button"
            class="add-question-group-btn"
            onclick="addQuestionGroup(this)"
        >
            + Add Question Type
        </button>
    `;

    container.appendChild(section);
}

function removeSection(button) {
    const section =
        button.closest(".section-block");

    if (!section) {
        return;
    }

    section.remove();

    updateSectionNames();
}

function updateSectionNames() {
    const sections =
        document.querySelectorAll(
            ".section-block"
        );

    sections.forEach(
        (section, index) => {
            const letter =
                String.fromCharCode(
                    65 + index
                );

            const heading =
                section.querySelector(
                    ".section-header h3"
                );

            const nameInput =
                section.querySelector(
                    ".section-name"
                );

            if (heading) {
                heading.innerText =
                    `Section ${letter}`;
            }

            if (nameInput) {
                nameInput.value =
                    `Section ${letter}`;
            }
        }
    );
}

function addQuestionGroup(button) {
    const section =
        button.closest(
            ".section-block"
        );

    if (!section) {
        return;
    }

    const container =
        section.querySelector(
            ".question-groups"
        );

    if (!container) {
        return;
    }

    const group =
        document.createElement("div");

    group.className =
        "question-group";

    group.innerHTML = `
        <div class="row">
            <div>
                <label>Question Type</label>
                <select class="question-type">
                    <option value="MCQ">MCQ</option>
                    <option value="Short Answer">Short Answer</option>
                    <option value="Long Answer">Long Answer</option>
                    <option value="Case Study">Case Study</option>
                    <option value="Assertion-Reason">Assertion-Reason</option>
                    <option value="Application-based">Application-based</option>
                    <option value="HOTS">HOTS</option>
                    <option value="True/False">True/False</option>
                    <option value="Fill in Blanks">Fill in Blanks</option>
                    <option value="Match Following">Match Following</option>
                    <option value="One Word Answer">One Word Answer</option>
                    <option value="Source-Based">Source-Based</option>
                </select>
            </div>

            <div>
                <label>Number of Questions</label>
                <input
                    type="number"
                    class="question-count"
                    min="1"
                    value="3"
                >
            </div>

            <div>
                <label>Marks Each</label>
                <input
                    type="number"
                    class="marks-each"
                    min="1"
                    value="1"
                >
            </div>
        </div>

        <button
            type="button"
            class="remove-question-group-btn"
            onclick="removeQuestionGroup(this)"
        >
            Remove
        </button>
    `;

    container.appendChild(group);
}

function removeQuestionGroup(button) {
    const group =
        button.closest(
            ".question-group"
        );

    if (group) {
        group.remove();
    }
}

function validateForm() {
    const schoolName =
        document.getElementById(
            "schoolName"
        )?.value.trim();

    const examName =
        document.getElementById(
            "examName"
        )?.value.trim();

    const className =
        document.getElementById(
            "className"
        )?.value.trim();

    const subject =
        document.getElementById(
            "subject"
        )?.value.trim();

    const totalMarks =
        Number(
            document.getElementById(
                "totalMarks"
            )?.value
        );

    if (!schoolName) {
        alert(
            "Please enter school name."
        );
        return false;
    }

    if (!examName) {
        alert(
            "Please enter exam name."
        );
        return false;
    }

    if (!className) {
        alert(
            "Please enter class."
        );
        return false;
    }

    if (!subject) {
        alert(
            "Please enter subject."
        );
        return false;
    }

    if (
        !totalMarks ||
        totalMarks <= 0
    ) {
        alert(
            "Please enter valid total marks."
        );
        return false;
    }

    const groups =
        document.querySelectorAll(
            ".question-group"
        );

    if (!groups.length) {
        alert(
            "Please add at least one question group."
        );
        return false;
    }

    for (
        const group of groups
    ) {
        const count =
            Number(
                group.querySelector(
                    ".question-count"
                )?.value
            );

        const marks =
            Number(
                group.querySelector(
                    ".marks-each"
                )?.value
            );

        if (
            !count ||
            count <= 0
        ) {
            alert(
                "Question count must be greater than 0."
            );
            return false;
        }

        if (
            !marks ||
            marks <= 0
        ) {
            alert(
                "Marks per question must be greater than 0."
            );
            return false;
        }
    }

    return true;
}

function collectSections() {
    const sectionBlocks =
        document.querySelectorAll(
            ".section-block"
        );

    const sections = [];

    sectionBlocks.forEach(
        section => {
            const sectionName =
                section.querySelector(
                    ".section-name"
                )?.value.trim();

            const totalQuestions =
                Number(
                    section.querySelector(
                        ".section-total-questions"
                    )?.value
                );

            const groups =
                section.querySelectorAll(
                    ".question-group"
                );

            const questionTypes = [];

            groups.forEach(
                group => {
                    const type =
                        group.querySelector(
                            ".question-type"
                        )?.value;

                    const count =
                        Number(
                            group.querySelector(
                                ".question-count"
                            )?.value
                        );

                    const marks =
                        Number(
                            group.querySelector(
                                ".marks-each"
                            )?.value
                        );

                    questionTypes.push({
                        question_type: type,
                        count: count,
                        marks_each: marks
                    });
                }
            );

            sections.push({
                section_name:
                    sectionName,
                total_questions:
                    totalQuestions,
                question_types:
                    questionTypes
            });
        }
    );

    return sections;
}

async function generatePDF() {
    if (isGenerating) {
        return;
    }

    if (!validateForm()) {
        return;
    }

    isGenerating = true;

    setGenerationUI(true);

    showGenerationResult(
        "Generating your exam paper. This may take a few minutes...",
        true
    );

    try {
        const form =
            document.getElementById(
                "examForm"
            );

        if (!form) {
            throw new Error(
                "Exam form not found."
            );
        }

        const formData =
            new FormData();

        const schoolName =
            document.getElementById(
                "schoolName"
            )?.value.trim();

        const examName =
            document.getElementById(
                "examName"
            )?.value.trim();

        const className =
            document.getElementById(
                "className"
            )?.value.trim();

        const subject =
            document.getElementById(
                "subject"
            )?.value.trim();

        const topics =
            document.getElementById(
                "topics"
            )?.value.trim();

        const difficulty =
            document.getElementById(
                "difficulty"
            )?.value;

        const examType =
            document.getElementById(
                "examType"
            )?.value;

        const timeLimit =
            document.getElementById(
                "timeLimit"
            )?.value;

        const customTime =
            document.getElementById(
                "customTime"
            )?.value;

        const totalMarks =
            document.getElementById(
                "totalMarks"
            )?.value;

        const instructions =
            document.getElementById(
                "instructions"
            )?.value.trim();

        const includeAnswers =
            document.getElementById(
                "includeAnswers"
            )?.checked ?? true;

        const includeSolutions =
            document.getElementById(
                "includeSolutions"
            )?.checked ?? false;

        const sections =
            collectSections();

        formData.append(
            "school_name",
            schoolName
        );

        formData.append(
            "exam_name",
            examName
        );

        formData.append(
            "class_name",
            className
        );

        formData.append(
            "subject",
            subject
        );

        formData.append(
            "topics",
            topics || ""
        );

        formData.append(
            "difficulty",
            difficulty || ""
        );

        formData.append(
            "exam_type",
            examType || ""
        );

        formData.append(
            "time_limit",
            timeLimit || ""
        );

        formData.append(
            "custom_time",
            customTime || ""
        );

        formData.append(
            "total_marks",
            totalMarks
        );

        formData.append(
            "instructions",
            instructions || ""
        );

        formData.append(
            "sections",
            JSON.stringify(
                sections
            )
        );

        formData.append(
            "include_answers",
            includeAnswers
                ? "true"
                : "false"
        );

        formData.append(
            "include_solutions",
            includeSolutions
                ? "true"
                : "false"
        );

        const fileInput =
            document.getElementById(
                "referenceFiles"
            );

        if (
            fileInput &&
            fileInput.files
        ) {
            for (
                const file
                of fileInput.files
            ) {
                formData.append(
                    "reference_files",
                    file
                );
            }
        }

        const guestId =
            getGuestId();

        const token =
            localStorage.getItem(
                "token"
            );

        const controller =
            new AbortController();

        const timeout =
            setTimeout(
                () => {
                    controller.abort();
                },
                600000
            );

        const headers = {};

        if (token) {
            headers[
                "Authorization"
            ] = `Bearer ${token}`;
        }

        if (guestId) {
            headers[
                "X-Guest-ID"
            ] = guestId;
        }

        const response =
            await fetch(
                `${API_BASE_URL}/generate-paper`,
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

        clearTimeout(
            timeout
        );

        let data = null;

        try {
            data =
                await response.json();
        } catch {
            data = null;
        }

        if (
            response.status === 401
        ) {
            localStorage.removeItem(
                "token"
            );

            alert(
                "Your session has expired. Please login again."
            );

            window.location.href =
                "login.html";

            return;
        }

        if (
            response.status === 402
        ) {
            showNoCredits();

            return;
        }

        if (!response.ok) {
            const errorMessage =
                data?.detail ||
                data?.message ||
                "Failed to generate the exam paper.";

            showGenerationResult(
                escapeHTML(
                    String(
                        errorMessage
                    )
                ),
                false
            );

            return;
        }

        if (
            data?.download_url
        ) {
            const downloadLink =
                document.getElementById(
                    "downloadLink"
                );

            if (downloadLink) {
                let downloadURL =
                    data.download_url;

                if (
                    downloadURL.startsWith(
                        "/"
                    )
                ) {
                    downloadURL =
                        `${API_BASE_URL}${downloadURL}`;
                }

                downloadLink.href =
                    downloadURL;

                downloadLink.style.display =
                    "inline-block";

                downloadLink.innerText =
                    "Download Exam Paper";
            }
        }

        showGenerationResult(
            "Your exam paper is ready. Download it below.",
            true
        );

        await loadGuestCredits();
        await loadUserInfo();
    } catch (error) {
        if (
            error.name ===
            "AbortError"
        ) {
            showGenerationResult(
                "Generation is taking longer than expected. Please try again.",
                false
            );
        } else {
            console.error(
                "Generation error:",
                error
            );

            showGenerationResult(
                "Something went wrong while generating the exam paper. Please try again.",
                false
            );
        }
    } finally {
        isGenerating = false;

        setGenerationUI(false);
    }
}

function escapeHTML(value) {
    return value
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );
}

async function loadUserInfo() {
    const token =
        localStorage.getItem(
            "token"
        );

    const guestCard =
        document.getElementById(
            "guestCreditsCard"
        );

    const planCard =
        document.getElementById(
            "planCard"
        );

    if (!token) {
        if (guestCard) {
            guestCard.style.display =
                "block";
        }

        if (planCard) {
            planCard.style.display =
                "none";
        }

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

        if (
            response.status === 401
        ) {
            localStorage.removeItem(
                "token"
            );

            if (guestCard) {
                guestCard.style.display =
                    "block";
            }

            if (planCard) {
                planCard.style.display =
                    "none";
            }

            return;
        }

        if (!response.ok) {
            return;
        }

        const data =
            await response.json();

        if (guestCard) {
            guestCard.style.display =
                "none";
        }

        if (planCard) {
            planCard.style.display =
                "block";
        }

        const planName =
            document.getElementById(
                "currentPlan"
            );

        const userName =
            document.getElementById(
                "userName"
            );

        const userEmail =
            document.getElementById(
                "userEmail"
            );

        const userCredits =
            document.getElementById(
                "userCredits"
            );

        if (planName) {
            planName.innerText =
                data.plan ||
                "Free";
        }

        if (userName) {
            userName.innerText =
                data.name ||
                data.full_name ||
                "";
        }

        if (userEmail) {
            userEmail.innerText =
                data.email ||
                "";
        }

        if (userCredits) {
            userCredits.innerText =
                data.credits ??
                data.credits_remaining ??
                0;
        }
    } catch (error) {
        console.error(
            "Failed to load user info:",
            error
        );
    }
}

async function loadGuestCredits() {
    const token =
        localStorage.getItem(
            "token"
        );

    if (token) {
        return;
    }

    const guestCredits =
        document.getElementById(
            "guestCredits"
        );

    if (!guestCredits) {
        return;
    }

    const guestId =
        localStorage.getItem(
            "guest_id"
        );

    if (!guestId) {
        guestCredits.innerText =
            "2";

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

        if (!response.ok) {
            return;
        }

        const data =
            await response.json();

        guestCredits.innerText =
            data.credits ??
            data.credits_remaining ??
            0;

        if (
            Number(
                data.credits ??
                data.credits_remaining ??
                0
            ) <= 0
        ) {
            showNoCredits();
        }
    } catch (error) {
        console.error(
            "Failed to load guest credits:",
            error
        );
    }
}

function showNoCredits() {
    const noCredits =
        document.getElementById(
            "noCreditsBox"
        );

    if (noCredits) {
        noCredits.style.display =
            "block";
    }

    const generateBtn =
        document.getElementById(
            "generateBtn"
        );

    if (
        generateBtn &&
        !isGenerating
    ) {
        generateBtn.disabled =
            true;
    }
}

function hideNoCredits() {
    const noCredits =
        document.getElementById(
            "noCreditsBox"
        );

    if (noCredits) {
        noCredits.style.display =
            "none";
    }

    const generateBtn =
        document.getElementById(
            "generateBtn"
        );

    if (
        generateBtn &&
        !isGenerating
    ) {
        generateBtn.disabled =
            false;
    }
}

function openMyPapers() {
    if (isGenerating) {
        return;
    }

    window.location.href =
        "mypapers.html";
}

function logout() {
    localStorage.removeItem(
        "token"
    );

    window.location.href =
        "index.html";
}

function toggleSolutions() {
    const answerKey =
        document.getElementById(
            "includeAnswers"
        );

    const solutions =
        document.getElementById(
            "includeSolutions"
        );

    if (
        !answerKey ||
        !solutions
    ) {
        return;
    }

    if (!answerKey.checked) {
        solutions.checked =
            false;

        solutions.disabled =
            true;
    } else {
        solutions.disabled =
            false;
    }
}

function handleTimeLimit() {
    const timeLimit =
        document.getElementById(
            "timeLimit"
        );

    const customTimeContainer =
        document.getElementById(
            "customTimeContainer"
        );

    if (
        !timeLimit ||
        !customTimeContainer
    ) {
        return;
    }

    if (
        timeLimit.value ===
        "custom"
    ) {
        customTimeContainer.style.display =
            "block";
    } else {
        customTimeContainer.style.display =
            "none";
    }
}

function setupFileValidation() {
    const input =
        document.getElementById(
            "referenceFiles"
        );

    if (!input) {
        return;
    }

    input.addEventListener(
        "change",
        () => {
            const files =
                Array.from(
                    input.files
                );

            if (
                files.length > 5
            ) {
                alert(
                    "You can upload a maximum of 5 files."
                );

                input.value =
                    "";

                return;
            }

            const allowedTypes = [
                "application/pdf",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "image/png",
                "image/jpeg"
            ];

            for (
                const file
                of files
            ) {
                if (
                    !allowedTypes.includes(
                        file.type
                    )
                ) {
                    alert(
                        "Only PDF, DOCX, PNG and JPG/JPEG files are allowed."
                    );

                    input.value =
                        "";

                    return;
                }
            }
        }
    );
}

document.addEventListener(
    "DOMContentLoaded",
    () => {
        const form =
            document.getElementById(
                "examForm"
            );

        if (form) {
            form.addEventListener(
                "submit",
                event => {
                    event.preventDefault();

                    generatePDF();
                }
            );
        }

        const answerKey =
            document.getElementById(
                "includeAnswers"
            );

        if (answerKey) {
            answerKey.addEventListener(
                "change",
                toggleSolutions
            );
        }

        const timeLimit =
            document.getElementById(
                "timeLimit"
            );

        if (timeLimit) {
            timeLimit.addEventListener(
                "change",
                handleTimeLimit
            );
        }

        setupFileValidation();

        toggleSolutions();

        handleTimeLimit();

        loadUserInfo();

        loadGuestCredits();
    }
);