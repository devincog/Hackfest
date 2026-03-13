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

    generateBtn.addEventListener('click', () => {
        if (uploadedFiles.length === 0) {
            updateStatus('ERROR: NO DATA SOURCES PROVIDED', true);
            return;
        }

        const query = queryInput.value.trim();
        if (!query) {
            updateStatus('ERROR: QUERY REQUIRED', true);
            return;
        }

        // Simulate Generation Process
        generateBtn.disabled = true;
        loader.classList.remove('hidden');
        updateStatus('ANALYZING DOCUMENTS... CHUNKING AND EMBEDDING...');

        setTimeout(() => {
            updateStatus('COMMUNICATING WITH THE UPSIDE DOWN (LLM)...');
            
            setTimeout(() => {
                updateStatus('RENDERING ANIMATED DECK...');
                
                setTimeout(() => {
                    // Success State
                    updateStatus('TRANSMISSION COMPLETE. PRESENTATION RENDERED.');
                    loader.classList.add('hidden');
                    generateBtn.disabled = false;
                    
                    // Show Output Panel
                    outputPanel.classList.remove('hidden');
                    outputPanel.scrollIntoView({ behavior: 'smooth' });
                    
                }, 1500);
            }, 2000);
        }, 1500);
    });

    function updateStatus(message, isError = false) {
        statusText.textContent = message;
        if (isError) {
            statusText.style.color = '#ff5f56';
            setTimeout(() => {
                statusText.style.color = 'var(--text-terminal)';
                statusText.textContent = 'AWAITING INPUT...';
            }, 3000);
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
