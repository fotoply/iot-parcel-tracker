from flask import Flask, request

app = Flask(__name__)

import requests
import json

@app.route("/alarm")
def alarm():
    if request.args.get("id") == "1":
        return "True"
    return "False"

@app.route("/geolocation", methods = ['POST', 'GET'])
def geolocation():
    app.logger.info(request.get_json())
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    r = requests.post(url="https://www.googleapis.com/geolocation/v1/geolocate?key=", #Insert new key here, old key is compromised through publication to git, whoops
                      data=request.get_data(), headers=headers)
    return str(r.text)

@app.route("/save", methods = ['POST'])
def save():
    id = request.args.get("id")
    if id == None:
        return "ERROR"

    data = request.get_data()
    jData = json.loads(data)

    import csv
    with open(str(id) + '.csv', mode='a+') as csvFile:
        fieldnames = ["acceleration", "temperature", "humidity", "barometer", "location"]
        csvWriter = csv.DictWriter(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
        writer.writerow(jData)

    return "OK"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
