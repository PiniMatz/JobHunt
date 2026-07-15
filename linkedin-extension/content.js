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
    // Ignore to prevent looping on offline backend
  }
}

async function startScan(sendResponse) {
  await logToServer("JobHunt Dynamic Scan Started!");
  await logToServer("Current Page URL: " + window.location.href);
  
  // Find scrollable list container
  const listContainer = document.querySelector('.jobs-search-results-list, .scaffold-layout__list, ul.scaffold-layout__list-container, [class*="results-list"]');
  await logToServer(`List container found in DOM: ${!!listContainer}`);

  const scannedJobIds = new Set();
  let consecutiveFailures = 0;
  let importedCount = 0;
  const maxJobsToScan = 25; // Crawl depth limit per search page

  try {
    while (scannedJobIds.size < maxJobsToScan && consecutiveFailures < 6) {
      // Query currently rendered cards dynamically via broad link selectors
      const cards = [];
      const jobLinks = Array.from(document.querySelectorAll(
        'a.job-card-list__title, ' +
        'a[href*="/jobs/view/"], ' +
        'a[href*="currentJobId="], ' +
        'a.job-card-container__link'
      ));
      
      jobLinks.forEach(link => {
        const card = link.closest('li, .job-card-container, [data-job-id]') || link;
        const href = link.getAttribute('href') || "";
        const m = href.match(/\/view\/(\d+)/) || href.match(/currentJobId=(\d+)/);
        const jobId = m ? m[1] : null;
        
        if (jobId && !cards.some(c => c.jobId === jobId)) {
          cards.push({ card, jobId, link });
        }
      });
      
      await logToServer(`Currently rendered cards: ${cards.length}. Scanned IDs count: ${scannedJobIds.size}`);
      
      // Find the first unscanned card
      let target = null;
      for (const item of cards) {
        if (!scannedJobIds.has(item.jobId)) {
          target = item;
          break;
        }
      }
      
      // If no unscanned card is found, scroll list container down to load more virtualized items
      if (!target) {
        await logToServer("No new visible cards found, scrolling list container down to load more...");
        if (listContainer) {
          listContainer.scrollTop += 350;
        } else {
          window.scrollBy({ top: 350, behavior: 'smooth' });
        }
        await new Promise(r => setTimeout(r, 1500));
        consecutiveFailures++;
        continue;
      }
      
      consecutiveFailures = 0; // Reset failure counter on target card found
      const targetJobId = target.jobId;
      await logToServer(`Target job card identified - Job ID: ${targetJobId}`);
      
      // Send progress update to popup
      chrome.runtime.sendMessage({ 
        action: "scan-progress", 
        current: scannedJobIds.size + 1, 
        total: maxJobsToScan,
        title: "Loading job details..."
      });
      
      // Scroll card into view
      if (target.card.scrollIntoView) {
        await logToServer("Scrolling target card into view.");
        target.card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        await new Promise(r => setTimeout(r, 500));
      }
      
      // Click the card wrapper (closest li) to prevent full tab navigation
      if (target.card && target.card.click) {
        await logToServer("Clicking card element to load details panel.");
        target.card.click();
      } else if (target.link && target.link.click) {
        await logToServer("Clicking link fallback.");
        target.link.click();
      }
      
      // Wait for pane to render dynamically (polling loop up to 4s)
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
      if (!title && target.link) {
        title = target.link.textContent.trim();
      }
      
      let company = "LinkedIn Poster";
      const companyEl = document.querySelector('.job-details-jobs-unified-top-card__company-name, .jobs-unified-top-card__company-name a, .jobs-unified-top-card__company-name, .jobs-details-toggle__company-name');
      if (companyEl) {
        company = companyEl.textContent.trim();
      } else if (target.card) {
        const cardCompanyEl = target.card.querySelector('.job-card-container__company-name, .job-card-list__company-name, [class*="company-name"]');
        if (cardCompanyEl) {
          company = cardCompanyEl.textContent.trim();
        }
      }
      
      let location = "Israel";
      const locationEl = document.querySelector('.job-details-jobs-unified-top-card__primary-description-container span, .jobs-unified-top-card__bullet, .jobs-unified-top-card__primary-description span, .jobs-details-toggle__job-location');
      if (locationEl) {
        location = locationEl.textContent.trim().split('·')[0].trim();
      } else if (target.card) {
        const cardLocEl = target.card.querySelector('.job-card-container__metadata-item, .job-card-list__metadata-item, [class*="metadata-item"], [class*="location"]');
        if (cardLocEl) {
          location = cardLocEl.textContent.trim().split('·')[0].trim();
        }
      }
      
      // Get actual URL from address bar since it changes dynamically on click
      const urlParams = new URLSearchParams(window.location.search);
      const activeJobId = urlParams.get('currentJobId') || targetJobId;
      const jobUrl = `https://www.linkedin.com/jobs/view/${activeJobId}/`;
      
      await logToServer(`Extracted Details - Title: "${title}", Company: "${company}", Location: "${location}", Desc Length: ${description.length}`);
      
      scannedJobIds.add(targetJobId);
      
      if (title && description) {
        chrome.runtime.sendMessage({ 
          action: "scan-progress", 
          current: scannedJobIds.size, 
          total: maxJobsToScan,
          title: `${company} - ${title}`
        });
        
        try {
          await logToServer(`POSTing job details to local backend import API...`);
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
    
    await logToServer(`Scan complete. Scanned: ${scannedJobIds.size}, Imported: ${importedCount}`);
    sendResponse({ status: "success", scanned: scannedJobIds.size, imported: importedCount });
  } catch (e) {
    await logToServer(`General Scan Exception: ${e.message}`, "ERROR");
    sendResponse({ status: "error", message: e.message });
  }
}
