// static/js/click_canvas.js

function initializeCanvas(imageUrl, postUrl) {
    const canvas = document.getElementById('click-canvas');
    if (!canvas) {
        console.error("Canvas element #click-canvas not found!");
        return;
    }
    const ctx = canvas.getContext('2d');
    
    const clickCounterEl = document.getElementById('click-counter');
    const submitBtn = document.getElementById('submit-clicks');
    const resetBtn = document.getElementById('reset-clicks');
    const errorEl = document.getElementById('error-message');

    let clicks = [];
    const MAX_CLICKS = 3;

    const bgImage = new Image();
    bgImage.src = imageUrl;
    bgImage.onload = () => {
        canvas.width = bgImage.width;
        canvas.height = bgImage.height;
        redraw();
    };
    bgImage.onerror = () => {
        errorEl.textContent = 'Failed to load challenge image.';
        errorEl.style.display = 'block';
    };
    
    function redraw() {
        ctx.drawImage(bgImage, 0, 0, canvas.width, canvas.height);
        clicks.forEach((click, index) => {
            drawClickMarker(click.x, click.y, index + 1);
        });
    }

    function drawClickMarker(x, y, number) {
        ctx.fillStyle = 'rgba(255, 165, 0, 0.7)';
        ctx.strokeStyle = '#FFFFFF';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(x, y, 15, 0, 2 * Math.PI);
        ctx.fill();
        ctx.stroke();
        ctx.fillStyle = '#FFFFFF';
        ctx.font = 'bold 16px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(number, x, y);
    }
    
    canvas.addEventListener('click', (event) => {
        if (clicks.length >= MAX_CLICKS) { return; }
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        clicks.push({ x, y });
        updateUI();
        redraw();
    });

    resetBtn.addEventListener('click', () => {
        clicks = [];
        updateUI();
        redraw();
    });

    submitBtn.addEventListener('click', async () => {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Verifying...';
        errorEl.style.display = 'none';

        try {
            const response = await fetch(postUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ clicks: clicks }),
            });

            const data = await response.json();

            // --- THIS IS THE FIX ---
            // The new logic prioritizes the redirect URL from the server.
            // If the server provides a redirect URL for ANY reason (success or failure), we use it.
            if (data.redirect_url) {
                // This will now correctly handle the failure case during login
                // and redirect to the step_up_challenge page.
                window.location.href = data.redirect_url;
            } else {
                // If there is no redirect URL, it must be a hard error (e.g., during registration).
                // In this case, we show the error message.
                throw new Error(data.error || "An unknown verification error occurred.");
            }
        } catch (err) {
            // This catch block will now only be triggered for hard errors.
            errorEl.textContent = err.message;
            errorEl.style.display = 'block';
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Clicks';
        }
    });

    function updateUI() {
        clickCounterEl.textContent = clicks.length;
        submitBtn.disabled = clicks.length !== MAX_CLICKS;
        errorEl.style.display = 'none';
    }

    updateUI();
}