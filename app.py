from flask import Flask, request

app = Flask(__name__)

import requests
import json

@app.route("/alarm")
def alarm():
    import os
    return str(os.path.isfile(request.args.get("id") + ".alarm"))

@app.route("/geolocation", methods = ['POST', 'GET'])
def geolocation():
    print(request.get_data())
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    r = requests.post(url="https://www.googleapis.com/geolocation/v1/geolocate?key=", #Insert new key here, old key is compromised through publication to git, whoops
                      data=request.get_data(), headers=headers)
    return str(r.text)

@app.route("/save", methods = ['POST'])
def save():
    id = request.args.get("id")
    if id == None:
        return "ERROR"

    jData = request.get_json()
    #jData = json.loads(data)
    print(jData)

    import csv
    with open(str(id) + '.csv', mode='a+') as csvFile:
        lines = []
        for key in jData:
            for index in range(len(jData[key])):
                if len(lines)-1 < index:
                    line = {}
                    lines.append(line)
                else:
                    line = lines[index]

                print(key)
                print(line)
                value = jData[key]
                print(value)
                print(index)
                line[key] = value[index]
                print(line)

        for line in lines:
            fieldnames = ["timestamp", "acceleration", "temperature", "humidity", "barometer", "location", "extreme"]
            csvWriter = csv.DictWriter(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
            csvWriter.writerow(line)
    return "OK"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
