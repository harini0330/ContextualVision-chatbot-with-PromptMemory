document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const newChatBtn = document.getElementById('new-chat-btn');
    const chatList = document.getElementById('chat-list');
    const chatMessages = document.getElementById('chat-messages');
    const imageUpload = document.getElementById('image-upload');
    const uploadBtn = document.getElementById('upload-btn');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const imagePreview = document.getElementById('image-preview');
    const imagePreviewContainer = document.getElementById('image-preview-container');
    const chatTabBtn = document.getElementById('chat-tab-btn');
    const analysisTabBtn = document.getElementById('analysis-tab-btn');
    const chatContainer = document.getElementById('chat-container');
    const analysisContainer = document.getElementById('analysis-container');
    const analysisContent = document.getElementById('analysis-content');
    const themeToggle = document.getElementById('theme-toggle');
    const imageTabBtn = document.getElementById('image-tab-btn');
    const imageViewContainer = document.getElementById('image-view-container');
    const centeredImagePreview = document.getElementById('centered-image-preview');
    const analysisLoading = document.getElementById('analysis-loading');
    const chooseImageBtn = document.getElementById('choose-image-btn');
    const previewContainer = document.getElementById('preview-container');
    
    // State
    let currentChatId = null;
    let chats = [];
    let chatImages = {};  // Store images for each chat
    
    // Load all chats instead of creating a new one
    loadAllChats();
    
    // Event listeners
    newChatBtn.addEventListener('click', createNewChat);
    imageUpload.addEventListener('change', handleImageSelect);
    uploadBtn.addEventListener('click', uploadImage);
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    themeToggle.addEventListener('click', toggleTheme);
    imageTabBtn.addEventListener('click', function() {
        // Remove active class from all tabs
        chatTabBtn.classList.remove('active');
        analysisTabBtn.classList.remove('active');
        imageTabBtn.classList.add('active');
        
        // Hide chat and analysis containers
        chatContainer.classList.add('hidden');
        analysisContainer.classList.add('hidden');
        
        // Show the centered image view
        imageViewContainer.classList.add('active');
        
        // Update the centered image if we have one
        if (currentChatId && chatImages[currentChatId]) {
            centeredImagePreview.src = `data:image/jpeg;base64,${chatImages[currentChatId]}`;
        }
    });
    
    chatTabBtn.addEventListener('click', function() {
        chatTabBtn.classList.add('active');
        analysisTabBtn.classList.remove('active');
        imageTabBtn.classList.remove('active');
        chatContainer.classList.remove('hidden');
        analysisContainer.classList.add('hidden');
        imageViewContainer.classList.remove('active');
        
        // Hide image container
        imagePreviewContainer.classList.add('hidden');
        imagePreviewContainer.classList.remove('visible');
    });
    
    analysisTabBtn.addEventListener('click', function() {
        analysisTabBtn.classList.add('active');
        chatTabBtn.classList.remove('active');
        imageTabBtn.classList.remove('active');
        chatContainer.classList.add('hidden');
        analysisContainer.classList.remove('hidden');
        imageViewContainer.classList.remove('active');
        
        // Hide image container
        imagePreviewContainer.classList.add('hidden');
        imagePreviewContainer.classList.remove('visible');
        
        // Load analysis data if available
        if (currentChatId) {
            loadAnalysisData(currentChatId);
        }
    });

    // Add event listener for the choose image button
    chooseImageBtn.addEventListener('click', function() {
        imageUpload.click();
    });
    
    // Functions
    function createNewChat() {
        fetch('/create_chat', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            const chatId = data.chat_id;
            
            // Add to chats array
            const newChat = {
                id: chatId,
                name: `Chat ${chats.length + 1}`
            };
            chats.push(newChat);
            
            // Add to sidebar
            addChatToSidebar(newChat);
            
            // Set as current chat
            setCurrentChat(chatId);
            
            // Reset UI
            resetChatUI();
        })
        .catch(error => console.error('Error creating chat:', error));
    }
    
    function addChatToSidebar(chat) {
        const chatItem = document.createElement('div');
        chatItem.className = 'chat-item';
        chatItem.dataset.chatId = chat.id;
        
        // Create a simpler structure
        chatItem.innerHTML = `
            <div class="chat-item-content">
                <i class="fas fa-comments"></i>
                <span class="chat-name">${chat.name}</span>
            </div>
            <button class="chat-options-btn">
                <i class="fas fa-ellipsis-v"></i>
            </button>
        `;
        
        // Create options menu
        const optionsMenu = document.createElement('div');
        optionsMenu.className = 'chat-options-menu';
        optionsMenu.innerHTML = `
            <div class="chat-option-item rename-option">
                <i class="fas fa-edit"></i> Rename
            </div>
            <div class="chat-option-item delete-option">
                <i class="fas fa-trash"></i> Delete
            </div>
        `;
        
        // Add options menu to chat item
        chatItem.appendChild(optionsMenu);
        
        // Add click event for chat selection
        chatItem.querySelector('.chat-item-content').addEventListener('click', function() {
            setCurrentChat(chat.id);
        });
        
        // Add click event for options button
        chatItem.querySelector('.chat-options-btn').addEventListener('click', function(e) {
            e.stopPropagation();
            toggleOptionsMenu(optionsMenu);
        });
        
        // Add click events for options
        optionsMenu.querySelector('.rename-option').addEventListener('click', function(e) {
            e.stopPropagation();
            showRenameModal(chat);
            closeAllOptionsMenus();
        });
        
        optionsMenu.querySelector('.delete-option').addEventListener('click', function(e) {
            e.stopPropagation();
            showDeleteConfirmation(chat);
            closeAllOptionsMenus();
        });
        
        chatList.appendChild(chatItem);
        
        // If this is the current chat, mark it as active
        if (chat.id === currentChatId) {
            chatItem.classList.add('active');
        }
    }
    
    function setCurrentChat(chatId) {
        currentChatId = chatId;
        
        // Update active class in sidebar
        document.querySelectorAll('.chat-item').forEach(item => {
            if (item.dataset.chatId === chatId) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
        
        // Load chat history
        loadChatHistory(chatId);
        
        // Reset analysis content
        analysisContent.textContent = '';
    }
    
    function loadChatHistory(chatId) {
        fetch(`/get_chat_history/${chatId}`)
        .then(response => response.json())
        .then(data => {
            // Clear chat messages
            chatMessages.innerHTML = '';
            
            // Add messages to chat
            data.messages.forEach(msg => {
                addMessageToChat(msg.role, msg.content);
            });
            
            // Update UI based on image upload status
            if (data.image_uploaded) {
                uploadBtn.disabled = true;
                userInput.disabled = false;
                sendBtn.disabled = false;
                document.getElementById('image-upload-container').style.display = 'none';
                
                // Load the image but don't show it unless in image tab
                if (chatImages[chatId]) {
                    console.log("Found image for chat:", chatId);
                    imagePreview.src = `data:image/jpeg;base64,${chatImages[chatId]}`;
                    centeredImagePreview.src = `data:image/jpeg;base64,${chatImages[chatId]}`;
                } else {
                    console.log("No image found for chat:", chatId);
                    
                    // Try to fetch the image from the server
                    fetch(`/get_image/${chatId}`)
                    .then(response => response.json())
                    .then(imageData => {
                        if (imageData.image_data) {
                            console.log("Retrieved image from server for chat:", chatId);
                            chatImages[chatId] = imageData.image_data;
                            saveChatImagesToLocalStorage();
                            
                            imagePreview.src = `data:image/jpeg;base64,${imageData.image_data}`;
                            centeredImagePreview.src = `data:image/jpeg;base64,${imageData.image_data}`;
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching image:', error);
                    });
                }
            } else {
                // Reset UI for image upload
                uploadBtn.disabled = true;
                userInput.disabled = true;
                sendBtn.disabled = true;
                document.getElementById('image-upload-container').style.display = 'block';
                imagePreviewContainer.classList.add('hidden');
                imagePreviewContainer.classList.remove('visible');
            }
            
            // Scroll to bottom of chat
            chatMessages.scrollTop = chatMessages.scrollHeight;
        })
        .catch(error => {
            console.error('Error loading chat history:', error);
        });
    }
    
    function resetChatUI() {
        chatMessages.innerHTML = '';
        imageUpload.value = '';
        userInput.value = '';
        uploadBtn.disabled = true;
        userInput.disabled = true;
        sendBtn.disabled = true;
        imagePreviewContainer.classList.add('hidden');
        document.getElementById('image-upload-container').style.display = 'flex';
        
        // Switch to chat tab
        chatTabBtn.click();
    }
    
    function handleImageSelect() {
        if (imageUpload.files.length) {
            const file = imageUpload.files[0];
            
            // Clear previous preview
            previewContainer.innerHTML = '';
            
            // Create file info element
            const fileInfo = document.createElement('div');
            fileInfo.className = 'file-info';
            
            // Create file icon
            const fileIcon = document.createElement('i');
            fileIcon.className = 'fas fa-file-image';
            
            // Create filename element
            const fileName = document.createElement('span');
            fileName.className = 'file-name';
            fileName.textContent = file.name;
            
            // Create file size element
            const fileSize = document.createElement('span');
            fileSize.className = 'file-size';
            fileSize.textContent = formatFileSize(file.size);
            
            // Add elements to file info
            fileInfo.appendChild(fileIcon);
            fileInfo.appendChild(fileName);
            fileInfo.appendChild(fileSize);
            
            // Add file info to preview container
            previewContainer.appendChild(fileInfo);
            
            // Enable the upload button
            uploadBtn.disabled = false;
            uploadBtn.textContent = 'Analyze Image';
            uploadBtn.style.animation = 'pulse 1.5s infinite';
            
            // Update the choose image button
            chooseImageBtn.textContent = 'Change Image';
        } else {
            uploadBtn.disabled = true;
            uploadBtn.textContent = 'Analyze Image';
            uploadBtn.style.animation = '';
            previewContainer.innerHTML = '';
            chooseImageBtn.textContent = 'Choose Image';
        }
    }
    
    // Helper function to format file size
    function formatFileSize(bytes) {
        if (bytes < 1024) {
            return bytes + ' bytes';
        } else if (bytes < 1024 * 1024) {
            return (bytes / 1024).toFixed(1) + ' KB';
        } else {
            return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        }
    }
    
    function uploadImage() {
        if (!currentChatId || !imageUpload.files.length) {
            return;
        }
        
        const file = imageUpload.files[0];
        
        // Check file type
        if (!file.type.startsWith('image/')) {
            alert('Please select an image file (JPEG, PNG, etc.)');
            return;
        }
        
        // Check file size (5MB limit)
        if (file.size > 5 * 1024 * 1024) {
            alert('Image size exceeds 5MB limit. Please select a smaller image.');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        // Update button state
        uploadBtn.disabled = true;
        uploadBtn.textContent = 'Analyzing...';
        uploadBtn.style.animation = '';
        
        // Show loading animation
        analysisLoading.classList.add('active');
        
        fetch(`/upload_image/${currentChatId}`, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Store the image in our local storage with error handling
                if (data.image_data) {
                    try {
                        chatImages[currentChatId] = data.image_data;
                        saveChatImagesToLocalStorage();
                    } catch (storageError) {
                        console.warn('Could not save image to local storage:', storageError);
                        // Continue anyway - the image will be loaded from server when needed
                    }
                    
                    // Update image preview
                    imagePreview.src = `data:image/jpeg;base64,${data.image_data}`;
                    centeredImagePreview.src = `data:image/jpeg;base64,${data.image_data}`;
                    
                    // Update UI
                    document.getElementById('image-upload-container').style.display = 'none';
                    userInput.disabled = false;
                    sendBtn.disabled = false;
                    
                    // Add initial system message
                    if (data.initial_message) {
                        addMessageToChat('assistant', data.initial_message);
                    }
                    
                    // Hide loading animation after a slight delay for better UX
                    setTimeout(() => {
                        analysisLoading.classList.remove('active');
                    }, 500);
                }
            } else {
                // Hide loading animation
                analysisLoading.classList.remove('active');
                alert('Error uploading image: ' + (data.error || 'Unknown error'));
                
                // Reset button
                uploadBtn.disabled = false;
                uploadBtn.textContent = 'Analyze Image';
            }
        })
        .catch(error => {
            // Hide loading animation
            analysisLoading.classList.remove('active');
            console.error('Error uploading image:', error);
            alert('Error uploading image: ' + error.message);
            
            // Reset button
            uploadBtn.disabled = false;
            uploadBtn.textContent = 'Analyze Image';
        });
    }
    
    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessageToChat('user', message);
        
        // Clear input
        userInput.value = '';
        
        // Show loading message
        const loadingMsg = document.createElement('div');
        loadingMsg.className = 'message bot-message loading';
        loadingMsg.textContent = 'Thinking';
        chatMessages.appendChild(loadingMsg);
        
        // Disable input while processing
        userInput.disabled = true;
        sendBtn.disabled = true;
        
        // Send message to server
        const formData = new FormData();
        formData.append('message', message);
        
        fetch(`/send_message/${currentChatId}`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading message
            chatMessages.removeChild(loadingMsg);
            
            // Add bot response
            addMessageToChat('assistant', data.response);
            
            // Re-enable input
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
        })
        .catch(error => {
            console.error('Error sending message:', error);
            chatMessages.removeChild(loadingMsg);
            addMessageToChat('assistant', 'Error processing your request. Please try again.');
            userInput.disabled = false;
            sendBtn.disabled = false;
        });
    }
    
    function addMessageToChat(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = role === 'user' ? 'message user-message' : 'message bot-message';
        
        // Process content (handle markdown, links, etc.)
        messageDiv.textContent = content;
        
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Add function to load analysis data
    function loadAnalysisData(chatId) {
        fetch(`/get_analysis/${chatId}`)
        .then(response => response.json())
        .then(data => {
            if (data.analysis === "No image has been uploaded yet.") {
                analysisContent.textContent = "Please upload an image to see analysis.";
            } else {
                analysisContent.textContent = data.analysis;
            }
        })
        .catch(error => {
            console.error('Error loading analysis data:', error);
            analysisContent.textContent = 'Error loading analysis data.';
        });
    }
    
    // Update the saveChatImagesToLocalStorage function to handle storage limits
    function saveChatImagesToLocalStorage() {
        try {
            // Instead of storing all images, just store the IDs of chats that have images
            const chatImageIds = Object.keys(chatImages);
            localStorage.setItem('chatImageIds', JSON.stringify(chatImageIds));
            
            // Store each image separately with size limits
            for (const chatId of chatImageIds) {
                try {
                    // Compress or limit the image data if needed
                    const imageData = chatImages[chatId];
                    
                    // Skip if the image is too large (over 1MB)
                    if (imageData.length > 1000000) {
                        console.log(`Image for chat ${chatId} is too large for local storage. It will be loaded from server when needed.`);
                        continue;
                    }
                    
                    localStorage.setItem(`chatImage_${chatId}`, imageData);
                } catch (err) {
                    console.warn(`Could not save image for chat ${chatId} to local storage: ${err.message}`);
                    // Continue with other images
                }
            }
        } catch (error) {
            console.error('Error saving chat images to local storage:', error);
            // If we hit quota errors, clear some old data to make space
            try {
                clearOldImagesFromStorage();
            } catch (clearError) {
                console.error('Error clearing old images from storage:', clearError);
            }
        }
    }

    // Add a function to clear old images from storage
    function clearOldImagesFromStorage() {
        // Get all keys that start with 'chatImage_'
        const imageKeys = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key.startsWith('chatImage_')) {
                imageKeys.push(key);
            }
        }
        
        // If we have more than 5 images stored, remove the oldest ones
        if (imageKeys.length > 5) {
            // Sort by last access time if available, or just remove the first few
            imageKeys.slice(0, imageKeys.length - 5).forEach(key => {
                localStorage.removeItem(key);
            });
        }
    }

    // Update the loadChatImagesFromLocalStorage function
    function loadChatImagesFromLocalStorage() {
        try {
            // Load the list of chat IDs that have images
            const chatImageIds = JSON.parse(localStorage.getItem('chatImageIds') || '[]');
            
            // Load each image separately
            for (const chatId of chatImageIds) {
                try {
                    const imageData = localStorage.getItem(`chatImage_${chatId}`);
                    if (imageData) {
                        chatImages[chatId] = imageData;
                    }
                } catch (err) {
                    console.warn(`Could not load image for chat ${chatId} from local storage: ${err.message}`);
                }
            }
        } catch (error) {
            console.error('Error loading chat images from local storage:', error);
        }
    }

    // Call this function when the page loads
    loadChatImagesFromLocalStorage();

    // Add this function to load all existing chats
    function loadAllChats() {
        fetch('/get_all_chats')
        .then(response => response.json())
        .then(data => {
            // Clear existing chats
            chatList.innerHTML = '';
            chats = [];
            
            // Add each chat to the sidebar
            data.chats.forEach((chat, index) => {
                const newChat = {
                    id: chat.id,
                    name: `Chat ${index + 1}`
                };
                chats.push(newChat);
                addChatToSidebar(newChat);
            });
            
            // Select the first chat if available
            if (chats.length > 0) {
                setCurrentChat(chats[0].id);
            } else {
                // Create a new chat if none exist
                createNewChat();
            }
        })
        .catch(error => {
            console.error('Error loading chats:', error);
            // Create a new chat if there was an error
            createNewChat();
        });
    }

    function toggleTheme() {
        // Check current theme
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        
        // Toggle theme
        if (currentTheme === 'light') {
            document.documentElement.setAttribute('data-theme', 'dark');
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
            localStorage.setItem('theme', 'light');
        }
        
        // Force repaint of some elements that might not update properly
        document.querySelectorAll('.chat-input-container, .image-upload-container, .upload-prompt')
            .forEach(el => {
                el.style.display = 'none';
                // Trigger reflow
                void el.offsetHeight;
                el.style.display = '';
            });
    }

    function loadSavedTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        
        if (savedTheme === 'dark') {
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        } else {
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        }
    }

    // Call this function when the page loads
    loadSavedTheme();

    // Add these functions to handle chat options

    // Create modal elements
    const modalOverlay = document.createElement('div');
    modalOverlay.className = 'modal-overlay';
    document.body.appendChild(modalOverlay);

    function toggleOptionsMenu(menu) {
        // Close all other menus first
        closeAllOptionsMenus();
        
        // Toggle this menu
        menu.classList.toggle('active');
        event.stopPropagation();
    }

    function closeAllOptionsMenus() {
        document.querySelectorAll('.chat-options-menu').forEach(menu => {
            menu.classList.remove('active');
        });
    }

    function showRenameModal(chat) {
        // Create modal content
        modalOverlay.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Rename Chat</h3>
                </div>
                <div class="modal-body">
                    <input type="text" class="rename-input" value="${chat.name}" placeholder="Enter new name">
                </div>
                <div class="modal-footer">
                    <button class="modal-btn modal-btn-cancel">Cancel</button>
                    <button class="modal-btn modal-btn-confirm" style="background-color: var(--primary-color);">Rename</button>
                </div>
            </div>
        `;
        
        // Show modal
        modalOverlay.classList.add('active');
        
        // Focus input
        const input = modalOverlay.querySelector('.rename-input');
        input.focus();
        input.select();
        
        // Add event listeners
        modalOverlay.querySelector('.modal-btn-cancel').addEventListener('click', function() {
            modalOverlay.classList.remove('active');
        });
        
        modalOverlay.querySelector('.modal-btn-confirm').addEventListener('click', function() {
            const newName = input.value.trim();
            if (newName) {
                renameChat(chat.id, newName);
            }
            modalOverlay.classList.remove('active');
        });
        
        // Allow pressing Enter to confirm
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                const newName = input.value.trim();
                if (newName) {
                    renameChat(chat.id, newName);
                }
                modalOverlay.classList.remove('active');
            }
        });
    }

    function showDeleteConfirmation(chat) {
        // Create modal content
        modalOverlay.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Delete Chat</h3>
                </div>
                <div class="modal-body">
                    <p>Are you sure you want to delete "${chat.name}"? This action cannot be undone.</p>
                </div>
                <div class="modal-footer">
                    <button class="modal-btn modal-btn-cancel">Cancel</button>
                    <button class="modal-btn modal-btn-confirm">Delete</button>
                </div>
            </div>
        `;
        
        // Show modal
        modalOverlay.classList.add('active');
        
        // Add event listeners
        modalOverlay.querySelector('.modal-btn-cancel').addEventListener('click', function() {
            modalOverlay.classList.remove('active');
        });
        
        modalOverlay.querySelector('.modal-btn-confirm').addEventListener('click', function() {
            deleteChat(chat.id);
            modalOverlay.classList.remove('active');
        });
    }

    function renameChat(chatId, newName) {
        fetch(`/rename_chat/${chatId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: newName })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update chat in local array
                const chat = chats.find(c => c.id === chatId);
                if (chat) {
                    chat.name = newName;
                    
                    // Update UI
                    const chatItem = document.querySelector(`.chat-item[data-chat-id="${chatId}"]`);
                    if (chatItem) {
                        chatItem.querySelector('.chat-name').textContent = newName;
                    }
                }
            } else {
                console.error('Error renaming chat:', data.error);
            }
        })
        .catch(error => {
            console.error('Error renaming chat:', error);
        });
    }

    function deleteChat(chatId) {
        fetch(`/delete_chat/${chatId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove chat from local array
                chats = chats.filter(c => c.id !== chatId);
                
                // Remove from UI
                const chatItem = document.querySelector(`.chat-item[data-chat-id="${chatId}"]`);
                if (chatItem) {
                    chatItem.remove();
                }
                
                // If this was the current chat, select another one
                if (currentChatId === chatId) {
                    if (chats.length > 0) {
                        setCurrentChat(chats[0].id);
                    } else {
                        // Create a new chat if none exist
                        createNewChat();
                    }
                }
                
                // Remove from local storage
                delete chatImages[chatId];
                saveChatImagesToLocalStorage();
            } else {
                console.error('Error deleting chat:', data.error);
            }
        })
        .catch(error => {
            console.error('Error deleting chat:', error);
        });
    }
}); 