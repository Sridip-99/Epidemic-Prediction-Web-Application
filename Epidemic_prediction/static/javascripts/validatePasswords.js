function validatePassword() {
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm-password").value;
    const message = document.getElementById("password-message");

    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$/;

    if (!passwordRegex.test(password)) {
        message.style.color = "red";
        message.innerText = "Password must be at least 8 characters long and include uppercase, lowercase, numbers, and special characters.";
        return false;
    }

    if (password !== confirmPassword) {
        message.style.color = "red";
        message.innerText = "Passwords do not match.";
        return false;
    }

    message.innerText = ""; // Clear the message
    return true;
}