/* static/script.js */
async function sendMessage() {
    const user_input = document.getElementById("user_input").value.trim();
    if (!user_input) return;

    const response = await fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_input: user_input })
    }).then(res => res.json());

    const chatWindow = document.getElementById("chat_window");

    // Benutzer-Nachricht anzeigen
    const userMessageDiv = document.createElement("div");
    userMessageDiv.classList.add("chat-message", "user");
    const userBubble = document.createElement("div");
    userBubble.classList.add("chat-bubble", "user");
    userBubble.innerText = user_input;
    userMessageDiv.appendChild(userBubble);
    chatWindow.appendChild(userMessageDiv);

    // Antwort des ChatAssistenten anzeigen
    if (response.response) {
        const botMessageDiv = document.createElement("div");
        botMessageDiv.classList.add("chat-message", "chatassistant");
        const botBubble = document.createElement("div");
        botBubble.classList.add("chat-bubble", "chatassistant");
        botBubble.innerText = response.response;
        botMessageDiv.appendChild(botBubble);
        chatWindow.appendChild(botMessageDiv);
    } else {
        const errorMessageDiv = document.createElement("div");
        errorMessageDiv.classList.add("chat-message", "chatassistant");
        const errorBubble = document.createElement("div");
        errorBubble.classList.add("chat-bubble", "chatassistant");
        errorBubble.innerText = 'Fehler: ' + response.error;
        errorMessageDiv.appendChild(errorBubble);
        chatWindow.appendChild(errorMessageDiv);
    }

    document.getElementById("user_input").value = "";
    chatWindow.scrollTop = chatWindow.scrollHeight;
}


async function uploadPDF() {
    const fileInput = document.getElementById("pdf_upload");
    const formData = new FormData();
    formData.append("pdf", fileInput.files[0]);

    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    }).then(res => res.json());

    if (response.success) {
        const fileList = document.getElementById("file_list");
        const newFile = document.createElement("li");
        const fileLink = document.createElement("a");
        fileLink.href = `/uploads/${response.filename}`;
        fileLink.target = "_blank";
        fileLink.textContent = response.filename;
        newFile.appendChild(fileLink);
        fileList.appendChild(newFile);
    } else {
        alert("Fehler beim Hochladen der Datei");
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("user_input");
    inputField.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });
});


let selectedFile = null; // Variable, um die ausgewählte Datei zu speichern

// Datei auswählen oder Auswahl zurücksetzen
function selectFile(filename) {
    const fileListItems = document.querySelectorAll("#file_list li");

    // Wenn dieselbe Datei erneut angeklickt wird, wird die Auswahl zurückgesetzt
    if (selectedFile === filename) {
        selectedFile = null; // Auswahl zurücksetzen
        fileListItems.forEach(item => {
            item.style.backgroundColor = ""; // Markierung entfernen
            item.style.color = ""; // Standardfarbe
        });

        // Delete-Button ausblenden
        const deleteSection = document.getElementById("delete_section");
        deleteSection.style.display = "none";
        console.log("Auswahl zurückgesetzt");
        return;
    }

    // Neue Datei auswählen
    selectedFile = filename;

    // Alle Elemente zurücksetzen
    fileListItems.forEach(item => {
        item.style.backgroundColor = ""; // Markierung entfernen
        item.style.color = ""; // Standardfarbe
    });

    // Markiere das angeklickte Element
    const clickedItem = document.querySelector(`[data-filename='${filename}']`);
    if (clickedItem) {
        clickedItem.style.backgroundColor = "#007bff"; // Highlight-Farbe
        clickedItem.style.color = "#ffffff"; // Lesbare Textfarbe
    }

    // Delete-Button anzeigen
    const deleteSection = document.getElementById("delete_section");
    deleteSection.style.display = "block";

    console.log("Ausgewählte Datei:", selectedFile);
}

// Datei löschen
async function deleteSelectedFile() {
    if (!selectedFile) {
        alert("Bitte zuerst eine Datei auswählen!");
        return;
    }

    // Bestätigung
    if (!confirm(`Möchten Sie die Datei "${selectedFile}" wirklich löschen?`)) {
        return;
    }

    try {
        // Anfrage an den Server senden
        const response = await fetch('/delete_file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ filename: selectedFile })
        });
        const result = await response.json();

        if (result.success) {
            // Datei aus der Liste entfernen
            const fileListItem = document.querySelector(`[data-filename='${selectedFile}']`);
            if (fileListItem) {
                fileListItem.remove();
            }

            // Delete-Button ausblenden
            const deleteSection = document.getElementById("delete_section");
            deleteSection.style.display = "none";

            // Erfolgsmeldung anzeigen
            alert(`Datei "${selectedFile}" wurde erfolgreich gelöscht.`);
            selectedFile = null; // Auswahl zurücksetzen
        } else {
            alert(`Fehler beim Löschen: ${result.error}`);
        }
    } catch (error) {
        console.error("Fehler:", error);
        alert("Ein Fehler ist beim Löschen der Datei aufgetreten.");
    }
}
