chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "scanText",
        title: "Scan Text with AuthGuard",
        contexts: ["selection"]
    });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "scanText") {
        const textToScan = info.selectionText;
        
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            files: ['content.js']
        }, () => {
            chrome.tabs.sendMessage(tab.id, { action: 'scan_text', text: textToScan });
        });
    }
});
