/* GoogleMap*/
function initMap() {
  var origin_latlng = {lat: 35.696739, lng: 139.814484};
  var destination_latlng = {lat: 35.698383, lng: 139.773072};
  var center_latlng = {lat: (origin_latlng.lat+destination_latlng.lat)/2,
                       lng: (origin_latlng.lng+destination_latlng.lng)/2};

  // マップの生成
  var map = new google.maps.Map(document.getElementById("map"), {
    center: new google.maps.LatLng(center_latlng),
    zoom: 14,
    mapTypeControl: false,
    fullscreenControl: false
  });

  // マーカーを設置
  var origin_marker = new google.maps.Marker({
    position: origin_latlng,
    map: map,
    icon: {
      url:"/static/taxishare/place_update/images/black.png",
      scaledSize: new google.maps.Size(50, 50),
    },
  });

  var destination_marker = new google.maps.Marker({
    position: destination_latlng,
    map: map,
    icon: {
      url:"/static/taxishare/place_update/images/pink.png",
      scaledSize: new google.maps.Size(50, 50),
    },
    draggable: true,
  });

  //　クリックイベント
  google.maps.event.addListener(destination_marker, 'dragend', function() {
    outputLatLng(destination_marker.getPosition());
    map.panTo(destination_marker.getPosition());
  });
  outputLatLng(destination_marker.getPosition());
}

// 緯度経度を取得する関数
function outputLatLng(latlng) {
  document.getElementById("id_desitination_latitude").value = latlng.lat().toFixed(14);
  document.getElementById("id_desitination_longitude").value = latlng.lng().toFixed(14);
}

/* デジタル時計 */
function initClock(){
  var now  = new Date();
  var year = now.getFullYear();
  var month = now.getMonth()+1;
  var date = now.getDate();
  var dayOfWeekStr = new Array("Sun","Mon","Tue","Wes","Thu","Fri","Sat");
  var dayOfWeek = now.getDay();
  var hour = now.getHours();
  var min  = now.getMinutes();

  // 数値が1桁の場合、頭に0を付けて2桁で表示する指定
  if(hour < 10) {
    hour = "0" + hour;
  }
  if(min < 10) {
    min = "0" + min;
  }

  var clock = year+'/'+month+'/'+date+'（'+dayOfWeekStr[dayOfWeek]+'） '+hour+':'+min;

  document.getElementById('clock').innerHTML = clock.toLocaleString();

  // 1秒ごとに処理を実効
  window.setTimeout( "initClock()", 1000);
}

window.onload = initClock;
