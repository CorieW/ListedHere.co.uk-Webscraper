from global_variables import *
from locator import lookupLocation
import requests
from datetime import timedelta
from bs4 import BeautifulSoup
from csv import writer
from database import *

def webScrapeSite():
    _scrapeNewlyCreated()
    _scrapeNewlyUpdated()

def _scrapeNewlyCreated():
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

    response = requests.get(
        "https://www.pets4homes.co.uk/search/?results=20&sort=creatednew",
        headers=hdr
    )
    
    listings_page = BeautifulSoup(response.text, "html.parser")

    listing_count = listings_page.findAll(class_="headline").__len__()

    for i in range(listing_count):
        page_url = listings_page.select(".headline")[i].a["href"]
        
        try:
            if not containedInDatabase('pets', Cell('url', page_url)):
                listing = listings_page.select(".profilelisting")[i]
                data = _getData(listing, True)    
                sendInsertQuery("pets", data)
        except Exception as ex:
            # Writes the error into the errors.txt file.
            f = open(dir_path + "/errors.txt", "a")
            f.write("Error has occurred in the pets4homes-scraper script.\nURL Handling: %s \nError: %s\n\n" % (page_url, str(ex)))
            f.close()

def _scrapeNewlyUpdated():
    response = requests.get(
        "https://www.pets4homes.co.uk/search/?results=20&sort=datenew"
    )

    listings_page = BeautifulSoup(response.text, "html.parser")

    listing_count = listings_page.findAll(class_="headline").__len__()

    for i in range(listing_count):
        page_url = listings_page.select(".headline")[i].a["href"]
        
        try:
            updated = containedInDatabase('pets', Cell('url', page_url)) # Is there currently a listing in the database matching this page_url, make sure to overwrite the data contained as this is an update.
            listing = listings_page.select(".profilelisting")[i]
            data = _getData(listing, False)
            if not updated:  # Adding new row and not updating existing one
                sendInsertQuery("pets", data)
            else:
                sendUpdateQuery("pets", Cell("url", page_url), data)
        except Exception as ex:
            # Writes the error into the errors.txt file.
            f = open(dir_path + "/errors.txt", "a")
            f.write("Error has occurred in the pets4homes-scraper script.\nURL Handling: %s \nError: %s\n\n" % (page_url, str(ex)))
            f.close()

#Functions

def _getData(listing, newlyCreated):
    cells = []

    page_url = listing.select(".headline")[0].a["href"]
    page_url_cell = Cell("url", page_url)
    cells.append(page_url_cell)

    title_cell = Cell("title", (
        listing.select(".headline")[0]
        .get_text()
        .replace("\n", "")
        .replace("\"", "\\\"")
    ))
    cells.append(title_cell)

    species_cell = Cell("species", (
        listing.select(".categories")[0]
        .select("a")[1]
        .get_text()
        .replace("\n", "")
        .lstrip()
        .rstrip()
    ))
    cells.append(species_cell)
    if not containedInDatabase("species", Cell("species_name", species_cell.value)): # Stores the name of the species in the species table if the species hasn't already been listed
        sendInsertQuery("species", [Cell("species_name", species_cell.value)])

    breed_cell = Cell("breed", (
        listing.select(".categories")[0]
        .select("a")[2]
        .get_text()
        .replace("\n", "")
        .lstrip()
        .rstrip()
    ))
    cells.append(breed_cell)
    if not containedInDatabase('breeds', Cell("breed_name", breed_cell.value)): # Stores the name of the breed in the breeds table if the breed hasn't already been listed
        sendInsertQuery("breeds", [Cell("breed_name", breed_cell.value), Cell("species", species_cell.value)])

    advert_type_cell = Cell("advert_type", (
        listing.select(".categories")[0]
        .select("a")[0]
        .get_text()
        .replace("\n", "")
        .lstrip()
        .rstrip()
    ))
    cells.append(advert_type_cell)

    location = lookupLocation(listing.select(".location")[0].get_text().replace("\n", ""))
    if location.lat == None:
        location = lookupLocation(location.location.split(", ")[0])  # Enlargens the possible area to the city/town since it can't find the inner location
        
    location_cell = Cell("location", location.location)
    cells.append(location_cell)

    latitude_cell = Cell("latitude", location.lat)
    cells.append(latitude_cell)

    longitude_cell = Cell("longitude", location.long)
    cells.append(longitude_cell)

    price_cell = Cell("price", (
        listing.select(".listingprice")[0]
        .get_text()
        .replace("\n", "")
        .replace("£", "")
    ))
    price_cell.value = _getPriceInteger(price_cell.value)
    cells.append(price_cell)

    time_updated_cell = Cell("time_updated", (
        listing.select(".profile-listing-updated")[0]
        .get_text()
        .replace("\n", "")
        .lstrip()
    ))
    time_updated_cell.value = _getPostedDateTime(time_updated_cell.value)
    cells.append(time_updated_cell)

    if newlyCreated:
        cells.append(Cell('time_created', time_updated_cell.value)) # Adding time_created cell

    image_url_cell = Cell("image_url", DEFAULT_IMAGE) # Sets to default image incase it doesn't have an image
    if len(listing.select(".imageinner")) != 0: # Does the image exist?
        image_url_cell.value = (
            listing.select(".imageinner")[0]
            .select("a")[0]
            .select("img")[0]["src"]
        )
    cells.append(image_url_cell)

    council_licensed_cell = Cell("council_licensed", "")
    dob_cell = Cell("dob", None)
    kc_registered_cell = Cell("kc_registered", "")

    response = requests.get(page_url)
    listingPage = BeautifulSoup(response.text, "html.parser") #? What's this, consider changing variable name

    params = len(listingPage.select(".param-label"))
    for i in range(params):
        param = listingPage.select(".param-label")[i]
        if "Council Licensed" in param.get_text():
            council_licensed_cell.value = param.next_sibling.get_text().split(" ")[0]
            council_licensed_cell.value = _isCouncilLicensed(council_licensed_cell.value)
        elif "Current Age" in param.get_text():
            dob_cell.value = param.next_sibling.get_text()
            dob_cell.value = _getDOBAsDate(dob_cell.value)
        elif "KC Registered" in param.get_text():
            kc_registered_cell.value = param.next_sibling.get_text().split(" ")[0]
            kc_registered_cell.value = _isKCRegistered(kc_registered_cell.value)
    cells.append(council_licensed_cell)
    if dob_cell.value != "":
        cells.append(dob_cell)
    cells.append(kc_registered_cell)

    return cells

def _getPriceInteger(price):
    intPrice = ""

    price = price.split(",")
    for i in range(len(price)):
        intPrice = intPrice + price[i]
    return int(intPrice)

def _getPostedDateTime(time_updated):
    time_updated = time_updated.split(' ')
    if ("second" in time_updated[1]):
        time_updated = getCurrentTime() - timedelta(seconds=int(time_updated[0]))
    elif ("minute" in time_updated[1]):
        time_updated = getCurrentTime() - timedelta(minutes=int(time_updated[0]))
    elif ("hour" in time_updated[1]):
        time_updated = getCurrentTime() - timedelta(hours=int(time_updated[0]))
    elif ("day" in time_updated[1]):
        time_updated = getCurrentTime() - timedelta(days=int(time_updated[0]))
    else: # now
        time_updated = getCurrentTime()
    
    return time_updated

def _isCouncilLicensed(council_licensed):
    if ("Yes" in council_licensed):
        return 1
    else:
        return 0

def _getDOBAsDate(age):
    days_age = 0
    due = False

    age = age.split(", ")
    for i in range(len(age)):
        if ("Due" in age[0]):
            age[0] = age[0].strip('Due in ') # I do this because I get always look at [0] for adding to days_age. Without this i'd get an invalid literal error
            days_age = 0 
            due = True

        if ("Today" in age[i]):
            days_age = 1 # Animals born tpday are set to 1 day old.
        elif ("day" in age[i]):
            days_age = days_age + int(age[i].split(" ")[0])
        elif ("week" in age[i]):
            days_age = days_age + (7 * int(age[i].split(" ")[0]))
        elif ("month" in age[i]):
            days_age = days_age + (30 * int(age[i].split(" ")[0]))
        elif ("year" in age[i]):
            days_age = days_age + (365 * int(age[i].split(" ")[0]))

    if(not due):
        return getCurrentTime() - timedelta(days=days_age)
    else: # Will be ready in the future hence the +
        return getCurrentTime() + timedelta(days=days_age)

def _isKCRegistered(kc_registered):
    if ("Yes" in kc_registered):
        return 1
    else:
        return 0
