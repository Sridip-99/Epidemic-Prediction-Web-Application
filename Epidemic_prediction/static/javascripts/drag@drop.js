const dropZone = document.getElementById('upload-box');
const fileInput = document.getElementById('fileInput');
const uploadForm = document.getElementById('uploadForm');

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');

    // Check if the dropped file is a .csv file
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];

        // Check if the dropped file is a .csv file
        if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
            console.log('File accepted:', file.name);

            // Add the file to the file input
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;

            console.log('File added to input:', fileInput.files[0].name);
        } else {
            alert('Only .csv files are allowed.');
        }
    } else {
        alert('No file detected. Please drop a valid .csv file.');
    }
});
