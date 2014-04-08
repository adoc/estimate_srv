"use strict";

(function (window, document) {

    var chainScripts = function (scripts, doneCallback) {
        var scriptsList = scripts || [];

        var injectScript = function (src, next, callback) {
            var body = document.getElementsByTagName('body')[0],
                script = document.createElement('script'),
                done = false;

            script.type = "text/javascript";
            script.src = src;

            script.onload = script.onreadystatechange = function () {
                if (!done && (!this.readyState ||
                        this.readyState === "loaded" ||
                        this.readyState === "complete") ) {
                    // http://stackoverflow.com/a/4845802
                    done = true;

                    // "Iterator" Callback.
                    next();
                    // User Callback.
                    if (typeof callback === 'function') {
                        callback();
                    }
                }
            };
            body.appendChild(script);
        };

        this.add = function(src, callback) {
            if (typeof src === 'string' &&
                    (callback === undefined || typeof callback === 'function'))
                scriptsList.push([src, callback]);
            else
                throw "`chainScripts` expects a string 'src' and function 'callback' arguments.";
        };

        this.run = function(doneCallback) {
            var i = 0,
                next = function () {
                    var script = scriptsList[i];

                    if (!script) {
                        if (typeof doneCallback === 'function') {
                            return doneCallback();
                        }
                    }

                    if (script instanceof Array && script.length > 0) {
                        // splice in `next` as a callback.
                        script.splice(1, 0, next);
                        injectScript.apply(this, script);
                    }
                    else if (typeof script === 'string') {
                        injectScript.call(this, script, next);
                    }
                    else {
                        console.log(script);
                        throw "Bad item in script list. (Only [src, callback] array or src string.)";
                    }

                    i++;
                };

            next();
        }

        Object.defineProperty(this, 'done', {
            enumerable: true,
            configurable: true,
            writeable: false,
            get: function() { return scriptsList.length === 0; }
        });

        if (scripts.length > 0 && typeof doneCallback === 'function')
            this.run(doneCallback);
    };

    // Add utility func to Global scope.
    window.chainScripts = chainScripts;

    // Execute utility.
    new chainScripts(['https://code.webmob.net/js/api1.0/require.min.js',
                  '/js/oest-common.js'], function () {
        require(['oest_core', 'oest_config'],
            function (Oest, Config) {
                // Initialize backbone.js app.
                Config.requireApi = true;
                Config.apiTight = false;
                // Config.apiDefault = {remotes: ${remotes|n}};
                // Oest.initialize();
            }
        );
    });
}).call(this, window, document);