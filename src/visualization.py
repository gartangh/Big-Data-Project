from collections import defaultdict

import pygal


def visualize(title: str, series: defaultdict, filename: str, per_continent: bool) -> None:
	if per_continent:
		world = pygal.maps.world.SupranationalWorld()
	else:
		world = pygal.maps.world.World()

	world.title = title
	for s in series.items():
		world.add(*s)
	world.render_to_file(f'images/{filename}.svg')
