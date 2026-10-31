// Base API configuration
const API_BASE_URL = window.location.hostname === "localhost" 
  ? "http://127.0.0.1:8000" 
  : "https://zh-official-backend.onrender.com"; // Replace with your Render URL

let captchaA = 0;
let captchaB = 0;

// Initialize Math Captcha
function generateCaptcha() {
  captchaA = Math.floor(Math.random() * 20) + 1;
  captchaB = Math.floor(Math.random() * 15) + 1;
  document.getElementById('captchaQuestion').innerText = `${captchaA} + ${captchaB} = ?`;
  document.getElementById('captchaAnswer').value = '';
}

// Fetch and render public live logs
async function fetchActivityLogs() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/tokens/recent`);
    if (!res.ok) return;
    const logs = await res.json();
    const tbody = document.getElementById('activityTableBody');
    tbody.innerHTML = '';

    if (logs.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No conversions logged yet.</td></tr>';
      return;
    }

    logs.forEach(log => {
      const row = document.createElement('tr');
      const badgeClass = log.status === 'SUCCESS' ? 'badge-success' : 'badge-failed';
      const formattedTime = new Date(log.created_at).toLocaleTimeString();
      
      row.innerHTML = `
        <td>#${log.id}</td>
        <td><code>${log.conversion_type}</code></td>
        <td><code>${log.result_token_hint}</code></td>
        <td><span class="${badgeClass}">${log.status}</span></td>
        <td style="color: var(--text-muted);">${formattedTime}</td>
      `;
      tbody.appendChild(row);
    });
  } catch (err) {
    console.error("Telemetry failed:", err);
  }
}

// Handle Form Submission
document.getElementById('conversionForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const rawToken = document.getElementById('rawToken').value.trim();
  const conversionType = document.getElementById('conversionType').value;
  const telegramUsername = document.getElementById('telegramUser').value.replace('@', '').trim();
  const userAnswer = parseInt(document.getElementById('captchaAnswer').value, 10);
  const btn = document.getElementById('btnSubmit');

  // Verify challenge
  if (userAnswer !== (captchaA + captchaB)) {
    alert("Incorrect human verification challenge answer.");
    generateCaptcha();
    return;
  }

  btn.disabled = true;
  btn.innerText = "PROCESSING TRANSFORMATION...";

  try {
    const payload = {
      raw_token: rawToken,
      conversion_type: conversionType,
      telegram_username: telegramUsername || null,
      captcha_solution: String(userAnswer)
    };

    const response = await fetch(`${API_BASE_URL}/api/tokens/convert`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Conversion pipeline failed.");
    }

    // Display Output
    const resultBox = document.getElementById('resultBox');
    const tokenOutput = document.getElementById('tokenOutput');
    tokenOutput.innerText = data.converted_token;
    resultBox.style.display = "block";

    // Refresh history
    fetchActivityLogs();
  } catch (err) {
    alert("Error: " + err.message);
  } finally {
    btn.disabled = false;
    btn.innerText = "CONVERT CREDENTIAL";
    generateCaptcha();
  }
});

// Copy Token
document.getElementById('btnCopy').addEventListener('click', () => {
  const token = document.getElementById('tokenOutput').innerText;
  navigator.clipboard.writeText(token).then(() => {
    const copyBtn = document.getElementById('btnCopy');
    copyBtn.innerText = "✅ Copied to Clipboard!";
    setTimeout(() => { copyBtn.innerText = "📋 Copy Token to Clipboard"; }, 2500);
  });
});

// Initialization
window.addEventListener('DOMContentLoaded', () => {
  generateCaptcha();
  fetchActivityLogs();
  setInterval(fetchActivityLogs, 10000); // Poll telemetry every 10s
});