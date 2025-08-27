document.addEventListener('mouseup', event => {
  const selectedText = window.getSelection().toString().trim();
  if (selectedText) {
    chrome.runtime.sendMessage({ text: selectedText });
  }
});