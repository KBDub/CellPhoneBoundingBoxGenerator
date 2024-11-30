document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('uploadForm');
    const progress = document.getElementById('progress');
    const progressBar = progress.querySelector('.progress-bar');
    const imageContainer = document.getElementById('imageContainer');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        const videoFile = document.getElementById('video').files[0];
        
        if (!videoFile) {
            alert('Please select a video file');
            return;
        }

        formData.append('video', videoFile);

        // Show progress
        progress.classList.remove('d-none');
        progressBar.style.width = '0%';
        imageContainer.innerHTML = '';

        try {
            // Simulate progress while processing
            let progressInterval = setInterval(() => {
                const currentWidth = parseInt(progressBar.style.width);
                if (currentWidth < 90) {
                    progressBar.style.width = (currentWidth + 1) + '%';
                }
            }, 500);

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            clearInterval(progressInterval);
            progressBar.style.width = '100%';

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            const data = await response.json();
            
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

        } catch (error) {
            alert('Error processing video: ' + error.message);
        } finally {
            setTimeout(() => {
                progress.classList.add('d-none');
            }, 1000);
        }
    });
});
