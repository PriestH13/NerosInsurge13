document.addEventListener("DOMContentLoaded", () => {
  const toggleButtons = document.querySelectorAll(".btn-toggle-password");
  
  toggleButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const pwInput = btn.previousElementSibling;
      if (!pwInput) return;

      if (pwInput.type === "password") {
        pwInput.type = "text";
        btn.setAttribute("aria-label", "Nascondi password");
        btn.title = "Nascondi password";
      } else {
        pwInput.type = "password";
        btn.setAttribute("aria-label", "Mostra password");
        btn.title = "Mostra password";
      }
    });
  });

  //password 
  const password1 = document.getElementById("id_password1");
  const password2 = document.getElementById("id_password2");
  const feedback1 = document.getElementById("password-feedback");
  const feedback2 = document.getElementById("password2-feedback");
  const form = document.getElementById("register-form");

  function validatePasswords() {
    feedback1.textContent = "";
    feedback2.textContent = "";

    if (password1.value.length > 0 && password1.value.length < 8) {
      feedback1.textContent = "La password deve contenere almeno 8 caratteri.";
      feedback1.style.color = "var(--error-color)";
    } else if (password1.value.length >= 8) {
      feedback1.textContent = "Password valida.";
      feedback1.style.color = "var(--success-color)";
    }

    if (password2.value.length > 0 && password2.value !== password1.value) {
      feedback2.textContent = "Le password non corrispondono.";
      feedback2.style.color = "var(--error-color)";
    } else if (password2.value.length > 0 && password2.value === password1.value) {
      feedback2.textContent = "Password confermate.";
      feedback2.style.color = "var(--success-color)";
    }
  }

  password1.addEventListener("input", validatePasswords);
  password2.addEventListener("input", validatePasswords);

  form.addEventListener("submit", (e) => {
    if (password1.value.length < 8 || password2.value !== password1.value) {
      e.preventDefault();
      validatePasswords();
      password1.focus();
      alert("Correggi gli errori nel modulo prima di inviare.");
    }
  });
});
