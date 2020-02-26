function initMap() {
  var origin_latlng = {lat: 35.696739, lng: 139.814484};
  var center_latlng = {lat: 35.6885, lng: 139.79825997407};

  // マップの生成
  var map = new google.maps.Map(document.getElementById("map"),{
    center: new google.maps.LatLng(center_latlng),
    zoom: 14,
    mapTypeControl: false,
    fullscreenControl: false,
  });

  var origin_marker = new google.maps.Marker({
    position: origin_latlng,
    map: map,
    icon: {
      url:"/static/taxishare/taxi_result/images/black.png",
      scaledSize: new google.maps.Size(30, 30),
    },
  });

  addMarkers(map);
}
