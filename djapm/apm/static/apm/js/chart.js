const randomRgb = () => {
    var r = Math.floor(Math.random() * 255);
    var g = Math.floor(Math.random() * 255);
    var b = Math.floor(Math.random() * 255);
    return "rgb(" + r + "," + g + "," + b + ")";
}

const generateRandomColors = (n_of_colors) => {
    var colors = [];
    for (var i = 0; i < n_of_colors; i++) {
        colors.push(randomRgb());
    }
    return colors
}

const RED = 'rgb(255, 0, 0)';
const DARK_GREEN = 'rgb(53, 173, 19)'
const BLUE = 'rgb(0, 0, 255)';
const apiUrls = JSON.parse(document.getElementById("apiUrls").textContent);


async function loadRequestCountByDateChart() {
    const CHART_ID = "RequestsCountByDate"
    const json = await fetchJson(apiUrls[CHART_ID]);
    const data = {
        datasets: [
            {
                label: gettext('Requests'),
                backgroundColor: BLUE,
                borderColor: BLUE,
                data: json.requests,
            },
            {
                label: gettext('Errors'),
                backgroundColor: RED,
                borderColor: RED,
                data: json.errors,
            }
        ]
    };
    const config = {
        type: 'line',
        data: data,
        options: {
            plugins: {
                title: { display: true, text: gettext("Nº of requests per date") },
                subtitle: { display: true, text: gettext("The number requests registered at each date (last week)") }
            },
            scales: { y: { title: { display: true, text: gettext("Requests") } } }
        }
    };
    new Chart(
        document.getElementById(CHART_ID),
        config
    );

}

async function loadRequestsViewNameCountChart() {

    const json = await fetchJson(apiUrls["RequestsViewNameCountToday"]);
    const data = {
        datasets: [{
            label: gettext('Endpoints Requests'),
            data: json.requests,
            backgroundColor: Object.keys(json.requests).map(() => DARK_GREEN),
        },
        {
            label: gettext('Errors'),
            backgroundColor: RED,
            borderColor: RED,
            data: json.errors,
        }
        ]
    };
    const config = {
        type: 'bar',
        data: data,
        options: {
            plugins: {
                title: { display: true, text: gettext("Today's requests per view") },
                subtitle: { display: true, text: gettext("The number of today's requests on each view") }
            },
            scales: {
                x: { stacked: true },
                y: { stacked: true, title: { display: true, text: gettext("Requests") } }
            }
        }
    };
    new Chart(
        document.getElementById('RequestsViewNameCountToday'),
        config
    );
}

async function loadResponseEllapsedTimeByViewChart() {

    const CHART_ID = "ResponseEllapsedTimeByView"
    const json = await fetchJson(apiUrls[CHART_ID])
    const data = {
        datasets: [
            {
                label: gettext('Min time'),
                data: json.min,
                backgroundColor: DARK_GREEN,
                borderColor: DARK_GREEN,
            },
            {
                label: gettext('Avg time'),
                data: json.avg,
                backgroundColor: BLUE,
                borderColor: BLUE,
            },
            {
                label: gettext('Max time'),
                data: json.max,
                backgroundColor: RED,
                borderColor: RED,
            },
        ]
    };
    const config = {
        type: 'bar',
        data: data,
        options: {
            plugins: {
                title: { display: true, text: gettext("View response times") },
                subtitle: { display: true, text: gettext("The response's times at each view (last week)") }
            },
            scales: {
                y: {
                    title: { display: true, text: gettext("Time (seconds)") }
                }
            }
        }
    }
    new Chart(
        document.getElementById(CHART_ID),
        config
    );
}

async function loadResponseEllapsedTimeByDateChart() {

    const CHART_ID = "ResponseEllapsedTimeByDate"
    const json = await fetchJson(apiUrls[CHART_ID])
    const data = {
        datasets: [
            {
                label: 'Min time',
                data: json.min,
                backgroundColor: BLUE,
                borderColor: BLUE,
            },
            {
                label: 'Avg time',
                data: json.avg,
                backgroundColor: BLUE,
                borderColor: BLUE,
            },
            {
                label: 'Max time',
                data: json.max,
                backgroundColor: RED,
                borderColor: RED,
            },
        ]
    };
    const config = {
        type: 'line',
        data: data,
        options: {
            plugins: {
                title: { display: true, text: "Response times" },
                subtitle: { display: true, text: "The response's times at each date (last week)" }
            },
            scales: {
                y: { title: { display: true, text: "Time (seconds)" } }
            }
        }
    }
    new Chart(
        document.getElementById(CHART_ID),
        config
    );
}

async function loadRequestCountLast24HoursChart() {

    const CHART_ID = "RequestsCountLast24Hours"
    const json = await fetchJson(apiUrls[CHART_ID])
    const data = {
        datasets: [
            {
                label: gettext('Requests'),
                backgroundColor: BLUE,
                borderColor: BLUE,
                data: json,
            },
        ]
    };
    const config = {
        type: 'line',
        data: data,
        options: {
            plugins: {
                title: { display: true, text: gettext("Requests last 24 hours") },
                subtitle: { display: true, text: gettext("The number requests registered on the last 24 hours") }
            },
            scales: { y: { title: { display: true, text: gettext("Requests") } } }
        }
    };
    new Chart(
        document.getElementById(CHART_ID),
        config
    );
}

async function loadErrorsPerClassLastWeekChart() {
    const CHART_ID = "ErrorsPerClassLastWeek"
    const json = await fetchJson(apiUrls[CHART_ID])

    const data = {
        labels: Object.keys(json),
        datasets: [
            {
                label: gettext('Errors'),
                backgroundColor: generateRandomColors(Object.keys(json).length),
                data: Object.values(json),
            },
        ]
    };
    const config = {
        type: 'doughnut',
        data: data,
        options: {
            plugins: {
                title: { display: true, text: gettext("Errors per type") },
                subtitle: { display: true, text: gettext("The number of errors per exception class (last week)") }
            },
        }
    };
    new Chart(
        document.getElementById(CHART_ID),
        config
    );
}

const loadCharts = () => {
    Promise.all([
        loadRequestCountByDateChart(),
        loadRequestsViewNameCountChart(),
        loadResponseEllapsedTimeByViewChart(),
        loadResponseEllapsedTimeByDateChart(),
        loadRequestCountLast24HoursChart(),
        loadErrorsPerClassLastWeekChart(),
    ])
}

loadCharts();

function refreshCharts() {
    Object.keys(apiUrls).forEach((id) => {
        var canvas = document.getElementById(id);
        var parentDiv = canvas.parentElement;
        canvas.remove();
        var newCanvas = document.createElement("canvas");
        newCanvas.setAttribute("id", id);
        parentDiv.appendChild(newCanvas);
    })
    loadCharts();
}
setInterval(refreshCharts, 60000)