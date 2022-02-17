import os
import requests
import pandas as pd

from sodapy import Socrata
from datetime import datetime
from flask import Flask, flash, render_template, session, request, url_for

app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
# from https://dev.socrata.com/foundry/data.calgary.ca/c2es-76ed
client = Socrata("data.calgary.ca", None)
results = client.get("c2es-76ed", limit=1)
results_df = pd.DataFrame.from_records(results)


# routes
@app.route('/')
def index():
    return render_template("map.html", features='')


@app.route('/search', methods=["GET", "POST"])
def map_details():
    # api for Calgary Building Permits
    from_date = "'" + datetime.strptime(str(request.form.get("from_date")),'%Y-%m-%d').strftime('%Y/%m/%d') + "'"
    to_date = "'" + datetime.strptime(str(request.form.get("to_date")),'%Y-%m-%d').strftime('%Y/%m/%d') + "'"
    from_date = "'" + request.form.get("from_date") + "T00:00:00.000" + "'"
    to_date = "'" + request.form.get("to_date") + "T23:59:00.000" + "'"
    url = "https://data.calgary.ca/resource/c2es-76ed.geojson?$where=issueddate between " + from_date + " and " + to_date + "&$select=issueddate,latitude,longitude,workclassgroup,contractorname,communityname,originaladdress"

    calg_bp = requests.get(url)
    response = calg_bp.json()
    features = response['features']

    print(url)
    #print(features)

    return render_template("map.html", features=features)
