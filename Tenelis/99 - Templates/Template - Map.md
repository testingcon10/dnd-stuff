---
aliases: []
tags: [map]
---

# Map Name

```leaflet
id: map-name
image: [[REPLACE-WITH-MAP-IMAGE.jpg]]
bounds: [[0, 0], [100, 100]]
height: 600px
width: 95%
lat: 50
long: 50
minZoom: 1
maxZoom: 5
defaultZoom: 2
zoomDelta: 0.5
unit: miles
scale: 1
darkMode: false
```

## Usage

1. **Add your map image** - Drop an image file into the vault (it will save to `assets/`). Replace `REPLACE-WITH-MAP-IMAGE.jpg` above with the actual filename, e.g. `[[my-map.jpg]]`.
2. **Coordinates** - With bounds `[0,0]` to `[100,100]`, coordinates represent percentage positions on the image. `[50, 50]` is the center.
3. **Add markers** - Create location notes using the **Template - Location** template. Set the `location:` field in frontmatter to `[lat, long]` coordinates. Use `markerFolder` in the leaflet block to auto-load markers from a folder.
4. **Adjust zoom** - Change `minZoom`, `maxZoom`, and `defaultZoom` to suit your map's detail level.
