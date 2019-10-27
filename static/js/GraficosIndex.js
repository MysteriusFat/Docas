google.charts.load('current', {'packages':['corechart']});

google.charts.setOnLoadCallback(drawChart2);
google.charts.setOnLoadCallback(drawChart3);

function drawChart2() {
  var data = new google.visualization.DataTable();
  var areas =  $("#data").data('area');

  data.addColumn('string', 'Topping');
  data.addColumn('number', 'Slices');
  data.addRows([
    ['Area 0.00', areas[0]],
    ['Area 0.25', areas[1]],
    ['Area 0.50', areas[2]],
    ['Area 0.75', areas[3]],
    ['Area 1.00', areas[4]]
  ]);
  var options = {'title':'Areas',pieHole: 0.4};
  var chart = new google.visualization.PieChart(document.getElementById('grafico2'));
  chart.draw(data, options);
}

function drawChart3() {
  var percentil = $('#data').data('percentil')
  var data = google.visualization.arrayToDataTable([
         ['string', 'number'],
         ['P 0.25', 8.94    ],
         ['P 0.50', 10.49   ],
         ['P 0.75', 19.30   ],
         ['P 0.95', 21.45   ]
  ]);



  var options = {
    title: ' Percentiles ',
  };
  var chart = new google.visualization.ColumnChart( document.getElementById('grafico3'));
  chart.draw(data, options);
}

function drawHistogram(valores) {
  var data = google.visualization.arrayToDataTable( valores );
  var options = {
    title: 'NDVI distribution',
    width: 1500,
    height: 400,
    legend: { position: 'none' },
    colors: ['#4285F4'],

    hAxis: {
    ticks: [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]},
    bar: { gap: 0 },

    histogram: {
      bucketSize: 0.05,
      maxNumBuckets: 20,
      minValue: 0,
      maxValue: 1
    }
  };
  var chart = new google.visualization.Histogram(document.getElementById('grafico1'));
  chart.draw(data, options);
}

$(document).ready( function(){
  var _id = $('#data').data('_id');
  var cord = $('#data').data('central_point');
  var parametros = {
    "lat": cord[0],
    "lon": cord[1],
    "id" : _id
  };

  $.ajax({
    url: '/ndvi_time_serie',
    data: parametros,
    type: 'POST',
    success: function(response){
      var json = JSON.parse(response);
      var data = [];
      data.push( ['Dinosaur', 'Length']);
      for( var i=0 ; i<json.ndvi.length ; i++ ){
        data.push( [ json.month[i], json.ndvi[i] ]);
      }
      console.log( data );

      drawHistogram( data );
    },
    error: function(error){
      console.log(error);
    },
  });
});
