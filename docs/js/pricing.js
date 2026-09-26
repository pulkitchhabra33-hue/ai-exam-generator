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

async function selectPlan(plan) {

    // FREE PLAN
    if (plan === "FREE") {

        localStorage.removeItem("selected_plan");

        window.location.href = "index.html";

        return;
    }

    // Only allow paid plans
    if (!["PRO", "PREMIUM"].includes(plan)) {
        alert("Invalid plan selected.");
        return;
    }

    // Remember selected plan
    localStorage.setItem("selected_plan", plan);

    // Check login
    const token = localStorage.getItem("access_token");

    // Redirect guest to login
    if (!token) {

        localStorage.setItem(
            "auth_redirect",
            "pricing.html"
        );

        alert(
            `Please login or create an account to purchase the ${plan} plan.`
        );

        window.location.href = "login.html";

        return;
    }

    try {

        // Create Razorpay order through backend
        const response = await fetch(
            `${API_BASE_URL}/create-order`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },

                body: JSON.stringify({
                    plan: plan
                })
            }
        );

        const orderData = await response.json();

        if (!response.ok) {
            throw new Error(
                orderData.detail ||
                "Failed to create payment order."
            );
        }

        // Initialize Razorpay Checkout
        const options = {

            key: orderData.key_id,

            amount: orderData.amount,

            currency: orderData.currency,

            name: "AI Exam Generator",

            description: `${plan} Plan Subscription`,

            order_id: orderData.order_id,

            handler: async function (paymentResponse) {

                try {

                    // Verify payment through backend
                    const verifyResponse = await fetch(
                        `${API_BASE_URL}/verify-payment`,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type": "application/json",
                                "Authorization": `Bearer ${token}`
                            },

                            body: JSON.stringify({
                                razorpay_payment_id:
                                    paymentResponse.razorpay_payment_id,

                                razorpay_order_id:
                                    paymentResponse.razorpay_order_id,

                                razorpay_signature:
                                    paymentResponse.razorpay_signature
                            })
                        }
                    );

                    const verifyData = await verifyResponse.json();

                    if (!verifyResponse.ok) {
                        throw new Error(
                            verifyData.detail ||
                            "Payment verification failed."
                        );
                    }

                    alert(
                        verifyData.already_processed
                            ? "This payment was already processed."
                            : "Payment successful! Your plan has been activated."
                    );

                    window.location.reload();

                } catch (error) {

                    console.error(
                        "Payment verification error:",
                        error
                    );

                    alert(
                        error.message ||
                        "Payment was received, but verification could not be completed. Please contact support before trying to pay again."
                    );
                }
            },

            modal: {
                ondismiss: function () {
                    console.log(
                        "Razorpay Checkout closed by user."
                    );
                }
            }
        };


        // --------------------------------------------------
        // RAZORPAY CHECKOUT INITIALIZATION
        // --------------------------------------------------

        const razorpay = new Razorpay(options);

        // Handle payment failure
        razorpay.on("payment.failed", function (response) {

            console.error(
                "Razorpay payment failed:",
                response.error
            );

            const message =
              response.error?.description ||
              "Payment failed. Please try again.";

            alert(
                response.error.description ||
                "Payment failed. Please try again."
            );
        });

        // Open Razorpay Checkout modal
        razorpay.open();

    } catch (error) {

        console.error(
            "Plan selection error:",
            error
        );

        alert(
            error.message ||
            "Unable to initiate payment. Please try again."
        );
    }
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