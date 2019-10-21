
function initMap() {
    var map = new google.maps.Map(document.getElementById('mapSelect'), {
        zoom: 5,
        center: {lat: 24.886, lng: -70.268},
        mapTypeId: 'terrain'
    });

// Define the LatLng coordinates for the polygon's path.
    var poligono = [];

// Construct the polygon.
    var bermudaTriangle = new google.maps.Polygon({
        paths: poligono,
        strokeColor: '#FF0000',
        strokeOpacity: 0.8,
        strokeWeight: 2,
        strokeBorder : 0,
        fillColor: '#FF0000',
        fillOpacity: 0.35
    });
    bermudaTriangle.setMap( map );
 
    google.maps.event.addListener( map, 'click', function( e ){
        var cords = e.latLng;
        var lat = cords.lat();
        var lng = cords.lng();

        poligono.unshift({ lat, lng });

        bermudaTriangle.setMap( null );
        bermudaTriangle.setPath( poligono );
        bermudaTriangle.setMap( map );

    });
}

google.maps.event.addDomListener(window, 'load', function(){
    initMap();
});