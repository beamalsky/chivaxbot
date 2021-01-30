import os
import requests
import csv
import json
import pytz
import logging

from cairosvg import svg2png
from datetime import date, datetime, timedelta
import numpy as np

# source: https://data.cityofchicago.org/Health-Human-Services/COVID-19-Vaccine-Doses-by-ZIP-Code-Series-Complete/8u6c-48j3
vax_url = "https://data.cityofchicago.org/api/views/553k-3xzc/rows.json?accessType=DOWNLOAD"
vax_svg_path = os.path.join(os.getcwd(), "data", "zipcodes-vax.svg")

# source: https://data.cityofchicago.org/Health-Human-Services/COVID-19-Cases-Tests-and-Deaths-by-ZIP-Code/yhhz-zm2v
deaths_url= "https://data.cityofchicago.org/api/views/yhhz-zm2v/rows.json?accessType=DOWNLOAD"
deaths_svg_path = os.path.join(os.getcwd(), "data", "zipcodes-deaths.svg")

vax_colorscale = ["#feebe2", "#fbb4b9", "#f768a1", "#c51b8a", "#7a0177"]
deaths_colorscale =  ["#feebe2", "#f3cea3", '#f3b875', '#C83302', '#992702']

now = datetime.now(pytz.timezone('America/Chicago'))
yesterday = (now - timedelta(days = 1))
vax_output_path = os.path.join(os.getcwd(), "exports", "vax-{}.png".format(
    now.strftime("%Y-%m-%d-%H%M")
))
deaths_output_path = os.path.join(os.getcwd(), "exports", "deaths-{}.png".format(
    now.strftime("%Y-%m-%d-%H%M")
))

chicago_zips = [
    "60638",
    "60601",
    "60606",
    "60611",
    "60666",
    "60645",
    "60625",
    "60640",
    "60626",
    "60657",
    "60615",
    "60621",
    "60651",
    "60707",
    "60631",
    "60602",
    "60607",
    "60630",
    "60641",
    "60622",
    "60636",
    "60610",
    "60659",
    "60614",
    "60644",
    "60603",
    "60634",
    "60637",
    "60649",
    "60618",
    "60623",
    "60647",
    "60629",
    "60613",
    "60660",
    "60654",
    "60608",
    "60642",
    "60604",
    "60653",
    "60619",
    "60655",
    "60617",
    "60633",
    "60612",
    "60646",
    "60643",
    "60628",
    "60661",
    "60624",
    "60609",
    "60827",
    "60639",
    "60632",
    "60656",
    "60620",
    "60605",
    "60652",
    "60616"
]

def get_tweet():
    vax_res = requests.get(vax_url)
    vax_res_json = json.loads(vax_res.text)

    deaths_res = requests.get(deaths_url)
    deaths_res_json = json.loads(deaths_res.text)

    # loop over city data and return a dictionary of zipcodes and their vax rates
    # also, a sum of all vaccinations
    vax_perc = {}
    vax_sum = 0
    population_sum = 0
    max_date = max([datetime.strptime(i[9], '%Y-%m-%dT00:00:00') for i in vax_res_json["data"]])
    for row in vax_res_json["data"]:
        # we only want dose cumulatives from the latest date
        # res date should be in the format 2021-01-18T00:00:00
        if max_date == datetime.strptime(row[9], '%Y-%m-%dT00:00:00'):
            vax_perc[row[8]] = float(row[17])
            vax_sum += int(row[16])
            population_sum += int(row[18])

    deaths_perc = {}
    deaths_sum = 0
    max_week = max([int(i[9]) for i in deaths_res_json["data"]])
    for row in deaths_res_json["data"]:
        if max_week == int(row[9]):
            # take "death rate per 100,000 population through the week"
            deaths_perc[row[8]] = float(row[25])
            deaths_sum += int(row[23])

    # then, create a dictionary of zip codes and colors
    vax_colors = get_colors_dict(vax_perc, vax_colorscale, "vax")
    deaths_colors = get_colors_dict(deaths_perc, deaths_colorscale, "deaths")

    write_svg(vax_svg_path, vax_output_path, vax_colors)
    write_svg(deaths_svg_path, deaths_output_path, deaths_colors)

    percent_vaccinated = vax_sum / population_sum * 100
    tweet_text = "As of {date}, Chicago is reporting {vaccinations} people fully vaccinated: {percent}% of the population.\n\nWho is dying:           Who is vaccinated:".format(
        date=now.strftime("%B %d, %Y"), # January 26, 2021
        vaccinations=f'{vax_sum:,}',
        percent=round(percent_vaccinated, 1),
    )

    alt_text = '''
    Two maps of Chicago, side by side. The map on the left shows COVID-19 deaths
    per capita by ZIP code. The map on the right shows completed COVID-19
    vaccination per capita by ZIP code. The maps reveal a disconnect between
    where residents are getting vaccinated and where COVID-19 deaths are
    concentrated.
    '''

    return {
        "tweet_text": tweet_text,
        "deaths_map_path": deaths_output_path,
        "vax_map_path": vax_output_path,
        "alt_text": alt_text
    }


def get_colors_dict(values_dict, colorscale, data_type):
    colors_dict = {}
    arr = [value for name, value in values_dict.items() if name in chicago_zips]

    # alert us if there are unexpected zip values
    bad_zips_arr = [name for name, value in values_dict.items() if name not in chicago_zips and name != "Unknown"]
    if len(bad_zips_arr) > 0:
        logging.error("Unexpected zip values for {data_type} data: {bad_zips}".format(
            data_type=data_type,
            bad_zips=", ".join(bad_zips_arr)),
        )
        
    colors_dict["key_color1"] = colorscale[0]
    colors_dict["key_color2"] = colorscale[1]
    colors_dict["key_color3"] = colorscale[2]
    colors_dict["key_color4"] = colorscale[3]
    colors_dict["key_color5"] = colorscale[4]

    key_label0_raw = np.percentile(arr, 0)
    key_label1_raw = np.percentile(arr, 20)
    key_label2_raw = np.percentile(arr, 40)
    key_label3_raw = np.percentile(arr, 60)
    key_label4_raw = np.percentile(arr, 80)
    key_label5_raw = np.percentile(arr, 100)

    if data_type == "deaths":
        colors_dict["key_label0"] = round(key_label0_raw, 1)
        colors_dict["key_label1"] = round(key_label1_raw, 1)
        colors_dict["key_label2"] = round(key_label2_raw, 1)
        colors_dict["key_label3"] = round(key_label3_raw, 1)
        colors_dict["key_label4"] = round(key_label4_raw, 1)
        colors_dict["key_label5"] = round(key_label5_raw, 1)
    elif data_type == "vax":
        colors_dict["key_label0"] = "{}%".format(round(key_label0_raw * 100, 1))
        colors_dict["key_label1"] = "{}%".format(round(key_label1_raw * 100, 1))
        colors_dict["key_label2"] = "{}%".format(round(key_label2_raw * 100, 1))
        colors_dict["key_label3"] = "{}%".format(round(key_label3_raw * 100, 1))
        colors_dict["key_label4"] = "{}%".format(round(key_label4_raw * 100, 1))
        colors_dict["key_label5"] = "{}%".format(round(key_label5_raw * 100, 1))
    else:
        raise Exception("Unexpected key passed to function. Choose 'vax' or 'deaths'")

    for name, value in values_dict.items():
        # prepend "zip" to make these names less confusing
        # when they appear in the SVG
        svg_name = "zip{}".format(name)

        # divide results into 5 even percentiles
        if (value < key_label1_raw):
            colors_dict[svg_name] = colors_dict["key_color1"]
        elif (value < key_label2_raw):
            colors_dict[svg_name] = colors_dict["key_color2"]
        elif (value < key_label3_raw):
            colors_dict[svg_name] = colors_dict["key_color3"]
        elif (value < key_label4_raw):
            colors_dict[svg_name] = colors_dict["key_color4"]
        elif (value <= key_label5_raw):
            colors_dict[svg_name] = colors_dict["key_color5"]
        else:
            colors_dict[svg_name] = "white"

    return colors_dict


def write_svg(svg_path, output_path, colors_dict):
    # write colors into the SVG file and export
    with open(svg_path, "r") as svg_file:
        svg_string = svg_file.read().format(**colors_dict)
        svg2png(
            bytestring=svg_string,
            write_to=output_path,
            background_color="white",
        )
