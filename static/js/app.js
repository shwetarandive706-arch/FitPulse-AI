/**
 * FitPulse AI - Core Application Coordinator
 * Manages Auth State, Tab Routing, Toasts & Quick Demo Switchers
 */

const App = {
  state: {
    currentUser: null,
    activeTab: "dashboard",
    plans: [],
    members: []
  },

  init() {
    this.bindEvents();
    // Default to auto-login as admin for instant viva demonstration
    this.loginWithCredentials("admin", "admin123");
  },

  bindEvents() {
    // Navigation items
    document.querySelectorAll(".nav-item").forEach(item => {
      item.addEventListener("click", (e) => {
        e.preventDefault();
        const tab = item.getAttribute("data-tab");
        this.switchTab(tab);
      });
    });

    // Quick demo switcher buttons
    document.querySelectorAll(".demo-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const userType = btn.getAttribute("data-user");
        this.handleDemoSwitch(userType);
      });
    });

    // Logout
    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
      logoutBtn.addEventListener("click", () => this.logout());
    }
  },

  showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");
    if (!container) return;
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    const icon = type === "success" ? "✓" : (type === "error" ? "✕" : "ℹ");
    toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  },

  async loginWithCredentials(identifier, password) {
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ identifier, password })
      });
      const data = await res.json();
      if (data.success) {
        this.state.currentUser = data.user;
        const loginModal = document.getElementById("loginModal");
        if (loginModal) loginModal.classList.add("hidden");
        this.renderUserUI();
        this.showToast(data.message, "success");
      } else {
        this.showToast(data.message, "error");
      }
    } catch (err) {
      this.showToast("Connection error: " + err.message, "error");
    }
  },

  async handleLoginForm(e) {
    e.preventDefault();
    const identifier = document.getElementById("loginIdentifier").value;
    const password = document.getElementById("loginPassword").value;
    await this.loginWithCredentials(identifier, password);
  },

  handleDemoSwitch(userType) {
    document.querySelectorAll(".demo-btn").forEach(b => b.classList.remove("active"));
    const activeBtn = document.querySelector(`.demo-btn[data-user="${userType}"]`);
    if (activeBtn) activeBtn.classList.add("active");

    if (userType === "admin") {
      this.loginWithCredentials("admin", "admin123");
    } else if (userType === "member1") {
      this.loginWithCredentials("member1", "1234");
    } else if (userType === "member3") {
      this.loginWithCredentials("member3", "1234");
    } else if (userType === "member5") {
      this.loginWithCredentials("member5", "1234");
    }
  },

  renderUserUI() {
    const user = this.state.currentUser;
    if (!user) return;

    // Update Topbar Info
    document.getElementById("topUserName").textContent = user.name;
    document.getElementById("topUserRole").textContent = user.role.toUpperCase();
    document.getElementById("topUserAvatar").textContent = user.name.charAt(0).toUpperCase();

    // Toggle Role-based Navigation
    const isAdmin = user.role === "admin";
    document.querySelectorAll(".admin-only").forEach(el => {
      el.classList.toggle("hidden", !isAdmin);
    });
    document.querySelectorAll(".member-only").forEach(el => {
      el.classList.toggle("hidden", isAdmin);
    });

    if (isAdmin) {
      this.switchTab("dashboard");
      AdminModule.loadDashboard();
    } else {
      this.switchTab("member-portal");
      MemberModule.loadProfile(user);
    }
  },

  switchTab(tabId) {
    this.state.activeTab = tabId;
    document.querySelectorAll(".nav-item").forEach(item => {
      item.classList.toggle("active", item.getAttribute("data-tab") === tabId);
    });
    document.querySelectorAll(".tab-view").forEach(view => {
      view.classList.toggle("hidden", view.id !== `tab-${tabId}`);
    });

    // Tab-specific initializers
    if (tabId === "dashboard") AdminModule.loadDashboard();
    if (tabId === "members") AdminModule.loadMembers();
    if (tabId === "ai-hub") AdminModule.loadAIHub();
    if (tabId === "qr-terminal") AdminModule.loadTurnstileQR();
    if (tabId === "member-portal") MemberModule.loadProfile(this.state.currentUser);
  },

  async logout() {
    await fetch("/api/auth/logout", { method: "POST" });
    this.state.currentUser = null;
    this.showToast("Logged out successfully.", "info");
    this.handleDemoSwitch("admin");
  }
};

window.addEventListener("DOMContentLoaded", () => App.init());
