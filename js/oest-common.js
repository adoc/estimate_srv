"use strict";
/*
oest-common.js - Online Estimate Web Service Javascript API

This module is the require.js (http://requirejs.org/) configuration
where we load all the dependency modules required for the API
and Web Service.

This file will attempt to load dependency modules from
"//code.webmob.net" and also from the hosted location.

WARNING: These files **should** be delivered via SSL/HTTPS, otherwise
the encryption, security, and authentication is easily circumvented!
This means that the web page spawning connections to the Web Service
must be secured with SSL as well.

These modules requires HTML5.
*/
require.config({
    paths: {
        underscore: ['https://code.webmob.net/js/api1.0/underscore.min',
                    '/js/api1.0/underscore.min'],
        //jquery: ['https://code.webmob.net/js/api1.0/zepto.min',
        //            '/js/api1.0/zepto.min'],
        jquery: ['https://code.webmob.net/js/api1.0/jquery-min',
                    '/js/api1.0/jquery-min'],
        text: ['https://code.webmob.net/js/api1.0/text.min',
                '/js/api1.0/text.min'],
        backbone: ['https://code.webmob.net/js/api1.0/backbone.min',
                    '/js/api1.0/backbone.min'],
        crypto_core: ['https://code.webmob.net/js/api1.0/crypto-core.min',
                    '/js/api1.0/crypto-core.min'],
        crypto_sha: ['https://code.webmob.net/js/api1.0/crypto-sha256.min',
                    '/js/api1.0/crypto-sha256.min'],
        crypto_hmac: ['https://code.webmob.net/js/api1.0/crypto-hmac.min',
                    '/js/api1.0/crypto-hmac.min'],
        crypto_b64: ['https://code.webmob.net/js/api1.0/crypto-enc-base64.min',
                    '/js/api1.0/crypto-enc-base64.min'],
        rng: ['https://code.webmob.net/js/api1.0/rng.min',
                    '/js/api1.0/rng.min'],
        persist: ['https://code.webmob.net/js/api1.0/persist.min',
                    '/js/api1.0/persist.min'],
        serialize_object: ['https://code.webmob.net/js/api1.0/jquery.serialize-object.min',
                    '/js/api1.0/jquery.serialize-object.min'],
        oest_boot: ['/js/oest-boot'],
        oest_core: ['/js/oest-core'],
        oest_config: ['/js/oest-config'],
        oest_events: ['/js/oest-events'],
        oest_models: ['/js/oest-models'],
        admin_boot: ['/js/admin-boot'],
        admin_router: ['/js/admin-router'],
        admin_views: ['/js/admin-views']
    },
    shim: {
        underscore: {
            exports: '_'
        },
        jquery: {
            exports: '$',
            init: function () {
                window.jQuery = $;
            }
        },
        backbone: {
            deps: ['jquery', 'underscore'],
            exports: 'Backbone'
        },
        crypto_sha: {
            deps: ['crypto_core']
        },
        crypto_hmac: {
            deps: ['crypto_core', 'crypto_sha', 'crypto_b64']
        },
        crypto_b64: {
            deps: ['crypto_core']
        },
        persist: {
            exports: 'Persist'
        },
        serialize_object: {
            deps: ['jquery']
        },
        oest_core: {
            deps: ['backbone', 'oest_events'],
            exports: 'Oest'
        },
        oest_events: {
            deps: ['underscore', 'backbone'],
            exports: 'Oest.Events'
        },
        oest_models: {
            deps: ['backbone'],
            exports: 'Oest.Models'
        },
        oest_boot: {
            deps: ['oest_core', 'oest_config']
        },
        admin_boot: {
            dets: ['jquery', 'oest_core', 'oest_config']
        },
        admin_views: {
            deps: ['serialize_object'],
            exports: 'Oest.AdminViews'
        }
    },
    timeout: 5
});