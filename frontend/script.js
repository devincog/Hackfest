document.addEventListener('DOMContentLoaded', () => {
    // Generate floating spores (particles) for the Upside Down effect
    const particlesContainer = document.getElementById('particles');
    const particleCount = 40;

    for (let i = 0; i < particleCount; i++) {
        createParticle(particlesContainer);
    }

    // File Upload Logic
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileList = document.getElementById('file-list');
    let uploadedFiles = [];

    // Make the whole dropzone clickable
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    // Drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('dragover');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    });

    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        [...files].forEach(file => {
            // Check if file is txt or pdf
            if (file.name.endsWith('.pdf') || file.name.endsWith('.txt')) {
                if (!uploadedFiles.some(f => f.name === file.name)) {
                    uploadedFiles.push(file);
                    addFileToList(file);
                }
            } else {
                alert(`File ${file.name} is not a valid PDF or TXT.`);
            }
        });
        
        if (uploadedFiles.length > 0) {
            updateStatus('READY: ' + uploadedFiles.length + ' FILES LOADED IN MEMORY');
        }
    }

    function addFileToList(file) {
        const li = document.createElement('li');
        const size = (file.size / 1024).toFixed(1) + ' KB';
        li.innerHTML = `
            <span class="file-name">${file.name}</span>
            <span class="file-size">[${size}] - UPLOADED</span>
        `;
        fileList.appendChild(li);
    }

    // Generate Action Logic
    const generateBtn = document.getElementById('generate-btn');
    const queryInput = document.getElementById('query-input');
    const statusText = document.querySelector('.status-text');
    const loader = document.querySelector('.loader');
    const outputPanel = document.getElementById('output-panel');

    // Real API integration
    const API_BASE = 'http://127.0.0.1:8000/api';
    let currentProjectId = null;

    generateBtn.addEventListener('click', async (e) => {
        // Prevent any default behavior that might cause a page reload
        e.preventDefault();
        console.log("Generate button clicked. Starting pipeline...");

        if (uploadedFiles.length === 0) {
            updateStatus('ERROR: NO DATA SOURCES PROVIDED', true);
            return;
        }

        const query = queryInput.value.trim();
        if (!query) {
            updateStatus('ERROR: QUERY REQUIRED', true);
            return;
        }

        // Start Generation Process
        generateBtn.disabled = true;
        loader.classList.remove('hidden');
        outputPanel.classList.add('hidden'); // Hide during generation

        try {
            // STEP 1: UPLOAD FILES
            updateStatus('UPLOADING & CHUNKING DOCUMENTS TO THE UPSIDE DOWN...');
            const formData = new FormData();
            uploadedFiles.forEach(file => {
                formData.append('files', file);
            });
            if (currentProjectId) {
                formData.append('project_id', currentProjectId);
            }

            const uploadResponse = await fetch(`${API_BASE}/upload/`, {
                method: 'POST',
                body: formData
            });

            if (!uploadResponse.ok) throw new Error('Failed to upload and embed documents.');
            
            const uploadData = await uploadResponse.json();
            currentProjectId = uploadData.project_id;

            // STEP 2: GENERATE OR UPDATE SLIDE SCHEMA
            const isUpdate = currentProjectId !== null && document.getElementById('presentation-preview').src.includes(currentProjectId);
            
            if (isUpdate) {
                updateStatus('SENDING UPDATE... PRESERVING ANIMATION METADATA...');
                const updateResponse = await fetch(`${API_BASE}/update/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query, project_id: currentProjectId })
                });
                if (!updateResponse.ok) throw new Error('Failed to update presentation.');
                await updateResponse.json();
            } else {
                updateStatus('COMMUNICATING WITH THE MIND FLAYER (LLM GENERATION)...');
                const generateResponse = await fetch(`${API_BASE}/generate/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query, project_id: currentProjectId })
                });
                if (!generateResponse.ok) throw new Error('Failed to generate presentation schema.');
                await generateResponse.json();
            }

            // Change button text to indicate update mode
            document.querySelector('.btn-content').textContent = "UPDATE BRIEFING DECK";

            // STEP 3: RENDER
            updateStatus('TRANSMISSION COMPLETE. RENDERING DECK...');
            const iframe = document.getElementById('presentation-preview');
            // Add a timestamp query param to force iframe cache reload if user generates again
            iframe.src = `${API_BASE}/render/${currentProjectId}/?t=${new Date().getTime()}`;

            loader.classList.add('hidden');
            generateBtn.disabled = false;
            
            // Show Output Panel
            outputPanel.classList.remove('hidden');
            outputPanel.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            console.error(error);
            updateStatus(`ERROR: ${error.message.toUpperCase()}`, true);
            loader.classList.add('hidden');
            generateBtn.disabled = false;
        }
    });

    function updateStatus(message, isError = false) {
        statusText.textContent = message;
        if (isError) {
            statusText.style.color = '#ff5f56';
            setTimeout(() => {
                statusText.style.color = 'var(--text-terminal)';
                statusText.textContent = 'AWAITING INPUT...';
            }, 5000);
        } else {
            statusText.style.color = 'var(--text-terminal)';
        }
    }

    // Helper to create particles
    function createParticle(container) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
        const size = Math.random() * 4 + 1;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        
        particle.style.left = `${Math.random() * 100}vw`;
        particle.style.animationDuration = `${Math.random() * 10 + 10}s`;
        particle.style.animationDelay = `${Math.random() * 10}s`;
        
        container.appendChild(particle);
    }
});
