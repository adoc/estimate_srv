


Admin Panel
===========
Administration panel for the following.


Parameter List
==============
The following is a list of parameters and their descriptions.
These parameters are listed in later sections.

Control parameters
------------------
errors - Response error information (JSON Object).

Information Parameters:
location_id - Shop identifier code. (Specified in the admin panel.)
Validation: string, unique, min 2 char, max 32 char.

location_name - Shop/location displayed name. (Specified in the admin panel.)
Validation: string, min 3 char, max 128 char, forced proper case.


Estimate Parameters
-------------------
estimate_id - Estimate identifier. This is a long (UUID-like) code.

zip_code - Zip Code. 
Validation: string, 5 char min/max, must convert to integer,
    must be in valid zip list.

referral_text - Refferal source text.
Validation: string, 5 char min, 128 char max.

estimate_id
email_address - guest email address (Only returned if
                authenticated as admin.)

referred - ?? id or text?
referred_custom - text field for custom entry of referral
    information. (String, 3 to 1024 characters.)

full_name

address1 -
address2 -
city -
state -
zip -

phone - 

vehicle_make -
vehicle_model -
vehicle_year -

vin_number - 
vin_image_id -
vehicle_images -

email_address, referred, referred_custom, full_name, address1, address2, city, state, zip, phone, vehicle_make, vehicle_model, vehicle_year, vin_numer, vin_image, vehicle_image_#


Data Model
==========
Redis data types.

Strings
-------

Key                  | Description
---------------------|-------------------------------
`zip_location:{zip}` | Location id of given zip code.

Sorted Sets
-----------

Key | 

* *`location_idx`* - Full index of locations.
`estimate_idx` - Full index of estimates.
`location_active` - Index of active locations.
`estimate_active` - Index of active estimates.

`location_zip:{location_id}` - Zip codes in a given location_id.

Hashes
------

`location:{id}` - Location data.
`estimate:{id}` - Estimate data.


Data API
========    
Location
add -
    adds `location:{id}` hash.
    adds `location_id` to `location_idx`
del -
    sets `location:{id}` hash field `active` to false.
    remove location_id from `location_active` set.
move
add_zip
del_zip


Web Service Resource Locations:
===============================
    The following is a list of service URIs/locations and their
    espective function, parameters, responses, etc.    

    All services at root url https://scc1.webmob.net/api/v1/

    -------

    GET: /locations/zip/{zip_code}
        Accepts a zip code and returns the closest shop.

        URI Params - zip_code

        Response JSON Params - zip_code, location_id, location_name

        Responses HTTP Codes:
            200 - Zip was valid and returning matched shop.
            403 - Zip provided did not validate or was
                    malformed.
            404 - Zip did not match any shop.


    GET: /estimates     (Admin permissions)
        Gets a list of open estimates.


    POST: /estimates
        Used to initiate an online-estimate.

        Request Params - *email_address, *zip_code, (any other
            estimate parameter.)

        Response JSON Params - estimate_id, errors, (any other
            estimate parameter.)

        Response HTTP Codes:
            200 - Request OK but further `errors` might be present.
            

    PUT: /estimates/{estimate_id}
        Used for editing/modifying an existing estimate. Also used
        during any multi-step user input flow (e.g. mobile)

        Request Params - (any estimate parameter.)

        Response HTTP Codes:
            200 - 
            404 - Estimate ID was not found.

        Response JSON Params - estimate_id, errors, (any other
            estimate parameter.)


    GET: /estimates/{estimate_id}
        Retrieves the estimate data.

        Response JSON Params -(any estimate parameter.)
            Depending on permissions, only some data may be returned.

        Response HTTP Codes:
            200 - Estimate data was returned.
            404 - Estimate ID was not found.


    DELETE: /estimates/{estimate_id}     (Admin permissions)
        Deletes estimate data.

        Response HTTP Codes:
            200 - Estimate was deleted.
            404 - Estimate ID was not found.


    Optional:
    ---------

    GET: /estimates/access/{estimate_id}
        Used by guests to receive an access token to view/edit their
        estimate. The actual token is delivered via email.
