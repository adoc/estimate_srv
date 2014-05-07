define(['backbone', 'oest_models', 'text!/location_list.html.tmpl'],
    function (Backbone, Models, location_list_tmpl, location_zip_list_tmpl) {

        var invalidForm = function(form, prefix) {
            var that = this;
            /* Update view with errors/warnings for form validation. */
            function inner(model, errors) {
                /* validation error handler for this view. */
                that.invalid = true;

                $.each($('.form-group.has-error', form), function(i, clearme) {
                    // Clear any errors in the form.
                    $(clearme).removeClass('has-error');
                    $(clearme).children('label').html('');
                });

                for (i in errors) {
                    var error = errors[i];

                    if (error.hasOwnProperty('form')) {
                        var par = form.children('#form_label')
                        form.addClass('has-error');
                        par.children('label').html(error['msg']);

                    } else {
                        var field = error['field'];
                        if (prefix)
                            var name = prefix + '_' + field;
                        else
                            var name = field;
                        var el = form.find('input[name="' + name + '"]'); // TODO: Ugly. Use string replacement, templating, etc.
                        var par = el.parent('.form-group');
                        par.addClass('has-error');
                        par.children('label').html(error['msg']);
                    }
                }
            }
            return inner;
        };


        // General model can be included elsewhere.
        var List = Backbone.View.extend({
            _invalid: false,
            _selected: null,
            _edited: null,
            collection_model: null,
            collection_template: null,
            collection: null,
            deleteDelay: 3000,

            events: {
                'click tr.collection_item': 'selectItem',
                'click button[name="new_btn"]': 'newItem',
                'click button[name="save_btn"]': 'saveItem',
                'click button[name="edit_btn"]': 'editItem',
                'click button[name="delete_btn"]': 'deleteItem',
                'click button[name="cancel_btn"]': 'renderOnly'
            },
            initialize: function () {
                this.collection = new this.collection_model();

                this.collection.on('add', this.renderOnly, this);
                this.collection.on('remove', this.renderOnly, this);
            },
            renderOnly: function(selected, edited) {
                /* Render the data/template only. */
                this._selected = selected;
                this._edited = edited;
                var template = _.template(this.collection_template, {
                    collection: this.collection.models,
                    selected: selected,
                    edited: edited
                });
                this.$el.html(template);
                this.delete_state = null;
                this._invalid = false;
            },
            render: function() {
                /* Fetch data model and render template. */
                var that = this;
                this.collection.fetch({
                    success: function() {
                        that.renderOnly();
                    }
                });
            },
            getItemId: function(ev) {
                /* */
                return $(ev.currentTarget).data('id');
            },
            // New item intent. Serialize and save. 
            newItem: function(ev) {
                var that = this,
                    form = $(ev.currentTarget).closest('form'),
                    form_obj = form.serializeObject(),
                    item = new this.collection.model;
                
                item.on("invalid", invalidForm.call(form));

                item.save(form_obj, {
                    crossDomain: true,
                    success: function () {
                        that.collection.add(item);
                    },
                    error: function(model, xhr, response) {
                        if(xhr.status==400) {
                            var body = JSON.parse(xhr.responseText);
                            invalidForm.call(body);
                        } else {
                            throw("newItem: Server Error.");
                        }
                    }
                });
                return false;
            },
            selectItem: function (ev) {
                /* */
                var id = this.getItemId(ev);
                if (this._selected === id && this._edited !== id) {
                    this.renderOnly(id, id);
                }
                else if (this._edited !== id) {
                    this.renderOnly(id);
                }
                return false;
            },
            editItem: function (ev) {
                /* */
                var id = this.getItemId(ev);
                if (this._edited !== id) {
                    this.renderOnly(id, id);
                }
                return false;
            },
            saveItem: function(ev) {
                var that = this,
                    form = $(ev.currentTarget).closest('form'),
                    form_obj = form.serializeObject(),
                    id = this.getItemId(ev);

                var item = this.collection.get(id);
                item.on("invalid", invalidForm.call(this, form));
                item.set(form_obj, {validate: true});

                if (item.hasChanged()) { // Does .save really not check to see if the model has changed?
                    item.save(form_obj, {
                        success: function () {
                            that.render(); // Fetch and render.
                            //that.renderOnly();
                        },
                        error: function(xhr, textStatus) {
                            if(textStatus.status==400) {
                                throw("newItem: Server said request was bad.");
                            } else {
                                throw("newItem: Server Error.");
                            }
                        }
                    });
                }
                else if (!this.invalid) {
                    that.renderOnly();
                }

                return false;
            },
            deleteItem: function(ev) {
                /* Instructs removal of item of `id`. */
                var el = ev.currentTarget;
                if (this.delete_state && this.delete_state == el) {
                    var id = this.getItemId(ev);
                    var item = this.collection.get(id);
                    item.destroy();
                    this.deleteCancel(ev);
                } else if (this.delete_state && this.delete_state != el) {
                    this.deleteCancel(this.delete_state);
                    this.deleteReady(ev);
                } else {
                    this.deleteReady(ev);
                }

                return false;
            },
            deleteReady: function(ev) {
                /* Ready the delete. Start the timer. */
                var that = this;
                var el = ev.currentTarget;
                this.delete_state = el;
                clearInterval(this.deleteTimer);
                this.deleteTimer = setInterval(
                    function() {
                        that.deleteCancel(ev);
                    }, this.deleteDelay);
                $(ev.currentTarget).addClass('btn-danger');
            },
            deleteCancel: function(ev) {
                /* Cancel the delete and timer. */ 
                $(ev.currentTarget).removeClass('btn-danger');
                this.delete_state = null;
                clearInterval(this.deleteTimer);
            },
        });

        Object.defineProperty(List.prototype, 'invalid', {
            enumerable: true,
            configurable: true,
            writeable: false,
            get: function () { return this._invalid; }
        });


        var LocationList = List.extend({
            el: '.page',
            collection_model: Models.Locations,
            collection_template: location_list_tmpl,
            /*initialize: function () {
                List.prototype.initialize.apply(this, arguments);
                this.zip_codes_view = new ZipCodeList();
            }*/
        });

        /*
        var ZipCodeList = List.extend({
            // el is added as an `option` on construction.
            collection_model: Models.ZipCodes,
            collection_template: location_zip_list_tmpl,
            initialize: function () {
                console.log("Init ZipCodeList");

                var urlRoot = 'https://scc1.webmob.net/api/v1/location/'+this.id+'/zip',
                    ZipCode = Backbone.Model.extend({
                        urlRoot: urlRoot
                    });

                List.prototype.initialize.call(this, [], {model: ZipCode, url: urlRoot});

                this.el = '#' + this.id;

                console.log(this.collection_model.url)
            }
        });*/

        var ZipTest = Backbone.View.extend({
            events: {
                'click button[name="zip_test"]': 'zipTest',
            },
            zipTest: function(ev) {

            }
        });


        return {
            LocationList: LocationList,
            // ZipCodeList: ZipCodeList
        };

    }
);