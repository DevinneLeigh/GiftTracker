// Disable automatic scroll restoration by the browser
if ('scrollRestoration' in history) {
    history.scrollRestoration = 'manual';
}

// Save scroll position before leaving/reloading the page
window.addEventListener('beforeunload', () => {
    localStorage.setItem('scrollPos', window.scrollY);
});

// Restore scroll position after page load
window.addEventListener('DOMContentLoaded', () => {
    const scrollPos = localStorage.getItem('scrollPos');
    if (scrollPos) {
        window.scrollTo(0, parseInt(scrollPos));
        localStorage.removeItem('scrollPos'); // clean up
    }
});
