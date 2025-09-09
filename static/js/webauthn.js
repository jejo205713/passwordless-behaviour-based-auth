// static/js/webauthn.js

// --- Helper Functions (Unaltered) ---
function base64urlToBuffer(base64url) {
    if (typeof base64url !== "string") {
        throw new Error("Expected base64url string, got: " + typeof base64url);
    }
    const padding = "=".repeat((4 - (base64url.length % 4)) % 4);
    const base64 = base64url.replace(/-/g, "+").replace(/_/g, "/") + padding;
    const str = atob(base64);
    const bytes = new Uint8Array(str.length);
    for (let i = 0; i < str.length; i++) {
        bytes[i] = str.charCodeAt(i);
    }
    return bytes.buffer;
}

function bufferToBase64url(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = "";
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    const base64 = btoa(binary);
    return base64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

// --- Main Flow ---
async function initiateWebAuthn(options, formPostUrl, failureRedirectUrl) {
    const button = document.getElementById('webauthn-button');
    const statusMessage = document.getElementById('status-message');

    if (!button || !statusMessage) { return; }

    const startCeremony = async () => {
        if (!navigator.credentials || !navigator.credentials.create) {
            statusMessage.textContent = "Error: WebAuthn not supported or page is not secure (localhost/HTTPS).";
            button.disabled = true;
            return;
        }

        try {
            button.disabled = true;
            statusMessage.textContent = 'Waiting for fingerprint sensor...';
            
            const isRegistration = !!options.user;
            let credential;

            if (isRegistration) {
                options.challenge = base64urlToBuffer(options.challenge);
                options.user.id = base64urlToBuffer(options.user.id);
                credential = await navigator.credentials.create({ publicKey: options });
            } else {
                options.challenge = base64urlToBuffer(options.challenge);
                if (options.allowCredentials) {
                    options.allowCredentials.forEach(cred => cred.id = base64urlToBuffer(cred.id));
                }
                credential = await navigator.credentials.get({ publicKey: options });
            }
            
            await sendCredentialToServer(credential, formPostUrl);

        } catch (err) {
            console.error("WebAuthn browser-level error:", err);

            // --- THIS IS THE FIX ---
            // This 'catch' block handles browser errors (e.g., user clicks Cancel, timeout).
            // If we are in a login flow, `failureRedirectUrl` will be a string.
            if (failureRedirectUrl) {
                // Display the user-friendly message you requested.
                statusMessage.textContent = "Moving to image challenge...";
                statusMessage.style.color = 'var(--secondary-color)'; // Use a neutral color
                
                // Redirect to the next challenge after a short delay for the user to see the message.
                setTimeout(() => {
                    window.location.href = failureRedirectUrl;
                }, 750); // 0.75 second delay
            } else {
                // Otherwise, it's a registration failure, so we show the technical error.
                statusMessage.textContent = `Error: ${err.message}. Please try again.`;
                statusMessage.style.color = 'var(--error-color)';
                button.disabled = false;
            }
        }
    };

    button.addEventListener('click', startCeremony);
    startCeremony();
}

async function sendCredentialToServer(payload, url) {
    // This function handles the response from the server AFTER a successful browser interaction.
    const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });
    const data = await res.json();

    // If the server provides a redirect URL for any reason (success or failure), we use it.
    if (data.redirect_url) {
        window.location.href = data.redirect_url;
    } else {
        // If there is no redirect, it must be a hard error during registration.
        const statusMessage = document.getElementById('status-message');
        if (statusMessage) {
            statusMessage.textContent = `Error: ${data.error || "Unknown server error"}`;
            statusMessage.style.color = 'var(--error-color)';
            document.getElementById('webauthn-button').disabled = false;
        }
    }
}