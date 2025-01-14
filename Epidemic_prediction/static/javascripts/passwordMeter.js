document.addEventListener("DOMContentLoaded", function () {
    // Ensure the strength div is hidden on page load
    const strengthDiv = document.querySelector(".strength");
    strengthDiv.style.display = "none";

    // Add event listener for the password input field
    document.getElementById("password").addEventListener("input", function () {
        const password = this.value;
        const strength = zxcvbn(password).score; // Existing logic to calculate strength
        const strengthMeter = document.getElementById("strength-meter");
        const strengthText = ["Weak", "Fair", "Good", "Strong", "Very Strong"];
        const strengthColors = ["red", "orange", "rgb(215, 195, 0)", "rgb(0, 247, 0)", "green"];
        const strengthBackgroundColors = ["rgb(255, 196, 196)", "rgb(255, 236, 207)", "rgb(255, 253, 214)", "rgb(221, 255, 213)", "rgb(169, 255, 148)"];

        // Show the strength meter when there is input, otherwise hide it
        if (password.length > 0) {
            strengthDiv.style.display = "block"; // Show
        } else {
            strengthDiv.style.display = "none"; // Hide
        }

        // Update the strength meter's value
        strengthMeter.value = strength;

        // Update the strength text
        const strengthTextElement = document.getElementById("strength-text");
        strengthTextElement.innerText = strengthText[strength];

        // Dynamically update styles based on strength
        strengthTextElement.style.color = strengthColors[strength];
        strengthTextElement.style.backgroundColor = strengthBackgroundColors[strength];
    });
});
