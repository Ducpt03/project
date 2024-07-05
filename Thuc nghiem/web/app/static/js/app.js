// function encryptAndDisplay() {
//     // Get form data
//     const formData = new FormData(document.getElementById('uploadForm'));

//     // Get the uploaded file
//     const fileInput = document.getElementById('file');
//     const file = fileInput.files[0];

//     if (!file) {
//         alert("Please select a file.");
//         return;
//     }

//     // Create a FileReader object
//     const reader = new FileReader();

//     // Define what to do when file is read
//     reader.onload = function(e) {
//         const fileContent = e.target.result; // This is the file content
//         // Simulate encryption (replace with your actual encryption logic)
//         const encryptedContent = encrypt(fileContent); // Replace 'encrypt' with your encryption function

//         // Display original file content
//         const contentPre = document.getElementById('content');
//         contentPre.textContent = fileContent;
//         document.getElementById('file-content').style.display = 'block';

//         // Display encrypted content
//         const encryptedPre = document.getElementById('encrypted');
//         encryptedPre.textContent = encryptedContent;
//         document.getElementById('encrypted-content').style.display = 'block';

//         // Remove file from FormData (optional)


//         // Enable upload button
//         document.getElementById('uploadButton').disabled = false;
//     };

//     // Read the file as text
//     reader.readAsText(file);
// }

// function uploadEncrypted() {
//     // Get encrypted content and form data
//     const encryptedContent = document.getElementById('encrypted').textContent.trim();
//     const formData = new FormData(document.getElementById('uploadForm'));
//     // Add encrypted content to form data
//     formData.append('encrypted_content', encryptedContent);
//     formData.delete('file');
//     // Example: Send form data to server using fetch
//     fetch('{{ url_for("upload") }}', {
//         method: 'POST',
//         body: formData
//     })
//     .then(response => {
//         if (!response.ok) {
//             throw new Error('Network response was not ok');
//         }
//         return response.json();
//     })
//     .then(data => {
//         // Handle server response if needed
//         console.log('Server response:', data);
//         alert('Upload successful!');
//     })
//     .catch(error => {
//         console.error('Error:', error);
//         alert('Upload failed. Please try again.');
//     });
// }

// // Example encryption function (replace with your actual encryption logic)
// function encrypt(data) {
//     // This is a placeholder for actual encryption logic
//     // Here, we just return the data as is for demonstration
//     return data;
// }
