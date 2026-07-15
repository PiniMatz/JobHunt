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

  await logToServer("JobHunt Diagnostics Scan Started!");
  
  try {
    // 1. Locate the "results" header leaf element
    const allElements = Array.from(document.querySelectorAll('*'));
    const resultsEl = allElements.find(el => {
      const text = el.textContent.trim();
      return /^\d+\s+results$/i.test(text) && el.children.length === 0;
    });

    if (resultsEl) {
      await logToServer(`Found results header: "${resultsEl.textContent.trim()}" (Tag: ${resultsEl.tagName}, Class: "${resultsEl.className}")`);
      
      // Let's traverse up to 4 levels of parents and log their structures
      let parent = resultsEl.parentElement;
      for (let level = 1; level <= 4 && parent; level++) {
        const siblingsCount = parent.parentElement ? parent.parentElement.children.length : 0;
        await logToServer(`Parent Level ${level}: Tag=${parent.tagName}, Class="${parent.className}", SiblingCount=${siblingsCount}`);
        
        // Log child elements of this parent
        const childrenInfo = Array.from(parent.children).map((c, idx) => ({
          idx,
          tag: c.tagName,
          class: c.className,
          textSnippet: c.textContent.trim().substring(0, 50).replace(/\s+/g, ' ')
        }));
        await logToServer(`Parent Level ${level} Children: ${JSON.stringify(childrenInfo)}`);
        
        parent = parent.parentElement;
      }
    } else {
      await logToServer("Could not locate the 'results' header text leaf element.", "WARNING");
    }

    // 2. Log general document structure highlights
    const listContainers = allElements.filter(el => 
      el.className && (
        el.className.includes('results-list') || 
        el.className.includes('scaffold-layout__list') ||
        el.className.includes('jobs-search-results-list')
      )
    ).map(el => ({ tag: el.tagName, class: el.className, childrenCount: el.children.length }));
    await logToServer(`Potential List Containers: ${JSON.stringify(listContainers)}`);

  } catch (err) {
    await logToServer(`Diagnostics failed: ${err.message}`, "ERROR");
  }

  sendResponse({ status: "success", scanned: 0, imported: 0 });
}
