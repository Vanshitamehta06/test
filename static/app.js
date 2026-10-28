(() => {
  const form = document.getElementById("auth-form");
  const email = document.getElementById("email");
  const password = document.getElementById("password");
  const submit = document.getElementById("submit");
  const message = document.getElementById("message");
  const toggle = document.getElementById("toggle-password");
  const tabs = document.querySelectorAll(".tab");
  let mode = "login";

  function setError(field, text) {
    document.querySelector(`.field-error[data-for="${field.id}"]`).textContent = text;
    field.setAttribute("aria-invalid", text ? "true" : "false");
  }

  function validate() {
    let ok = true;
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email.value.trim())) {
      setError(email, "Enter a valid email address.");
      ok = false;
    } else {
      setError(email, "");
    }
    if (password.value.length < 8) {
      setError(password, "Password must be at least 8 characters.");
      ok = false;
    } else {
      setError(password, "");
    }
    return ok;
  }

  function show(text, kind) {
    message.textContent = text;
    message.className = kind;
  }

  tabs.forEach((tab) =>
    tab.addEventListener("click", () => {
      mode = tab.dataset.mode;
      tabs.forEach((t) => {
        t.classList.toggle("active", t === tab);
        t.setAttribute("aria-selected", String(t === tab));
      });
      submit.textContent = mode === "login" ? "Sign in" : "Create account";
      password.autocomplete = mode === "login" ? "current-password" : "new-password";
      show("", "");
    })
  );

  toggle.addEventListener("click", () => {
    const hidden = password.type === "password";
    password.type = hidden ? "text" : "password";
    toggle.textContent = hidden ? "Hide" : "Show";
    toggle.setAttribute("aria-label", hidden ? "Hide password" : "Show password");
  });

  [email, password].forEach((field) => field.addEventListener("blur", validate));

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!validate()) return;
    submit.disabled = true;
    show(mode === "login" ? "Signing in…" : "Creating account…", "");
    try {
      const response = await fetch(mode === "login" ? "/api/login" : "/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.value.trim(), password: password.value }),
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) {
        show(typeof body.detail === "string" ? body.detail : "Something went wrong.", "error");
      } else if (mode === "login") {
        sessionStorage.setItem("token", body.token);
        show(`Welcome back, ${body.email}!`, "success");
      } else {
        show("Account created. You can sign in now.", "success");
        tabs[0].click();
      }
    } catch {
      show("Could not reach the server. Check your connection.", "error");
    } finally {
      submit.disabled = false;
    }
  });
})();
