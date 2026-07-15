document.addEventListener("DOMContentLoaded", async () => {
  const connStatus = document.getElementById("conn-status");
  const scanBtn = document.getElementById("scan-btn");
  const progressBox = document.getElementById("progress-box");
  const progressText = document.getElementById("progress-text");
  const progressFill = document.getElementById("progress-fill");
  const currentJob = document.getElementById("current-job");
  const resultBox = document.getElementById("result-box");

  // 1. Check local backend status
  try {
    const res = await fetch("http://127.0.0.1:8000/api/settings");
    if (res.ok) {
      connStatus.textContent = "Online";
      connStatus.className = "status-badge online";
      scanBtn.disabled = false;
    } else {
      throw new Error("HTTP error");
    }
  } catch (e) {
    connStatus.textContent = "Offline";
    connStatus.className = "status-badge offline";
    scanBtn.disabled = true;
  }

  // 2. Scan button action
  scanBtn.addEventListener("click", async () => {
    scanBtn.disabled = true;
    resultBox.style.display = "none";
    progressBox.style.display = "block";
    
    // Get the active tab to send message
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) {
      showResult("error", "No active browser tab found.");
      scanBtn.disabled = false;
      return;
    }
    
    if (!tab.url || !tab.url.includes("linkedin.com")) {
      showResult("error", "Please open a LinkedIn search page first.");
      scanBtn.disabled = false;
      return;
    }
    
    // Set up message listener for content script updates
    chrome.runtime.onMessage.addListener(function listener(message) {
      if (message.action === "scan-progress") {
        const pct = Math.round((message.current / message.total) * 100);
        progressText.textContent = `${message.current} / ${message.total}`;
        progressFill.style.width = `${pct}%`;
        currentJob.textContent = message.title;
      }
    });

    // Send trigger to content script
    chrome.tabs.sendMessage(tab.id, { action: "start-scan" }, (response) => {
      progressBox.style.display = "none";
      scanBtn.disabled = false;
      
      if (chrome.runtime.lastError) {
        showResult("error", "Make sure you refresh the LinkedIn page after installing the extension.");
        console.error(chrome.runtime.lastError);
        return;
      }
      
      if (response && response.status === "success") {
        showResult("success", `Sync Completed! Scanned: ${response.scanned}, Imported ${response.imported} new offers.`);
      } else {
        showResult("error", response ? response.message : "Scanning failed.");
      }
    });
  });

  function showResult(type, message) {
    resultBox.textContent = message;
    resultBox.className = `result-message ${type}`;
    resultBox.style.display = "block";
  }
});
