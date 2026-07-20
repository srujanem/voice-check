chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "scanText",
        title: "Scan Text with AuthGuard",
        contexts: ["selection"]
    });
    chrome.contextMenus.create({
        id: "scanImage",
        title: "Scan Image with AuthGuard",
        contexts: ["image"]
    });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
    const isImage = info.menuItemId === "scanImage";
    const payload = isImage ? info.srcUrl : info.selectionText;
    
    // Inject content script if not there
    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['content.js']
    }, () => {
        // Show loading state
        chrome.tabs.sendMessage(tab.id, { 
            action: 'show_loading', 
            type: isImage ? 'image' : 'text'
        });
        
        // Handle fetch in background script to avoid CORS
        analyzeContent(payload, isImage, tab.id);
    });
});

async function analyzeContent(payload, isImage, tabId) {
    try {
        let formData = new FormData();
        
        if (isImage) {
            // Fetch the image to get a blob, then send to API
            const imageRes = await fetch(payload);
            const blob = await imageRes.blob();
            formData.append('file', blob, 'image.jpg');
            formData.append('type', 'image');
        } else {
            // Text analysis
            // Create a temporary text file for the API
            const blob = new Blob([payload], { type: 'text/plain' });
            formData.append('file', blob, 'text.txt');
            formData.append('type', 'text');
        }
        
        // Assuming user runs local node server on port 8000
        const res = await fetch('http://localhost:8000/api/infer', {
            method: 'POST',
            body: formData
        });
        
        if (!res.ok) throw new Error("Backend server not reachable");
        
        const data = await res.json();
        chrome.tabs.sendMessage(tabId, { action: 'show_result', data: data });
        
    } catch (err) {
        chrome.tabs.sendMessage(tabId, { action: 'show_error', error: err.message });
    }
}
