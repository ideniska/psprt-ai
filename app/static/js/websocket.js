// const wsSchema = window.location.protocol == 'https' ? 'wss' : 'ws'

// var loc = window.location,
//     wsSchema;
// if (loc.protocol === "https:") {
//     wsSchema = "wss:";
// } else {
//     wsSchema = "ws:";
// }

// const currentDomain = window.location.host

var websocket = new WebSocket(((window.location.protocol === "https:") ? "wss://" : "ws://") + window.location.host + "/ws");

// const websocket = new WebSocket(`${wsSchema}://${currentDomain}/ws/progress/`)


websocket.onclose = OnClose
websocket.onmessage = ReceiveMessage
websocket.onopen = OnOpen

function submitForm() {
    var form = document.getElementById("document-type-form");
    var formData = new FormData(form);


    $.ajax({
        url: '/prepare-backend/',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function (data) {
            // handle success response from server
            console.log(data);
        },
        error: function (xhr, status, error) {
            // handle error response from server
            console.log(xhr.responseText);
        }
    });
}

$(document).ready(function () {
    $('#document-type-form').on('submit', function (event) {
        event.preventDefault();
        submitForm();
    });
});



function ReceiveMessage(e) {
    const data = JSON.parse(e.data);
    console.log('Receive Message:', data.event);
    if (data.event == 'started') {
        $("#loading-animation").css({
            'display': 'block',
        })
    } else if (data.event == 'finished') {
        window.location.href = '/prepared/'
    }
}

function OnClose() {
    console.log('close');
}

function OnOpen(e) {
    console.log('on open:', e);
}