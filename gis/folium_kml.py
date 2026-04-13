import folium
from fastkml.kml import KML


def read_kml(fname='ss.kml'):
    kml = KML()
    kml.from_string(open(fname).read())
    points = dict()
    for feature in kml.features:
        for placemark in feature.features():
            if placemark.styleUrl.startswith('#hf'):
                points.update(
                    {
                        placemark.name: (
                            placemark.geometry.y,
                            placemark.geometry.x,
                        )
                    }
                )
    return points


def inline_map(m: folium.Map, width=650, height=500):
    """Takes a folium instance and embed HTML."""
    m._build_map()
    srcdoc = m.HTML.replace('"', '&quot;')
    embed = HTML(
        '<iframe srcdoc="{}" '
        'style="width: {}px; height: {}px; '
        'border: none"></iframe>'.format(srcdoc, width, height)
    )
    return embed


width, height = 650, 500
radars = folium.Map(
    location=[40, -122], zoom_start=5, tiles='OpenStreetMap', width=width, height=height
)

fname = './data/ss.kml'
locations = read_kml(fname)
for name, location in locations.items():
    radars.simple_marker(location=location, popup=name)

inline_map(radars)
