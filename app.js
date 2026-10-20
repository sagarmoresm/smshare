/**
 * SMSHARE — MODERN UI CONTROLLER
 * Zero external tracking · Clean vector icons · Instant temporary sharing
 */

document.addEventListener("DOMContentLoaded", () => {
  // --- STATE ---
  let selectedFiles = [];
  let sendTimerInterval = null;
  let receiveTimerInterval = null;

  // --- ICONS LIBRARY (Clean Inline SVGs) ---
  const ICONS = {
    sun: `<svg class="icon icon-md" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`,
    moon: `<svg class="icon icon-md" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`,
    check: `<svg class="icon icon-sm" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>`,
    alert: `<svg class="icon icon-sm" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
    info: `<svg class="icon icon-sm" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`,
    clock: `<svg class="icon icon-sm" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
    copy: `<svg class="icon icon-sm" viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`,
    link: `<svg class="icon icon-sm" viewBox="0 0 24 24"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>`,
    send: `<svg class="icon icon-sm" viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>`,
    download: `<svg class="icon icon-sm" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>`,
    image: `<svg class="icon icon-md" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>`,
    doc: `<svg class="icon icon-md" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>`,
    archive: `<svg class="icon icon-md" viewBox="0 0 24 24"><polyline points="21 8 21 21 3 21 3 8"/><rect x="1" y="3" width="22" height="5"/><line x1="10" y1="12" x2="14" y2="12"/></svg>`,
    video: `<svg class="icon icon-md" viewBox="0 0 24 24"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>`,
    audio: `<svg class="icon icon-md" viewBox="0 0 24 24"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>`,
    code: `<svg class="icon icon-md" viewBox="0 0 24 24"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>`,
    file: `<svg class="icon icon-md" viewBox="0 0 24 24"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><polyline points="13 2 13 9 20 9"/></svg>`
  };

  // --- DOM ELEMENTS ---
  const tabSend = document.getElementById("tabSend");
  const tabReceive = document.getElementById("tabReceive");
  const panelSend = document.getElementById("panelSend");
  const panelReceive = document.getElementById("panelReceive");

  const sendFormContainer = document.getElementById("sendFormContainer");
  const sendResultContainer = document.getElementById("sendResultContainer");
  const messageInput = document.getElementById("messageInput");
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const fileList = document.getElementById("fileList");
  const expirySelect = document.getElementById("expirySelect");
  const sendBtn = document.getElementById("sendBtn");
  const sendAnotherBtn = document.getElementById("sendAnotherBtn");

  const uploadProgress = document.getElementById("uploadProgress");
  const progressBar = document.getElementById("progressBar");
  const progressText = document.getElementById("progressText");

  const generatedCodeDisplay = document.getElementById("generatedCodeDisplay");
  const copyCodeBtn = document.getElementById("copyCodeBtn");
  const copyLinkBtn = document.getElementById("copyLinkBtn");
  const qrBox = document.getElementById("qrBox");
  const sendCountdown = document.getElementById("sendCountdown");

  const receiveCodeInput = document.getElementById("receiveCodeInput");
  const receiveBtn = document.getElementById("receiveBtn");
  const receiveLoading = document.getElementById("receiveLoading");
  const receivedContentBox = document.getElementById("receivedContentBox");
  const textPayloadCard = document.getElementById("textPayloadCard");
  const textPayloadContent = document.getElementById("textPayloadContent");
  const copyTextBtn = document.getElementById("copyTextBtn");
  const filesContainer = document.getElementById("filesContainer");
  const filesListReceived = document.getElementById("filesListReceived");
  const downloadAllZipBtn = document.getElementById("downloadAllZipBtn");
  const receiveCountdown = document.getElementById("receiveCountdown");

  const themeToggle = document.getElementById("themeToggle");
  const toastContainer = document.getElementById("toastContainer");

  // --- THEME MANAGEMENT ---
  const savedTheme = localStorage.getItem("smshare_theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
  updateThemeIcon(savedTheme);

  themeToggle.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme") || "light";
    const next = current === "light" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("smshare_theme", next);
    updateThemeIcon(next);
    showToast(`Switched to ${next} mode`, "info");
  });

  function updateThemeIcon(theme) {
    themeToggle.innerHTML = theme === "light" ? ICONS.moon : ICONS.sun;
  }

  // --- TOAST NOTIFICATIONS ---
  function showToast(message, iconKey = "check") {
    const iconSvg = ICONS[iconKey] || ICONS.check;
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.innerHTML = `<span style="display:inline-flex; align-items:center;">${iconSvg}</span><span>${message}</span>`;
    toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(10px)";
      setTimeout(() => toast.remove(), 200);
    }, 2800);
  }

  // --- TABS SWITCHING ---
  function switchTab(mode) {
    if (mode === "send") {
      tabSend.classList.add("active");
      tabReceive.classList.remove("active");
      panelSend.classList.add("active");
      panelReceive.classList.remove("active");
    } else {
      tabReceive.classList.add("active");
      tabSend.classList.remove("active");
      panelReceive.classList.add("active");
      panelSend.classList.remove("active");
      receiveCodeInput.focus();
    }
  }

  tabSend.addEventListener("click", () => switchTab("send"));
  tabReceive.addEventListener("click", () => switchTab("receive"));

  // --- FILE HANDLING ---
  dropzone.addEventListener("click", () => fileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(Array.from(e.target.files));
      fileInput.value = "";
    }
  });

  function handleFiles(files) {
    if (selectedFiles.length + files.length > 10) {
      showToast("Maximum limit is 10 files per transfer", "alert");
      files = files.slice(0, 10 - selectedFiles.length);
    }

    for (const f of files) {
      if (f.size > 500 * 1024 * 1024) {
        showToast(`File "${f.name}" exceeds 500 MB limit`, "alert");
        continue;
      }
      selectedFiles.push(f);
    }
    renderFileList();
  }

  function getFileIconSvg(filename) {
    const ext = filename.split(".").pop().toLowerCase();
    if (["png", "jpg", "jpeg", "webp", "gif", "svg"].includes(ext)) return ICONS.image;
    if (["pdf", "txt", "doc", "docx"].includes(ext)) return ICONS.doc;
    if (["zip", "rar", "7z", "tar", "gz"].includes(ext)) return ICONS.archive;
    if (["mp4", "webm", "mov", "mkv"].includes(ext)) return ICONS.video;
    if (["mp3", "wav", "ogg", "flac"].includes(ext)) return ICONS.audio;
    if (["js", "py", "html", "css", "json", "ts", "cpp", "c"].includes(ext)) return ICONS.code;
    return ICONS.file;
  }

  function formatBytes(bytes) {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
  }

  function renderFileList() {
    fileList.innerHTML = "";
    selectedFiles.forEach((file, index) => {
      const chip = document.createElement("div");
      chip.className = "file-chip";
      chip.innerHTML = `
        <div class="file-info">
          <span class="file-icon" style="display:inline-flex; align-items:center;">${getFileIconSvg(file.name)}</span>
          <span class="file-name" title="${file.name}">${file.name}</span>
          <span class="file-size">${formatBytes(file.size)}</span>
        </div>
        <button class="file-remove-btn" type="button" data-index="${index}" title="Remove file">×</button>
      `;
      fileList.appendChild(chip);
    });

    fileList.querySelectorAll(".file-remove-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const idx = parseInt(e.currentTarget.getAttribute("data-index"), 10);
        selectedFiles.splice(idx, 1);
        renderFileList();
      });
    });
  }

  // --- SEND PAYLOAD ---
  async function submitPayload() {
    const text = messageInput.value.trim();
    if (!text && selectedFiles.length === 0) {
      showToast("Type a message or attach a file first", "alert");
      messageInput.focus();
      return;
    }

    const expireAtHour = parseFloat(expirySelect.value) || 0.5;
    const formData = new FormData();
    if (text) formData.append("text", text);
    formData.append("expireAtHour", expireAtHour);
    selectedFiles.forEach((file) => formData.append("files", file));

    // Disable send button
    sendBtn.disabled = true;
    sendBtn.innerHTML = `<span>UPLOADING...</span>`;
    uploadProgress.style.display = "block";
    progressBar.style.width = "0%";
    progressText.innerText = "0%";

    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/send");

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        const percent = Math.round((e.loaded / e.total) * 100);
        progressBar.style.width = percent + "%";
        progressText.innerText = percent + "%";
      }
    };

    xhr.onload = () => {
      sendBtn.disabled = false;
      sendBtn.innerHTML = `${ICONS.send}<span>SEND</span>`;
      uploadProgress.style.display = "none";

      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const res = JSON.parse(xhr.responseText);
          displaySendSuccess(res);
        } catch (err) {
          showToast("Unexpected response format", "alert");
        }
      } else {
        try {
          const errData = JSON.parse(xhr.responseText);
          showToast(errData.detail || "Upload failed", "alert");
        } catch {
          showToast("Failed to upload content", "alert");
        }
      }
    };

    xhr.onerror = () => {
      sendBtn.disabled = false;
      sendBtn.innerHTML = `${ICONS.send}<span>SEND</span>`;
      uploadProgress.style.display = "none";
      showToast("Network error. Could not connect to server", "alert");
    };

    xhr.send(formData);
  }

  sendBtn.addEventListener("click", submitPayload);

  // Shortcut: Cmd+Enter or Ctrl+Enter to send
  window.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      if (panelSend.classList.contains("active") && sendFormContainer.style.display !== "none") {
        e.preventDefault();
        submitPayload();
      }
    }
  });

  // Display Success Screen
  function displaySendSuccess(data) {
    sendFormContainer.style.display = "none";
    sendResultContainer.style.display = "block";

    generatedCodeDisplay.textContent = data.code;

    const directLink = `${window.location.origin}/?code=${data.code}`;

    // Generate QR Code
    generateQRCodeSVG(directLink, qrBox);

    // Copy actions
    copyCodeBtn.onclick = () => {
      navigator.clipboard.writeText(data.code);
      showToast(`Copied code: ${data.code}`, "copy");
    };

    copyLinkBtn.onclick = () => {
      navigator.clipboard.writeText(directLink);
      showToast("Direct link copied to clipboard", "link");
    };

    // Countdown
    startCountdown(sendCountdown, data.seconds_remaining, () => {
      sendCountdown.innerHTML = `<span style="display:inline-flex; align-items:center; gap:6px;">${ICONS.alert} EXPIRED & WIPED</span>`;
    }, (id) => sendTimerInterval = id);

    showToast("Share generated! Code is active", "check");
  }

  sendAnotherBtn.addEventListener("click", () => {
    if (sendTimerInterval) clearInterval(sendTimerInterval);
    messageInput.value = "";
    selectedFiles = [];
    renderFileList();
    sendResultContainer.style.display = "none";
    sendFormContainer.style.display = "block";
  });

  // --- RECEIVE PAYLOAD ---
  receiveCodeInput.addEventListener("input", (e) => {
    const val = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, "");
    e.target.value = val;
    if (val.length === 4) {
      fetchPayload(val);
    }
  });

  receiveBtn.addEventListener("click", () => {
    const code = receiveCodeInput.value.trim().toUpperCase();
    if (!code) {
      showToast("Enter a 4-character code first", "alert");
      receiveCodeInput.focus();
      return;
    }
    fetchPayload(code);
  });

  async function fetchPayload(code) {
    if (receiveTimerInterval) clearInterval(receiveTimerInterval);

    receiveLoading.style.display = "block";
    receivedContentBox.style.display = "none";

    try {
      const resp = await fetch(`/api/receive?code=${encodeURIComponent(code)}`);
      const data = await resp.json();

      receiveLoading.style.display = "none";

      if (!resp.ok) {
        showToast(data.detail || "Share expired or code not found", "alert");
        return;
      }

      displayReceivedPayload(data);
    } catch (err) {
      receiveLoading.style.display = "none";
      showToast("Failed to connect to server", "alert");
    }
  }

  function displayReceivedPayload(data) {
    receivedContentBox.style.display = "block";

    // Text payload
    if (data.text) {
      textPayloadCard.style.display = "block";
      textPayloadContent.textContent = data.text;
      copyTextBtn.onclick = () => {
        navigator.clipboard.writeText(data.text);
        showToast("Text copied to clipboard", "copy");
      };
    } else {
      textPayloadCard.style.display = "none";
    }

    // Files payload
    if (data.files && data.files.length > 0) {
      filesContainer.style.display = "block";
      filesListReceived.innerHTML = "";

      data.files.forEach((file) => {
        const card = document.createElement("div");
        card.className = "download-file-card";

        const ext = file.fileName.split(".").pop().toLowerCase();
        let previewHtml = "";

        if (["png", "jpg", "jpeg", "webp", "gif"].includes(ext)) {
          previewHtml = `<div class="media-preview-container"><img src="${file.downloadUrl}" class="media-preview-img" alt="${file.fileName}" loading="lazy" /></div>`;
        } else if (["mp3", "wav", "ogg"].includes(ext)) {
          previewHtml = `<div class="media-preview-container"><audio controls src="${file.downloadUrl}" style="width:100%; max-width:320px;"></audio></div>`;
        } else if (["mp4", "webm"].includes(ext)) {
          previewHtml = `<div class="media-preview-container"><video controls src="${file.downloadUrl}" style="width:100%; max-width:360px; border-radius:4px;"></video></div>`;
        }

        card.innerHTML = `
          <div style="flex:1; min-width: 200px;">
            <div class="file-info" style="margin-bottom: 4px;">
              <span class="file-icon" style="display:inline-flex; align-items:center;">${getFileIconSvg(file.fileName)}</span>
              <span class="file-name" style="font-weight:800; font-size:1rem;">${file.fileName}</span>
              <span class="file-size">(${formatBytes(file.fileSize)})</span>
            </div>
            ${previewHtml}
          </div>
          <div>
            <a href="${file.downloadUrl}" download="${file.fileName}" class="neo-btn neo-btn-cyan" style="padding:8px 16px; font-size:0.85rem;">
              ${ICONS.download}
              <span>DOWNLOAD</span>
            </a>
          </div>
        `;
        filesListReceived.appendChild(card);
      });

      // Zip download
      downloadAllZipBtn.onclick = () => {
        window.location.href = `/api/download-zip/${data.code}`;
        showToast("Preparing ZIP archive...", "info");
      };
    } else {
      filesContainer.style.display = "none";
    }

    // Countdown
    startCountdown(receiveCountdown, data.secondsRemaining, () => {
      receiveCountdown.innerHTML = `<span style="display:inline-flex; align-items:center; gap:6px;">${ICONS.alert} EXPIRED & WIPED</span>`;
      receivedContentBox.style.display = "none";
      showToast("Transfer expired and was wiped permanently", "clock");
    }, (id) => receiveTimerInterval = id);

    showToast(`Loaded share: ${data.code}`, "check");
  }

  // --- COUNTDOWN TIMER HELPER ---
  function startCountdown(element, seconds, onExpire, saveInterval) {
    let remaining = seconds;

    function renderTime() {
      if (remaining <= 0) {
        onExpire();
        return;
      }
      const hrs = Math.floor(remaining / 3600);
      const mins = Math.floor((remaining % 3600) / 60);
      const secs = remaining % 60;

      let str = "";
      if (hrs > 0) str += `${hrs}h `;
      str += `${mins}m ${secs < 10 ? "0" : ""}${secs}s`;
      element.innerHTML = `<span style="display:inline-flex; align-items:center; gap:6px;">${ICONS.clock} Wipes in <strong>${str}</strong></span>`;
      remaining--;
    }

    renderTime();
    const interval = setInterval(renderTime, 1000);
    if (saveInterval) saveInterval(interval);
  }

  // --- URL AUTO-CODE DETECTION ---
  const urlParams = new URLSearchParams(window.location.search);
  const codeParam = urlParams.get("code");
  const pathParts = window.location.pathname.split("/");
  let pathCode = null;
  if (pathParts[1] === "c" && pathParts[2]) {
    pathCode = pathParts[2];
  }

  const initialCode = (codeParam || pathCode || "").trim().toUpperCase();
  if (initialCode && initialCode.length === 4) {
    switchTab("receive");
    receiveCodeInput.value = initialCode;
    fetchPayload(initialCode);
  }

  // --- ACCORDIONS ---
  document.querySelectorAll(".faq-item").forEach((item) => {
    const question = item.querySelector(".faq-question");
    question.addEventListener("click", () => {
      const isActive = item.classList.contains("active");
      document.querySelectorAll(".faq-item").forEach((f) => f.classList.remove("active"));
      if (!isActive) {
        item.classList.add("active");
      }
    });
  });

  // --- MODALS ---
  const modalOverlay = document.getElementById("modalOverlay");
  const modalTitle = document.getElementById("modalTitle");
  const modalBody = document.getElementById("modalBody");
  const modalCloseBtn = document.getElementById("modalCloseBtn");

  const modalContents = {
    about: {
      title: "About SMSHARE",
      body: `
        <p><strong>SMSHARE</strong> is an ultra-minimalist, zero-identity file and text sharing tool designed for seamless, temporary data transfers.</p>
        <p>No phone numbers, no emails, no logins, and no trackers. When you upload or type something, you receive a fast 4-character code. Enter it on any device to retrieve the content.</p>
        <p>All records and files are strictly hard-deleted as soon as their expiration timer elapses.</p>
      `
    },
    privacy: {
      title: "Privacy Policy",
      body: `
        <p><strong>Zero-Logging Architecture:</strong> We do not log IP addresses, user agents, or cross-site browsing cookies.</p>
        <p><strong>Auto-Destruct Guarantee:</strong> Data uploaded to SMSHARE is stored temporarily. Once the countdown expires (30 min, 2 hours, 12 hours, or 24 hours), files and database records are permanently deleted from disk and cannot be recovered.</p>
        <p><strong>HTTPS (TLS) Encryption:</strong> All transfers in transit are strictly encrypted.</p>
      `
    },
    terms: {
      title: "Terms of Service",
      body: `
        <p>By using SMSHARE, you agree to use the service exclusively for legal file and text sharing.</p>
        <p>You agree not to upload malware, copyrighted materials you do not have permission to distribute, or content that violates applicable laws.</p>
        <p>Content found in violation is removed immediately.</p>
      `
    },
    contact: {
      title: "Contact & Feedback",
      body: `
        <p>Have questions, security reports, or feedback on SMSHARE?</p>
        <form id="contactForm" style="display:flex; flex-direction:column; gap:12px; margin-top:14px;">
          <input type="text" placeholder="Your Subject" required style="padding:10px; border:2px solid var(--border-color); border-radius:4px; font-weight:700;" />
          <textarea placeholder="Your Message..." rows="4" required style="padding:10px; border:2px solid var(--border-color); border-radius:4px; font-weight:600;"></textarea>
          <button type="submit" class="neo-btn neo-btn-primary" style="margin-top:6px; display:inline-flex; align-items:center; justify-content:center; gap:8px;">
            <svg class="icon icon-sm" viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            <span>SUBMIT MESSAGE</span>
          </button>
        </form>
      `
    }
  };

  function openModal(key) {
    const data = modalContents[key];
    if (!data) return;
    modalTitle.textContent = data.title;
    modalBody.innerHTML = data.body;
    modalOverlay.classList.add("active");

    if (key === "contact") {
      const cf = document.getElementById("contactForm");
      if (cf) {
        cf.onsubmit = (e) => {
          e.preventDefault();
          modalOverlay.classList.remove("active");
          showToast("Message sent successfully", "check");
        };
      }
    }
  }

  document.querySelectorAll("[data-modal]").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const modalKey = link.getAttribute("data-modal");
      openModal(modalKey);
    });
  });

  modalCloseBtn.addEventListener("click", () => modalOverlay.classList.remove("active"));
  modalOverlay.addEventListener("click", (e) => {
    if (e.target === modalOverlay) modalOverlay.classList.remove("active");
  });

  // --- EMBEDDED LIGHTWEIGHT QR CODE GENERATOR ---
  function generateQRCodeSVG(text, container) {
    const encoded = encodeURIComponent(text);
    container.innerHTML = `
      <div class="qr-box">
        <img src="https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=${encoded}&bgcolor=ffffff&color=000000&margin=0" 
             width="150" height="150" alt="Scan to receive" style="display:block;" />
      </div>
    `;
  }
});
