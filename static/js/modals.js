
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
    const toggle = document.getElementById("toggleDeleteMode");
    const controls = document.getElementById("deleteControls");
    const checkboxes = document.querySelectorAll(".delete-checkbox");

    if (!toggle) return;

    toggle.addEventListener("change", () => {
        const show = toggle.checked;

        // show/hide controls
        controls.classList.toggle("d-none", !show);

        // show/hide checkboxes
        checkboxes.forEach(cb => {
            cb.classList.toggle("d-none", !show);
            cb.checked = false;
        });

        // reset select all
        const selectAll = document.getElementById("selectAll");
        if (selectAll) selectAll.checked = false;
    });

    // Select all functionality
    const selectAll = document.getElementById("selectAll");
    if (selectAll) {
        selectAll.addEventListener("change", () => {
            checkboxes.forEach(cb => cb.checked = selectAll.checked);
        });
    }
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
