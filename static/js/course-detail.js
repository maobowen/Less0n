// Grade chart
Highcharts.chart('grade-chart', {
    chart: {
        backgroundColor:'rgba(255, 255, 255, 0.0)',
        plotBorderWidth: 0,
        plotShadow: false
    },
    title: {
        text: 'Grades',
        align: 'center',
        verticalAlign: 'middle',
        y: 0
    },
    tooltip: {
        pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
    },
    plotOptions: {
        pie: {
            dataLabels: {
                enabled: false,
                distance: -10,
                style: {
                    fontWeight: 'bold',
                    color: 'white'
                }
            },
            startAngle: -90,
            endAngle: 90
        }
    },
    exporting: { 
        enabled: false 
    },
    credits: {
      enabled: false
    },
    series: [{
        type: 'pie',
        name: 'Browser share',
        innerSize: '50%',
        data: [
            ['A+', 58.9],
            ['A', 13.29],
            ['A-', 13],
            ['B+', 3.78],
            ['B', 3.42],
            ['B-', 3.42],
            {
                name: 'Other',
                y: 7.61,
                dataLabels: {
                    enabled: false
                }
            }
        ]
    }]
});

