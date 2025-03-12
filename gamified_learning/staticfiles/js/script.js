document.addEventListener("DOMContentLoaded", function() {
    console.log("Gamified Learning Platform Loaded!");
    let xpBar = document.getElementById("xp-bar");
    let xpValue = parseInt(xpBar.style.width);
    
    setTimeout(() => {
        xpBar.style.width = xpValue + "%";
    }, 300);

    let challengeBtn = document.getElementById("daily-challenge-btn");

    challengeBtn.addEventListener("click", function () {
        challengeBtn.innerText = "✅ Completed!";
        challengeBtn.disabled = true;
    });
});
