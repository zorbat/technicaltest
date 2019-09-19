import json
from datetime import datetime

# date format in data.json
date_format = "%Y-%m-%d"

# list of the rentals
rentals = []
rental_modifications = []

# find the car corresponding to the rental
def find_car(rental):
    return [car for car in data['cars'] if car['id'] == rental['car_id']][0]

# find the rental corresponding to the modification
def find_rental(modification):
    return [rental for rental in data['rentals'] if rental['id'] == modification['rental_id']][0]

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

# compute the actions for each actor
def compute_actions(rental):
    price = compute_price(rental)
    deductible = compute_deductible(rental)
    commission_details = compute_commission(rental)
    commission = sum(commission_details.values())

    driver = {"who": "driver", "type": "debit", "amount": price + deductible}
    owner = {"who": "owner", "type": "credit", "amount": price - commission}
    insurance = {"who": "insurance", "type": "credit", "amount": commission_details['insurance_fee']}
    assistance = {"who": "assistance", "type": "credit", "amount": commission_details['assistance_fee']}
    drivy = {"who": "drivy", "type": "credit", "amount": commission_details['drivy_fee'] + deductible}

    return [driver, owner, insurance, assistance, drivy]

# compute the deltas for each actor
def compute_modifications(modification):
    rental = find_rental(modification)
    initial_actions = compute_actions(rental)

    new_rental = rental

    if 'start_date' in modification:
        new_rental['start_date'] = modification['start_date']
    if 'end_date' in modification:
        new_rental['end_date'] = modification['end_date']
    if 'distance' in modification:
        new_rental['distance'] = modification['distance']

    new_actions = compute_actions(new_rental)

    driver_delta = new_actions[0]['amount'] - initial_actions[0]['amount']
    owner_delta = new_actions[1]['amount'] - initial_actions[1]['amount']
    insurance_delta = new_actions[2]['amount'] - initial_actions[2]['amount']
    assistance_delta = new_actions[3]['amount'] - initial_actions[3]['amount']
    drivy_delta = new_actions[4]['amount'] - initial_actions[4]['amount']

    if driver_delta < 0:
        driver = {"who": "driver", "type": "credit", "amount": abs(driver_delta)}
    else:
        driver = {"who": "driver", "type": "debit", "amount": driver_delta}

    if owner_delta < 0:
        owner = {"who": "owner", "type": "debit", "amount": abs(owner_delta)}
    else:
        owner = {"who": "owner", "type": "credit", "amount": owner_delta}

    if insurance_delta < 0:
        insurance = {"who": "insurance", "type": "debit", "amount": abs(insurance_delta)}
    else:
        insurance = {"who": "insurance", "type": "credit", "amount": insurance_delta}

    if assistance_delta < 0:
        assistance = {"who": "assistance", "type": "debit", "amount": abs(assistance_delta)}
    else:
        assistance = {"who": "assistance", "type": "credit", "amount": assistance_delta}

    if drivy_delta < 0:
        drivy = {"who": "drivy", "type": "debit", "amount": abs(drivy_delta)}
    else:
        drivy = {"who": "drivy", "type": "credit", "amount": drivy_delta}

    return [driver, owner, insurance, assistance, drivy]

# open data.json
with open('data.json') as data_file:
    data = json.load(data_file)

# for each rental, compute the price and put it in the list of rentals
for rental in data['rentals']:
    rentals.append({'id': rental['id'], 'actions': compute_actions(rental)})

# for each modification, compute the deltas
for modification in data['rental_modifications']:
    rental_modifications.append({'id': modification['id'], 'rental_id': modification['rental_id'], 'actions': compute_modifications(modification)})

# write result.json
with open('result.json', 'w') as outfile:
    json.dump({'rental_modifications': rental_modifications}, outfile, indent=2)
