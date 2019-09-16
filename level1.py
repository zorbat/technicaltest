import json
from datetime import datetime

# date format in data.json
date_format = "%Y-%m-%d"

# list of the rentals
rentals = []

# find the car corresponding to the rental
def find_car(rental):
    return [car for car in data['cars'] if car['id'] == rental['car_id']][0]

# compute the number of days of a rental
def number_of_days(rental):
    return (datetime.strptime(rental['end_date'], date_format) - datetime.strptime(rental['start_date'], date_format)).days + 1

# compute the price of a rental
def compute_price(rental):
    car = find_car(rental)
    rental_days = number_of_days(rental)

    return int(rental_days*car['price_per_day']+rental['distance']*car['price_per_km'])

# open data.json
with open('data.json') as data_file:
    data = json.load(data_file)

# for each rental, compute the price and put it in the list of rentals
for rental in data['rentals']:
    rentals.append({'id': rental['id'], 'price': compute_price(rental)})

# write result.json
with open('result.json', 'w') as outfile:
    json.dump({'rentals': rentals}, outfile, indent=2)
