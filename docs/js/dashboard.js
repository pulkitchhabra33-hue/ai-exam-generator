const API_BASE_URL =
    "https://ai-exam-generator-backend.onrender.com";


// ============================================================
// LOAD DASHBOARD
// ============================================================

async function loadDashboard() {

    const token =
        localStorage.getItem("access_token");


    if (!token) {

        window.location.href =
            "login.html";

        return;
    }


    await loadUserInfo(token);

    await loadRecentPapers(token);
}



// ============================================================
// LOAD USER INFORMATION
// ============================================================

async function loadUserInfo(token) {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/current-user`,
                {
                    method: "GET",

                    headers: {
                        Authorization:
                            `Bearer ${token}`
                    }
                }
            );


        if (!response.ok) {

            if (response.status === 401) {

                localStorage.removeItem(
                    "access_token"
                );

                window.location.href =
                    "login.html";

                return;
            }

            throw new Error(
                "Failed to load user information."
            );
        }


        const user =
            await response.json();


        // ----------------------------------------------------
        // NAME
        // ----------------------------------------------------

        const userName =
            document.getElementById(
                "userName"
            );

        const welcomeName =
            document.getElementById(
                "welcomeName"
            );


        if (userName) {

            userName.textContent =
                user.name || "User";
        }


        if (welcomeName) {

            welcomeName.textContent =
                user.name || "User";
        }


        // ----------------------------------------------------
        // PLAN
        // ----------------------------------------------------

        const userPlan =
            document.getElementById(
                "userPlan"
            );


        if (userPlan) {

            userPlan.textContent =
                user.plan || "FREE";
        }


        // ----------------------------------------------------
        // CREDITS
        // ----------------------------------------------------

        const userCredits =
            document.getElementById(
                "userCredits"
            );


        if (userCredits) {

            userCredits.textContent =
                user.credits ?? 0;
        }


        // ----------------------------------------------------
        // EXPIRY
        // ----------------------------------------------------

        const userExpiry =
            document.getElementById(
                "userExpiry"
            );


        if (userExpiry) {

            if (
                user.plan !== "FREE" &&
                user.days_left !== undefined
            ) {

                userExpiry.textContent =
                    `${user.days_left} days left`;

            } else {

                userExpiry.textContent =
                    "No active plan";
            }
        }


    } catch (error) {

        console.error(
            "Dashboard user error:",
            error
        );

        alert(
            "Unable to load your account information."
        );
    }
}



// ============================================================
// LOAD RECENT PAPERS
// ============================================================

async function loadRecentPapers(token) {

    const container =
        document.getElementById(
            "recentPapers"
        );


    if (!container) {
        return;
    }


    try {

        const response =
            await fetch(
                `${API_BASE_URL}/my-papers`,
                {
                    method: "GET",

                    headers: {
                        Authorization:
                            `Bearer ${token}`
                    }
                }
            );


        if (!response.ok) {

            throw new Error(
                "Failed to load papers."
            );
        }


        const papers =
            await response.json();


        if (!papers.length) {

            container.innerHTML = `
                <div class="empty-papers">

                    <p>
                        You haven't generated any papers yet.
                    </p>

                    <button
                        type="button"
                        onclick="generateExam()"
                    >
                        Generate Your First Paper
                    </button>

                </div>
            `;

            return;
        }


        // Show only latest 5 papers

        const recentPapers =
            papers.slice(0, 5);


        container.innerHTML =
            recentPapers
                .map(
                    paper => `

                    <div class="paper-card">

                        <div class="paper-info">

                            <h3>
                                ${
                                    paper.exam_name ||
                                    "Untitled Exam"
                                }
                            </h3>

                            <p>
                                Subject:
                                ${
                                    paper.subject ||
                                    "Not specified"
                                }
                            </p>

                            <p>
                                ${
                                    paper.exam_type ||
                                    "General"
                                }
                            </p>

                        </div>


                        <button
                            type="button"
                            onclick="downloadPaper(
                                '${paper.download_url}'
                            )"
                        >
                            📥 Download
                        </button>

                    </div>

                `
                )
                .join("");


    } catch (error) {

        console.error(
            "Dashboard papers error:",
            error
        );

        container.innerHTML = `
            <p>
                Unable to load your papers.
            </p>
        `;
    }
}



// ============================================================
// DOWNLOAD PAPER
// ============================================================

async function downloadPaper(
    downloadPath
) {

    const token =
        localStorage.getItem(
            "access_token"
        );


    if (!token) {

        window.location.href =
            "login.html";

        return;
    }


    try {

        const response =
            await fetch(
                `${API_BASE_URL}${downloadPath}`,
                {
                    method: "GET",

                    headers: {
                        Authorization:
                            `Bearer ${token}`
                    }
                }
            );


        if (!response.ok) {

            throw new Error(
                "Failed to generate download link."
            );
        }


        const data =
            await response.json();


        if (!data.download_url) {

            throw new Error(
                "Download URL missing."
            );
        }


        window.open(
            data.download_url,
            "_blank"
        );


    } catch (error) {

        console.error(
            "Download error:",
            error
        );

        alert(
            "Unable to download the PDF."
        );
    }
}



// ============================================================
// NAVIGATION
// ============================================================

function generateExam() {

    window.location.href =
        "index.html";
}


function openMyPapers() {

    window.location.href =
        "mypapers.html";
}



// ============================================================
// LOGOUT
// ============================================================

function logout() {

    localStorage.removeItem(
        "access_token"
    );

    window.location.href =
        "login.html";
}



// ============================================================
// INITIALIZE
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    loadDashboard
);