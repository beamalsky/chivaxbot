import os
import csv
import json
import pytz

from datetime import date, datetime, timedelta

from utils import vax_url, deaths_url, get_json, get_vax_perc_by_date, chicago_zips, get_colors_dict, write_svg

vax_svg_path = os.path.join(os.getcwd(), "data", "zipcodes-vax.svg")
deaths_svg_path = os.path.join(os.getcwd(), "data", "zipcodes-deaths.svg")

vax_colorscale = ["#feebe2", "#fbb4b9", "#f768a1", "#c51b8a", "#7a0177"]
deaths_colorscale =  ["#feebe2", "#f3cea3", '#f3b875', '#C83302', '#992702']

now = datetime.now(pytz.timezone('America/Chicago'))
vax_output_path = os.path.join(os.getcwd(), "exports", "vax-{}.png".format(
	now.strftime("%Y-%m-%d-%H%M")
))
vax_output_path_latest = os.path.join(os.getcwd(), "exports", "vax-latest.png")

deaths_output_path = os.path.join(os.getcwd(), "exports", "deaths-{}.png".format(
	now.strftime("%Y-%m-%d-%H%M")
))
deaths_output_path_latest = os.path.join(os.getcwd(), "exports", "deaths-latest.png")

sentence_output_path_latest = os.path.join(os.getcwd(), "exports", "sentence-latest.json")

def get_tweet():
	vax_res_json = get_json(vax_url)
	deaths_res_json = get_json(deaths_url)

	max_date = max([datetime.strptime(i[9], '%Y-%m-%dT00:00:00') for i in vax_res_json["data"]])
	vax_dict = get_vax_perc_by_date(vax_res_json, max_date, save_totals=True)

	deaths_perc = {}
	deaths_sum = 0
	max_week = max([int(i[9]) for i in deaths_res_json["data"]])
	for row in deaths_res_json["data"]:
		if max_week == int(row[9]):
			# take "death rate per 100,000 population through the week"
			deaths_perc[row[8]] = float(row[25])
			deaths_sum += int(row[23])

	as_of = now.strftime("%B %-d, %Y") # January 2, 2021
	vaccinations = f'{vax_dict["vax_sum"]:,}'
	percent_vaccinated = round(vax_dict["vax_sum"] / vax_dict["population_sum"] * 100, 1)
	tweet_text = "As of {date}, Chicago is reporting {vaccinations} people fully vaccinated: {percent}% of the population.\n\nWho is dying:		   Who is vaccinated:".format(
		date=as_of,
		vaccinations=vaccinations,
		percent=percent_vaccinated,
	)

	write_sentence_json(sentence_output_path_latest, {
		"as_of": as_of,
		"vaccinations": vaccinations,
		"percent_vaccinated": percent_vaccinated,
	})

	# then, create a dictionary of zip codes and colors
	vax_colors = get_colors_dict(vax_dict["vax_perc"], vax_colorscale, "vax")
	deaths_colors = get_colors_dict(deaths_perc, deaths_colorscale, "deaths")

	write_svg(
		vax_svg_path,
		[vax_output_path, vax_output_path_latest],
		vax_colors
	)
	write_svg(
		deaths_svg_path,
		[deaths_output_path, deaths_output_path_latest],
		deaths_colors
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
		"alt_text": alt_text,
		"deaths_map_path_latest": deaths_output_path_latest,
		"vax_map_path_latest": vax_output_path_latest,
		"sentence_path_latest": sentence_output_path_latest,
	}

def write_sentence_json(output_path, dict):
	with open(output_path, 'w') as json_file:
		json.dump(dict, json_file)
		print("Saved sentence file {}".format(output_path))