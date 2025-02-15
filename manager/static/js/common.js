function post(api, bodyData, fn) {
    let basePath = 'http://localhost:8001';
    let token = localStorage.getItem('token');
    fetch(basePath + api, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'Authorization': token,
        },
        body: bodyData==null ? null : JSON.stringify(bodyData)
    })
        .then(response => response.json())
        .then(data => {
            if(data.code === 401){
                window.location = 'login.html';
                return
            }
            fn(data);
        });
}

function get(api, fn) {
    let basePath = 'http://localhost:8001';
    let token = localStorage.getItem('token');
    fetch(basePath + api, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json',
            'Authorization': token,
        },
    })
        .then(response => response.json())
        .then(data => {
            if(data.code === 401){
                window.location = 'login.html';
                return
            }
            fn(data);
        });
}