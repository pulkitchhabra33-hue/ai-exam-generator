const loginForm = document.getElementById(
    "loginForm"
);

if (loginForm) {

    loginForm.addEventListener(

        "submit",

        loginUser

    );

}

const signupForm = document.getElementById(
    "signupForm"
);

if (signupForm) {

    signupForm.addEventListener(

        "submit",

        signupUser

    );

}