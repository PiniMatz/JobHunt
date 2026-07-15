chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "start-scan") {
    startScan(sendResponse);
    return true; // Keep response channel open for async execution
  }
});

async function startScan(sendResponse) {
  console.log("JobHunt Scan Started!");
  
  // Find scrollable list container with multiple fallbacks
  const listContainer = document.querySelector('.jobs-search-results-list, .scaffold-layout__list, ul.scaffold-layout__list-container, .jobs-search__results-list, [class*="results-list"]');
  
  // Scroll list container to bottom to trigger lazy loading of list cards
  if (listContainer) {
    listContainer.scrollTop = listContainer.scrollHeight;
    await new Promise(r => setTimeout(r, 1500));
    listContainer.scrollTop = 0;
  } else {
    // Fallback to scrolling window
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    await new Promise(r => setTimeout(r, 1500));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  
  // Robust selectors for job cards
  const selectors = [
    '.scaffold-layout__list-container li[data-occludable-job-id]',
    'li[data-occludable-job-id]',
    '.jobs-search-results-list__list-item',
    '.job-card-container',
    '[data-job-id]'
  ];
  
  let items = [];
  for (const selector of selectors) {
    items = Array.from(document.querySelectorAll(selector));
    if (items.length > 0) {
      console.log(`Matched selector: ${selector} with ${items.length} items.`);
      break;
    }
  }
  
  // Fallback: search for direct jobs/view links
  if (items.length === 0) {
    const jobLinks = Array.from(document.querySelectorAll('a[href*="/jobs/view/"]'));
    if (jobLinks.length > 0) {
      items = jobLinks.map(link => {
        let parent = link.parentElement;
        while (parent && parent.tagName !== 'LI' && !parent.classList.contains('job-card-container')) {
          parent = parent.parentElement;
        }
        return parent || link;
      }).filter((v, i, self) => self.indexOf(v) === i);
      console.log(`Fallback matched ${items.length} items from jobs/view links.`);
    }
  }
  
  console.log(`Found ${items.length} job cards to scan.`);
  
  if (items.length === 0) {
    sendResponse({ status: "error", message: "No job cards found. Make sure you are on the LinkedIn jobs page and jobs are visible." });
    return;
  }
  
  let scannedCount = 0;
  let importedCount = 0;
  
  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    
    // Update progress to popup via runtime message
    chrome.runtime.sendMessage({ 
      action: "scan-progress", 
      current: i + 1, 
      total: items.length,
      title: "Loading..."
    });
    
    // Scroll item into view and click it
    if (item.scrollIntoView) {
      item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    const clickable = item.querySelector('a.job-card-list__title, .job-card-container, a[href*="/jobs/view/"]') || item;
    if (clickable && clickable.click) {
      clickable.click();
    }
    
    // Wait for description pane to load
    await new Promise(r => setTimeout(r, 2000));
    
    // Extract info with robust selectors
    const titleEl = document.querySelector('.job-details-jobs-unified-top-card__job-title, h1.t-24, .jobs-unified-top-card__job-title, h2.jobs-details-toggle__title');
    const title = titleEl ? titleEl.textContent.trim() : "";
    
    const companyEl = document.querySelector('.job-details-jobs-unified-top-card__company-name, .jobs-unified-top-card__company-name a, .jobs-unified-top-card__company-name, .jobs-details-toggle__company-name');
    const company = companyEl ? companyEl.textContent.trim() : "LinkedIn Poster";
    
    const locationEl = document.querySelector('.job-details-jobs-unified-top-card__primary-description-container span, .jobs-unified-top-card__bullet, .jobs-unified-top-card__primary-description span, .jobs-details-toggle__job-location');
    const location = locationEl ? locationEl.textContent.trim().split('·')[0].trim() : "Israel";
    
    const descEl = document.querySelector('.jobs-description-content__text, .jobs-description__container, .jobs-box__html-content, .jobs-description');
    const description = descEl ? descEl.textContent.trim() : "";
    
    // Extract URL
    const urlParams = new URLSearchParams(window.location.search);
    const jobId = urlParams.get('currentJobId');
    const jobUrl = jobId ? `https://www.linkedin.com/jobs/view/${jobId}/` : window.location.href;
    
    if (title && description) {
      scannedCount++;
      
      // Update progress with title
      chrome.runtime.sendMessage({ 
        action: "scan-progress", 
        current: i + 1, 
        total: items.length,
        title: `${company} - ${title}`
      });
      
      // POST to local FastAPI backend
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
  
  sendResponse({ status: "success", scanned: scannedCount, imported: importedCount });
}
