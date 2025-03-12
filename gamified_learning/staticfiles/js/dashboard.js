document.addEventListener("DOMContentLoaded", function () {
    let xpBar = document.querySelector(".progress-bar");
    let xpValue = xpBar.getAttribute("data-xp");

    // Animate XP Bar Fill
    setTimeout(() => {
        xpBar.style.width = xpValue + "%";
    }, 300);

    // Daily Challenge Button Effect
    let challengeBtn = document.getElementById("daily-challenge-btn");
    challengeBtn.addEventListener("click", function () {
        challengeBtn.innerText = "✅ Completed!";
        challengeBtn.style.background = "linear-gradient(90deg, #ff7300, #ffeb00)";
        challengeBtn.style.color = "#0a0a0a";
        challengeBtn.disabled = true;
    });

    // Hover Glowing Effect
    let buttons = document.querySelectorAll(".task-btn, .challenge-btn, .leaderboard-btn");
    buttons.forEach(button => {
        button.addEventListener("mouseenter", function () {
            button.style.boxShadow = "0px 0px 25px rgba(0, 255, 255, 0.9)";
        });
        button.addEventListener("mouseleave", function () {
            button.style.boxShadow = "0px 0px 15px rgba(0, 255, 255, 0.5)";
        });
    });
});
