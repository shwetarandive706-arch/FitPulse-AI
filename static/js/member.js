/**
 * FitPulse AI - Member Self-Service Module
 * Handles Member Profile, Dynamic QR Entry Pass & AI Fitness / Nutrition Planner
 */

const MemberModule = {
  memberQrInterval: null,

  loadProfile(user) {
    if (!user) return;
    document.getElementById("memPassName").textContent = user.name;
    document.getElementById("memPassId").textContent = `#FP-${user.id}`;
    
    const sub = user.subscription;
    if (sub && sub.is_active) {
      document.getElementById("memPassPlan").textContent = `${sub.plan_name} (${sub.plan_tier})`;
      document.getElementById("memPassDays").textContent = `${sub.days_remaining} Days Remaining`;
      document.getElementById("memPassExpiry").textContent = `Valid Until: ${sub.end_date}`;
      document.getElementById("memPassBadge").className = "badge badge-success";
      document.getElementById("memPassBadge").textContent = "ACTIVE";
    } else {
      document.getElementById("memPassPlan").textContent = "No Active Plan";
      document.getElementById("memPassDays").textContent = "Expired";
      document.getElementById("memPassExpiry").textContent = "Please renew at the front desk";
      document.getElementById("memPassBadge").className = "badge badge-danger";
      document.getElementById("memPassBadge").textContent = "EXPIRED";
    }

    document.getElementById("memTotalVisits").textContent = user.total_visits || 0;
    document.getElementById("memWeeklyAvg").textContent = `${user.avg_weekly_visits || 0} / wk`;
    document.getElementById("memLastVisit").textContent = user.last_visit ? user.last_visit.substring(0, 10) : 'Never';

    this.generateMemberQR(user.id);
  },

  async generateMemberQR(memberId) {
    const res = await fetch(`/api/checkin/generate-token?member_id=${memberId}`);
    const data = await res.json();
    if (!data.success) return;

    const tok = data.token_data.token;
    const box = document.getElementById("memberQrBox");
    box.innerHTML = "";
    new QRCode(box, {
      text: tok,
      width: 180,
      height: 180,
      colorDark: "#0a0d14",
      colorLight: "#ffffff",
      correctLevel: QRCode.CorrectLevel.H
    });

    let seconds = data.token_data.valid_seconds;
    const timerElem = document.getElementById("memberQrTimer");

    if (this.memberQrInterval) clearInterval(this.memberQrInterval);
    this.memberQrInterval = setInterval(() => {
      seconds--;
      if (timerElem) timerElem.textContent = `Refreshes in ${seconds}s`;
      if (seconds <= 0) {
        clearInterval(this.memberQrInterval);
        this.generateMemberQR(memberId);
      }
    }, 1000);
  },

  async generateAIPlan(e) {
    e.preventDefault();
    const weight = parseFloat(document.getElementById("aiWeight").value);
    const height = parseFloat(document.getElementById("aiHeight").value);
    const age = parseInt(document.getElementById("aiAge").value);
    const gender = document.getElementById("aiGender").value;
    const goal = document.getElementById("aiGoal").value;
    const diet = document.getElementById("aiDiet").value;
    const days = parseInt(document.getElementById("aiDays").value);

    try {
      const res = await fetch("/api/ai/recommend-fitness", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          weight_kg: weight,
          height_cm: height,
          age: age,
          gender: gender,
          fitness_goal: goal,
          dietary_pref: diet,
          days_per_week: days
        })
      });
      const data = await res.json();
      if (!data.success) return;

      const p = data.plan;
      document.getElementById("aiPlanResults").classList.remove("hidden");

      // Biometrics
      document.getElementById("resBmi").textContent = `${p.biometrics.bmi} (${p.biometrics.bmi_category})`;
      document.getElementById("resTdee").textContent = `${p.target_calories} kcal / day`;
      document.getElementById("resProtein").textContent = `${p.macronutrients.protein_g}g`;
      document.getElementById("resCarbs").textContent = `${p.macronutrients.carbs_g}g`;
      document.getElementById("resFat").textContent = `${p.macronutrients.fat_g}g`;
      document.getElementById("resWater").textContent = `${p.daily_water_liters} Liters`;

      // Routine
      const routineList = document.getElementById("resWorkoutRoutine");
      routineList.innerHTML = Object.entries(p.weekly_workout_schedule).map(([day, exercises]) => `
        <div style="margin-bottom:14px; background:var(--bg-card); padding:14px; border-radius:var(--radius-md); border:1px solid var(--border);">
          <strong style="color:var(--secondary);">${day}</strong>
          <ul style="margin-top:6px; margin-left:18px; font-size:0.85rem; color:var(--text-main);">
            ${exercises.map(ex => `<li>${ex}</li>`).join("")}
          </ul>
        </div>
      `).join("");

      // Diet Plan
      const mealList = document.getElementById("resMealPlan");
      mealList.innerHTML = Object.entries(p.daily_meal_plan).map(([meal, desc]) => `
        <div style="margin-bottom:10px; background:var(--bg-card); padding:12px; border-radius:var(--radius-md); border:1px solid var(--border);">
          <strong style="color:var(--primary); text-transform:capitalize;">${meal}:</strong>
          <span style="font-size:0.85rem; color:var(--text-main); margin-left:6px;">${desc}</span>
        </div>
      `).join("");

      App.showToast("Personalized AI Workout & Nutrition Plan generated!", "success");
    } catch (err) {
      App.showToast("Failed to generate AI plan: " + err.message, "error");
    }
  }
};
