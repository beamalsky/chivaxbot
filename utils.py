import os
import requests
import json
import logging

from google.cloud import storage
from google.oauth2 import service_account
from cairosvg import svg2png
import numpy as np

# source: https://data.cityofchicago.org/Health-Human-Services/COVID-19-Vaccine-Doses-by-ZIP-Code-Series-Complete/8u6c-48j3
vax_url = "https://data.cityofchicago.org/api/views/553k-3xzc/rows.json?accessType=DOWNLOAD"
# source: https://data.cityofchicago.org/Health-Human-Services/COVID-19-Cases-Tests-and-Deaths-by-ZIP-Code/yhhz-zm2v
deaths_url= "https://data.cityofchicago.org/api/views/yhhz-zm2v/rows.json?accessType=DOWNLOAD"

def get_json(url):
	res = requests.get(url)
	return json.loads(res.text)

def get_colors_dict(values_dict, colorscale, data_type):
	colors_dict = {}
	arr = [value for name, value in values_dict.items() if name in chicago_zips]

	# alert us if there are unexpected zip values
	bad_zips_arr = [name for name, value in values_dict.items() if name not in chicago_zips + ["Unknown", "60666"]]
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

	key_label0_raw = np.percentile(arr, 0, interpolation="nearest")
	key_label1_raw = np.percentile(arr, 20, interpolation="nearest")
	key_label2_raw = np.percentile(arr, 40, interpolation="nearest")
	key_label3_raw = np.percentile(arr, 60, interpolation="nearest")
	key_label4_raw = np.percentile(arr, 80, interpolation="nearest")
	key_label5_raw = np.percentile(arr, 100, interpolation="nearest")

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

def write_svg(svg_path, output_paths, colors_dict):
    # write colors into the SVG file and export
    with open(svg_path, "r") as svg_file:
        svg_string = svg_file.read().format(**colors_dict)
        for output_path in output_paths:
            svg2png(
                bytestring=svg_string,
                write_to=output_path,
                background_color="white",
            )
            print("Saved image file {}".format(output_path))

# gcloud utils
def get_bucket(bucket_name, cred_str):
    json_data = json.loads(cred_str, strict=False)
    json_data['private_key'] = json_data['private_key'].replace('\\n', '\n')
    credentials = service_account.Credentials.from_service_account_info(
        json_data)
    storage_client = storage.Client(
        project=bucket_name, credentials=credentials)
    return storage_client.bucket(bucket_name)

def upload_to_gcloud(bucket, source_file_name):
    destination_name = os.path.basename(source_file_name)
    blob = bucket.blob(destination_name)
    blob.upload_from_filename(source_file_name)
    print(
        "File {} uploaded to {} on Google Cloud.".format(
            source_file_name, destination_name
        )
    )

chicago_zips = [
    "60638",
    "60601",
    "60606",
    "60611",
    # "60666", removed due to population of 0
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