async function loginUser(event) {

    event.preventDefault();

    const email = document.getElementById(
        "email"
    ).value;

    const password = document.getElementById(
        "password"
    ).value;

    try {

        const response = await apiRequest(

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

        alert("Login Successful!");

        window.location.href =
            "index.html";

    }

    catch (error) {

        alert(

            "Invalid email or password."

        );

        console.error(error);

    }

}