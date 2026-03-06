// Work 24 - Main JavaScript File

class Work24App {
    constructor() {
        this.currentLanguage = localStorage.getItem('work24_language') || 'english';
        this.init();
    }

    init() {
        this.setupLanguageModal();
        this.setupNavigation();
        this.setupSearch();
        this.setupForms();
        this.setupAnimations();
        this.checkFirstVisit();
    }

    // Language Management
    checkFirstVisit() {
        if (!localStorage.getItem('work24_visited')) {
            this.showLanguageModal();
            localStorage.setItem('work24_visited', 'true');
        }
    }

    showLanguageModal() {
        const modal = document.getElementById('languageModal');
        if (modal) {
            modal.style.display = 'flex';
        }
    }

    hideLanguageModal() {
        const modal = document.getElementById('languageModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    setupLanguageModal() {
        const languageButtons = document.querySelectorAll('.language-option');
        languageButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const language = e.target.dataset.lang;
                this.setLanguage(language);
                this.hideLanguageModal();
            });
        });

        // Close modal on outside click
        const modal = document.getElementById('languageModal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideLanguageModal();
                }
            });
        }
    }

    setLanguage(language) {
        this.currentLanguage = language;
        localStorage.setItem('work24_language', language);
        
        // Redirect to set language in session
        window.location.href = `/set_language/${language}`;
    }

    // Navigation
    // Navigation
setupNavigation() {
    // Burger menu functionality
    const burgerMenu = document.getElementById('burgerMenu');
    const navMenu = document.getElementById('navMenu');

    if (burgerMenu && navMenu) {
        burgerMenu.addEventListener('click', () => {
            burgerMenu.classList.toggle('active');
            navMenu.classList.toggle('active');
        });

        // Close menu when clicking on a link
        navMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                burgerMenu.classList.remove('active');
                navMenu.classList.remove('active');
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!burgerMenu.contains(e.target) && !navMenu.contains(e.target)) {
                burgerMenu.classList.remove('active');
                navMenu.classList.remove('active');
            }
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

    // Search Functionality
    setupSearch() {
        const searchInput = document.getElementById('searchInput');
        const searchResults = document.getElementById('searchResults');
        const categoryFilter = document.getElementById('categoryFilter');

        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.performSearch(e.target.value);
                }, 300);
            });
        }

        if (categoryFilter) {
            categoryFilter.addEventListener('change', (e) => {
                this.filterByCategory(e.target.value);
            });
        }
    }

    async performSearch(query) {
        if (query.length < 2) return;

        try {
            const response = await fetch(`/api/search_workers?q=${encodeURIComponent(query)}`);
            const results = await response.json();
            this.displaySearchResults(results);
        } catch (error) {
            console.error('Search error:', error);
        }
    }

    displaySearchResults(results) {
        const container = document.getElementById('searchResults');
        if (!container) return;

        if (results.length === 0) {
            container.innerHTML = '<p class="text-center">No results found</p>';
            return;
        }

        const html = results.map(item => `
            <div class="profile-card">
                <div class="profile-header">
                    <div class="profile-avatar">${item.name.charAt(0)}</div>
                    <div class="profile-info">
                        <h3>${item.name}</h3>
                        <div class="profile-rating">
                            <span class="stars">${this.generateStars(item.rating)}</span>
                            <span>${item.rating} (${item.total_reviews} reviews)</span>
                        </div>
                    </div>
                </div>
                <div class="profile-details">
                    <div class="detail-item">
                        <span>🔧</span>
                        <span>${item.category}</span>
                    </div>
                    <div class="detail-item">
                        <span>📅</span>
                        <span>${item.experience} years experience</span>
                    </div>
                    <div class="detail-item">
                        <span>📱</span>
                        <span>${item.phone}</span>
                    </div>
                </div>
                <div class="profile-actions">
                    <button class="btn btn-primary btn-small" onclick="bookService(${item.id})">Book Now</button>
                    <button class="btn btn-secondary btn-small" onclick="viewProfile(${item.id})">View Profile</button>
                    <button class="btn btn-secondary btn-small" onclick="chatWithWorker(${item.id})">Chat</button>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

        generateStars(rating) {
        const fullStars = Math.floor(rating);
        const halfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
        
        return '★'.repeat(fullStars) + 
               (halfStar ? '☆' : '') + 
               '☆'.repeat(emptyStars);
    }

    filterByCategory(category) {
        const url = new URL(window.location);
        if (category) {
            url.searchParams.set('category', category);
        } else {
            url.searchParams.delete('category');
        }
        window.location.href = url.toString();
    }

    // Form Handling
    setupForms() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });
        });

        // Real-time validation
        const inputs = document.querySelectorAll('.form-control');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
        });
    }

    validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('.form-control[required]');
        
        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        return isValid;
    }

    validateField(field) {
        const value = field.value.trim();
        const fieldType = field.type;
        const fieldName = field.name;
        let isValid = true;
        let errorMessage = '';

        // Remove existing error
        this.clearFieldError(field);

        // Required field validation
        if (field.hasAttribute('required') && !value) {
            errorMessage = 'This field is required';
            isValid = false;
        }
        // Email validation
        else if (fieldType === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                errorMessage = 'Please enter a valid email address';
                isValid = false;
            }
        }
        // Phone validation
        else if (fieldName === 'phone' && value) {
            const phoneRegex = /^[6-9]\d{9}$/;
            if (!phoneRegex.test(value)) {
                errorMessage = 'Please enter a valid 10-digit phone number';
                isValid = false;
            }
        }
        // Aadhar validation
        else if (fieldName === 'aadhar' && value) {
            const aadharRegex = /^\d{12}$/;
            if (!aadharRegex.test(value)) {
                errorMessage = 'Please enter a valid 12-digit Aadhar number';
                isValid = false;
            }
        }
        // GST validation
        else if (fieldName === 'gst_number' && value) {
            const gstRegex = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/;
            if (!gstRegex.test(value)) {
                errorMessage = 'Please enter a valid GST number';
                isValid = false;
            }
        }

        if (!isValid) {
            this.showFieldError(field, errorMessage);
        }

        return isValid;
    }

    showFieldError(field, message) {
        field.classList.add('error');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }

    clearFieldError(field) {
        field.classList.remove('error');
        const errorMessage = field.parentNode.querySelector('.error-message');
        if (errorMessage) {
            errorMessage.remove();
        }
    }

    // Animations
    setupAnimations() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        // Observe elements for animation
        document.querySelectorAll('.service-card, .profile-card, .stat-card').forEach(el => {
            observer.observe(el);
        });
    }

    // Utility Methods
    showLoading(element) {
        element.innerHTML = '<div class="loading"></div>';
    }

    hideLoading() {
        document.querySelectorAll('.loading').forEach(el => el.remove());
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Global Functions
function bookService(workerId) {
    // Implement booking functionality
    console.log('Booking service for worker:', workerId);
    app.showNotification('Booking feature coming soon!', 'info');
}

function viewProfile(workerId) {
    // Implement profile view
    console.log('Viewing profile for worker:', workerId);
    window.location.href = `/worker/${workerId}`;
}

function chatWithWorker(workerId) {
    // Implement chat functionality
    console.log('Starting chat with worker:', workerId);
    app.showNotification('Chat feature coming soon!', 'info');
}

function contactSeller(sellerId) {
    console.log('Contacting seller:', sellerId);
    app.showNotification('Contact feature coming soon!', 'info');
}

function addToCart(materialId) {
    console.log('Adding to cart:', materialId);
    app.showNotification('Item added to cart!', 'success');
}

// Initialize app when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new Work24App();
});

// Service Worker for PWA (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

