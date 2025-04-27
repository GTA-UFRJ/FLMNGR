async function submitForm(event) {
    event.preventDefault();
    
    const formData = {
        task_id: document.getElementById("task_id").value
    };

    fetch("http://localhost:9001/rpc_exec_get_task_by_id", {
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
    else if(data.includes("not registered")) throw new Error(`This task is not registered`);
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
            <title>Task Details</title>
            <link rel="stylesheet" href="../css/style.css">
        </head>
        <body>
            <h1 style="text-align: center;">Task Details</h1>
            <table>
                <tr><th>Campo</th><th>Valor</th></tr>`;
    
    for (let key in data) {
        let value = Array.isArray(data[key]) ? data[key].join(", ") : data[key];
        html += `<tr><td>${key}</td><td>${value}</td></tr>`;
    }
    
    html += `</table>
        </body>
        </html>`;
    
    newWindow.document.write(html);
    newWindow.document.close();
}
