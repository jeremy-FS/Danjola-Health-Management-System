document.addEventListener("DOMContentLoaded", function () {
    // Auto-hide flash messages after 3 seconds
    setTimeout(function () {
        let flashMessages = document.querySelectorAll(".alert");
        flashMessages.forEach(function (message) {
            message.style.display = "none";
        });
    }, 3000);

    // Confirmation before deleting records
    let deleteButtons = document.querySelectorAll(".delete-btn");
    deleteButtons.forEach(function (btn) {
        btn.addEventListener("click", function (event) {
            if (!confirm("Are you sure you want to delete this record?")) {
                event.preventDefault();
            }
        });
    });

    // Live search functionality
    let searchInput = document.getElementById("searchInput");
    if (searchInput) {
        searchInput.addEventListener("keyup", function () {
            let filter = searchInput.value.toLowerCase();
            let rows = document.querySelectorAll("table tbody tr");

            rows.forEach(function (row) {
                let text = row.innerText.toLowerCase();
                if (text.includes(filter)) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }
            });
        });
    }
});
