function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: email,
            password: password
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.message === "Login successful") {

            // Save user info (temporary storage)
            localStorage.setItem("user_id", data.user_id);
            localStorage.setItem("role", data.role);
            localStorage.setItem("name", data.name);
            localStorage.setItem("email", email);

            // Redirect based on role
            if (data.role === "ADMIN") {
                window.location.href = "authority.html";
            } else {
                window.location.href = "citizen.html";
            }

        } else {
            document.getElementById("error").innerText = data.message;
        }
    })
    .catch(err => {
        document.getElementById("error").innerText = "Server error";
    });
}
