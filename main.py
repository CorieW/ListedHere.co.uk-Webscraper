# -*- coding: UTF-8 -*-

from global_variables import *
import pets4homes_scraper

lastScrapes = []

def _initializeScraping():
    lastScrapes.append(getCurrentTime())
    pets4homes_scraper.webScrapeSite()

    _beginScheduledScraping()

def _beginScheduledScraping():
    print("Scheduled scraping beginning...")
    while (True):
        #if getTimeDifference(getCurrentTime(), lastScrapes[0]).seconds >= 30:
        lastScrapes[0] = getCurrentTime()
        print("webscraping")
        pets4homes_scraper.webScrapeSite()
        print("finished webscraping")

def getTimeDifference(timeA, timeB):
    return timeA - timeB

_initializeScraping()

# TODO
# - The age isn't exactly correct because each month is assumed to be 30 days instead of the days changing depending on the month
# - Need to remove listings that are ancient or respond with an error
# - Need to change the values of the total_listings, demand and average_price columns in the species and breeds tables
# - Remove console logs
#! - It's technically possible that some that should be getting put in the recently created, will be put in recently updated. 
#! This will happen if the listing is created after the new created listings page is checked and moves onto the recently updated listings.

#! Be more human-like and harder to detect
# - Provide some randomness. Don't be too consistent otherwise it'll be easy to see that patterns are very specific.
# - Rotate proxies to send requests from multiple IP addresses
# - Rotate headers to act as different browser agents
# - Use a headless browser so if the reciever tests to see if you're a browser with a javascript file, the javascript file will work and you will be precieved as a client.
# - Don't use cookies unless the bot requires
# - Slow down the bot when listings are less regular
# https://www.scrapehero.com/how-to-prevent-getting-blacklisted-while-scraping/#unique-identifier4