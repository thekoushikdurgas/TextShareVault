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