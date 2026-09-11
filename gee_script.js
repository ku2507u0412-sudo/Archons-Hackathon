
Map.setCenter(22.95, -27.20, 12);

var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(geometry)
  .filterDate('2023-01-01', '2023-12-31')
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10));


var image = s2.first();

Map.addLayer(image, {bands: ['B4', 'B3', 'B2'], min: 0, max: 3000}, 'True Color (Hotazel)');

var swirRatio = image.select('B12').divide(image.select('B11')).rename('Manganese_Ratio');

Map.addLayer(swirRatio, {
  min: 0.8,
  max: 2.0,
  palette: ['blue', 'yellow', 'red']
}, 'Manganese SWIR Ratio');