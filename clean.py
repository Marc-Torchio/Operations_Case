import pandas as pd
import numpy as np
import resources


# Creating a high level classification for NPs, CCs, and Scribes for both dfs

def Role_classification(df):
    conditions = [
        df['Positions'].str.contains('NP', na=False),
        df['Positions'].str.contains('CC', na=False),
        df['Positions'].str.contains('Scribe', na=False)
    ]
    # Define corresponding choices
    choices = ['NP', 'CC', 'Scribe']

    # Create a new column based on conditions
    df['Role'] = np.select(conditions, choices, default='Unknown')
    return df


# Function to transform datatime variable into integer to represent avg hours worked each week
def duration_to_hours(duration_str):
    if pd.isna(duration_str):  # Check for NaN
        return float('nan')
    duration = pd.Timedelta(duration_str)
    return round(duration.total_seconds() / 3600)




def clean_shifts(excel_name = resources.excel_file_path):
    # Importing all worksheets
    workers = pd.read_excel(excel_name,sheet_name=0)
    f_shifts = pd.read_excel(excel_name,sheet_name=1)
    u_shifts = pd.read_excel(excel_name,sheet_name=2)

    # Cleaning shift dfs to merge
    f_shifts  = f_shifts.drop(columns=['Shift Start Date', 'Shift End Date'])
    u_shifts = u_shifts.rename(columns={'start_time':'Shift Start Time','end_time': 'Shift End Time'})
    u_shifts['Worker ID'] = 'unfulfilled'

    # Merging dfs 
    shifts = pd.concat([f_shifts,u_shifts]).reset_index(drop=True)

    # Renaming Position Name Col
    shifts = shifts.rename(columns={'Position Name': 'Positions'})

    # Creating a shift length col
    shifts['Shift Length'] = shifts['Shift End Time'] - shifts['Shift Start Time']


    shifts = Role_classification(shifts)
    workers = Role_classification(workers)

    shifts = shifts[['Worker ID', 'Role','Positions', 'Shift Start Time', 'Shift End Time','Shift Length']]
    workers = workers[['Worker ID', 'Role','Schedules', 'Positions', 'Preferred Hours']]

    # Pulling out the total amount of hours worked by each worker last month
    shifts_grouped = shifts.groupby('Worker ID')['Shift Length'].sum()

    # Merging the data into the workers df 
    workers = pd.merge(workers, shifts_grouped, on='Worker ID', how = 'left')

    # Rounding the shift length into (average) weekly hours worked
    workers['Shift Length'] = workers['Shift Length']/4


    # Running funtion on both dfs to create actual hours worked col
    workers['Actual Hours'] = workers['Shift Length'].apply(duration_to_hours)
    shifts['Shift Length'] = shifts['Shift Length'].apply(duration_to_hours)
    
    # Creating an is_fufilled col
    shifts['Is_Fufilled'] = shifts['Worker ID'].apply(lambda x: x != 'unfulfilled')

    # Imputing missing preferred hours with actual hours worked last month
    workers['Preferred Hours'] = workers['Preferred Hours'].fillna(workers['Actual Hours'])
    # Dropping now redundnat col
    workers = workers.drop(columns='Shift Length')

    # Examining the workers who did not work any hours last month 
    workers[workers['Actual Hours'].isna()].reset_index(drop=True)

    # Dropping the workers who did not have preferred Hours and did not have actual hours
    workers = workers[~workers['Preferred Hours'].isna()].reset_index(drop=True)

    # Re-ordering df
    workers = workers[['Worker ID', 'Schedules','Role', 'Positions', 'Preferred Hours','Actual Hours']]

    # Filling NA values with 0 
    workers['Actual Hours'] = workers['Actual Hours'].fillna(0)
    
    return workers, shifts




def Positional_Pivot(shifts, position):
    # Filter shifts by position and convert 'Shift Start Time' to a datetime object
    NP_CA_shifts = shifts[shifts['Positions'] == position].reset_index(drop=True)
    NP_CA_shifts['Shift Start Time'] = pd.to_datetime(NP_CA_shifts['Shift Start Time'])
    NP_CA_shifts.set_index('Shift Start Time', inplace=True)

    # Group by fulfillment status and hour, then aggregate 'Shift Length'
    aggregated_by_hour = NP_CA_shifts.groupby(['Is_Fufilled', NP_CA_shifts.index.hour])['Shift Length'].sum().reset_index()
    aggregated_by_hour.columns = ['Is_Fufilled', 'Hour', 'Shift Length']

    # Pivot the DataFrame to have separate columns for 'Fulfilled' and 'Unfulfilled'
    pivot_df = aggregated_by_hour.pivot_table(index='Hour', columns='Is_Fufilled', values='Shift Length', aggfunc='sum')
    pivot_df.columns = ['Unfulfilled', 'Fulfilled']
    pivot_df = pivot_df.fillna(0)

    # Function to classify shifts into categories
    def classify_shift(hour):
        if 6 <= hour <= 11:
            return 'Morning'
        elif 12 <= hour <= 17:
            return 'Afternoon'
        elif 18 <= hour <= 23:
            return 'Evening'
        else:
            return 'Night'

    # Apply the classification function to create a new column
    pivot_df['Shift Category'] = pivot_df.index.map(classify_shift)

    # Define the desired order
    shift_order = ['Morning', 'Afternoon', 'Evening', 'Night']
    pivot_df['Shift Category'] = pd.Categorical(pivot_df['Shift Category'], categories=shift_order, ordered=True)

    # Group by the new shift categories and sum the values
    grouped_df = pivot_df.groupby('Shift Category').sum()
    
    TOD_pivot = grouped_df
    hour_pivot = pivot_df
    return hour_pivot, TOD_pivot