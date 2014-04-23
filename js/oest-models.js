"use strict";
/*
*/

define(['backbone'], function(Backbone) {

    // http://stackoverflow.com/a/10916733
    var Images = Backbone.Model.extend({
        readFile: function(fileElement, idx) {
            var reader = new FileReader(),
                that = this;
            // adoc: I think I optimized this. The extra closure wasn't
            // neccessary due to scope.
            reader.onload = function(el) {
                    //set model
                    var img_obj = {};
                    img_obj["image_"+idx+"_name"] = fileElement.name;
                    img_obj["image_"+idx+"_data"] = el.target.result;
                    that.set(img_obj);
                };
            // Read in the image file as a data URL.
            reader.readAsDataURL(fileElement);
        }   
    });


    // Location model.
    // Careful with this namespace `Location`.
    var Location = Backbone.Model.extend({
        idAttribute: "_id",
        urlRoot: 'https://scc1.webmob.net/api/v1/location'
    });


    // Collection of Location objects.
    var Locations = Backbone.Collection.extend({
        url: 'https://scc1.webmob.net/api/v1/location',
        model: Location
    });


    var Estimate = Images.extend({
        url: '/estimate'
    });


    return {
        Location: Location,
        Locations: Locations,
        Estimate: Estimate
    };
});