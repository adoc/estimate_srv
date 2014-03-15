TOC
===
[Introduction](#section_introduction)  
[Parameter Glossary](#section_parameter_glossary)  
[Data API](#section_data_api)  
[Data Model](#section_data_model)  
[Web Service Resource Locations](#section_resource_locations)  


<a name="#section_introduction"></a>
Introduction
===
This is the developer documentation for the Online Estimate web service and API. 

**[APIs](#section_data_api)**  
The Python API is found in the `oest` module. The Javascript API can be loaded with the `oest.js` module. *(This requires Backbone.js, Underscore.js and jQuery)*


<a name="section_parameter_glossary"></a>
Parameter Glossary
===
The following is a list of parameters and their descriptions.
These parameters are listed in later sections.

Param | Description
------|------------
**Control parameters** |
errors | Response error information Object.
**Information Parameters** |
location_id | Shop identifier code. (Specified in the admin panel.)
  | *Validation:* `string`, `unique`, `min(2)`, `max(32)`
location_name | Shop/location displayed name. 
  | *Validation:* `string`, `min(3)`, `max(128)`
  | *Other:* Proper cased during display.
<a name="parameter_glossary_sub_estimate_params"></a>**Estimate Parameters** |
estimate_id | Estimate identifier. This is a long (UUID-like) code.
zip_code | 5-digit zip code.
  | *Validation:* `string`, `min(5)`, `max(5)`, `cast(integer)`, must be in valid zip list.
referral_text | Refferal source text.
  | *Validation:* `string`, `min(5)`, `max(128)`
email_address | guest email address.
referred_custom | text field for referral entry.
  | *Validation:* `string`, `min(3)`, `max(1024)`
full_name | guest full name.
  | *Validation:* `string`, `min(5)`, `max(256)`
address1 | guest Address, line one.
address2 | guest Address, line two.
city | guest City of Residence.
state | guest State/Province.
phone | guest Phone Number.
vehicle_year | guest Vehicle Year
vehicle_make | guest Vehicle Make
vehicle_model | guest Vehicle Model
vin_number | Vehicle VIN.
vin_image_id | Vehicle VIN Image id.
vehicle_images | List of Vehicle Image id's.


<a name="section_data_api"></a>
Data API
========
These APIs are (mostly) implemented in Python and Javascript (with jQuery/Backbonejs). The Python API will interact directly with the Redis data models and other backend persistence since we're handling images too. The Javascript API along with Backbone.js provide connectivity to data via the web service.

### General
These are general methods that apply to all objects. (Applies to Location and Estimate object APIs.)

Method | Action
-------|-------
list(`active_only`) | Get a list of Location objects. `active_only` set to `true` for only active Locations.
idx(`id`) | Get integer index position of the object with `id`.
move(`id`, `to_idx`) | Move an object `to_idx` position. (This inserts before the object at `to_idx`.)
get(`id`) | Get object with `id`.
  | *Returns:* `{object}`
add(`{object}`) | Add an object.
  | *Returns:* `id` of new object.
update(`id`, `{object}`) | Update an existing object with `id`.
  | *Returns:* Updated `{object}`.
del(`id`) | Delete a object with `id`. (Really just sets it inactive and queues it for the next archive operation.)


### Location
Location objects represent Store/Shop locations. This API provides methods to interact with Location objects. , while the Javascript API will be the "AJAX" connection to the web service.

Method | Action
-------|-------
add_zip(`location_id`, `zip_code`) | Add a zip code match for this location.
del_zip(`zip_code`) | Delete a zip code.

##### Python Usage
```python
location_api = Location(api_connection)
location_api.add_zip('1111-1111-1111-1111', '91016')
```
`api_connection` refers to the Redis API connection.

##### Javascript
```javascript
var locationApi = new Location(LocationModel);
locaionApi.del_zip("1111-1111-1111-1111", '91016');
```
`LocationModel` refers to the Backbone.Model extension for `Location`.

### Estimate
Estimate objects represent individual Estimate records submitted by guests.

##### Method List
Method | Action
-------|-------
close(`estimate_id`) | Close the estimate at `id`.


<a name="section_data_model"></a>
Data Model
==========
The data model is persisted using Redis and its data types. This is how the data is represented in Redis. *(Not applicable to Javascript implementations)

Key | Description
----|------------
**Strings** |
zip_location:`zip` | `location_id` of given `zip` code.
**Sorted Sets** |
location_idx | Full index of locations.
estimate_idx | Full index of estimates.
location_active | Index of *active* locations.
estimate_active | Index of *active* estimates.
location_zip:`location_id` | Zip codes in a given `location_id`.
**Hashes** |
location:`id` | Location specific data.
estimate:`id` | Individual estimate data.


<a name="section_resource_locations"></a>
Web Service Resource Locations
===
The following is a list of service URIs/locations and their respective function, parameters, responses, etc. These URIs are implemented by the [Javascript API](#section_data_api) module of this project.

*All services at root url https://scc1.webmob.net/api/v1/*

URI | Methods | Actions
----|---------|--------
/locations/zip/`zip_code` | [GET](#resource_locations_zip_get) | Accepts a zip code and returns the matching Location.
/estimates | [GET](#resource_locations_estimates_get), [POST](#resource_locations_estimates_post) | GET returns a list of Active and Open Estimates.<br />POST is used for creating a new Estimate.
/estimates/`estimate_id`| [GET](#resource_locations_estimates_id_get), [PUT](#resource_locations_estimates_id_put), [DELETE](#resource_locations_estimates_id_delete) | GET Retrieves the Estimate data.<br />PUT is used for editing/modifying an existing Estimate.<br />DELETE sets an Estimate as inactive, thereby removing it from any views.

<a name="resource_locations_zip_get"></a>
/locations/zip/`zip_code` **_GET_**
---
Accepts a zip code and returns the closest shop.

##### Response JSON Params
`zip_code`, `location_id`, `location_name`

##### Responses HTTP Codes
Code | Description
-----|------------
200 | Zip was valid and returning matched shop.
403 | Zip provided did not validate or was malformed.
404 | Zip did not match any shop.


<a name="resource_locations_estimates_get"></a>
/estimates **_GET_**
---
Gets a list of open estimates. *(Admin permissions)*


<a name="resource_locations_estimates_post"></a>
/estimates **_POST_**
---
Used to initiate/create an online-estimate.

##### Request Params
**`email_address`**, **`zip_code`**, [any other estimate parameter](#parameter_glossary_sub_estimate_params)

##### Response JSON Params
`estimate_id`**, `errors`, [any other estimate parameter](#parameter_glossary_sub_estimate_params)

##### Response HTTP Codes
Code | Description
-----|------------
200 | Request OK but further `errors` might be present.


<a name="resource_locations_estimates_id_get"></a>
/estimates/`estimate_id` **_GET_**
---
Retrieves the estimate data.

##### Response JSON Params
[any estimate parameter](#parameter_glossary_sub_estimate_params)
*Depending on permissions, only some data may be returned.*

##### Response HTTP Codes
Code | Description
-----|------------
200 | Estimate data was returned.
404 | Estimate ID was not found.


<a name="resource_locations_estimates_id_put"></a>
/estimates/`estimate_id` **_PUT_**
---
Used for editing/modifying an existing estimate. Also used during any multi-step user input flow (e.g. mobile)

##### Request Params
[any estimate parameter](#parameter_glossary_sub_estimate_params)

##### Response JSON Params
`estimate_id`, `errors`, [any other estimate parameter](#parameter_glossary_sub_estimate_params)

##### Response HTTP Codes
Code | Description
-----|------------
200 | ???
404 | Estimate ID was not found.


<a name="resource_locations_estimates_id_delete"></a>
/estimates/`estimate_id` **_DELETE_**
---
Deletes estimate data.
*(Admin permissions)*
    
##### Response HTTP Codes
Code | Description
-----|------------
200 | Estimate was deleted.
404 | Estimate ID was not found.


<a name="resource_locations_access_estimates_id_get"></a>
/estimates/access/`estimate_id` **_GET_**
---
Used by guests to receive an access token to view/edit their estimate. The actual token is delivered via email.

  
  
  
  
---
&copy; 2014 Nicholas Long. All Rights Reserved. 