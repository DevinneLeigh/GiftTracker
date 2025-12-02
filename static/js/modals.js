
// Open Add/Edit Modal
function openModal(title, url) {
    const modalTitle = document.getElementById("addModalTitle");
    modalTitle.textContent = title;

    // Load form via Django
    fetch(url)
        .then(resp => resp.text())
        .then(html => {
            document.getElementById("addModalBody").innerHTML = html;

            // Update form action:
            const form = document.getElementById("addModalForm");
            form.action = url;
        });
}


// Open Delete Modal
function openDeleteModal(url, label) {
    const form = document.getElementById("deleteForm");
    form.action = url;

    document.getElementById("deleteModalTitle").textContent = `Delete ${label}`;
    document.getElementById("deleteModalBody").textContent =
        `Are you sure you want to delete this ${label}?`;
}



// Toggle delete mode on/off
document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("bulkDeleteToggle");
    const boxes = document.querySelectorAll(".delete-checkbox");
    const selectAll = document.getElementById("selectAll");

    function updateCheckboxVisibility() {
        if (toggle.checked) {
            boxes.forEach(cb => cb.style.visibility = "visible");
        } else {
            boxes.forEach(cb => cb.style.visibility = "hidden");
        }
    }

    // Run once on page load
    updateCheckboxVisibility();

    // Run whenever toggle changes
    toggle.addEventListener("change", updateCheckboxVisibility);

        if (selectAll) {
        selectAll.addEventListener("change", () => {
            const checked = selectAll.checked;
            boxes.forEach(cb => {
                cb.checked = checked;
            });
        });
    }

    boxes.forEach(cb => {
    cb.addEventListener("change", () => {
        if (!cb.checked && selectAll.checked) {
            selectAll.checked = false;
        }
    });
});
});


// Open modal for bulk delete
function openBulkDeleteModal() {
    const checked = Array.from(document.querySelectorAll(".delete-checkbox"))
                         .filter(cb => cb.checked)
                         .map(cb => cb.value);

    const deleteForm = document.getElementById("deleteForm");
    const body = document.getElementById("deleteModalBody");
    const title = document.getElementById("deleteModalTitle");

    // Set form action to bulk delete URL
    deleteForm.action = "/wishlist/bulk_delete/";

    title.textContent = "Delete Selected Items";
    body.textContent = `Are you sure you want to delete ${checked.length} item(s)?`;

    // Add hidden field containing IDs
    let hidden = document.getElementById("bulkDeleteIds");
    if (hidden) hidden.remove(); // remove old one

    hidden = document.createElement("input");
    hidden.type = "hidden";
    hidden.name = "ids";
    hidden.id = "bulkDeleteIds";
    hidden.value = checked.join(",");

    deleteForm.appendChild(hidden);
}

window.openBulkDeleteModal = openBulkDeleteModal;

