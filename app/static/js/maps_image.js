USGSOverlay.prototype = new google.maps.OverlayView();
var overlay;
function initMap() {
    coords = $("#data").data('coords');
    central_point = $("#data").data( 'central_point' );

    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 14,
        center: { lat:central_point[0], lng: central_point[1] },
        mapTypeId: 'satellite'
    });

    var bounds = new google.maps.LatLngBounds(
      new google.maps.LatLng( coords[1][0], coords[0][1] ),
      new google.maps.LatLng( coords[0][0], coords[1][1] )
    );

        // The photograph is courtesy of the U.S. Geological Survey.
    var srcImage = $("#data").data('url_1');

    overlay = new USGSOverlay(bounds, srcImage, map);
}

      /** @constructor */
function USGSOverlay(bounds, image, map) {

        // Now initialize all properties.
    this.bounds_ = bounds;
    this.image_ = image;
    this.map_ = map;

    this.div_ = null;
    this.setMap(map);

}
USGSOverlay.prototype.onAdd = function() {

  var div = document.createElement('div');
  div.style.border      = 'none';
  div.style.borderWidth = '0px';
  div.style.position    = 'absolute';
  div.style.opacity     = '0.5'

  // Create the img element and attach it to the div.
  var img = document.createElement('img');
  img.src          = this.image_;
  img.style.width  = '100%';
  img.style.height = '100%';

  div.appendChild(img);

  this.div_ = div;

  var panes = this.getPanes();
  panes.overlayImage.appendChild(this.div_);
};

USGSOverlay.prototype.draw = function() {

  var  overlayProjection = this.getProjection();
  var sw = overlayProjection.fromLatLngToDivPixel(this.bounds_.getSouthWest());
  var ne = overlayProjection.fromLatLngToDivPixel(this.bounds_.getNorthEast());

  var div = this.div_;
  div.style.left = sw.x + 'px';
  div.style.top = ne.y + 'px';
  div.style.width = (ne.x - sw.x) + 'px';
  div.style.height = (sw.y - ne.y) + 'px';
};

USGSOverlay.prototype.onRemove = function() {
  this.div_.parentNode.removeChild( this.div_);
};

USGSOverlay.prototype.hide = function() {
  if (this.div_) {
    this.div_.style.visibility = 'hidden';
  }
};

USGSOverlay.prototype.show = function() {
  if (this.div_) {
    this.div_.style.visibility = 'visible';
  }
};

USGSOverlay.prototype.toggle = function() {
  if (this.div_) {
    if (this.div_.style.visibility === 'hidden') {
      this.show();
    } else {
      this.hide();
    }
  }
};

// Detach the map from the DOM via toggleDOM().
// Note that if we later reattach the map, it will be visible again,
// because the containing <div> is recreated in the overlay's onAdd() method.
USGSOverlay.prototype.toggleDOM = function() {
  if (this.getMap()) {
    // Note: setMap(null) calls OverlayView.onRemove()
    this.setMap(null);
  } else {
    this.setMap(this.map_);
  }
};

google.maps.event.addDomListener(window, 'load', initMap);
