chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "start-scan") {
    startScan(sendResponse);
    return true; // Keep response channel open for async execution
  }
});

async function logToServer(message, level = "INFO") {
  console.log(`[${level}] ${message}`);
  try {
    await fetch("http://127.0.0.1:8000/api/logs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ level, message })
    });
  } catch (e) {
    // Ignore
  }
}

async function startScan(sendResponse) {
  if (window.top !== window.self) {
    return;
  }

  await logToServer("JobHunt Dynamic Scan Started!");
  await logToServer("Current Page URL: " + window.location.href);
  
  // Find left panel scrollable container
  const leftPanel = document.querySelector('._24f220ff, [class*="_24f220ff"]');
  if (!leftPanel) {
    await logToServer("Could not find left panel container class '_24f220ff'. Aborting.", "ERROR");
    sendResponse({ status: "error", message: "Job list panel container not found." });
    return;
  }

  const scannedKeys = new Set();
  let consecutiveFailures = 0;
  let importedCount = 0;
  const maxJobsToScan = 25; // Crawl depth limit per search page

  try {
    while (scannedKeys.size < maxJobsToScan && consecutiveFailures < 6) {
      // Find all card buttons inside the left panel
      const cards = Array.from(leftPanel.querySelectorAll('[role="button"]'));
      
      let targetCard = null;
      let targetKey = "";
      
      for (const card of cards) {
        const text = card.textContent.trim().replace(/\s+/g, ' ');
        // Ignore buttons that are not job cards (like "More" pagination button or Premium banners)
        if (text.length < 15 || text.includes("Reactivate Premium") || text.includes("Show match details") || text.includes("Help Center")) {
          continue;
        }
        
        if (!scannedKeys.has(text)) {
          targetCard = card;
          targetKey = text;
          break;
        }
      }
      
      // If no unscanned card is found, scroll list container down to load more virtualized items
      if (!targetCard) {
        await logToServer("No new unscanned cards found in DOM, scrolling list container down...");
        leftPanel.scrollTop += 350;
        await new Promise(r => setTimeout(r, 1500));
        consecutiveFailures++;
        continue;
      }
      
      consecutiveFailures = 0; // Reset failure counter on target card found
      await logToServer(`Target card identified - Title: "${targetKey.substring(0, 45)}..."`);
      
      // Send progress update to popup
      chrome.runtime.sendMessage({ 
        action: "scan-progress", 
        current: scannedKeys.size + 1, 
        total: maxJobsToScan,
        title: "Loading job details..."
      });
      
      // Scroll card into view
      if (targetCard.scrollIntoView) {
        targetCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        await new Promise(r => setTimeout(r, 500));
      }
      
      // Dispatch a clean bubbling click event on the card [role="button"]
      // This clicks the card content safely, bypassing any close/dismiss "X" buttons.
      await logToServer("Dispatching bubbling click event on card button.");
      const clickEvent = new MouseEvent('click', {
        bubbles: true,
        cancelable: true,
        view: window
      });
      targetCard.dispatchEvent(clickEvent);
      
      // Wait for details pane to load and populate description
      let descEl = null;
      let description = "";
      await logToServer("Waiting for details description pane to populate...");
      for (let attempts = 0; attempts < 8; attempts++) {
        descEl = document.querySelector('#job-details, article, .jobs-description-content__text, .jobs-description__container, .jobs-box__html-content, .jobs-description, .jobs-description__content, .jobs-description-content');
        if (descEl) {
          description = descEl.textContent.trim();
          if (description.length > 100) {
            break;
          }
        }
        await new Promise(r => setTimeout(r, 500));
      }
      
      // Extract details
      const titleEl = document.querySelector('.job-details-jobs-unified-top-card__job-title, h1.t-24, .jobs-unified-top-card__job-title, h2.jobs-details-toggle__title');
      let title = titleEl ? titleEl.textContent.trim() : "";
      
      let company = "LinkedIn Poster";
      const companyEl = document.querySelector('.job-details-jobs-unified-top-card__company-name, .jobs-unified-top-card__company-name a, .jobs-unified-top-card__company-name, .jobs-details-toggle__company-name');
      if (companyEl) {
        company = companyEl.textContent.trim();
      }
      
      let location = "Israel";
      const locationEl = document.querySelector('.job-details-jobs-unified-top-card__primary-description-container span, .jobs-unified-top-card__bullet, .jobs-unified-top-card__primary-description span, .jobs-details-toggle__job-location');
      if (locationEl) {
        location = locationEl.textContent.trim().split('·')[0].trim();
      }
      
      // Get actual URL from address bar (it is updated dynamically by LinkedIn SPA router after clicking the card)
      const urlParams = new URLSearchParams(window.location.search);
      const activeJobId = urlParams.get('currentJobId') || "unknown";
      const jobUrl = `https://www.linkedin.com/jobs/view/${activeJobId}/`;
      
      await logToServer(`Extracted Details - ID: ${activeJobId}, Title: "${title}", Company: "${company}", Location: "${location}", Desc Length: ${description.length}`);
      
      scannedKeys.add(targetKey);
      
      if (title && description) {
        chrome.runtime.sendMessage({ 
          action: "scan-progress", 
          current: scannedKeys.size, 
          total: maxJobsToScan,
          title: `${company} - ${title}`
        });
        
        try {
          await logToServer(`POSTing job details to backend...`);
          const res = await fetch("http://127.0.0.1:8000/api/jobs/import", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify([{ title, company, location, description, url: jobUrl }])
          });
          if (res.ok) {
            const data = await res.json();
            await logToServer(`Import Response: ${JSON.stringify(data)}`);
            if (data.new_jobs > 0) {
              importedCount++;
            }
          } else {
            await logToServer(`Import failed with status: ${res.status}`, "ERROR");
          }
        } catch (err) {
          await logToServer(`Failed to sync job details: ${err.message}`, "ERROR");
        }
      } else {
        await logToServer("Skipped syncing because title or description was parsed as empty.", "WARNING");
      }
    }
    
    await logToServer(`Scan complete. Scanned: ${scannedKeys.size}, Imported: ${importedCount}`);
    sendResponse({ status: "success", scanned: scannedKeys.size, imported: importedCount });
  } catch (e) {
    await logToServer(`General Scan Exception: ${e.message}`, "ERROR");
    sendResponse({ status: "error", message: e.message });
  }
}
