document.addEventListener('DOMContentLoaded', function () {
    const socket = io();
    const tableBody = document.querySelector('table tbody');

    // Remove the "No reports found" row if it exists
    const noReportsRow = document.querySelector('#no-reports-row');

    socket.on('new_report', function(report) {
        if (noReportsRow) {
            noReportsRow.remove();
        }

        const newRow = document.createElement('tr');

        const aiSuggestionBadge = report.ai_suggestion
            ? `<span class="badge bg-info text-dark">${report.ai_suggestion}</span>`
            : 'N/A';

        newRow.innerHTML = `
            <td>${report.id}</td>
            <td>${report.time}</td>
            <td>${report.animal}</td>
            <td>${aiSuggestionBadge}</td>
            <td>${report.condition}</td>
            <td><span class="badge bg-danger">${report.status}</span></td>
            <td>Unclaimed</td>
            <td>
                <form method="POST" style="display: inline;">
                    <button type="submit" formaction="${report.claim_url}" class="btn btn-primary btn-sm">Claim</button>
                </form>
            </td>
        `;

        tableBody.prepend(newRow);

        if (Notification.permission === "granted") {
            new Notification("New Incident Reported!", {
                body: `A ${report.animal} needs help. Click to view dashboard.`,
                icon: "/static/favicon.ico" // Optional: Add an icon
            });
        } else if (Notification.permission !== "denied") {
            Notification.requestPermission().then(permission => {
                if (permission === "granted") {
                    new Notification("New Incident Reported!");
                }
            });
        }
    });
});