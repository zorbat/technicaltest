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

# compute the deductible component
def compute_deductible(rental):
    deductible_component = 0

    if rental['deductible_reduction']:
        deductible_component += number_of_days(rental) * 400

    return deductible_component

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

# compute the details of the commission
def compute_commission(rental):
    price = compute_price(rental)

    commission = 0.3*price

    insurance_fee = 0.5*commission
    assistance_fee = 100*number_of_days(rental)
    drivy_fee = commission - (insurance_fee+assistance_fee)

    return {'insurance_fee': int(insurance_fee), 'assistance_fee': int(assistance_fee), 'drivy_fee': int(drivy_fee)}

# open data.json
with open('data.json') as data_file:
    data = json.load(data_file)

# for each rental, compute the price and put it in the list of rentals
for rental in data['rentals']:
    rentals.append({'id': rental['id'], 'price': compute_price(rental), 'options': {'deductible_reduction': compute_deductible(rental)}, 'commission': compute_commission(rental)})

# write result.json
with open('result.json', 'w') as outfile:
    json.dump({'rentals': rentals}, outfile, indent=2)
