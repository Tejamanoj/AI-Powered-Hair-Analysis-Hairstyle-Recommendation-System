// ===== AUTH.JS — Strong Password Validation =====

// ===== PASSWORD STRENGTH CHECKER =====
function checkPasswordStrength(password) {
  const result = {
    score: 0,
    checks: {
      length:    password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number:    /[0-9]/.test(password),
      special:   /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password),
    }
  };
  result.score = Object.values(result.checks).filter(Boolean).length;
  return result;
}

// ===== LOGIN =====
function login() {
  const email    = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  clearErrors();

  let valid = true;

  // Email validation
  if (!email) {
    showError("email", "Email is required");
    valid = false;
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    showError("email", "Enter a valid email address");
    valid = false;
  }

  // Password validation
  if (!password) {
    showError("password", "Password is required");
    valid = false;
  } else if (password.length < 8) {
    showError("password", "Password must be at least 8 characters");
    valid = false;
  }

  if (!valid) return;

  // ✅ All good — proceed to dashboard
  window.location.href = "dashboard.html";
}

// ===== SIGNUP =====
function signup() {
  const name     = document.getElementById("name").value.trim();
  const email    = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const confirm  = document.getElementById("confirmPassword")?.value;

  clearErrors();

  let valid = true;

  // Name validation
  if (!name) {
    showError("name", "Full name is required");
    valid = false;
  } else if (name.length < 2) {
    showError("name", "Name must be at least 2 characters");
    valid = false;
  }

  // Email validation
  if (!email) {
    showError("email", "Email is required");
    valid = false;
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    showError("email", "Enter a valid email address");
    valid = false;
  }

  // Strong password validation
  if (!password) {
    showError("password", "Password is required");
    valid = false;
  } else {
    const strength = checkPasswordStrength(password);
    if (!strength.checks.length) {
      showError("password", "Password must be at least 8 characters");
      valid = false;
    } else if (!strength.checks.uppercase) {
      showError("password", "Password must contain at least one uppercase letter (A-Z)");
      valid = false;
    } else if (!strength.checks.lowercase) {
      showError("password", "Password must contain at least one lowercase letter (a-z)");
      valid = false;
    } else if (!strength.checks.number) {
      showError("password", "Password must contain at least one number (0-9)");
      valid = false;
    } else if (!strength.checks.special) {
      showError("password", "Password must contain at least one special character (!@#$%^&*)");
      valid = false;
    }
  }

  // Confirm password
  if (confirm !== undefined && password !== confirm) {
    showError("confirmPassword", "Passwords do not match");
    valid = false;
  }

  if (!valid) return;

  // ✅ All good — proceed to login
  alert("Account created successfully! Please login.");
  window.location.href = "login.html";
}

// ===== TOGGLE PASSWORD VISIBILITY =====
function togglePassword(fieldId, btn) {
  const input = document.getElementById(fieldId);
  if (input.type === "password") {
    input.type = "text";
    btn.textContent = "🙈";
  } else {
    input.type = "password";
    btn.textContent = "👁";
  }
}

function clearFieldError(fieldId) {
  const input = document.getElementById(fieldId);
  if (!input) return;
  input.style.borderColor = "";
  const err = input.parentNode.querySelector(".error-msg");
  if (err) err.remove();
  const formErr = document.getElementById("formError");
  if (formErr) formErr.style.display = "none";
}

// ===== SHOW/CLEAR ERRORS =====
function showError(fieldId, message) {
  const input = document.getElementById(fieldId);
  if (!input) return;

  input.style.borderColor = "#e85a5a";

  // Remove existing error if any
  const existing = input.parentNode.querySelector(".error-msg");
  if (existing) existing.remove();

  const err = document.createElement("div");
  err.className = "error-msg";
  err.style.cssText = "color:#e85a5a; font-size:0.78rem; margin-top:6px; padding-left:2px;";
  err.textContent = "⚠ " + message;
  input.parentNode.appendChild(err);
}

function clearErrors() {
  document.querySelectorAll(".error-msg").forEach(e => e.remove());
  document.querySelectorAll("input").forEach(i => i.style.borderColor = "");
}

// ===== LIVE PASSWORD STRENGTH METER (signup only) =====
document.addEventListener("DOMContentLoaded", () => {
  const pwInput = document.getElementById("password");
  const meter   = document.getElementById("strengthMeter");
  const label   = document.getElementById("strengthLabel");

  if (!pwInput || !meter) return;

  pwInput.addEventListener("input", () => {
    const val      = pwInput.value;
    const strength = checkPasswordStrength(val);
    const score    = strength.score;

    const colors = ["#e85a5a", "#e85a5a", "#e8834a", "#f0c060", "#4acea8", "#4acea8"];
    const labels = ["", "Very Weak", "Weak", "Fair", "Strong", "Very Strong"];

    meter.style.width   = (score / 5 * 100) + "%";
    meter.style.background = colors[score];
    if (label) label.textContent = val.length > 0 ? labels[score] : "";

    // Show which rules are met
    const rules = document.getElementById("passwordRules");
    if (!rules) return;
    rules.innerHTML = `
      <div style="color:${strength.checks.length    ? '#4acea8':'#888899'}">
        ${strength.checks.length    ? '✓':'✗'} At least 8 characters
      </div>
      <div style="color:${strength.checks.uppercase ? '#4acea8':'#888899'}">
        ${strength.checks.uppercase ? '✓':'✗'} One uppercase letter (A-Z)
      </div>
      <div style="color:${strength.checks.lowercase ? '#4acea8':'#888899'}">
        ${strength.checks.lowercase ? '✓':'✗'} One lowercase letter (a-z)
      </div>
      <div style="color:${strength.checks.number    ? '#4acea8':'#888899'}">
        ${strength.checks.number    ? '✓':'✗'} One number (0-9)
      </div>
      <div style="color:${strength.checks.special   ? '#4acea8':'#888899'}">
        ${strength.checks.special   ? '✓':'✗'} One special character (!@#$%^&*)
      </div>
    `;
  });
});