var pendingApplications = [];
var confirmedApplications = [];
var lastData = 0;

class UpdateStatusRequest {
    constructor(user_id, name, dataCreate, status) {
        this.user_id = user_id;
        this.name = name;
        this.dataCreate = dataCreate;
        this.status = status;
    }
}

async function sendApplicationStatus(request) {
    const url = 'http://localhost:8001/update_status';
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: request.user_id,
                name: request.name,
                dataCreate: request.dataCreate,
                status: request.status,
            }),
        });

        if (response.ok) {
            console.log(`Application status updated: ${request.status}`);
        } else {
            console.error('Failed to update application status');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

async function getLastUsers(lastDataCreate) {
    try {
        const response = await fetch(`http://localhost:8001/last_data?lastDataCreate=${lastDataCreate}`);
        const data = await response.json();
        lastData = data.reduce((maxDataCreate, application) => {
            return Math.max(maxDataCreate, application.dataCreate);
        }, lastData);
        return data;
    } catch (error) {
        console.error('Error:', error);
        return [];
    }
}

async function getApplications() {
    try {
        const response = await fetch('http://localhost:8001/data');
        const data = await response.json();

        lastData = data.reduce((maxDataCreate, application) => {
            return Math.max(maxDataCreate, application.dataCreate);
        }, lastData);
        return data;
    } catch (error) {
        console.error('Error:', error);
        return [];
    }
}


const refreshInterval = 5000; // 5 секунд = 5000 мілісекунд
setInterval(displayLast, refreshInterval);

function updateRowNumbers(table, numberOfNewRows) {
    // Отримати всі рядки таблиці
    var rows = table.querySelectorAll("tr");

    // Оновити номера рядків
    rows.forEach(function(row, index) {
        row.querySelector("td:first-child").textContent = index + numberOfNewRows;
    });
}

async function displayLast() {
    const applications = await getLastUsers(lastData);
    const pendingTable = document.querySelector("#pendingApplicationsTable tbody");
    const confirmedTable = document.querySelector("#confirmedApplicationsTable tbody");

    applications.forEach(function(application, index) {
        application.address = [
            application.street,
            application.house,
            application.apartment
        ].filter(value => value !== null).join(', ');

        var row = document.createElement("tr");
        var data = Object.values({
            name: application.name,
            typeReq: application.typeReq,
            phone: application.phone,
            address: application.address,
            timeQuests: application.timeQuests,
            pcsQuests: application.pcsQuests,
            car: application.car,
        });

        var numberCell = document.createElement("td");
        numberCell.textContent = index + 1;
        row.appendChild(numberCell);

        data.forEach(function(value) {
            var cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);
        });

        if (application.status === 'Очікує підтвердження') {
            var actionsCell = document.createElement("td");
            var confirmButton = document.createElement("button");
            confirmButton.textContent = "Підтвердити";
            confirmButton.classList.add("confirm-button");
            confirmButton.addEventListener("click", function() {
                if (!confirmButton.disabled) {
                    confirmButton.disabled = true;
                    rejectButton.disabled = true;
                    confirmAction("підтвердити", row, application, pendingTable, confirmedTable);
                }
            });

            var rejectButton = document.createElement("button");
            rejectButton.textContent = "Відхилити";
            rejectButton.classList.add("reject-button");
            rejectButton.addEventListener("click", function() {
                if (!rejectButton.disabled) {
                    confirmButton.disabled = true;
                    rejectButton.disabled = true;
                    confirmAction("відхилити", row, application, pendingTable, confirmedTable);
                }
            });

            actionsCell.appendChild(confirmButton);
            actionsCell.appendChild(rejectButton);
            row.appendChild(actionsCell);

            // Вставити рядок на початок таблиці
            pendingTable.insertBefore(row, pendingTable.firstChild);
            pendingApplications.unshift(application);

            updateRowNumbers(pendingTable, applications.length);
        } else {
            var actionsCell = document.createElement("td");
            actionsCell.textContent = application.status;
            row.appendChild(actionsCell);

            // Вставити рядок на початок таблиці
            confirmedTable.insertBefore(row, confirmedTable.firstChild);
            confirmedApplications.unshift({
                name: application.name,
                typeReq: application.typeReq,
                phone: application.phone,
                address: application.address,
                timeQuests: application.timeQuests,
                pcsQuests: application.pcsQuests,
                car: application.car,
            });

            updateRowNumbers(pendingTable, applications.length);
        }
    });
}


async function displayApplications() {
    const applications = await getApplications();
    const pendingTable = document.querySelector("#pendingApplicationsTable tbody");
    const confirmedTable = document.querySelector("#confirmedApplicationsTable tbody");


    pendingTable.innerHTML = '';
    confirmedTable.innerHTML = '';

    applications.forEach(function(application, index) {
        application.address = [
            application.street,
            application.house,
            application.apartment
        ].filter(value => value !== null).join(', ');

        var row = document.createElement("tr");
        var data = Object.values({
            name: application.name,
            typeReq: application.typeReq,
            phone: application.phone,
            address: application.address,
            timeQuests: application.timeQuests,
            pcsQuests: application.pcsQuests,
            car: application.car,

        });

        var numberCell = document.createElement("td");
        numberCell.textContent = index + 1;
        row.appendChild(numberCell);

        data.forEach(function(value) {
            var cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);
        });

        if (application.status === 'Очікує підтвердження') {
            var actionsCell = document.createElement("td");
            var confirmButton = document.createElement("button");
            confirmButton.textContent = "Підтвердити";
            confirmButton.classList.add("confirm-button");
            confirmButton.addEventListener("click", function() {
                if (!confirmButton.disabled) {
                    confirmButton.disabled = true;
                    rejectButton.disabled = true;
                    confirmAction("підтвердити", row, application, pendingTable, confirmedTable);
                }
            });

            var rejectButton = document.createElement("button");
            rejectButton.textContent = "Відхилити";
            rejectButton.classList.add("reject-button");
            rejectButton.addEventListener("click", function() {
                if (!rejectButton.disabled) {
                    confirmButton.disabled = true;
                    rejectButton.disabled = true;
                    confirmAction("відхилити", row, application, pendingTable, confirmedTable);
                }
            });

            actionsCell.appendChild(confirmButton);
            actionsCell.appendChild(rejectButton);
            row.appendChild(actionsCell);

            pendingTable.appendChild(row);
            pendingApplications.push(application);
        } else {


            // row.cells[row.cells.length +1].textContent = application.status;
            var actionsCell = document.createElement("td");
            actionsCell.textContent = application.status;
            row.appendChild(actionsCell);
            confirmedTable.appendChild(row);
            confirmedApplications.push({
                name: application.name,
                typeReq: application.typeReq,
                phone: application.phone,
                address: application.address,
                timeQuests: application.timeQuests,
                pcsQuests: application.pcsQuests,
                car: application.car,
            });
        }
    });
}

async function sortApplications() {
    const applications = await getApplications();
    applications.sort(function(a, b) {
        if (a.status === 'Очікує підтвердження' && b.status !== 'Очікує підтвердження') {
            return -1;
        } else if (a.status !== 'Очікує підтвердження' && b.status === 'Очікує підтвердження') {
            return 1;
        } else {
            return 0;
        }
    });

    return applications;
}

async function confirmAction(action, row, application, pendingTable, confirmedTable) {
    if (confirm(`Ви впевнені, що бажаєте ${action} заявку?`)) {
        application.status = action === 'підтвердити' ? 'Підтверджено' : 'Відхилено';
        console.log(application);
        // Update the status directly in the "Status" column and add a styling class
        row.cells[8].textContent = application.status;
        row.cells[8].classList.add(application.status.toLowerCase());

        if (application.status === 'Підтверджено' || application.status === 'Відхилено') {

            const updateRequest = new UpdateStatusRequest(
                application.user_id,
                application.name,
                application.dataCreate,
                application.status
            );

            await sendApplicationStatus(updateRequest);
            console.log(updateRequest);

            pendingTable.removeChild(row);
            confirmedTable.appendChild(row);
            confirmedApplications.push(application);

            var index = pendingApplications.indexOf(application);
            if (index > -1) {
                pendingApplications.splice(index, 1);
            }
        }
    } else {
        var confirmButton = row.querySelector(".confirm-button");
        var rejectButton = row.querySelector(".reject-button");
        confirmButton.disabled = false;
        rejectButton.disabled = false;
    }
}

displayApplications();