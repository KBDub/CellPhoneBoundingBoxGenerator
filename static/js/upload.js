document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('uploadForm');
    const progress = document.getElementById('progress');
    const progressBar = progress.querySelector('.progress-bar');
    const imageContainer = document.getElementById('imageContainer');
    
    const MAX_FILE_SIZE = 500 * 1024 * 1024; // 500MB in bytes

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        const videoFile = document.getElementById('video').files[0];
        
        if (!videoFile) {
            showError('Please select a video file');
            return;
        }

        // Check file size
        if (videoFile.size > MAX_FILE_SIZE) {
            showError(`File size exceeds limit (${formatFileSize(MAX_FILE_SIZE)}). Please choose a smaller file.`);
            return;
        }

        formData.append('video', videoFile);

        // Show progress
        progress.classList.remove('d-none');
        progressBar.style.width = '0%';
        progressBar.textContent = '0%';
        imageContainer.innerHTML = '';

        try {
            const xhr = new XMLHttpRequest();
            
            xhr.upload.onprogress = function(e) {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    const formattedPercent = Math.round(percentComplete);
                    progressBar.style.width = formattedPercent + '%';
                    progressBar.textContent = formattedPercent + '%';
                }
            };

            xhr.onload = async function() {
                if (xhr.status === 200) {
                    const data = JSON.parse(xhr.responseText);
                    displayResults(data);
                } else {
                    let errorMessage = 'Upload failed';
                    try {
                        const errorData = JSON.parse(xhr.responseText);
                        errorMessage = errorData.error || errorMessage;
                    } catch (e) {
                        if (xhr.status === 413) {
                            errorMessage = 'File size too large. Please choose a smaller file.';
                        }
                    }
                    throw new Error(errorMessage);
                }
            };

            xhr.onerror = function() {
                throw new Error('Network error occurred while uploading');
            };

            xhr.open('POST', '/upload', true);
            xhr.send(formData);

        } catch (error) {
            showError('Error processing video: ' + error.message);
        }
    });

    function showError(message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show mt-3';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        form.insertAdjacentElement('afterend', alertDiv);
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function displayResults(data) {
        if (data.images && data.images.length > 0) {
            data.images.forEach(imagePath => {
                const col = document.createElement('div');
                col.className = 'col-md-4 mb-3';
                
                const card = document.createElement('div');
                card.className = 'card';
                
                const img = document.createElement('img');
                img.className = 'card-img-top';
                img.src = '/download/' + imagePath;
                
                const cardBody = document.createElement('div');
                cardBody.className = 'card-body';
                
                const downloadBtn = document.createElement('a');
                downloadBtn.href = '/download/' + imagePath;
                downloadBtn.className = 'btn btn-sm btn-secondary';
                downloadBtn.textContent = 'Download';
                downloadBtn.download = '';
                
                cardBody.appendChild(downloadBtn);
                card.appendChild(img);
                card.appendChild(cardBody);
                col.appendChild(card);
                imageContainer.appendChild(col);
            });
        } else {
            imageContainer.innerHTML = '<p class="text-muted">No phones detected in the video.</p>';
        }
    }
});
