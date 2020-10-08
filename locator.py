# !IMPORTANT
# No heavy uses (an absolute maximum of 1 request per second).
# Provide a valid HTTP Referer or User-Agent identifying the application (stock User-Agents as set by http libraries will not do).
# Clearly display attribution as suitable for your medium.
# Data is provided under the ODbL license which requires to share alike (although small extractions are likely to be covered by fair usage / fair dealing).

from global_variables import *
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time
from database import *

DELAY = 1  # Measured in seconds
lastGeocode = 0

geolocator = Nominatim(user_agent="listedhere_webscraper")

class Location:
    def __init__(self, location, lat, long):
        self.location = location
        self.lat = lat
        self.long = long

def lookupLocation(location):
    import locator

    print("\nFINDING...")
    fetched = getFromDatabase("locations", Cell("location", location))
    print(_getWaitTime())

    if (len(fetched) == 0):
        print("not found")
        time.sleep(_getWaitTime())
        country ="Uk"
        fetched = geolocator.geocode(location + ',' + country)
        locator.lastGeocode = time.time()
        if fetched != None:
            sendInsertQuery("locations", [Cell("location", location), Cell("latitude", fetched.latitude), Cell("longitude", fetched.longitude)])
            return Location(location, fetched.latitude, fetched.longitude)
        else:
            return Location(location, None, None)

    return Location(location, fetched[0][1], fetched[0][2])

# Returns the exact amount of time that must be waited before I can use the Geolocator again
def _getWaitTime():
    waitTime = DELAY - (time.time() - lastGeocode)
    return max(min(waitTime, 1), 0)