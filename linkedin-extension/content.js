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

// Deep recursive query selector that penetrates shadow roots and same-origin iframes
function querySelectorAllRecursive(root, selector) {
  let elements = [];
  try {
    elements = Array.from(root.querySelectorAll(selector));
  } catch (e) {
    // Ignore selector errors
  }
  
  try {
    const allNodes = root.querySelectorAll('*');
    allNodes.forEach(node => {
      if (node.shadowRoot) {
        elements = elements.concat(querySelectorAllRecursive(node.shadowRoot, selector));
      }
      if (node.tagName === 'IFRAME') {
        try {
          if (node.contentDocument) {
            elements = elements.concat(querySelectorAllRecursive(node.contentDocument, selector));
          }
        } catch (e) {
          // Ignore cross-origin container
        }
      }
    });
  } catch (e) {
    // Ignore traversal errors
  }
  
  return elements;
}

// Find standard LinkedIn Jobs "Next Page" pagination button
function findNextPageButton() {
  const selectors = [
    'button.jobs-search-pagination__button--next',
    'button[aria-label="Next"]',
    'button[aria-label="Page Next"]',
    'button[aria-label*="next" i]',
    '[class*="pagination"] button[aria-label*="next" i]',
    'button[class*="pagination-next" i]',
    'button[class*="pagination__button--next"]'
  ];
  
  for (const selector of selectors) {
    const btn = querySelectorAllRecursive(document, selector)[0];
    if (btn && !btn.disabled && !btn.getAttribute('aria-disabled')) {
      return btn;
    }
  }
  
  // Fallback: search all buttons text content
  const allButtons = querySelectorAllRecursive(document, 'button');
  for (const btn of allButtons) {
    const label = (btn.getAttribute('aria-label') || '').toLowerCase();
    const text = btn.textContent.toLowerCase();
    if ((label.includes('next') || text.includes('next')) && !btn.disabled && !btn.getAttribute('aria-disabled')) {
      return btn;
    }
  }
  
  return null;
}

async function startScan(sendResponse) {
  if (window.top !== window.self) {
    return;
  }

  await logToServer("JobHunt Dynamic Multi-Page Scan Started!");
  await logToServer("Current Page URL: " + window.location.href);
  
  let totalScanned = 0;
  let totalImported = 0;
  let pageIndex = 1;
  const maxPages = 5; // Scan limit up to 5 pages

  try {
    while (pageIndex <= maxPages) {
      await logToServer(`--- Scanning Search Page ${pageIndex} ---`);
      
      // Find left panel container
      const leftPanel = querySelectorAllRecursive(document, '._24f220ff, [class*="_24f220ff"]')[0];
      if (!leftPanel) {
        await logToServer("Could not find left panel container class '_24f220ff'. Aborting page scan.", "ERROR");
        break;
      }

      const scannedKeys = new Set();
      let consecutiveFailures = 0;
      const maxJobsPerPage = 25; // Standard LinkedIn results per page limit

      while (scannedKeys.size < maxJobsPerPage && consecutiveFailures < 6) {
        // Query card buttons inside the left panel
        const cards = Array.from(leftPanel.querySelectorAll('[role="button"]'));
        let targetCard = null;
        let targetKey = "";
        
        for (const card of cards) {
          const text = card.textContent.trim().replace(/\s+/g, ' ');
          if (text.length < 15 || text.includes("Reactivate Premium") || text.includes("Show match details") || text.includes("Help Center")) {
            continue;
          }
          if (!scannedKeys.has(text)) {
            targetCard = card;
            targetKey = text;
            break;
          }
        }
        
        // If no unscanned card is found, scroll list container down to load virtualized items
        if (!targetCard) {
          await logToServer("No new unscanned cards found on screen, scrolling list container down...");
          leftPanel.scrollTop += 350;
          await new Promise(r => setTimeout(r, 1500));
          consecutiveFailures++;
          continue;
        }
        
        consecutiveFailures = 0; // Reset failure counter
        const targetJobId = scannedKeys.size + 1;
        await logToServer(`Target card: "${targetKey.substring(0, 45)}..."`);
        
        // Send progress update to popup
        chrome.runtime.sendMessage({ 
          action: "scan-progress", 
          current: totalScanned + targetJobId, 
          total: maxJobsPerPage * maxPages,
          title: `Page ${pageIndex} - Loading job details...`
        });
        
        // Scroll card into view
        if (targetCard.scrollIntoView) {
          targetCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          await new Promise(r => setTimeout(r, 500));
        }
        
        // Click the job card container safely
        await logToServer("Clicking card container.");
        const clickEvent = new MouseEvent('click', {
          bubbles: true,
          cancelable: true,
          view: window
        });
        targetCard.dispatchEvent(clickEvent);
        
        // Wait for details pane description
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
        
        const urlParams = new URLSearchParams(window.location.search);
        const activeJobId = urlParams.get('currentJobId') || "unknown";
        const jobUrl = `https://www.linkedin.com/jobs/view/${activeJobId}/`;
        
        await logToServer(`Extracted Details - ID: ${activeJobId}, Title: "${title}", Company: "${company}", Desc Length: ${description.length}`);
        
        scannedKeys.add(targetKey);
        
        if (title && description) {
          chrome.runtime.sendMessage({ 
            action: "scan-progress", 
            current: totalScanned + scannedKeys.size, 
            total: maxJobsPerPage * maxPages,
            title: `Page ${pageIndex}: ${company} - ${title}`
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
              if (data.new_jobs > 0) {
                totalImported++;
              }
            }
          } catch (err) {
            await logToServer(`Failed to sync job details: ${err.message}`, "ERROR");
          }
        }
      }
      
      totalScanned += scannedKeys.size;
      
      // Page completed, find the Next page button
      await logToServer(`Completed Page ${pageIndex}. Searching for next page pagination button...`);
      const nextBtn = findNextPageButton();
      
      if (nextBtn) {
        await logToServer("Next page pagination button found! Navigating to the next page...");
        
        if (nextBtn.scrollIntoView) {
          nextBtn.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          await new Promise(r => setTimeout(r, 500));
        }
        
        // Dispatch bubbling click to pagination button
        const clickEvent = new MouseEvent('click', {
          bubbles: true,
          cancelable: true,
          view: window
        });
        nextBtn.dispatchEvent(clickEvent);
        
        pageIndex++;
        await logToServer("Waiting for new page search results to load (4s delay)...");
        await new Promise(r => setTimeout(r, 4000));
      } else {
        await logToServer("No clickable Next page pagination button found. Multi-page scan completed.");
        break;
      }
    }
    
    await logToServer(`Scan complete. Total Scanned: ${totalScanned}, Total Imported: ${totalImported}`);
    sendResponse({ status: "success", scanned: totalScanned, imported: totalImported });
  } catch (e) {
    await logToServer(`General Scan Exception: ${e.message}`, "ERROR");
    sendResponse({ status: "error", message: e.message });
  }
}
