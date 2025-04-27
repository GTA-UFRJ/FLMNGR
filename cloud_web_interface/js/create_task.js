async function submitForm(event) {
    event.preventDefault();

    const formData = {
        task_id: document.getElementById("task_id").value,
        host: document.getElementById("host").value,
        port: parseInt(document.getElementById("port").value),
        username: document.getElementById("username").value,
        password: document.getElementById("password").value,
        files_paths: document.getElementById("files_paths").value.split(",").map(s => s.trim()),
        selection_criteria: document.getElementById("selection_criteria").value,
        server_arguments: document.getElementById("server_arguments").value,
        client_arguments: document.getElementById("client_arguments").value,
        tags: document.getElementById("tags").value.split(",").map(s => s.trim())
    };

    if(formData.port < 0 || formData.port > 65535) {
        alert("Invalid port. Should be an integer between 0 and 65535");
        return;
    }
    const isValid = await validateFormData(formData);
    if (!isValid) {
        return;
    }

    fetch("http://localhost:9001/rpc_exec_create_task", {
        method: "POST",
        mode: "cors",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(formData)
    })
    .then(handleResponse)
    .catch(handleError);
}

async function handleResponse(response) {
    const data = await response.json();
    switch (response.status) {
        case 200:
            alert("Task created with success.")
            window.location.href = "../index.html";
            break;
        case 400:
            alert("Fatal error: invalid request");
            break;
        case 500:
            if(data.includes("UNIQUE constraint failed"))
                alert("A task with this name is alredy registered");
            else {
                alert("Internal server error.");
                console.log(data);
            }
            break;
        default:
            alert("Error " + response.status);
            break;
    }
}

function handleError(error) {
    alert("Error: " + error);
}

async function loadSchema(url) {
    const response = await fetch(url);
    return await response.json();
}

async function validateFormData(formData) {
    const schema = await loadSchema("../schemas/rpc_exec_create_task.json"); 
    const ajv = new ajv7.default()
    const validate = ajv.compile(schema);

    const valid = validate(formData);

    if (!valid) {
        console.error(validate.errors[0].instancePath);
        switch(validate.errors[0].instancePath) {
            case "/port":
                alert("Invalid port. Should be an integer between 0 and 65535");
                break;
            default:
                alert("Invalid form. Review the fields.")
                console.log(validate.errors)
                break;
        }
        return false;
    }
    return true;
}
