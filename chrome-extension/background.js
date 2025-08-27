chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("Message received in background script:", request);
  if (request.text) {
    const port = chrome.runtime.connectNative('com.google.chrome.example.echo');
    port.onMessage.addListener(response => {
      console.log('Received from native script:', response);
    });
    port.onDisconnect.addListener(() => {
      if (chrome.runtime.lastError) {
        console.error('Disconnect error:', chrome.runtime.lastError.message);
      }
    });
    port.postMessage({ text: request.text });
  }
});