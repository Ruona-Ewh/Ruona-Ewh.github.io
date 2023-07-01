document.addEventListener('DOMContentLoaded', function() {
  const copyLinkBtn = document.getElementById('copy-link-btn');
  copyLinkBtn.addEventListener('click', function() {
    const shortUrlInput = document.getElementById('short-url');
    shortUrlInput.select();
    document.execCommand('copy');
    alert('Copied to clipboard!');
  });
});