function submitForm(event) {
    event.preventDefault();
    
    const taskId = document.getElementById("task_id").value;
    const files = document.getElementById("file_input").files;
    
    if (!taskId) {
        alert("Task ID is required");
        return;
    }

    const formData = new FormData();
    formData.append("task_id", taskId);
    for (const file of files) {
        formData.append("files", file);
    }

    fetch("http://localhost:5000/upload_files", {
        method: "POST",
        mode: "cors",
        body: formData
    })
    .then(response => response.json())
    .then(data => alert("Files uploaded"))
    .catch(error => alert("Invalid request"));
}