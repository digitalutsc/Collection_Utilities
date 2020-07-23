import geopy, sys
import pandas
from geopy.geocoders import Nominatim, GoogleV3
# versions used: geopy 1.10.0, pandas 0.16.2, python 2.7.8

inputfile=str(sys.argv[1])
namecolumn=str(sys.argv[2])
# your command will look something like 'python2/python3 geocoder-singlecolumn.py census-historic-population-borough.csv Area_Name'

def main():
  io = pandas.read_csv(inputfile, index_col=None, header=0, sep=",")

  def get_latitude(x):
    # print(x)
    if x is None: # if geocoding attempt failed, resulting in Nonetype
      return x
    else:
      return x.latitude
    # how do i assign an int or any value to x if it's none? how do i get the initial input x?
    # could use lambda function here. x is original value in the series type if it's been successfully geocoded.

  def get_longitude(x):
    # print(x)
    if x is None:
      return x
    else:
      return x.longitude

  geolocator = GoogleV3(api_key="apikey", timeout=5)
  # geolocator = Nominatim()
  # get api key for googlev3 at https://developers.google.com/maps/documentation/geocoding/usage-limits or https://console.developers.google.com/
  # uncomment the geolocator you want to use
  # change the timeout value if you get a timeout error, for instance, geolocator = Nominatim(timeout=60)
  # io[namecolumn] is a series or object dtype, you apply action to an entire series not a single value
  geolocate_column = io[namecolumn].apply(geolocator.geocode)
  io['latitude'] = geolocate_column.apply(get_latitude)
  io['longitude'] = geolocate_column.apply(get_longitude)
  print(io['longitude'])
  # print(type(io['latitude']))

  io.to_csv('geocoding-output.csv')

if __name__ == '__main__':
  main()

