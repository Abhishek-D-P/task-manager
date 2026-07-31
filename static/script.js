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