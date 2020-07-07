from geopy import Nominatim
from geopy.exc import GeocoderTimedOut
import pandas
import re

def process_address(locations,geolocator):
    location = None
    i = 0
    while i < len(locations) and location == None:
        try:
            location = geolocator.geocode(locations[i])
        except GeocoderTimedOut:
            location = None
        i+=1
    #print("selected",locations[i-1])
    if location == None:
        #print("Address not found")
        lat = None
        long = None
    else:
        lat = location.latitude
        long = location.longitude
        #print(location.latitude, location.longitude)
    return lat, long
def valid_location(location):
    # Checks if the location is not None and is not just of the form 'x locations'
    invalid_regex = [r'^[0-9]* locations.*$']
    if pandas.notna(location):
        for regex in invalid_regex:
            if re.match(regex, location):
                return False
    else:
        return False
    return True
def main():
    geolocator = Nominatim()

    fields = ["mods_subject_hierarchicalGeographic_citySection","mods_subject_hierarchicalGeographic_city",
              "mods_subject_hierarchicalGeographic_province","mods_subject_hierarchicalGeographic_country","mods_subject_hierarchicalGeographic_continent"]
    io = pandas.read_excel("SpillerPhase1_2_3.xlsx", index_col=None, header=0, sep=",")
    targetColumn = "mods_subject_cartographics"
    outputDict = {targetColumn: ["address"]}
    length = len(io[fields[0]].values)
    # Miss the first row because the first row are the names
    for i in range(1,length):
        all_locations = []
        for field in fields:
            if (valid_location(io[field][i])):
                all_locations.append(io[field].values[i])
        lat, long = process_address(all_locations, geolocator)
        outputDict[targetColumn].append(str(lat)+" "+str(long))
    io.update(outputDict)
    io.to_csv('coordOutput.csv')

if __name__ == '__main__':
  main()
