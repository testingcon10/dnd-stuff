---
aliases: ["World Map"]
tags: [map, world]
---

# World Map — Tenelis

```leaflet
id: tenelis-world-map
image: [[TenelisWorldMap.png]]
bounds: [[0, 0], [100, 100]]
height: 700px
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
markerFolder: 06 - World/Locations
```

## Locations Index

```dataview
TABLE location_type AS "Type", region AS "Region", population AS "Population"
FROM "06 - World/Locations"
SORT file.name ASC
```
