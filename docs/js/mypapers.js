const API_BASE_URL =
  "https://ai-exam-generator-backend.onrender.com";


async function loadPaperHistory() {

  const token =
    localStorage.getItem("access_token");

  const container =
    document.getElementById("paperHistory");


  if (!token) {

    container.innerHTML = `
      <p>
        Please login to view your papers.
      </p>
    `;

    return;
  }


  try {

    const res = await fetch(
      `${API_BASE_URL}/my-papers`,
      {
        headers: {
          Authorization:
            `Bearer ${token}`
        }
      }
    );


    if (!res.ok) {

      if (res.status === 401) {

        container.innerHTML = `
          <p>
            Your session has expired.
            Please login again.
          </p>
        `;

        return;
      }

      throw new Error(
        "Failed to load paper history."
      );
    }


    const papers =
      await res.json();


    if (!papers.length) {

      container.innerHTML = `
        <p>
          You haven't generated any papers yet.
        </p>
      `;

      return;
    }


    container.innerHTML = "";


    papers.forEach(
      paper => {

        const createdDate =
          new Date(
            paper.created_at
          ).toLocaleString();


        container.innerHTML += `

          <div>

            <h3>
              ${paper.exam_name}
            </h3>

            <p>
              Subject: ${paper.subject}
            </p>

            <p>
              Exam Type: ${
                paper.exam_type || "General"
              }
            </p>

            <p>
              Created: ${createdDate}
            </p>

            <button
              type="button"
              onclick="downloadPaper('${paper.download_url}')"
            >
              📥 Download PDF
            </button>

          </div>

          <hr>

        `;
      }
    );

  } catch (error) {

    console.error(
      "Paper history error:",
      error
    );

    container.innerHTML = `
      <p>
        Unable to load your papers.
        Please try again.
      </p>
    `;
  }
}

async function downloadPaper(downloadPath) {

  const token =
    localStorage.getItem("access_token");

  if (!token) {
    alert("Please login to download your paper.");
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
      "Unable to download the PDF. Please try again."
    );
  }
}

loadPaperHistory();