const output = document.getElementById("output");
const resultPanel = document.getElementById("result-panel");
const toast = document.getElementById("toast");
const toastTitle = document.getElementById("toast-title");
const toastMsg = document.getElementById("toast-msg");
const testBtn = document.getElementById("btn-test");

function show(data) {
  output.textContent =
    typeof data === "string" ? data : JSON.stringify(data, null, 2);
}

function formatError(detail) {
  if (!detail) return "Request failed";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
  }
  return String(detail);
}

function readCredentials(form) {
  const data = new FormData(form);
  const fromEmail = (data.get("from_email") || "").toString().trim();
  return {
    host: data.get("host"),
    port: Number(data.get("port")),
    username: data.get("username"),
    password: data.get("password"),
    use_tls: form.use_tls.checked,
    use_ssl: form.use_ssl.checked,
    from_email: fromEmail || null,
    from_name: data.get("from_name") || "SMTP Test Server",
  };
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(formatError(body.detail) || body.message || `Request failed (${response.status})`);
  }
  return body;
}

function openToast(state, title, message) {
  toast.hidden = false;
  toast.classList.remove("is-loading", "is-ok", "is-bad");
  toast.classList.add(state);
  toastTitle.textContent = title;
  toastMsg.textContent = message;
}

function closeToast() {
  toast.hidden = true;
  toast.classList.remove("is-loading", "is-ok", "is-bad");
}

function scrollToResult() {
  resultPanel.classList.remove("is-highlight");
  resultPanel.scrollIntoView({ behavior: "smooth", block: "center" });
  // restart highlight animation
  void resultPanel.offsetWidth;
  resultPanel.classList.add("is-highlight");
}

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function showTestOutcome(ok, title, message, details) {
  openToast(ok ? "is-ok" : "is-bad", title, message);
  show(details);
  await wait(1400);
  closeToast();
  scrollToResult();
}

document.getElementById("creds-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    show("Saving credentials…");
    const credentials = readCredentials(event.target);
    const result = await api("/smtp/credentials", {
      method: "POST",
      body: JSON.stringify(credentials),
    });
    show(result);
  } catch (error) {
    show({ success: false, message: error.message });
  }
});

document.getElementById("btn-status").addEventListener("click", async () => {
  try {
    show("Checking status…");
    show(await api("/smtp/status"));
  } catch (error) {
    show({ success: false, message: error.message });
  }
});

testBtn.addEventListener("click", async () => {
  testBtn.disabled = true;
  openToast("is-loading", "Testing…", "Checking your SMTP connection");
  show("Testing SMTP connection…");

  try {
    const result = await api("/smtp/test-connection", {
      method: "POST",
      body: "{}",
    });
    await showTestOutcome(
      true,
      "Connection OK",
      "Your SMTP credentials work.",
      result
    );
  } catch (error) {
    await showTestOutcome(
      false,
      "Connection failed",
      error.message || "Could not authenticate with the SMTP server.",
      { success: false, message: error.message }
    );
  } finally {
    testBtn.disabled = false;
  }
});

document.getElementById("send-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const sendBtn = event.target.querySelector('button[type="submit"]');
  sendBtn.disabled = true;
  openToast("is-loading", "Sending…", "Delivering your test email");
  show("Sending test email…");

  try {
    const data = new FormData(event.target);
    const result = await api("/smtp/send-test", {
      method: "POST",
      body: JSON.stringify({
        to_email: data.get("to_email"),
        subject: data.get("subject"),
        body: data.get("body"),
      }),
    });
    await showTestOutcome(
      true,
      "Email sent",
      "Check the inbox (and spam folder).",
      result
    );
  } catch (error) {
    await showTestOutcome(
      false,
      "Send failed",
      error.message || "Could not send the test email.",
      { success: false, message: error.message }
    );
  } finally {
    sendBtn.disabled = false;
  }
});
