document.addEventListener("DOMContentLoaded", function () {
    let xpBar = document.getElementById("xp-bar");
    let xpValue = parseInt(xpBar.style.width);

    // Smooth XP bar fill effect
    setTimeout(() => {
        xpBar.style.width = xpValue + "%";
    }, 300);

    // Daily challenge button effect
    let challengeBtn = document.getElementById("daily-challenge-btn");
    challengeBtn.addEventListener("click", function () {
        challengeBtn.innerText = "✅ Completed!";
        challengeBtn.disabled = true;
    });
});
