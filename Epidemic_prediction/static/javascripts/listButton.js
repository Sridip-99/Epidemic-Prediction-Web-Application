// Get all virus buttons and the hidden input field for the selected virus
const buttons = document.querySelectorAll('.listButton');
const selectedVirusInput = document.getElementById('selectedVirus');

// Add click event listeners to the buttons
buttons.forEach(button => {
    button.addEventListener('click', function () {
        // Remove the "selected" class from all buttons
        buttons.forEach(btn => btn.classList.remove('selected'));

        // Add the "selected" class to the clicked button
        this.classList.add('selected');

        // Update the hidden input with the selected virus value
        const virusValue = this.querySelector('.selectedVirusInput').value;
        selectedVirusInput.value = virusValue;

        console.log('Selected Virus:', virusValue); // For debugging
    });
});

// Ensure form submission even if no virus is selected
document.getElementById('uploadForm').addEventListener('submit', function (e) {
    if (!selectedVirusInput.value) {
        console.warn('No virus type selected.');
    }
});
