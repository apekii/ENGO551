function marker(geojson){

L.geoJSON(geojsonFeature).addTo(mymap)

L.marker(calgary).addTo(mymap)
    .bindPopup('A pretty CSS3 popup.<br> Easily customizable.')
    .openPopup();

}