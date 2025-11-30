//Save the active open tab on page reloads


document.addEventListener("DOMContentLoaded", function () {
    const tabButtons = document.querySelectorAll('button[data-bs-toggle="tab"]');

    // Restore active tab from localStorage
    const activeTab = localStorage.getItem("activeTab");
    if (activeTab) {
        const triggerEl = document.querySelector(`button[data-bs-target="${activeTab}"]`);
        if (triggerEl) {
            const tab = new bootstrap.Tab(triggerEl);
            tab.show();
        }
    }

    // Save active tab to localStorage whenever it changes
    tabButtons.forEach(tab => {
        tab.addEventListener("shown.bs.tab", function (e) {
            localStorage.setItem("activeTab", e.target.getAttribute("data-bs-target"));
        });
    });
});
