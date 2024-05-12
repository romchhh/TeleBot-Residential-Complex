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
setInterval(displayApplications, refreshInterval);

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
  toggleNoPendingApplicationsMessage();
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



const pendingTable = document.querySelector("#pendingApplicationsTable");
const noPendingApplicationsMessage = document.createElement("p");
noPendingApplicationsMessage.textContent = "Немає нових заявок";
noPendingApplicationsMessage.style.fontSize = "24px";
noPendingApplicationsMessage.style.fontWeight = "bold";
noPendingApplicationsMessage.style.color = "#333";
noPendingApplicationsMessage.style.textAlign = "center";
noPendingApplicationsMessage.style.padding = "10px";
noPendingApplicationsMessage.style.borderRadius = "5px";

function toggleNoPendingApplicationsMessage() {
  const pendingApplicationsCount = pendingTable.querySelectorAll("tbody tr").length;
  if (pendingApplicationsCount === 0) {
    if (!noPendingApplicationsMessage.parentNode) {
      // Додати повідомлення, якщо його ще немає в DOM
      pendingTable.parentNode.insertBefore(noPendingApplicationsMessage, pendingTable.nextSibling);
    }
  } else {
    if (noPendingApplicationsMessage.parentNode) {
      // Видалити повідомлення, якщо воно вже є в DOM
      noPendingApplicationsMessage.remove();
    }
  }
}

// Відобразити повідомлення "Немає нових заявок" відразу після завантаження сторінки
toggleNoPendingApplicationsMessage();

displayApplications();
setInterval(displayApplications, refreshInterval);