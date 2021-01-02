//initilize page
var currentCountry = "US";
var currentCategory = "Education";
var currentMetric = "likes";
var currentYear = "2019";

// Create a custom function to run a filter on the data when the search values are given and the 'Filter button' is pressed
// Select the button
var button = d3.select("#filter-btn");

button.on("click", function () {

    // Select the input element and get the raw HTML node
    var inputElement1 = d3.select("#countrySelection");
    var inputElement2 = d3.select("#categorySelection");
    var inputElement3 = d3.select("#metricSelection");
    var inputElement4 = d3.select("#yearSelection");

    // Get the value property of the input element
    currentCountry = inputElement1.property("value");
    currentCategory = inputElement2.property("value");
    currentMetric = inputElement3.property("value");
    currentYear = inputElement4.property("value");

    console.log(currentCountry, currentCategory, currentMetric, currentYear);

    graphUpdate();


    //Country Buttons
    var usButton = d3.select("#US");
    usButton.on("click", function () {
        currentCountry = (this.id);
        graphUpdate();
    });
    var caButton = d3.select("#CA");
    caButton.on("click", function () {
        currentCountry = (this.id);
        graphUpdate();
    });
    var mxButton = d3.select("#MX");
    mxButton.on("click", function () {
        currentCountry = (this.id);
        graphUpdate();
    });
    var brButton = d3.select("#BR");
    brButton.on("click", function () {
        currentCountry = (this.id);
        graphUpdate();
    });
    //metric buttons
    var likeButton = d3.select("#like");
    likeButton.on("click", function () {
        currentMetric = "likes";
        graphUpdate();
    });
    var viewButton = d3.select("#view");
    viewButton.on("click", function () {
        currentMetric = "view_count";
        graphUpdate();
    });
    var dislikeButton = d3.select("#dislike");
    dislikeButton.on("click", function () {
        currentMetric = "dislikes";
        graphUpdate();
    });
    var commentButton = d3.select("#comment");
    commentButton.on("click", function () {
        currentMetric = "comment_count";
        graphUpdate();
    });
    //this function call all the graph making functions
    function graphUpdate() {
        // console.log(data);
        barPlot();
        grabTableData();
        lineGraph();
    };
    function barPlot() {
        url = `/bar/${currentCountry}/${currentMetric}`
        d3.json(url).then(function (response) {

            //Jinah: building the bar chart using Plotly

            var x_value = Object.keys(response);
            x_value = x_value.map(function (entry) {
                if (entry == 29) {
                    return "Nonprofits & Activism";
                } else {
                    return entry;
                };
            });
            //console.log(x_value);

            var y_value = Object.values(response);
            //console.log(y_value);

            var trace1 = {
                x: x_value,
                y: y_value,
                type: "bar",
                name: `${currentMetric} for Country: ${currentCountry}`
            }

            var data1 = [trace1];

            var layout1 = {
                title: `${currentMetric} for Country: ${currentCountry}`,
                font: {
                    color: '#ffffff'
                },
                plot_bgcolor: "#2F2B44",
                paper_bgcolor: "#2F2B44",
                xaxis: {
                    tickangle: 30,
                    title: "Category Names"
                },
                yaxis: {
                    title: `Total Counts of ${currentMetric}`
                }
            };
            var config = { responsive: true }

            Plotly.newPlot("bar", data1, layout1);
        })
    };

    // // // // ========================================================= // // // // 
    // // // //      FUNCTION TO GET DATA FOR A TABLE                     // // // //
    // // // // ========================================================= // // // // 
    // function buildTable(categoryId, title, channelTitle, view_count, comment_count, trending_date, likes, dislikes, thumbnail_link) {
    function grabTableData() {
        url = `/data/${currentCountry}`
        d3.json(url).then(function (response) {

            // currentMetric = "likes"
            // console.log(response);
            var sortedData = response.sort((a, b) => a[currentMetric] - b[currentMetric]);
            sortedData.reverse()

            var top10TableData = []


            // // // ===================== START ==================== // // //
            // To remove any duplicated videos
            for (var i = 0; i < (sortedData.length - 1); i++) {

                if (sortedData[i].title !== sortedData[i + 1].title) {
                    top10TableData.push(sortedData[i])
                }
            }
            // // // ===================== END ==================== // // //


            top10TableData = top10TableData.slice(0, 10);

            // console.log(`Top 10 list for ${currentCountry} ${currentMetric}`);
            console.log(top10TableData);

            buildTable_v1(top10TableData)
        })
    }

    function buildTable_v1(data) {
        teebody = d3.select("tbody");
        teebody.html("");
        var table = d3.select("#summary-table");
        var tbody = table.select("tbody");
        var trow;

        for (var i = 0; i < data.length; i++) {
            // console.log(data[i])
            trow = teebody.append("tr");
            trow.append("td").text(data[i].categoryId);
            trow.append("td").text(data[i].title);
            trow.append("td").text(data[i].channelTitle);
            trow.append("td").text(data[i].view_count);
            trow.append("td").text(data[i].comment_count);
            trow.append("td").text(data[i].trending_date);
            trow.append("td").text(data[i].likes);
            trow.append("td").text(data[i].dislikes);
            trow.append("td").append("a")
                .attr("href", `https://www.youtube.com/watch?v=${data[i].video_id}`)
                .attr("target", "_blank")
                .append("img")
                .attr("src", data[i].thumbnail_link);
        }
    }

    function lineGraph() {
        url = `/line/${currentCountry}/${currentMetric}`
        data = d3.json(url).then(function (response) {
            // console.log(response);
            dates = Object.keys(response).map(function (entry) {
                return new Date(entry * 1000);
            });

            var x_value = dates;
            //console.log(x_value);

            var y_value = Object.values(response);
            //console.log(y_value);

            var trace1 = {
                x: x_value,
                y: y_value,
                type: "line",
                name: `${currentMetric} for Country: ${currentCountry}`
            }
            var data1 = [trace1];

            var layout1 = {
                title: "Top Category Over Time",
                yaxis: {
                    type: 'log',
                    autorange: true,
                    title: `Total Views of ${currentMetric}`
                },
                xaxis: {
                    title: "Dates: Aug 2020 to Dec 2020"
                },
                font: {
                    color: '#ffffff'
                },
                plot_bgcolor: "#2F2B44",
                paper_bgcolor: "#2F2B44"
            };
            Plotly.newPlot("line", data1, layout1);
        })
    }