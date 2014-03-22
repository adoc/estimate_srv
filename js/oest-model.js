/*


*/

define(['backbone'], function(Backbone) {

    // http://stackoverflow.com/a/10916733
    var Images = Backbone.Model.extend({
        read: function(fileElement, idx) {
            var reader = new FileReader(),
                that = this;
            // adoc: I think I optimized this. The extra closure wasn't
            // neccessary due to scope.
            reader.onload = function(el) {
                    //set model
                    that.set({"image_"+idx+"_name": fileElement.name,
                                "image_"+idx+"_data": el.target.result});
                };
            // Read in the image file as a data URL.
            reader.readAsDataURL(fileElement);
        }   
    });


    // Location model.
    // Careful with this namespace `Location`.
    var Location = Backbone.Model.extend({
        url: '/location'
    });


    // Collection of Location objects.
    var Locations = Backbone.Collection.extend({
        url: '/location',
        model: Location
    });


    var 

    return {
        Location: Location,
        Locations: Locations
    };
});