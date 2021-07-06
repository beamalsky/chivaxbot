import os
import pytz
import glob

from datetime import date, datetime, timedelta
from PIL import Image
from utils import vax_url, get_json, get_vax_perc_by_date, get_colors_dict_absolute, write_svg

gif_svg_path = os.path.join(os.getcwd(), "data", "zipcodes-vax-for-gif.svg")

exports_gif_dir = os.path.join(os.getcwd(), "exports", "gif")
png_input_paths = os.path.join(exports_gif_dir, "vax-*.png")
now = datetime.now()
gif_output_path = os.path.join(
	exports_gif_dir,
	"gif-{}.gif".format(now.strftime("%Y-%m-%d-%H%M"))
)

start_date = '2021-01-25'
gif_colorscale = [
    '#a50026',
    '#d73027',
    '#f46d43',
    '#fdae61',
    '#fee08b',
    '#d9ef8b',
    '#a6d96a',
    '#66bd63',
    '#1a9850',
    '#006837'
]

def get_gif_tweet():
	# clear out gif folder (to make local testing easier)
	for f in os.listdir(exports_gif_dir):
		if f != ".gitkeep":
			os.remove(os.path.join(exports_gif_dir, f))

	# generate still images with alphabetical names
	# set starting date and then incremement by 7 until we hit today
	vax_res_json = get_json(vax_url)
	date = datetime.strptime(start_date, '%Y-%m-%d')
	while date <= now:
		vax_perc = get_vax_perc_by_date(vax_res_json, date, save_totals=False)
		vax_colors = get_colors_dict_absolute(vax_perc, gif_colorscale, date)
		output_path = os.path.join(
			os.getcwd(),
		 	"exports",
			"gif",
			"vax-{}.png".format(date.strftime("%Y-%m-%d"))
		)

		write_svg(
			gif_svg_path,
			[output_path],
			vax_colors,
   			dpi=75,
		)
		date += timedelta(7)

	# turn them into a gif
	# https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#gif
 	# copy the last frame to the front so we get it as the gif preview
	img_paths = sorted(glob.glob(png_input_paths))
	img_paths.insert(0, img_paths[-1])
	img, *imgs = [Image.open(f) for f in img_paths]
	img.save(
		fp=gif_output_path,
		format='GIF',
		append_images=imgs,
		save_all=True,
		duration=500,
		loop=0
	)

	# generate the sentence and alt text too
	tweet_text = '''
		Read the latest on Chicago's widening vaccine disparity from @maerunes for @SouthSideWeekly: https://southsideweekly.com/chicagos-vaccine-disparity-widens/
	'''

	alt_text = '''
		The animated gif shows a map of Chicago with vaccination rates for each ZIP code over time. As time passes from late January until today, the north west side pulls ahead of the rest of the city in vaccination rates.
	'''

	return {
		"tweet_text": tweet_text,
		"gif_path": gif_output_path,
		"alt_text": alt_text,
	}