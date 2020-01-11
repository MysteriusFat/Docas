var map;
function initMap() {
	map = new google.maps.Map(document.getElementById('map'), {
		center: {lat: -33.43720, lng: -70.65060},
		zoom: 8
    });
}
initMap();