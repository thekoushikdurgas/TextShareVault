document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle functionality
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');

    // Set initial state based on screen size
    function setInitialState() {
        if (window.innerWidth <= 576) {
            sidebar.classList.add('collapsed');
            content.classList.add('expanded');
        }
    }

    setInitialState();

    // Toggle sidebar when button is clicked
    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        content.classList.toggle('expanded');
    });

    // Initialize Quill editor if we're on the create/edit page
    if (document.getElementById('editor')) {
        var quill = new Quill('#editor', {
            theme: 'snow',
            modules: {
                toolbar: '#editor-toolbar'
            }
        });

        // Handle image upload
        quill.getModule('toolbar').addHandler('image', () => {
            const input = document.createElement('input');
            input.setAttribute('type', 'file');
            input.setAttribute('accept', 'image/*');
            input.click();

            input.onchange = async () => {
                const file = input.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        const range = quill.getSelection(true);
                        quill.insertEmbed(range.index, 'image', e.target.result);
                    };
                    reader.readAsDataURL(file);
                }
            };
        });

        // Handle form submission
        const form = document.getElementById('pasteForm');
        const hiddenContent = document.getElementById('hiddenContent');
        const imagesInput = document.createElement('input');
        imagesInput.type = 'hidden';
        imagesInput.name = 'images[]';
        form.appendChild(imagesInput);

        if (form) {
            form.onsubmit = function() {
                // Get editor content
                const content = quill.root.innerHTML;
                hiddenContent.value = content;

                // Extract image URLs
                const images = [];
                quill.root.querySelectorAll('img').forEach(img => {
                    images.push(img.src);
                });

                // Update images input
                imagesInput.value = JSON.stringify(images);

                return true;
            };
        }
    }

    // Initialize clipboard.js for the URL copy button
    const clipboard = new ClipboardJS('.copy-url');

    clipboard.on('success', function(e) {
        const button = e.trigger;
        const originalText = button.textContent;

        button.textContent = 'Copied!';
        setTimeout(() => {
            button.textContent = originalText;
        }, 2000);

        e.clearSelection();
    });

    clipboard.on('error', function(e) {
        const button = e.trigger;
        button.textContent = 'Failed to copy';
        setTimeout(() => {
            button.textContent = 'Copy URL';
        }, 2000);
    });

    // Handle AI Analysis
    const analyzeBtn = document.querySelector('.analyze-btn');
    if (analyzeBtn) {
        const analysisModal = new bootstrap.Modal(document.getElementById('analysisModal'));
        const analysisResult = document.getElementById('analysisResult');

        analyzeBtn.addEventListener('click', async function() {
            const pasteId = this.dataset.pasteId;
            analyzeBtn.disabled = true;
            analysisResult.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div><p class="mt-2">Analyzing content...</p></div>';
            analysisModal.show();

            try {
                const response = await fetch(`/${pasteId}/analyze`, {
                    method: 'POST'
                });
                const data = await response.json();

                if (data.error) {
                    throw new Error(data.error);
                }

                analysisResult.innerHTML = `<div class="analysis-content">${data.analysis}</div>`;
            } catch (error) {
                analysisResult.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
            } finally {
                analyzeBtn.disabled = false;
            }
        });
    }

    // Auto-resize textarea
    const textareas = document.querySelectorAll('textarea.code-editor');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });

    // Initialize Prism.js for syntax highlighting
    if (typeof Prism !== 'undefined') {
        Prism.highlightAll();
    }
});