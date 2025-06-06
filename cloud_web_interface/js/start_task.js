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
        task_id: document.getElementById("task_id").value,
        arguments: document.getElementById("arguments").value
    };

    fetch(`http://${host}/rpc_exec_start_server_task`, {
        method: "POST",
        mode: "cors",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(formData)
    })
    .then(response => 
        response.json().then(data=>({response,data}))
    )
    .then(({ response, data }) => {
        switch(response.status) {
            case 200:
            alert("Task started at the server");
            window.location.href = "../index.html";
            break;

            case 400:
            console.error(data);
            throw new Error("Invalid request (fatal)");

            case 500:
            ret = handleStartTaskError(data);
            throw new Error(ret);

            default:
            console.error(data);
            throw new Error(response.status);
        }
    })
    .catch(error => alert(error));
}

function handleStartTaskError(error_msg) {
    var possible_error_messages = [
        "does not exist.",
        "alredy exists",
        "not registered"
    ]
    var user_error_msgs = [
        "Task files not found. Upload them before starting",
        "Task alredy started",
        "Task not registered"
    ] 
    for (let i=0; i<possible_error_messages.length; i++) {
        if(error_msg.includes(possible_error_messages[i]))
            return user_error_msgs[i];
    }
    console.error(error_msg);
    return "Unknown error"
}
