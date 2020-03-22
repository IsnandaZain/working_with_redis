from flask import Flask, request, jsonify

import string
import random
import json

import logging

from cache import cache

app_instance = Flask(__name__)
app_instance.make_null_session()

log = logging.getLogger(__name__)

KEY_CACHE = "user_profile"

def get_id():
    _id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(7)])
    return _id

app_instance.route("/input_redis", methods=["POST"])
def input_redis():
    profile_id = "%s" % get_id()
    username = request.form.get("username")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")

    # generate fullname
    fullname = first_name + " " + last_name

    # save into redis
    dict_cache_profile = json.dumps({
        "id": profile_id,
        "username": username,
        "fullname": fullname
    })

    cache.set(key=KEY_CACHE + "_" + profile_id, value=dict_cache_profile)

    response = {
        "status": 200,
        "message": "Berhasil membuat profile",
        "result": {
            "id": profile_id,
            "username": username,
            "fullname": fullname,
        }
    }

    return jsonify(response)


app_instance.route("/get_redis/<str:profile_id>")
def get_redis(profile_id):
    # get from cache
    data_profile = cache.get(key=KEY_CACHE + "_" + profile_id, return_type=str)

    if data_profile:
        dict_cache_profile = json.loads(data_profile)
    else:
        dict_cache_profile = None

    response = {
        "status": 200 if dict_cache_profile else 204,
        "result": dict_cache_profile
    }

    return jsonify(response)


app_instance.route("/delete_redis", methods=["POST"])
def delete_redis():
    profile_id = request.form.get("profile_id")

    # get data from cache
    data_profile = cache.get(key=KEY_CACHE + "_" + profile_id, return_type=str)
    
    if data_profile:
        dict_cache_profile = json.loads(data_profile)
        cache.delete(key=KEY_CACHE + "_" + profile_id)
    else:
        response = {
            "status": 204,
            "message": "Data profile tidak ditemukan"
        }

    response = {
        "status": 200,
        "username": dict_cache_profile["username"],
        "message": "Berhasil menghapus profile dari cache"
    }

    return jsonify(response)


app_instance.route("/update_redis", methods=["POST"])
def update_redis():
    profile_id = request.form.get("profile_id")
    username = request.form.get("username")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")

    # generate fullname
    fullname = first_name + " " + last_name

    data_profile = cache.get(key=KEY_CACHE + "_" + profile_id, return_type=str)

    if data_profile:
        dict_cache_profile = json.loads(data_profile)

        # update data
        dict_cache_profile["username"] = username
        dict_cache_profile["first_name"] = first_name
        dict_cache_profile["last_name"] = last_name
        dict_cache_profile["fullname"] = fullname

        json_cache_profile = json.dumps(dict_cache_profile)

        cache.update(key=KEY_CACHE + "_" + profile_id, value=json_cache_profile)

    else:
        response = {
            "status": 204,
            "message": "Data profile tidak ditemukan",
        }

        return jsonify(response)

    response = {
        "status": 200,
        "message": "Berhasil mengupdate profile cache",
        "result": dict_cache_profile
    }

    return jsonify(response)


app_instance.run(host="127.0.0.1", port=5000, debug=True)