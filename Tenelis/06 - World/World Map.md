---
aliases: ["World Map"]
tags: [map, world]
---

# World Map — Tenelis

```leaflet
id: tenelis-world-map
image: [[REPLACE-WITH-MAP-IMAGE.jpg]]
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
marker: default,50,50,[[Tenelis City]],Tenelis City
marker: default,35,72,[[The Whispering Woods]],The Whispering Woods
```

> [!info] Getting Started
> **To add your map image:**
> 1. Drop the map image file into the vault (it will save to `assets/`)
> 2. Replace `REPLACE-WITH-MAP-IMAGE.jpg` above with the actual filename (e.g. `[[tenelis-world-map.jpg]]`)
> 3. The map will render with the two example markers below
>
> **To add new locations:**
> - Create a new note in `06 - World/Locations/` using the **Template - Location** template
> - Set the `location:` field to `[lat, long]` (coordinates from 0–100, percentage of map)
> - The marker will auto-appear on this map via `markerFolder`
>
> **Coordinates guide:** `[0,0]` = bottom-left, `[100,100]` = top-right, `[50,50]` = center

## Locations Index

```dataview
TABLE location_type AS "Type", region AS "Region", population AS "Population"
FROM "06 - World/Locations"
SORT file.name ASC
```
