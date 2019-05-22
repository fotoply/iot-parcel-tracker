from flask import Flask, request

app = Flask(__name__)

import requests
import json


@app.route("/geolocation", methods = ['POST', 'GET'])
def geolocation():
    app.logger.info(request.get_json())
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    r = requests.post(url="https://www.googleapis.com/geolocation/v1/geolocate?key=", #Insert new key here, old key is compromised through publication to git, whoops
                      data=request.get_data(), headers=headers)
    return str(r.text)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
