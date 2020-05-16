
/*
 * carbon-map
 * 
 * Copyright 2020 Chris Pointon
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

"use strict";

/*
 * Custom user interface elements for pure knob.
 */

class CarbonMap {
    constructor() {
        this.dataRoot = 'https://data.cambridgecarbonmap.org';
        this.initialLatLon = [52.205, 0.1218];
        this.initialZoom = 12.5;
        this.mapDiv = 'mainMap';
    }

    initialize() {
        if (typeof (L) == 'undefined') {
            console.log('Please include Leaflet before initializing CarbonMap');
            return;
        }
        console.log("Initialised")
        this.mainMap = L.map(this.mapDiv).setView(this.initialLatLon, this.initialZoom);
        const attribution = '&copy; <a href="https://www.openstreetmap/copyright">OpenStreeMap</a> contributors';

        const tiles = L.tileLayer('http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
            maxZoom: 20,
            subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
        });

        tiles.addTo(this.mainMap);

        this.lock = false;
        var first_dict = {};

        var that = this;

        function changeDisplay(layer, mode) {
            if (mode == 0) {
                // Main object, seen on surface, not hovered over
                layer.setStyle({ "fillColor": "#0000ff", "fillOpacity": 0.35, "opacity": 0 })
                layer.bringToFront();
            }
            if (mode == 1) {
                // Parent object, being hover over ///// next iteration: have children show if this mode is stayed on for long enough
                layer.setStyle({ "fillColor": "#ff0000", "fillOpacity": 0.3, "opacity": 0 })
            }
            if (mode == 2) {
                // Parent object, has been selected, so now faint to show children
                layer.setStyle({ "fillColor": "#0000ff", "color": "#cc0000", "fillOpacity": 0, "opacity": 0.3 })
            }
            if (mode == 3) {
                // Child object, parent not selected so is invisible
                layer.setStyle({ "fillColor": "#0000ff", "fillOpacity": 0, "opacity": 0 })
            }
            if (mode == 4) {
                // Child object, parent has been selected so is now visible, not hovered over
                layer.setStyle({ "fillColor": "#669900", "fillOpacity": 0.5, "opacity": 0 })
                layer.bringToFront();
            }
            if (mode == 5) {
                // Child object, being hovered over
                layer.setStyle({ "fillColor": "#ff0000", "fillOpacity": 0.3, "opacity": 0 })
            }
        }

        this.childDict = {};
        this.layerDict = {};
        this.fullList = {};

        function findParents(item){
            
            var searcher = item.properties.id;
            var parent = null;
            
            while(true){
                parent = findShow(searcher);
                if(parent == null){

                    searcher = searcher.split(".");
                    var popped = searcher.pop()

                    if (searcher.length == 0){
                        break;
                    }

                    searcher = searcher.join(".")
                }
                else{
                    break
                }
            }
            return parent
        }

        function arraysEqual(a1,a2) {
            /* WARNING: arrays must not contain {objects} or behavior may be undefined */

            var a = JSON.stringify(a1)==JSON.stringify(a2);
            return a
        }

        function findChildren(parent){

            parent = parent.split(".")

            var parentLength = parent.length
            var j
            var children = []
            var isChild

            for (j in that.childList){
                isChild = false

                if(that.childList[j].split(".").length>=parentLength){

                    if(arraysEqual(that.childList[j].split(".").slice(0, parentLength), parent)){

                        if(!arraysEqual(that.childList[j].split("."), parent)){
                            isChild = true
                        }
                    }
                }
                if(isChild){
                    children.push(that.childList[j])
                }
            }

            return children

        }

        this.mainMap.on('click', function (e) {
            that.lock = !that.lock
        });

        // Will have to generate this in next iteration
        this.startList = ["uk.ac.cam.st-edmunds", "uk.ac.cam.kings", "net.theleys"]
        this.childList = ["uk.ac.cam.st-edmunds.white-cottage", "uk.ac.cam.st-edmunds.norfolk-building", "uk.ac.cam.st-edmunds.richard-laws", "uk.ac.cam.kings.kingsparade","uk.ac.cam.kings.spalding","uk.ac.cam.kings.kingsfield","uk.ac.cam.kings.garden","uk.ac.cam.kings.grasshopper","uk.ac.cam.kings.cranmer","uk.ac.cam.kings.st-edwards","uk.ac.cam.kings.tcr","uk.ac.cam.kings.market","uk.ac.cam.kings.plodge","uk.ac.cam.kings.bodleys","uk.ac.cam.kings.old-site","uk.ac.cam.kings.provosts-lodge","uk.ac.cam.kings.webbs","uk.ac.cam.kings.keynes","uk.ac.cam.kings.a-staircase","uk.ac.cam.kings.wilkins"]
        
        function putOnMap (addr){
            $.getJSON(that.dataRoot + "/geojson/" + addr + ".geojson", function (geojson) {
                L.geoJSON(geojson,
                {
                    onEachFeature: function (feature, layer) {


                        first_dict[feature.properties.id] = false;

                        that.childDict[feature.properties.id] = []

                        var parent = findParents(feature)
                        if(parent == feature.properties.id){
                        }else{
                            that.childDict[parent].push(feature.properties.id)
                        }

                        var popup = new L.Popup({
                            autoPan: false,
                            keepInView: true,
                        }).setContent(feature.properties.name);
                        layer.bindPopup(popup, { maxWidth: 800 });

                        if (feature.properties.show) { var startmode = 0 } else { var startmode = 4 }
                        changeDisplay(layer, startmode)
                        console.log(feature.properties.name, startmode)

                        that.layerDict[addr] = [layer, startmode];

                        that.mainMap.closePopup();

                        layer.on('click', function (e) {

                                                 

                            // Saves having to make a link popup until it's clicked on anyway
                            if (first_dict[feature.properties.id] == false) {
                                first_dict[feature.properties.id] = makeLink(feature);
                                // Add all children to the item
                                var children = findChildren(feature.properties.id)
                                var j

                                for(j in children){
                                    putOnMap(children[j])
                                }      
                            }

                            // Is a parent, not yet selected, so when it is clicked, it's popup stays the same, but we get it's children turn light green
                            if (that.layerDict[addr][1] == 1) {
                                that.layerDict[addr][1] = 2;
                                changeDisplay(layer, that.layerDict[addr][1]);

                                if (that.childDict[addr]) {
                                    for (var j in that.childDict[addr]) {
                                        that.layerDict[that.childDict[addr][j]][1] = 4;
                                        changeDisplay(that.layerDict[that.childDict[addr][j]][0], that.layerDict[that.childDict[addr][j]][1]);
                                    }
                                }
                            }

                                // Is a parent that has been selected, now that it is is selected again it will hide all children and go back to normal
                            else if (that.layerDict[addr][1] == 2) {
                                that.layerDict[addr][1] = 1;
                                changeDisplay(layer, that.layerDict[addr][1]);

                                if (that.childDict[addr]) {
                                    for (var j in that.childDict[addr]) {
                                        console.log(that.layerDict[that.childDict[addr][j]])
                                        that.layerDict[that.childDict[addr][j]][1] = 3;
                                        changeDisplay(that.layerDict[that.childDict[addr][j]][0], that.layerDict[that.childDict[addr][j]][1]);
                                    }
                                }
                            }

                            that.lock = !that.lock;

                            if (that.lock) {
                                that.mainMap.closePopup();
                                popup.setContent(first_dict[feature.properties.id]);
                                popup.setLatLng(e.latlng).openOn(that.mainMap);
                            }

                            else {
                                popup.setContent(feature.properties.name);
                            }
                        });

                        layer.on('mouseover', function (e) {
                            // Is a parent object, just getting hovered over
                            if (that.layerDict[addr][1] == 0) {
                                that.layerDict[addr][1] = 1;
                                changeDisplay(layer, that.layerDict[addr][1]);
                            } 
                                // Is a child, has just been revealed
                            else if (that.layerDict[addr][1] == 4 && !that.lock) {
                                that.layerDict[addr][1] = 5;
                                changeDisplay(layer, that.layerDict[addr][1]);
                            }

                            if (!that.lock && that.layerDict[addr][1] != 3 && that.layerDict[addr][1] != 2) {

                                popup.setLatLng(e.latlng).openOn(that.mainMap);
                                popup.setContent(feature.properties.name);
                            };


                        });

                        layer.on('mouseout', function (e) {
                            // Is a parent object, was just hovered over but not clicked
                            if (that.layerDict[addr][1] == 1) {
                                that.layerDict[addr][1] = 0;
                                changeDisplay(that.layerDict[addr][0], that.layerDict[addr][1]);
                            }
                                // Is a child, has been revealed but not clicked, so is now going back to 
                            else if (that.layerDict[addr][1] == 5) {
                                that.layerDict[addr][1] = 4;
                                changeDisplay(layer, that.layerDict[addr][1]);
                            }

                            if (!that.lock) {
                                that.mainMap.closePopup();
                            }
                        });

                        layer.on('mousemove', function (e) {

                            if (!that.lock && that.layerDict[addr][1] != 3 && that.layerDict[addr][1] != 2) {
                                that.mainMap.closePopup();
                                popup.setLatLng(e.latlng).openOn(that.mainMap);
                            }
                        });

                        popup.setLatLng([0, 0]).openOn(that.mainMap);
                        that.mainMap.closePopup();
                    }
                }).addTo(that.mainMap);
            });
        }


        Object.keys(that.startList).forEach(function (addr, index) {
            putOnMap(that.startList[index])
        });

        function findData(id){
            var obj = null
            $.ajax({
                'async': false,
                'global': false,
                'url': `https://data.cambridgecarbonmap.org/reporting_entities/`+id+`.json`,
                'dataType': "json",
                'success': function (data) {
                    obj = data;
                    console.log(obj)
                }
            });
            return obj
        }

        function findShow(id){
            var found = null
            $.ajax({
                'async': false,
                'global': false,
                'url': `https://data.cambridgecarbonmap.org/geojson/`+id+`.geojson`,
                'dataType': "json",
                'success': function (data) {
                    if(data.features[0].properties.show){found = data.features[0].properties.id}
                }
            });
            return found
        }

        function makeLink(feature) {

            // var div = document.createElement("a");
            // div.href = "reporting_entities/" + feature.properties.id;
            // div.innerHTML = feature.properties.name;
            // return div

            var div = document.createElement("div");
            div.align = "center"

            var searcher = feature.properties.id;
            var datajson = null;
            var own = true;
            
            while(true){
                datajson = findData(searcher);
                if(datajson == null){

                    own = false;
                    searcher = searcher.split(".");
                    var popped = searcher.pop()

                    if (searcher.length == 0){
                        break;
                    }

                    searcher = searcher.join(".")
                }
                else{
                    break
                }
            }



            // Change to be monthly?
            var emissionsNumber = datajson.emissions[0].value * 15.6 + datajson.emissions[1].value * 21.3;
            var toptext
            var bottext = "Click here for more"
            
            if(own){
                toptext = `Emissions for ${feature.properties.name}:`
            } else{
                toptext = `No stats for this building individually! Emissions for ${datajson.name}:`
            }

            div.innerHTML = `
                ${toptext}</br>
                <p style="font-size:25px">${emissionsNumber}</p>
                </br>
                <a href = "reporting_entities/${feature.properties.id}">${bottext}</a>
            `
            return div
        }

        }
    };