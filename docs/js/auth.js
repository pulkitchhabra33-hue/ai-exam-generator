async function loginUser(event) {

    event.preventDefault();

    const email =
        document.getElementById("email")
            .value
            .trim();

    const password =
        document.getElementById("password")
            .value;

    try {

        const response =
            await apiRequest(
                "/login",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        email,
                        password
                    })
                }
            );

        localStorage.setItem(
            "access_token",
            response.access_token
        );

        window.location.href =
            "index.html";

    }

    catch (error) {

        console.error(
            "Login error:",
            error
        );

        alert(
            "Login failed. Check your email and password."
        );
    }
}


async function signupUser(event) {

    event.preventDefault();

    const name =
        document.getElementById("name")
            .value
            .trim();

    const email =
        document.getElementById("email")
            .value
            .trim();

    const password =
        document.getElementById("password")
            .value;

    const confirmPassword =
        document.getElementById(
            "confirmPassword"
        ).value;

    if (password !== confirmPassword) {

        alert(
            "Passwords do not match."
        );

        return;
    }

    try {
        const response= 
            await apiRequest(
                "/signup",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        name,
                        email,
                        password
                    })
                }
            );

            localStorage.setItem(
                "access_token",
                response.access_token
            )

            alert(
                "Account created successfully. Continue to generate."
            );

            window.location.href =
                "login.html";
    }

    catch (error) {

        console.error(
            "Signup error:",
            error
        );

        alert(
            "Signup failed. The email may already be registered."
        );
    }
}

const loginForm =
    document.getElementById(
        "loginForm"
    );

if (loginForm) {

    loginForm.addEventListener(
        "submit",
        loginUser
    );
}


const signupForm =
    document.getElementById(
        "signupForm"
    );

if (signupForm) {

    signupForm.addEventListener(
        "submit",
        signupUser
    );
}