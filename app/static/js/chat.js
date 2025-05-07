// Add this to your existing chat.js file or create a new one

// Function to show typing indicator
function showTypingIndicator() {
    const chatContainer = document.querySelector('.chat-container');
    
    // Create typing indicator
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.id = 'typing-indicator';
    
    // Add the animated dots
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('span');
        typingIndicator.appendChild(dot);
    }
    
    // Add to chat container
    chatContainer.appendChild(typingIndicator);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Function to hide typing indicator
function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Update the sendMessage function to show/hide typing indicator
async function sendMessage() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();
    
    if (message === '') return;
    
    // Clear input
    messageInput.value = '';
    
    // Add user message to chat
    addMessageToChat('user', message);
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Send message to server
        const response = await fetch(`/send_message/${currentChatId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });
        
        const data = await response.json();
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Add assistant response to chat
        addMessageToChat('assistant', data.response);
    } catch (error) {
        console.error('Error sending message:', error);
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Show error message
        addMessageToChat('assistant', 'Sorry, there was an error processing your message. Please try again.');
    }
}

// Enhanced function to add messages with animations
function addMessageToChat(role, content) {
    const chatContainer = document.querySelector('.chat-container');
    
    const messageElement = document.createElement('div');
    messageElement.className = `message ${role}-message`;
    
    // Add animation class
    messageElement.style.opacity = '0';
    
    // Set message content
    messageElement.textContent = content;
    
    // Add to chat container
    chatContainer.appendChild(messageElement);
    
    // Trigger animation
    setTimeout(() => {
        messageElement.style.opacity = '1';
    }, 10);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Add event listener for input to activate send button
document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.querySelector('.send-button');
    
    messageInput.addEventListener('input', function() {
        if (this.value.trim() !== '') {
            sendButton.classList.add('active');
        } else {
            sendButton.classList.remove('active');
        }
    });
    
    // Add enter key support
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}); 