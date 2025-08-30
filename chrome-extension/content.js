document.addEventListener("keydown", (event) => {
  if (event.ctrlKey && event.key === "g") {
    event.preventDefault();
    const selectedText = window.getSelection().toString().trim();
    if (selectedText) {
      chrome.runtime.sendMessage({ text: selectedText });
    }
  }
});
