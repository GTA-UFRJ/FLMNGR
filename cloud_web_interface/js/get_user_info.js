let host;

// Load config first
async function loadConfig() {
    try {
        const response = await fetch('../js/hostinfo.json');
        const config = await response.json();
        host = config.host;
    } catch (error) {
        console.error('Error loading hostinfo:', error);
    }
}

loadConfig();

function submitForm(event) {
    event.preventDefault();
    
    const formData = {
        user_id: document.getElementById("user_id").value
    };

    fetch(`http://${host}/rpc_exec_get_user_info`, {
        method: "POST",
        mode: "cors",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(formData)
    })
    .then(response => handleResponse(response))
    .then(data => generateResultPage(data))
    .catch(error => alert(error));
}

async function handleResponse(response) {
    const data = await response.json()
    if (response.ok) return data;
    else if (response.status == 400) throw new Error("Invalid request (fatal)");
    else if(data.includes("not registered")) throw new Error(`This user is not registered`);
    else { 
        console.error(data)
        throw new Error("Error " + response.status);
    }
}

function generateResultPage(data) {
    let newWindow = window.open("", "_blank");
    let html = `
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>User Details</title>
            <link rel="stylesheet" href="../css/style.css">
        </head>
        <body>
            <h1 style="text-align: center;">User Details</h1>
            <div class="center-container">
            <table>
                <tr><th>Campo</th><th>Valor</th></tr>`;
    
    for (let key in data) {
        let value = Array.isArray(data[key]) ? data[key].join(", ") : data[key];
        html += `<tr><td>${key}</td><td>${value}</td></tr>`;
    }
    
    html += `</table>
        </div>
        </body>
        </html>`;
    
    newWindow.document.write(html);
    newWindow.document.close();
}