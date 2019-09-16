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

    price_per_day = car['price_per_day']

    # compute the distance component of the price
    distance_component = rental['distance']*car['price_per_km']

    # compute the time component of the price
    if rental_days > 10:
        time_component = price_per_day + 3*(0.9*price_per_day) + 6*(0.7*price_per_day) + (rental_days-10)*(0.5*price_per_day)
    elif rental_days > 4:
        time_component = price_per_day + 3*(0.9*price_per_day) + (rental_days-4)*(0.7*price_per_day)
    elif rental_days > 1:
        time_component = price_per_day + (rental_days-1)*(0.9*price_per_day)
    else:
        time_component = price_per_day

    return int(time_component+distance_component)


# open data.json
with open('data.json') as data_file:
    data = json.load(data_file)

# for each rental, compute the price and put it in the list of rentals
for rental in data['rentals']:
    rentals.append({'id': rental['id'], 'price': compute_price(rental)})

# write result.json
with open('result.json', 'w') as outfile:
    json.dump({'rentals': rentals}, outfile, indent=2)
