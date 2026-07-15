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
    const allElements = Array.from(document.querySelectorAll('*'));
    const resultsEl = allElements.find(el => {
      const text = el.textContent.trim();
      return /^\d+\s+results$/i.test(text) && el.children.length === 0;
    });

    if (resultsEl) {
      await logToServer(`Found results header: "${resultsEl.textContent.trim()}" (Tag: ${resultsEl.tagName})`);
      
      let headerElement = resultsEl;
      while (headerElement && headerElement.tagName !== 'HEADER') {
        headerElement = headerElement.parentElement;
      }
      
      if (headerElement) {
        await logToServer(`Found ancestor <header> (Class: "${headerElement.className}")`);
        
        // Log all siblings of this header element! One of them MUST be the jobs list container!
        const siblings = Array.from(headerElement.parentElement.children);
        await logToServer(`Header parent container tag: ${headerElement.parentElement.tagName}, class: "${headerElement.parentElement.className}"`);
        await logToServer(`Header has ${siblings.length} siblings in its parent container.`);
        
        for (let i = 0; i < siblings.length; i++) {
          const sib = siblings[i];
          await logToServer(`Sibling ${i}: Tag=${sib.tagName}, Class="${sib.className}", ChildrenCount=${sib.children.length}`);
          
          // Dump the first level of child elements inside this sibling
          const subChildren = Array.from(sib.children).map((c, idx) => ({
            idx,
            tag: c.tagName,
            class: c.className,
            textSnippet: c.textContent.trim().substring(0, 80).replace(/\s+/g, ' ')
          }));
          await logToServer(`Sibling ${i} Children Snippet: ${JSON.stringify(subChildren)}`);
          
          // If this sibling contains a list of children (e.g. 5+ cards), let's inspect the cards!
          if (sib.children.length > 1) {
            await logToServer(`--- Inspecting Sibling ${i} Children in Detail ---`);
            Array.from(sib.children).slice(0, 5).forEach((child, idx) => {
              // Log the child element's tags and child count
              const childLinks = Array.from(child.querySelectorAll('a')).map(a => ({
                text: a.textContent.trim(),
                href: a.getAttribute('href'),
                class: a.className
              }));
              logToServer(`Card ${idx}: Tag=${child.tagName}, Class="${child.className}", Links: ${JSON.stringify(childLinks)}`);
            });
          }
        }
      } else {
        await logToServer("Could not find ancestor <header> element.", "WARNING");
      }
    } else {
      await logToServer("Could not locate the 'results' header text leaf element.", "WARNING");
    }

  } catch (err) {
    await logToServer(`Diagnostics failed: ${err.message}`, "ERROR");
  }

  sendResponse({ status: "success", scanned: 0, imported: 0 });
}
