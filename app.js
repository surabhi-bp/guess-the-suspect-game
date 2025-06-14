document.getElementById("ask-form").addEventListener("submit", function (e) {
  e.preventDefault(); // prevent page reload

  const suspect = document.getElementById("suspect").value;
  const question = document.getElementById("question").value;

  // Check inputs
  if (!suspect || !question) {
    alert("Please select both a suspect and a question.");
    return;
  }

  fetch("/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ suspect, question }),
  })
    .then((res) => {
      if (!res.ok) {
        return res.json().then((err) => Promise.reject(err));
      }
      return res.json();
    })
    .then((data) => {
      const log = data.log;
      const logDiv = document.getElementById("log");
      logDiv.innerHTML = ""; // clear previous log

      log.forEach((entry) => {
        const div = document.createElement("div");
        div.className = "log-entry";
        div.innerHTML = `<strong>${entry.suspect}:</strong> "${entry.answer}"`;
        logDiv.appendChild(div);
      });

      // Show forensic hint after round 2
      if (data.show_hint) {
        document.getElementById("hint-container").innerHTML = `
          <div class="neon-hint">
            🧬 <strong>FORENSIC HINT UNLOCKED:</strong><br>
            - Poison was found <strong>only</strong> in the glass, not the wine bottle.<br>
            - The butler confirms he served the wine.
          </div>
        `;
      }

      // If 4 questions are over, disable further asking and show final guess button
      if (data.game_over) {
        document.getElementById("conclusion-btn").innerHTML = `
          <a href="/conclusion" class="btn btn-warning">
            🧠 Guess the Murderer
          </a>
        `;

        document
          .getElementById("ask-form")
          .querySelector("button[type=submit]").disabled = true;
      }
    })
    .catch((err) => {
      console.error("Error:", err);
      alert(err.error || "An error occurred while processing your request.");
    });
});
