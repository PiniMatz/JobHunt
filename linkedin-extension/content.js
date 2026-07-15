chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "start-scan") {
    startScan(sendResponse);
    return true; // Keep response channel open for async execution
  }
});

async function startScan(sendResponse) {
  console.log("JobHunt Dynamic Scan Started!");
  
  // Find scrollable list container with multiple fallbacks
  const listContainer = document.querySelector('.jobs-search-results-list, .scaffold-layout__list, ul.scaffold-layout__list-container, [class*="results-list"], [class*="scaffold-layout__list"]');
  if (!listContainer) {
    console.warn("Scrollable container not found by class. Using scrollIntoView fallback.");
  }

  const scannedJobIds = new Set();
  let consecutiveFailures = 0;
  let importedCount = 0;
  const maxJobsToScan = 25; // Crawl depth limit per search page

  while (scannedJobIds.size < maxJobsToScan && consecutiveFailures < 6) {
    // Query currently rendered cards dynamically via view links
    const cards = [];
    const jobLinks = Array.from(document.querySelectorAll('a[href*="/jobs/view/"]'));
    
    jobLinks.forEach(link => {
      const card = link.closest('li, .job-card-container, [data-job-id]') || link;
      const href = link.getAttribute('href') || "";
      const m = href.match(/\/view\/(\d+)/) || href.match(/currentJobId=(\d+)/);
      const jobId = m ? m[1] : null;
      
      if (jobId && !cards.some(c => c.jobId === jobId)) {
        cards.push({ card, jobId, link });
      }
    });
    
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
      console.log("No new visible cards found, scrolling list down...");
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
    
    // Send progress update
    chrome.runtime.sendMessage({ 
      action: "scan-progress", 
      current: scannedJobIds.size + 1, 
      total: maxJobsToScan,
      title: "Loading job details..."
    });
    
    // Scroll and Click card
    if (target.card.scrollIntoView) {
      target.card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    if (target.link && target.link.click) {
      target.link.click();
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
