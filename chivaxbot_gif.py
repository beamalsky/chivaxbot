import os
import pytz
import glob

from datetime import date, datetime, timedelta
from PIL import Image

png_input_paths = os.path.join(os.getcwd(), "exports", "gif", "vax-*.png")
now = datetime.now(pytz.timezone('America/Chicago'))
gif_output_path = os.path.join(
	os.getcwd(),
	"exports",
	"gif",
	"gif-{}.gif".format(now.strftime("%Y-%m-%d-%H%M"))
)

def get_gif_tweet():
	# generate still images with alphabetical names
  vax_res_json = get_json(vax_url)
	deaths_res_json = get_json(deaths_url)

	# turn them into a gif
	# https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#gif
	img, *imgs = [Image.open(f) for f in sorted(glob.glob(png_input_paths))]
	img.save(
		fp=gif_output_path,
  	format='GIF',
		append_images=imgs,
		save_all=True,
		duration=200,
  	loop=0
  )

	# tweet them out
	return {
		"tweet_text": tweet_text,
		"gif_path": deaths_output_path,
		"alt_text": alt_text,
	}