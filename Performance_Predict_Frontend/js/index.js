function postData(url, data) {
    // Default options are marked with *
    return fetch(url, {
        body: JSON.stringify(data), // must match 'Content-Type' header
        cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
        credentials: "same-origin", // include, same-origin, *omit
        headers: {
            "user-agent": "Example",
            "content-type": "application/json",
      },
        method: "POST", // *GET, POST, PUT, DELETE, etc.
        mode: "cors", // no-cors, cors, *same-origin
        redirect: "follow", // manual, *follow, error
        referrer: "no-referrer", // *client, no-referrer
    })
        .then((response) => response.json()); // 輸出成 json
}



function submit(){
    const distance =document.getElementById("distance").value;
    const weather =document.getElementById('weather').value;
    const temperature =document.getElementById('temperature').value;

    const data = {
        distance,
        weather,
        temperature
    }

    postData('http://127.0.0.1:3000/predict',data)
    .then(data => {
        
        console.log(data)
        
    })

}