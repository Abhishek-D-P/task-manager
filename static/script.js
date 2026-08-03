rows = document.querySelectorAll(".js-list-status");
rows.forEach(row => {
    let status = row.value;
    let parent = row.parentElement;
    switch(status){
        case "To Do":
            parent.style.borderLeft = "3px solid red"
            parent.style.borderBottom = "3px solid red"
            break;
        case "Ready":
            parent.style.borderLeft = "3px solid orange"
            parent.style.borderBottom = "3px solid orange"
            break;
        case "In Progress":
            parent.style.borderLeft = "3px solid blue"
            parent.style.borderBottom = "3px solid blue"
            break;
        case "Done":
            parent.style.borderLeft = "3px solid green"
            parent.style.borderBottom = "3px solid green"
            break;

    }
});




function deleteTask(id){
    fetch("tasks",{
        method:'DELETE',
        headers:{
            'Content-Type':'application/json',
        },
        body:JSON.stringify({
            id:id
        })
    }).then(res => location.reload());
    console.log("in");
}

function updateTask(id){
    let taskName = document.getElementById(`task-name-${id}`).textContent;
    let status = document.getElementById(`status-${id}`).value;
    fetch("tasks",{
        method:"PATCH",
        headers:{
            'Content-Type':'application/json',
        },
        body:JSON.stringify({
            id:id,
            task:taskName,
            status:status
        })
    }).then(res=>location.reload());
}