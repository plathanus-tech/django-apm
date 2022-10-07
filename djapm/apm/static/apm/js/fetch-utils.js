function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function fetchJson(url, method = "GET") {
    return fetch(url, {
        method: method,
        credentials: 'same-origin',
        headers: {
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
        }
    }).then(res => res.json())
}