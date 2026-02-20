const API_URL = "http://127.0.0.1:5000";
let currentEmail = "";

function showMessage(text, isError = false) {
    const messageEl = document.getElementById("message");
    messageEl.innerText = text;
    messageEl.className = isError ? "mt-3 text-center text-danger" : "mt-3 text-center text-success";
}

function sendOTP() {
    const email = document.getElementById("email").value.trim();

    if (!email) {
        showMessage("Please enter email", true);
        return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showMessage("Please enter a valid email address", true);
        return;
    }

    // Show loading state
    document.getElementById("sendOtpText").classList.add("d-none");
    document.getElementById("sendOtpSpinner").classList.remove("d-none");

    fetch(`${API_URL}/send-otp`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: email
        })
    })
    .then(res => res.json())
    .then(data => {
        // Hide loading state
        document.getElementById("sendOtpText").classList.remove("d-none");
        document.getElementById("sendOtpSpinner").classList.add("d-none");

        if (data.message === "OTP sent to your email") {
            currentEmail = email;
            
            // Show step 2
            document.getElementById("step1").classList.add("d-none");
            document.getElementById("step2").classList.remove("d-none");
            document.getElementById("userEmail").innerText = email;
            
            showMessage("OTP sent successfully! Check your email.", false);
        } else {
            showMessage(data.message, true);
        }
    })
    .catch(err => {
        // Hide loading state
        document.getElementById("sendOtpText").classList.remove("d-none");
        document.getElementById("sendOtpSpinner").classList.add("d-none");
        
        showMessage("Server error. Please try again.", true);
        console.error(err);
    });
}

function registerWithOTP() {
    const otp = document.getElementById("otp").value.trim();
    const name = document.getElementById("name").value.trim();
    const contact_number = document.getElementById("contact_number").value.trim();
    const address_house = document.getElementById("address_house").value.trim();
    const address_street = document.getElementById("address_street").value.trim();
    const address_city = document.getElementById("address_city").value.trim();
    const address_state = document.getElementById("address_state").value.trim();
    const address_pincode = document.getElementById("address_pincode").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    if (!otp || !name || !contact_number || !address_house || !address_street || !address_city || !address_state || !address_pincode || !password || !confirmPassword) {
        showMessage("Please fill all fields", true);
        return;
    }

    if (otp.length !== 6) {
        showMessage("OTP must be 6 digits", true);
        return;
    }

    if (password.length < 6) {
        showMessage("Password must be at least 6 characters", true);
        return;
    }

    if (password !== confirmPassword) {
        showMessage("Passwords do not match", true);
        return;
    }

    // Show loading state
    document.getElementById("registerText").classList.add("d-none");
    document.getElementById("registerSpinner").classList.remove("d-none");

    fetch(`${API_URL}/register-with-otp`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: currentEmail,
            otp: otp,
            name: name,
            contact_number: contact_number,
            address_house: address_house,
            address_street: address_street,
            address_city: address_city,
            address_state: address_state,
            address_pincode: address_pincode,
            password: password
        })
    })
    .then(res => res.json())
    .then(data => {
        // Hide loading state
        document.getElementById("registerText").classList.remove("d-none");
        document.getElementById("registerSpinner").classList.add("d-none");

        if (data.message === "Registration successful! Please login.") {
            showMessage(data.message, false);
            
            // Redirect to login after 2 seconds
            setTimeout(() => {
                window.location.href = "index.html";
            }, 2000);
        } else {
            showMessage(data.message, true);
        }
    })
    .catch(err => {
        // Hide loading state
        document.getElementById("registerText").classList.remove("d-none");
        document.getElementById("registerSpinner").classList.add("d-none");
        
        showMessage("Server error. Please try again.", true);
        console.error(err);
    });
}

function resendOTP() {
    // Reset step 2 fields
    document.getElementById("otp").value = "";
    document.getElementById("name").value = "";
    document.getElementById("contact_number").value = "";
    document.getElementById("address_house").value = "";
    document.getElementById("address_street").value = "";
    document.getElementById("address_city").value = "";
    document.getElementById("address_state").value = "";
    document.getElementById("address_pincode").value = "";
    document.getElementById("password").value = "";
    document.getElementById("confirmPassword").value = "";
    
    // Go back to step 1 to resend OTP
    document.getElementById("step2").classList.add("d-none");
    document.getElementById("step1").classList.remove("d-none");
    
    // Restore previous values
    document.getElementById("email").value = currentEmail;
    
    showMessage("Please click 'Send OTP' to receive a new code", false);
}
