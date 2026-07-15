chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "start-scan") {
    startScan(sendResponse);
    return true; // Keep response channel open for async execution
  }
});

async function startScan(sendResponse) {
  console.log("JobHunt Dynamic Scan Started!");
  
  // Find scrollable list container
  const listContainer = document.querySelector('.jobs-search-results-list, .scaffold-layout__list, ul.scaffold-layout__list-container, [class*="results-list"]');
  if (!listContainer) {
    sendResponse({ status: "error", message: "Scrollable job list container not found. Make sure you are on a LinkedIn jobs search page." });
    return;
  }

  const scannedJobIds = new Set();
  let consecutiveFailures = 0;
  let importedCount = 0;
  const maxJobsToScan = 25; // Crawl depth limit per search page

  while (scannedJobIds.size < maxJobsToScan && consecutiveFailures < 6) {
    // Query currently rendered cards
    const cards = Array.from(document.querySelectorAll('li[data-occludable-job-id], [data-job-id], .job-card-container'));
    
    // Find the first unscanned card
    let targetCard = null;
    let targetJobId = null;
    
    for (const card of cards) {
      let jobId = card.getAttribute('data-occludable-job-id') || card.getAttribute('data-job-id');
      if (!jobId) {
        // Fallback to finding href
        const link = card.querySelector('a[href*="/jobs/view/"]');
        if (link) {
          const m = link.href.match(/\/view\/(\d+)/);
          if (m) jobId = m[1];
        }
      }
      
      if (jobId && !scannedJobIds.has(jobId)) {
        targetCard = card;
        targetJobId = jobId;
        break;
      }
    }
    
    // If no unscanned card is found, scroll list container down to load more virtualized items
    if (!targetCard) {
      console.log("No new visible cards found, scrolling list down...");
      listContainer.scrollTop += 350;
      await new Promise(r => setTimeout(r, 1500));
      consecutiveFailures++;
      continue;
    }
    
    consecutiveFailures = 0; // Reset failure counter on target card found
    
    // Send progress update
    chrome.runtime.sendMessage({ 
      action: "scan-progress", 
      current: scannedJobIds.size + 1, 
      total: maxJobsToScan,
      title: "Loading job details..."
    });
    
    // Scroll and Click card
    if (targetCard.scrollIntoView) {
      targetCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    const clickable = targetCard.querySelector('a.job-card-list__title, .job-card-container, a[href*="/jobs/view/"]') || targetCard;
    if (clickable && clickable.click) {
      clickable.click();
    }
    
    // Wait for pane to render
    await new Promise(r => setTimeout(r, 2000));
    
    // Extract details
    const titleEl = document.querySelector('.job-details-jobs-unified-top-card__job-title, h1.t-24, .jobs-unified-top-card__job-title, h2.jobs-details-toggle__title');
    const title = titleEl ? titleEl.textContent.trim() : "";
    
    const companyEl = document.querySelector('.job-details-jobs-unified-top-card__company-name, .jobs-unified-top-card__company-name a, .jobs-unified-top-card__company-name, .jobs-details-toggle__company-name');
    const company = companyEl ? companyEl.textContent.trim() : "LinkedIn Poster";
    
    const locationEl = document.querySelector('.job-details-jobs-unified-top-card__primary-description-container span, .jobs-unified-top-card__bullet, .jobs-unified-top-card__primary-description span, .jobs-details-toggle__job-location');
    const location = locationEl ? locationEl.textContent.trim().split('·')[0].trim() : "Israel";
    
    const descEl = document.querySelector('.jobs-description-content__text, .jobs-description__container, .jobs-box__html-content, .jobs-description');
    const description = descEl ? descEl.textContent.trim() : "";
    
    // Get actual URL from address bar since it changes dynamically on click
    const urlParams = new URLSearchParams(window.location.search);
    const activeJobId = urlParams.get('currentJobId') || targetJobId;
    const jobUrl = `https://www.linkedin.com/jobs/view/${activeJobId}/`;
    
    scannedJobIds.add(targetJobId);
    
    if (title && description) {
      chrome.runtime.sendMessage({ 
        action: "scan-progress", 
        current: scannedJobIds.size, 
        total: maxJobsToScan,
        title: `${company} - ${title}`
      });
      
      try {
        const res = await fetch("http://127.0.0.1:8000/api/jobs/import", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify([{ title, company, location, description, url: jobUrl }])
        });
        if (res.ok) {
          const data = await res.json();
          if (data.new_jobs > 0) {
            importedCount++;
          }
        }
      } catch (err) {
        console.error("Failed to sync job details:", err);
      }
    }
  }
  
  sendResponse({ status: "success", scanned: scannedJobIds.size, imported: importedCount });
}
