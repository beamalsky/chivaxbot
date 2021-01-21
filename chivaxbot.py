import os
import requests
import csv
import json
import pytz

from cairosvg import svg2png
from datetime import date, datetime, timedelta
import numpy as np 

vax_url = "https://data.cityofchicago.org/api/views/553k-3xzc/rows.json?accessType=DOWNLOAD"
deaths_url= "https://data.cityofchicago.org/api/views/yhhz-zm2v/rows.json?accessType=DOWNLOAD"
zip_svg_path = os.path.join(os.getcwd(), "data", "zipcodes.svg")

vax_colorscale = ["#feebe2", "#fbb4b9", "#f768a1", "#c51b8a", "#7a0177"]
deaths_colorscale = ["#feebe2", "#fbb4b9", "#f768a1", "#c51b8a", "#7a0177"]
now = datetime.now(pytz.timezone('America/Chicago'))
yesterday = (now - timedelta(days = 1))

vax_output_path = os.path.join(os.getcwd(), "exports", "vax-{}.png".format(
    now.strftime("%Y-%m-%d-%H%M")
))
deaths_output_path = os.path.join(os.getcwd(), "exports", "deaths-{}.png".format(
    now.strftime("%Y-%m-%d-%H%M")
))

def get_tweet():
    vax_res = requests.get(vax_url)
    vax_res_json = json.loads(vax_res.text)

    deaths_res = requests.get(deaths_url)
    deaths_res_json = json.loads(deaths_res.text)

    # loop over city data and return a dictionary of zipcodes and their vax rates
    # also, a sum of all vaccinations
    vax_perc = {}
    vax_sum = 0
    max_date = max([datetime.strptime(i[9], '%Y-%m-%dT00:00:00') for i in vax_res_json["data"]])
    for row in vax_res_json["data"]:
        # we only want dose cumulatives from the latest date
        # res date should be in the format 2021-01-18T00:00:00
        if max_date == datetime.strptime(row[9], '%Y-%m-%dT00:00:00'):
            vax_perc[row[8]] = float(row[17])
            vax_sum += int(row[16])

    deaths_perc = {}
    deaths_sum = 0
    max_week = max([int(i[9]) for i in deaths_res_json["data"]])
    for row in deaths_res_json["data"]:
        if max_week == int(row[9]):
            # take "death rate per 100,000 population through the week"
            deaths_perc[row[8]] = float(row[25])
            deaths_sum += int(row[23])

    # then, create a dictionary of zip codes and colors
    vax_colors = get_colors_dict(vax_perc, vax_colorscale)
    deaths_colors = get_colors_dict(deaths_perc, deaths_colorscale)

    write_svg(vax_output_path, vax_colors)
    write_svg(deaths_output_path, deaths_colors)

    tweet_text = "Chicago is currently reporting {vaccinations} vaccinations and {deaths} total deaths from Covid-19.\n\nWho is dying:               Who is vaccinated:".format(
        vaccinations=f'{vax_sum:,}',
        deaths=f'{deaths_sum:,}',
    )
    return {
        "tweet_text": tweet_text,
        "deaths_map_path": deaths_output_path,
        "vax_map_path": vax_output_path,
    }


def get_colors_dict(values_dict, colorscale):
    colors_dict = {}
    arr = list(values_dict.values())
    for name, value in values_dict.items():
        # prepend "zip" to make these names less confusing
        # when they appear in the SVG
        svg_name = "zip{}".format(name)

        # divide results into 5 even quantiles
        if (value < np.quantile(arr, .20)):
            colors_dict[svg_name] = colorscale[0]
        elif (value < np.quantile(arr, .40)):
            colors_dict[svg_name] = colorscale[1]
        elif (value < np.quantile(arr, .60)):
            colors_dict[svg_name] = colorscale[2]
        elif (value < np.quantile(arr, .80)):
            colors_dict[svg_name] = colorscale[3]
        elif (value <= np.quantile(arr, 1)):
            colors_dict[svg_name] = colorscale[4]
        else:
            colors_dict[svg_name] = "white"

    return colors_dict


def write_svg(output_path, colors_dict):
    # write colors into the SVG file and export
    with open(zip_svg_path, "r") as svg_file:
        svg_string = svg_file.read().format(**colors_dict)
        svg2png(
            bytestring=svg_string,
            write_to=output_path,
            background_color="white",
        )