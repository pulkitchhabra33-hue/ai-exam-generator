const API_BASE_URL = 
  "https://ai-exam-generator-backend.onrender.com";


async function loadPaperHistory() {

  const token =
    localStorage.getItem(
      "access_token"
    );

  const res = await fetch(

    `${API_BASE_URL}/my-papers`,

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

        <h3>
        ${paper.exam_name}
        </h3>

        <p>
        ${paper.subject}
        </p>

        <a
          href="${API_BASE_URL}/download/${paper.pdf_path}"
          target="_blank"
        >

          Download PDF

        </a>

      </div>

      <hr>

      `;

    }
  );

}


loadPaperHistory();