from clean import duration_to_hours

class Worker:
    def __init__(self, name, worker_ID, positions, preferred_hours):
        """
        Initialize a Worker object.

        Args:
            name (str): Name of the worker.
            worker_ID (str/int): Unique identifier for the worker.
            positions (str): Position(s) the worker holds.
            preferred_hours (int/float): Preferred number of hours the worker wants to work per week.
        """
        self.name = name
        self.worker_ID = worker_ID
        self.positions = positions
        self.preferred_hours = preferred_hours
        self.total_hours_pref = preferred_hours * 4
        self.shifts = []  # List to hold all shifts picked up throughout the month



    def meets_preferred_hours(self, shift_length):
        """Check if adding the shift would exceed the worker's preferred hours."""
        return (self.total_hours_pref - shift_length) > 0



    def is_free(self, start, end):
        """
        Check if the worker is free during a specific time range.

        Args:
            start (datetime.time): Start time to check.
            end (datetime.time): End time to check.

        Returns:
            bool: True if the worker is free, False otherwise.
        """
        for shift in self.shifts:
            shift_start, shift_end = shift

            # Check for overlap
            if not ((end <= shift_start) or (start >= shift_end)):
                return False  # Overlapping shift found
        return True  # No overlap found



    def is_qualified(self, shift_name):
        """
        Checks to see if the worker is qualified for the specified shift.

        Args:
            shift_name (str): Name of the shift to check.

        Returns:
            bool: True if the worker is qualified, False otherwise.
        """
        return shift_name in self.positions
    


    def add_shift(self, shift, shift_length):
        """
        Add a shift to the list of shifts for this worker.
        Shifts should be input as a list object: [Start date.datetime, end date.datetime]
        
        Args:
            shift (list): Shift details to be added to the worker's list of shifts.
        """
        self.shifts.append(shift)
        self.total_hours_pref -= shift_length
        
        

    def get_shifts(self):
        """
        Return the list of shifts picked up by the worker.

        Returns:
            list: List of shifts picked up by the worker.
        """
        return self.shifts
    
    
    
    def __str__(self):
        """
        String representation of the Worker object.

        Returns:
            str: A string representing the worker's information.
        """
        return f"Worker(Name: {self.name}, ID: {self.worker_ID}, Positions: {self.positions}, Preferred Hours: {self.preferred_hours}, Shifts: {len(self.shifts)})"


