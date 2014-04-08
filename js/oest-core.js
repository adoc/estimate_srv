"use strict";
/*
*/
define(['backbone', 'oest_events'], function(Backbone, Events) {
    return {        
        from_config: function (params) {
            params = params || {};
            if (params.url) {
                var parsed = urlParse(params.url);

            }
        },
        ready: function (callback) {
            Events.on('oest.ready', callback);
        }
    };
});