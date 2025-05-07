document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    
    // Theme toggle functionality
    themeToggle.addEventListener('click', toggleTheme);
    
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
    
    // Load saved theme
    loadSavedTheme();
    
    // Optional: Add some dynamic elements
    function createRandomParticles() {
        const particleContainer = document.querySelector('.particle-network');
        const numParticles = 5; // Add 5 more particles
        
        for (let i = 0; i < numParticles; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.top = `${Math.random() * 100}%`;
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.animationDuration = `${20 + Math.random() * 10}s`;
            particle.style.animationDelay = `${Math.random() * 5}s`;
            particleContainer.appendChild(particle);
        }
    }
    
    // Create some additional particles
    createRandomParticles();
}); 