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

function dumpDOMTree(element, depth = 0, maxElements = 150) {
  if (!element || depth > 8 || maxElements <= 0) return [];
  
  let infoList = [];
  const textSnippet = element.children.length === 0 ? element.textContent.trim().substring(0, 50) : "";
  
  infoList.push({
    depth,
    tag: element.tagName,
    class: element.className,
    id: element.id || "",
    role: element.getAttribute('role') || "",
    text: textSnippet.replace(/\s+/g, ' ')
  });
  
  const children = Array.from(element.children);
  for (let child of children) {
    infoList = infoList.concat(dumpDOMTree(child, depth + 1, maxElements - infoList.length));
    if (infoList.length >= maxElements) break;
  }
  
  return infoList;
}

async function startScan(sendResponse) {
  if (window.top !== window.self) {
    return;
  }

  await logToServer("JobHunt Deep Tree Diagnostics Started!");
  
  try {
    // Locate the left panel container
    const leftPanel = document.querySelector('._24f220ff, [class*="_24f220ff"]');
    if (leftPanel) {
      await logToServer(`Found left panel element (Tag: ${leftPanel.tagName}, Class: "${leftPanel.className}")`);
      
      const treeDump = dumpDOMTree(leftPanel);
      await logToServer(`Left Panel DOM Tree (First 150 elements): ${JSON.stringify(treeDump)}`);
    } else {
      await logToServer("Could not find left panel element with class containing '_24f220ff'", "WARNING");
      
      // Fallback: search for results header parent
      const resultsEl = Array.from(document.querySelectorAll('*')).find(el => {
        const text = el.textContent.trim();
        return /^\d+\s+results$/i.test(text) && el.children.length === 0;
      });
      if (resultsEl) {
        let parent = resultsEl.parentElement;
        for (let i = 0; i < 6 && parent; i++) {
          if (parent.className.includes('_24f220ff')) {
            await logToServer(`Found results parent match at level ${i}`);
            const treeDump = dumpDOMTree(parent);
            await logToServer(`Parent Match DOM Tree: ${JSON.stringify(treeDump)}`);
            break;
          }
          parent = parent.parentElement;
        }
      }
    }
  } catch (err) {
    await logToServer(`Deep Diagnostics failed: ${err.message}`, "ERROR");
  }

  sendResponse({ status: "success", scanned: 0, imported: 0 });
}
