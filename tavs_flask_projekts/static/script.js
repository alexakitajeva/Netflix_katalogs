document.addEventListener("DOMContentLoaded", function () {
    const genreCtx = document.getElementById("genreChart").getContext("2d");
    new Chart(genreCtx, {
        type: "bar",
        data: {
            labels: ["Drama", "Comedy", "Thriller", "Action"],
            datasets: [{
                label: "Žanru popularitāte",
                data: [120, 150, 80, 100],
                backgroundColor: "rgba(255, 99, 132, 0.6)"
            }]
        }
    });

    const yearCtx = document.getElementById("yearChart").getContext("2d");
    new Chart(yearCtx, {
        type: "line",
        data: {
            labels: ["2015", "2016", "2017", "2018", "2019"],
            datasets: [{
                label: "Filmu skaits",
                data: [50, 60, 100, 120, 140],
                borderColor: "rgba(54, 162, 235, 1)",
                fill: false
            }]
        }
    });
});
