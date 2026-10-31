const API_BASE_URL = window.location.hostname === "localhost" 
  ? "http://127.0.0.1:8000" 
  : "https://zh-official-backend.onrender.com";

let adminToken = "";

document.getElementById('btnLoginAdmin').addEventListener('click', async () => {
  const secret = document.getElementById('adminSecret').value.trim();
  if (!secret) return alert("Please supply key.");

  adminToken = secret;

  try {
    const res = await fetch(`${API_BASE_URL}/api/admin/stats`, {
      headers: { "Authorization": `Bearer ${adminToken}` }
    });

    if (!res.ok) throw new Error("Unauthorized access.");

    const stats = await res.json();
    document.getElementById('adminAuthSection').style.display = 'none';
    document.getElementById('adminDashboard').style.display = 'block';

    document.getElementById('statTotalConv').innerText = stats.total_conversions;
    document.getElementById('statTodayConv').innerText = stats.today_conversions;
    document.getElementById('statFailures').innerText = stats.failed_conversions;
    document.getElementById('statUsers').innerText = stats.active_users;

  } catch (err) {
    alert("Authorization Denied: " + err.message);
  }
});

document.getElementById('btnSaveConfig').addEventListener('click', async () => {
  const isMaint = document.getElementById('maintToggle').checked;

  try {
    const res = await fetch(`${API_BASE_URL}/api/admin/settings`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${adminToken}`
      },
      body: JSON.stringify({
        maintenance_mode: isMaint,
        telegram_alerts_active: true
      })
    });

    if (!res.ok) throw new Error("Failed to persist settings.");
    alert("Settings updated successfully.");
  } catch (e) {
    alert(e.message);
  }
});