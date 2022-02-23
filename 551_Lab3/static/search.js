function BP_locations(geojson_features){

    var popup = new L.Popup();

    var oms = new OverlappingMarkerSpiderfier(mymap);
    oms.addListener('click', function(marker) {
    popup.setContent(marker.desc);
    popup.setLatLng(marker.getLatLng());
    mymap.openPopup(popup);
    });
    oms.addListener('spiderfy', function(markers) {
        mymap.closePopup();
    });

    var markers = L.markerClusterGroup();

    for (var i=0; i<Object.keys(geojson_features).length;i++){
        var loc = new L.LatLng(geojson_features[i].properties.latitude, geojson_features[i].properties.longitude);
        var marker = new L.Marker(loc);
        var popcontent="Issued Date: "+geojson_features[i].properties.issueddate+"<br>"+
                        "Work Class Group: "+geojson_features[i].properties.workclassgroup+"<br>"+
                        "Contractor Name: "+geojson_features[i].properties.contractorname+"<br>"+
                        "Community Name: "+geojson_features[i].properties.communityname+"<br>"+
                        "Original Address: "+geojson_features[i].properties.originaladdress;
        marker.desc = popcontent;
        mymap.addLayer(markers);
        oms.addMarker(marker);
        markers.addLayer(marker);
    }
}