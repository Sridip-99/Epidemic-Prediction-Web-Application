// Timer logic
let timeLeft = 60; // 60 seconds

// Get the source page from the hidden input field
let sourcePage = document.getElementById("source-page").value;

// Update the sourcePage based on conditions
if (sourcePage === "doctor_signup") {
    sourcePage = "doctor";
} else if (sourcePage === "end_user_signup") {
    sourcePage = "end_user";
}

const timerInterval = setInterval(() => {
    if (timeLeft > 0) {
        timeLeft--; // Decrement the time
        document.getElementById("time-left").textContent = timeLeft;
    } else {
        clearInterval(timerInterval); // Stop the timer
        alert("OTP has expired! Please request a new one.");
        // Redirect based on the source page
        // window.location.href = `/auth/signup/${sourcePage}/`;
        window.location.href = `/auth/signup/`;
    }
}, 1000); // Update every second
