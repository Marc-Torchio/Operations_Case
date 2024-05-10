from faker import Faker
from clean import workers, shifts
from workers import Worker
import random

# Instantiate Faker as fake
fake = Faker()
fake.first_name()

# Instantiate needed DFs
workers_df = workers
shifts_df = shifts
unfufilled_shifts = shifts_df[shifts_df['Worker ID'] == 'unfufilled']
fufilled_shifts = shifts_df[shifts_df['Worker ID'] != 'unfufilled']

# Establish list to hold all workers 
Forward_staff = []


# Iterate through worker df to create Worker object based on each row of data
for index, row in workers_df.iterrows():
    first_name = fake.first_name()
    worker = Worker(first_name, row['Worker ID'], row['Positions'], row['Preferred Hours'])
    Forward_staff.append(worker)


# append all fufilled shifts into each workers shift attribute
for worker in Forward_staff:
    for index, row in fufilled_shifts.iterrows():
        if worker.worker_ID == row['Worker ID']:
            shift = [row['Shift Start Time'], row['Shift End Time']]
            worker.add_shift(shift)


# First Iterate through each row or shift 
for index, row in unfufilled_shifts.iterrows():
    possible_workers = []
    # Second iterate through each worker to compare the matching criteria 
    for worker in Forward_staff:
        if worker.is_free(row['Shift Start Time'], row['Shift End Time']) and \
                        worker.meets_preferred_hours(row['Shift Length']) and \
                        worker.is_qualified(row['Positions']):
            possible_workers.append(worker.worker_ID)
            
    # Conditional to test if there were any matching workers identified
    if possible_workers:
        # Select worker at random from list
        selected_worker = random.choice(possible_workers)
        # Assign selected worker to shift
        unfufilled_shifts.at[index,'Worker ID'] = selected_worker
    else:
        # If not match, set worker ID to 'No Availability'
        unfufilled_shifts.at[index,'Worker ID'] = 'No Availability'