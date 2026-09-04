// Backend URL

const API_BASE_URL =
  "https://ai-exam-generator-backend.onrender.com";


// --------------------------------------------------
// LOAD CURRENT USER
// --------------------------------------------------

async function loadPricingUser() {

  const token =
    localStorage.getItem(
      "access_token"
    );

  const userElement =
    document.getElementById(
      "pricingUser"
    );

  const planElement =
    document.getElementById(
      "pricingPlan"
    );

  const creditsElement =
    document.getElementById(
      "pricingCredits"
    );


  if (!userElement) {
    return;
  }


  /*
   * Guest user
   */

  if (!token) {

    userElement.innerText =
      "You are currently browsing as a guest.";

    if (planElement) {
      planElement.innerText =
        "Plan: Free";
    }

    if (creditsElement) {
      creditsElement.innerText =
        "Login or signup to purchase a plan.";
    }

    return;
  }


  /*
   * Logged-in user
   */

  try {

    const response =
      await fetch(
        `${API_BASE_URL}/current-user`,
        {
          method: "GET",

          headers: {
            "Authorization":
              `Bearer ${token}`
          }
        }
      );


    /*
     * Invalid / expired session
     */

    if (!response.ok) {

      localStorage.removeItem(
        "access_token"
      );

      userElement.innerText =
        "Session expired. Please login again.";

      if (planElement) {
        planElement.innerText = "";
      }

      if (creditsElement) {
        creditsElement.innerText = "";
      }

      return;
    }


    const user =
      await response.json();


    userElement.innerText =
      `Account: ${user.name}`;


    if (planElement) {

      planElement.innerText =
        `Plan: ${user.plan}`;

    }


    if (creditsElement) {

      creditsElement.innerText =
        `Credits: ${user.credits}`;

    }

  }

  catch (error) {

    console.error(
      "Failed to load pricing user:",
      error
    );

    userElement.innerText =
      "Unable to load account information.";

  }

}


// --------------------------------------------------
// SELECT PLAN
// --------------------------------------------------

function selectPlan(plan) {

  /*
   * FREE PLAN
   */

  if (plan === "FREE") {

    localStorage.removeItem(
      "selected_plan"
    );

    window.location.href =
      "index.html";

    return;
  }


  /*
   * Remember the selected plan.
   */

  localStorage.setItem(
    "selected_plan",
    plan
  );


  /*
   * Check whether the user is logged in.
   */

  const token =
    localStorage.getItem(
      "access_token"
    );


  /*
   * Logged-in user
   *
   * Payment integration will be
   * connected here later.
   */

  if (token) {

    alert(
      `${plan} selected. Payment integration will be available here.`
    );

    return;
  }


  /*
   * Guest user
   *
   * After authentication, return
   * to the pricing page.
   */

  localStorage.setItem(
    "auth_redirect",
    "pricing.html"
  );


  alert(
    `Please login or create an account to purchase the ${plan} plan.`
  );


  window.location.href =
    "login.html";

}


// --------------------------------------------------
// HIGHLIGHT SELECTED PLAN
// --------------------------------------------------

function highlightSelectedPlan() {

  const selectedPlan =
    localStorage.getItem(
      "selected_plan"
    );


  if (!selectedPlan) {
    return;
  }


  const planButtons =
    document.querySelectorAll(
      "[data-plan]"
    );


  planButtons.forEach(
    button => {

      if (
        button.dataset.plan ===
        selectedPlan
      ) {

        button.classList.add(
          "selected-plan"
        );

      }

    }
  );

}


// --------------------------------------------------
// PAGE INITIALIZATION
// --------------------------------------------------

window.addEventListener(
  "DOMContentLoaded",
  () => {

    loadPricingUser();

    highlightSelectedPlan();

  }
);