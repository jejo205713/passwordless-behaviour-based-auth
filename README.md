# Adaptive Behavioral Authentication System

This project is a web application, built with Streamlit, that demonstrates a modern, multi-layered, passwordless authentication system. It goes beyond simple passwords by verifying a user's identity through a combination of **fingerprint biometrics** and their unique, **personalized behavioral profiles**.

The system implements an **adaptive step-up authentication** flow: a fast, convenient primary challenge is presented first, and only if it fails does the user "step-up" to a more robust secondary challenge.

---

## 🚀 Core Features

*   **Login-First Design**: A clean, professional UI that prioritizes the login flow for returning users.
*   **Passwordless Primary Factor**: Securely registers and authenticates users with their device's built-in **fingerprint scanner** via the WebAuthn API.
*   **Personalized Behavioral Profiling**:
    *   **Typing Dynamics**: Creates a baseline of a user's natural typing speed and rhythm.
    *   **Cognitive Biometrics (Click Patterns)**: Creates a baseline of a user's unique "click passphrase" on an image.
*   **Adaptive Step-Up Authentication**:
    1.  The primary login challenge is the fast and convenient **Image Click Test**.
    2.  If the click pattern is incorrect, the user is not locked out. Instead, they are "stepped-up" to a secondary challenge that combines **Typing Analysis** and a **Secret Passkey**.
*   **Secret Passkey Recovery**: During registration, a one-time secret passkey is generated, providing a secure backup verification method.

---

## ⚙️ How It Works: The Authentication Flow

### Registration Flow
1.  A new user provides their email and registers their device using their fingerprint.
2.  They are guided to create their personalized behavioral profile:
    *   They type a challenge sentence three times to establish a **typing speed baseline**.
    *   They click on three memorable points on an image to establish a **click pattern baseline**.
3.  A unique **Secret Passkey** is generated, which they are prompted to save securely.

### Login Flow
1.  The user enters their email and is prompted to use their **fingerprint**.
2.  **Primary Challenge**: They are immediately shown the image and must click their three secret points in the correct order.
    *   **On Success**: Access to the dashboard is granted instantly.
3.  **Step-Up Challenge (only if clicks fail)**: The user is presented with a recovery screen where they must:
    *   Type the challenge sentence (testing their typing behavior against their baseline).
    *   Enter their saved **Secret Passkey**.
    *   **On Success**: Access is granted.
    *   **On Failure**: Access is denied.

---
## 📸 Gallery

<p align="center">
   <img src="https://github.com/jejo205713/passwordless-behaviour-based-auth/blob/main/img/home.png" width="45%" />
   <img src="https://github.com/jejo205713/passwordless-behaviour-based-auth/blob/main/img/biometric.png" width="45%" />
</p>

<p align="center">
   <img src="https://github.com/jejo205713/passwordless-behaviour-based-auth/blob/main/img/img%20challenge.png" width="45%" />
   <img src="https://github.com/jejo205713/passwordless-behaviour-based-auth/blob/main/img/behaviour-based-auth.png" width="45%" />
</p>

---
## 💻 Setup and Installation for Windows

Follow these instructions to set up and run the project on your Windows machine using PowerShell.

### Prerequisites
*   **Git**: You must have Git installed to clone the repository.
*   **Python 3.11**: This project requires a stable version of Python. The newest versions (3.12+) may cause issues with library installations. We strongly recommend **Python 3.11**.
    *   You can download it from the [official Python website](https://www.python.org/downloads/windows/).
    *   **IMPORTANT**: During installation, make sure to check the box that says **"Add python.exe to PATH"**.

### Step-by-Step Instructions

**1. Clone the Repository**
Open PowerShell and clone the project from GitHub.
```powershell
git clone <your-github-repository-url>
cd passwordless-behaviour-based-auth-main
```
**2. Create the Virtual Environment**
This creates an isolated environment for the project's dependencies.
code
Powershell
```
# This command specifically uses Python 3.11 to create the venv folder
py -3.11 -m venv venv
```
3. Activate the Virtual Environment
You must activate the environment in every new terminal session before working on the project.
```powershell
.\venv\Scripts\Activate.ps1
```
Your terminal prompt should now start with `(venv)`.

> **Troubleshooting**: If you get a red error message about "execution of scripts is disabled", run the following command to allow scripts for your current session, then try activating again:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`

**4. Install Dependencies**
With the environment active, install all the required libraries from the `requirements.txt` file.
```powershell
pip install -r requirements.txt
```
## ▶️ Running the Application

**1. Add a Background Image**
Before running, you must add an image for the click challenge.
*   Find any image file (e.g., a `.jpg` or `.png`).
*   Copy it into the root of the project folder (`passwordless-behaviour-based-auth-main`).
*   Rename the file to **`background.png`**.

**2. Launch the Streamlit App**
Make sure your virtual environment is still active (`(venv)` is visible in your prompt) and run the following command:
```powershell
streamlit run app.py
```

