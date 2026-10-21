/**
 * FitPulse AI - Admin Management Module
 * Handles KPIs, Member Roster, Subscriptions, AI Batch Churn Scan & Footfall Forecasting
 */

const AdminModule = {
  qrTimerInterval: null,

  async loadDashboard() {
    try {
      const res = await fetch("/api/admin/dashboard");
      const data = await res.json();
      if (!data.success) return;

      const m = data.metrics;
      document.getElementById("kpiTotalMembers").textContent = m.total_members;
      document.getElementById("kpiActiveSubs").textContent = m.active_subscribers;
      document.getElementById("kpiTodayCheckins").textContent = m.today_checkins;
      document.getElementById("kpiTotalRevenue").textContent = "₹" + m.total_revenue.toLocaleString();

      this.loadRecentCheckins();
      this.loadPeakHourForecast();
    } catch (err) {
      console.error("Dashboard error:", err);
    }
  },

  async loadRecentCheckins() {
    const res = await fetch("/api/checkin/recent");
    const data = await res.json();
    const tbody = document.getElementById("recentCheckinsTbody");
    if (!tbody) return;

    if (!data.records || data.records.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">No recent check-ins recorded.</td></tr>';
      return;
    }

    tbody.innerHTML = data.records.map(r => `
      <tr>
        <td><strong>${r.member_name}</strong><br><small style="color:var(--text-dim);">${r.member_email}</small></td>
        <td><span class="badge badge-info">${r.method.toUpperCase()}</span></td>
        <td>${r.checkin_time}</td>
        <td>${r.duration_mins} mins</td>
      </tr>
    `).join("");
  },

  async loadMembers() {
    const res = await fetch("/api/members");
    const data = await res.json();
    const tbody = document.getElementById("membersTableTbody");
    if (!tbody) return;

    App.state.members = data.members;
    document.getElementById("memberCountBadge").textContent = `${data.count} Members`;

    tbody.innerHTML = data.members.map(m => {
      const statusBadge = m.days_remaining > 0 ? 
        `<span class="badge badge-success">Active (${m.days_remaining}d)</span>` : 
        `<span class="badge badge-danger">Expired</span>`;

      return `
        <tr>
          <td>#${m.id}</td>
          <td><strong>${m.name}</strong><br><small style="color:var(--text-dim);">${m.phone || m.email}</small></td>
          <td>${m.plan_name ? `${m.plan_name} <br><small style="color:var(--secondary);">${m.plan_tier}</small>` : 'None'}</td>
          <td>${statusBadge}</td>
          <td>${m.total_checkins} visits</td>
          <td>${m.days_since_last_visit} days ago</td>
          <td>
            <button class="btn btn-secondary" style="padding:4px 8px; font-size:0.75rem;" onclick="AdminModule.openRenewModal(${m.id})">Renew</button>
            <button class="btn btn-primary" style="padding:4px 8px; font-size:0.75rem;" onclick="AdminModule.runMemberChurnScan(${m.id})">AI Scan</button>
          </td>
        </tr>
      `;
    }).join("");
  },

  async loadAIHub() {
    try {
      const res = await fetch("/api/ai/scan-all-churn");
      const data = await res.json();
      if (!data.success) return;

      const bk = data.risk_breakdown;
      document.getElementById("churnHighRiskCount").textContent = bk.high;
      document.getElementById("churnMedRiskCount").textContent = bk.medium;
      document.getElementById("churnLowRiskCount").textContent = bk.low;

      const tbody = document.getElementById("churnScanTbody");
      if (!tbody) return;

      tbody.innerHTML = data.results.map(r => `
        <tr>
          <td><strong>${r.member_name}</strong></td>
          <td>${r.plan_name}</td>
          <td><span class="badge badge-${r.risk_badge}">${r.risk_level} (${r.churn_probability}%)</span></td>
          <td>${r.risk_factors.join("<br>• ")}</td>
          <td><small style="color:var(--primary); font-weight:600;">${r.retention_action}</small></td>
        </tr>
      `).join("");
    } catch (err) {
      console.error("AI Hub scan error:", err);
    }
  },

  async runMemberChurnScan(memberId) {
    try {
      const res = await fetch(`/api/ai/predict-churn/${memberId}`);
      const data = await res.json();
      if (!data.success) return;

      const p = data.prediction;
      alert(`AI Churn Risk for ${p.member_name}:\n` +
            `• Risk Tier: ${p.risk_level} (${p.churn_probability}% Probability)\n` +
            `• Key Drivers:\n  - ${p.risk_factors.join('\n  - ')}\n` +
            `• Recommended Retention Action:\n  ${p.retention_action}`);
    } catch (err) {
      alert("AI scan failed: " + err.message);
    }
  },

  async loadPeakHourForecast() {
    const res = await fetch("/api/ai/peak-hours");
    const data = await res.json();
    if (!data.success) return;

    const f = data.forecast;
    document.getElementById("currOccupancyStatus").textContent = `${f.current_status.occupancy_percentage}% Capacity (${f.current_status.status})`;
    
    const container = document.getElementById("footfallBarChart");
    if (!container) return;

    container.innerHTML = f.hourly_breakdown.map(h => `
      <div style="display:flex; flex-direction:column; align-items:center; gap:4px; flex:1;">
        <div style="height:100px; width:100%; display:flex; align-items:flex-end; background:rgba(255,255,255,0.02); border-radius:4px;">
          <div style="width:100%; height:${h.occupancy_percentage}%; background: ${h.color === 'danger' ? 'var(--danger)' : (h.color === 'warning' ? 'var(--warning)' : 'var(--primary)')}; border-radius:4px; transition:height 0.5s ease;"></div>
        </div>
        <span style="font-size:0.65rem; color:var(--text-dim); font-family:var(--font-mono);">${h.hour}h</span>
      </div>
    `).join("");
  },

  async loadTurnstileQR() {
    const res = await fetch("/api/checkin/generate-token");
    const data = await res.json();
    if (!data.success) return;

    const tok = data.token_data.token;
    const qrContainer = document.getElementById("turnstileQrBox");
    qrContainer.innerHTML = "";
    new QRCode(qrContainer, {
      text: tok,
      width: 220,
      height: 220,
      colorDark: "#0a0d14",
      colorLight: "#ffffff",
      correctLevel: QRCode.CorrectLevel.H
    });

    let seconds = data.token_data.valid_seconds;
    const timerElem = document.getElementById("turnstileTimer");

    if (this.qrTimerInterval) clearInterval(this.qrTimerInterval);
    this.qrTimerInterval = setInterval(() => {
      seconds--;
      if (timerElem) timerElem.textContent = `Expires in: ${seconds}s (Dynamic Refresh)`;
      if (seconds <= 0) {
        clearInterval(this.qrTimerInterval);
        this.loadTurnstileQR();
      }
    }, 1000);
  },

  async simulateCheckin() {
    const select = document.getElementById("testMemberSelect");
    const memberId = select.value;
    if (!memberId) return alert("Select a member first.");

    // Generate token for this member
    const tokRes = await fetch(`/api/checkin/generate-token?member_id=${memberId}`);
    const tokData = await tokRes.json();
    const token = tokData.token_data.token;

    // Verify token
    const vRes = await fetch("/api/checkin/verify-token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, member_id: memberId })
    });
    const vData = await vRes.json();

    if (vData.success) {
      App.showToast(vData.message, "success");
      this.loadDashboard();
    } else {
      App.showToast(vData.message, "error");
    }
  },

  openRenewModal(memberId) {
    document.getElementById("renewMemberIdInput").value = memberId;
    document.getElementById("renewModal").classList.remove("hidden");
  },

  closeRenewModal() {
    document.getElementById("renewModal").classList.add("hidden");
  },

  async submitRenewal(e) {
    e.preventDefault();
    const memberId = document.getElementById("renewMemberIdInput").value;
    const planId = document.getElementById("renewPlanSelect").value;

    const res = await fetch("/api/subscriptions/assign", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ member_id: memberId, plan_id: planId })
    });
    const data = await res.json();
    if (data.success) {
      App.showToast("Subscription updated successfully!", "success");
      this.closeRenewModal();
      this.loadMembers();
      this.loadDashboard();
    } else {
      App.showToast(data.message, "error");
    }
  }
};
