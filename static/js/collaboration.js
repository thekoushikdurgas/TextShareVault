class CollaborativeEditor {
    constructor(quill, pasteId) {
        this.quill = quill;
        this.pasteId = pasteId;
        this.socket = io();
        this.cursors = {};
        this.setupSocketHandlers();
        this.setupQuillHandlers();
    }

    setupSocketHandlers() {
        // Handle text changes from other users
        this.socket.on('text-change', (delta, userId) => {
            if (userId !== this.socket.id) {
                this.quill.updateContents(delta);
            }
        });

        // Handle cursor movements from other users
        this.socket.on('cursor-move', (range, userId, username) => {
            if (userId !== this.socket.id) {
                this.updateCursor(userId, range, username);
            }
        });

        // Handle user join/leave events
        this.socket.on('user-join', (userId, username) => {
            this.addUserCursor(userId, username);
        });

        this.socket.on('user-leave', (userId) => {
            this.removeUserCursor(userId);
        });
    }

    setupQuillHandlers() {
        // Send local text changes to server
        this.quill.on('text-change', (delta, oldDelta, source) => {
            if (source === 'user') {
                this.socket.emit('text-change', {
                    delta: delta,
                    pasteId: this.pasteId
                });
            }
        });

        // Send cursor position updates
        this.quill.on('selection-change', (range, oldRange, source) => {
            if (source === 'user' && range) {
                this.socket.emit('cursor-move', {
                    range: range,
                    pasteId: this.pasteId
                });
            }
        });
    }

    updateCursor(userId, range, username) {
        if (!this.cursors[userId]) {
            this.addUserCursor(userId, username);
        }

        const cursor = this.cursors[userId];
        const bounds = this.quill.getBounds(range.index);
        
        cursor.style.top = `${bounds.top}px`;
        cursor.style.left = `${bounds.left}px`;
    }

    addUserCursor(userId, username) {
        const cursor = document.createElement('div');
        cursor.className = 'ql-cursor';
        cursor.innerHTML = `
            <div class="ql-cursor-flag">
                <span class="ql-cursor-name">${username}</span>
            </div>
            <div class="ql-cursor-caret"></div>
        `;

        this.quill.container.appendChild(cursor);
        this.cursors[userId] = cursor;
    }

    removeUserCursor(userId) {
        if (this.cursors[userId]) {
            this.cursors[userId].remove();
            delete this.cursors[userId];
        }
    }
}

// Initialize collaborative editing when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const editor = document.getElementById('editor');
    if (editor) {
        const pasteId = editor.dataset.pasteId;
        const quill = new Quill('#editor', {
            theme: 'snow',
            modules: {
                toolbar: '#editor-toolbar'
            }
        });
        
        new CollaborativeEditor(quill, pasteId);
    }
});
