
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


// modals.js (replace existing content)
function getCookie(name) {
    // basic cookie-getter for CSRF
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function giftModal(title, url) {
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

            // Reset submit button text to "Search"
            const submitBtn = form.querySelector("button[type='submit']");
            if (submitBtn) {
                submitBtn.textContent = "Search";
                submitBtn.dataset.mode = "search"; // custom flag
            }

            // ensure scrapeResults hidden initially
            const results = document.getElementById("scrapeResults");
            if (results) results.style.display = "none";
        });
}

// Intercept submit events for the modal form:
document.addEventListener("DOMContentLoaded", function() {
    const modalForm = document.getElementById("addModalForm");

    if (!modalForm) return;

    modalForm.addEventListener("submit", function(e) {
        // find the submit button to read mode
        const submitBtn = modalForm.querySelector("button[type='submit']");
        const mode = submitBtn ? submitBtn.dataset.mode : "submit";

        // If we're in 'search' mode, intercept and perform AJAX scrape:
        if (mode === "search") {
            e.preventDefault();

            // get url field value
            const urlField = modalForm.querySelector("input[name='item_url']");
            const url = urlField ? urlField.value.trim() : "";

            if (!url) {
                // simple inline error message
                if (!modalForm.querySelector("#urlError")) {
                    const err = document.createElement("div");
                    err.id = "urlError";
                    err.className = "text-danger small mt-1";
                    err.textContent = "Please enter a product URL.";
                    if (urlField && urlField.parentNode) urlField.parentNode.appendChild(err);
                }
                return;
            } else {
                const existingErr = modalForm.querySelector("#urlError");
                if (existingErr) existingErr.remove();
            }

            // disable button while searching
            submitBtn.disabled = true;
            submitBtn.textContent = "Searching...";

            // Prepare form data
            const formData = new FormData();
            formData.append("item_url", url);

            // CSRF
            const csrftoken = getCookie("csrftoken");

            fetch("/scrape-product/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                },
                body: formData
            })
            .then(resp => resp.json().then(json => ({ status: resp.status, body: json })))
            .then(({ status, body }) => {
                if (status >= 200 && status < 300 && !body.error) {
                    // populate fields
                    const nameInput = modalForm.querySelector("#id_product_name");
                    const priceInput = modalForm.querySelector("#id_product_price");
                    const imagePreview = modalForm.querySelector("#id_product_image_preview");
                    const imageHidden = modalForm.querySelector("#id_product_image");

                    if (nameInput) nameInput.value = body.name || "";
                    if (priceInput) priceInput.value = body.price || "";

                    if (body.image) {
                        if (imagePreview) {
                            imagePreview.src = body.image;
                            imagePreview.style.display = "block";
                        }
                        if (imageHidden) imageHidden.value = body.image;
                    } else {
                        if (imagePreview) {
                            imagePreview.src = "";
                            imagePreview.style.display = "none";
                        }
                        if (imageHidden) imageHidden.value = "";
                    }

                    // show results area
                    const results = modalForm.querySelector("#scrapeResults");
                    if (results) results.style.display = "block";

                    // switch button to submit mode
                    if (submitBtn) {
                        submitBtn.textContent = "Submit";
                        submitBtn.dataset.mode = "submit";
                        submitBtn.disabled = false;
                    }
                } else {
                    // show message that scraping failed but allow manual input
                    const results = modalForm.querySelector("#scrapeResults");
                    if (results) results.style.display = "block";

                    // clear fields
                    const nameInput = modalForm.querySelector("#id_product_name");
                    const priceInput = modalForm.querySelector("#id_product_price");
                    const imagePreview = modalForm.querySelector("#id_product_image_preview");
                    const imageHidden = modalForm.querySelector("#id_product_image");

                    if (nameInput) nameInput.value = "";
                    if (priceInput) priceInput.value = "";
                    if (imagePreview) {
                        imagePreview.src = "";
                        imagePreview.style.display = "none";
                    }
                    if (imageHidden) imageHidden.value = "";

                    // show inline alert
                    let alertArea = modalForm.querySelector("#scrapeAlert");
                    if (!alertArea) {
                        alertArea = document.createElement("div");
                        alertArea.id = "scrapeAlert";
                        alertArea.className = "text-warning small mt-2";
                        const urlField = modalForm.querySelector("input[name='item_url']");
                        if (urlField && urlField.parentNode) urlField.parentNode.appendChild(alertArea);
                    }
                    alertArea.textContent = body.error || "Could not automatically extract product info. Please enter name and price manually.";

                    // set button to Submit so user can save manual inputs
                    if (submitBtn) {
                        submitBtn.textContent = "Submit";
                        submitBtn.dataset.mode = "submit";
                        submitBtn.disabled = false;
                    }
                }
            })
            .catch(err => {
                console.error("Scrape request failed:", err);
                // show manual input area
                const results = modalForm.querySelector("#scrapeResults");
                if (results) results.style.display = "block";

                // show inline error
                let alertArea = modalForm.querySelector("#scrapeAlert");
                if (!alertArea) {
                    alertArea = document.createElement("div");
                    alertArea.id = "scrapeAlert";
                    alertArea.className = "text-danger small mt-2";
                    const urlField = modalForm.querySelector("input[name='item_url']");
                    if (urlField && urlField.parentNode) urlField.parentNode.appendChild(alertArea);
                }
                alertArea.textContent = "Network error while trying to fetch product data. You can still enter name and price manually.";

                if (submitBtn) {
                    submitBtn.textContent = "Submit";
                    submitBtn.dataset.mode = "submit";
                    submitBtn.disabled = false;
                }
            });
        } else {
            // mode === "submit": let the browser perform the normal POST to the existing endpoint
            // we do not intercept; this will close the modal via normal redirect.
            // But to be safe, ensure the submit button is not in 'search' mode
            // and that scrapeResults exists (so server can get posted fields).
            // No preventDefault here.
        }
    });
});


// function editGiftModal(title, url) {
//     const modalTitle = document.getElementById("addModalTitle");
//     modalTitle.textContent = title;

//     // Load edit form
//     fetch(url)
//         .then(resp => resp.text())
//         .then(html => {
//             document.getElementById("addModalBody").innerHTML = html;

//             // Update form action
//             const form = document.getElementById("addModalForm");
//             form.action = url;

//             // Remove search functionality completely
//             const submitBtn = form.querySelector("button[type='submit']");
//             if (submitBtn) {
//                 submitBtn.textContent = "Submit";
//                 submitBtn.dataset.mode = "submit";  // ALWAYS submit
//             }

//             // Show edit fields right away
//             const results = document.getElementById("scrapeResults");
//             if (results) results.style.display = "block";
//         });
// }


function editGiftModal(title, url) {
    const modalTitle = document.getElementById("addModalTitle");
    modalTitle.textContent = title;

    fetch(url)
        .then(resp => resp.text())
        .then(html => {
            const modalBody = document.getElementById("addModalBody");
            modalBody.innerHTML = html;

            const form = document.getElementById("addModalForm");
            form.action = url;

            const submitBtn = form.querySelector("button[type='submit']");
            if (submitBtn) submitBtn.dataset.mode = "edit"; // mark as edit
        });
}

// Intercept the edit form submit
document.addEventListener("submit", function(e) {
    const form = e.target;
    const submitBtn = form.querySelector("button[type='submit']");
    if (!submitBtn) return;
    const mode = submitBtn.dataset.mode;
    if (mode === "edit") {
        e.preventDefault();

        const formData = new FormData(form);
        const csrftoken = getCookie("csrftoken");

        fetch(form.action, {
            method: "POST",
            headers: { "X-CSRFToken": csrftoken },
            body: formData,
        })
        .then(resp => resp.text())
        .then(html => {
            // close modal and refresh page or update table
            const modalEl = document.getElementById("addModal");
            const modal = bootstrap.Modal.getInstance(modalEl);
            modal.hide();

            // optionally reload the gifts table
            location.reload();
        });
    }
});




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

    if (toggle) {
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

