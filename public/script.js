// Telegram WebApp Integration
const tg = window.Telegram?.WebApp;

// Initialize Telegram WebApp
if (tg) {
    tg.ready();
    tg.expand();

    // Apply Telegram theme colors if available
    document.documentElement.style.setProperty('--tg-theme-bg-color', tg.backgroundColor || '#0a0a0f');
}

// DOM Elements
const navTabs = document.querySelectorAll('.nav-tab');
const tabContents = document.querySelectorAll('.tab-content');
const feedbackForm = document.getElementById('feedback-form');
const submitBtn = document.getElementById('submit-btn');
const successMessage = document.getElementById('success-message');
const errorMessage = document.getElementById('error-message');
const errorText = document.getElementById('error-text');
const messageTextarea = document.getElementById('message');
const charCount = document.getElementById('char-count');

// Tab Navigation
navTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const targetTab = tab.dataset.tab;

        // Update nav tabs
        navTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        // Update content
        tabContents.forEach(content => {
            content.classList.remove('active');
            if (content.id === targetTab) {
                content.classList.add('active');
            }
        });

        // Haptic feedback for Telegram
        if (tg?.HapticFeedback) {
            tg.HapticFeedback.selectionChanged();
        }
    });
});

// Character Counter
if (messageTextarea && charCount) {
    messageTextarea.addEventListener('input', () => {
        const count = messageTextarea.value.length;
        charCount.textContent = count;

        if (count > 1800) {
            charCount.style.color = '#ef4444';
        } else {
            charCount.style.color = '';
        }
    });
}

// Form Submission
if (feedbackForm) {
    feedbackForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Reset messages
        successMessage.classList.add('hidden');
        errorMessage.classList.add('hidden');

        // Get form data
        const formData = new FormData(feedbackForm);
        const data = {
            name: formData.get('name') || 'Аноним',
            type: formData.get('type'),
            message: formData.get('message'),
            username: tg?.initDataUnsafe?.user?.username || null,
            userId: tg?.initDataUnsafe?.user?.id || null
        };

        // Validate
        if (!data.message || data.message.trim() === '') {
            showError('Пожалуйста, напишите сообщение');
            return;
        }

        // Show loading state
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;

        try {
            const response = await fetch('/api/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                // Success
                feedbackForm.classList.add('hidden');
                successMessage.classList.remove('hidden');

                // Haptic feedback
                if (tg?.HapticFeedback) {
                    tg.HapticFeedback.notificationOccurred('success');
                }

                // Reset form after a delay
                setTimeout(() => {
                    feedbackForm.reset();
                    charCount.textContent = '0';
                }, 1000);
            } else {
                showError(result.error || 'Произошла ошибка при отправке');
            }
        } catch (err) {
            console.error('Fetch error:', err);
            showError('Не удалось связаться с сервером');
        } finally {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }
    });
}

function showError(message) {
    errorText.textContent = message;
    errorMessage.classList.remove('hidden');

    if (tg?.HapticFeedback) {
        tg.HapticFeedback.notificationOccurred('error');
    }
}

// Reset form button (for sending another message)
document.addEventListener('click', (e) => {
    if (e.target.closest('.success-message')) {
        successMessage.classList.add('hidden');
        feedbackForm.classList.remove('hidden');
    }
});

// Smooth scroll for internal links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Add subtle parallax to background on scroll
let ticking = false;
window.addEventListener('scroll', () => {
    if (!ticking) {
        window.requestAnimationFrame(() => {
            const scroll = window.scrollY;
            const particles = document.querySelector('.bg-particles');
            if (particles) {
                particles.style.transform = `translateY(${scroll * 0.3}px)`;
            }
            ticking = false;
        });
        ticking = true;
    }
});

console.log('⚔️ Тени Эльдории WebApp загружен');
