import os

from flask import Flask, flash, render_template, request, url_for, session

def map_details(date):
    # api for Google Books ratings
    calg_bp = requests.get("https://data.calgary.ca/resource/c2es-76ed.json")
    response = calg_bp.json()

    results =
    rating = (response['items'][0]['volumeInfo']['averageRating'])
    no_rating = (response['items'][0]['volumeInfo']['ratingsCount'])

    return render_template("map.html", results=results)

# how do you render_template when you're just refreshing
# the map and not going to different html page?