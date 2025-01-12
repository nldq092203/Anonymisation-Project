import random
import csv
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from models.Adult import Adult
from models.Child import Child
from models.Older import Older
from osm_integration import OSMManager


class Survey:
    def __init__(self, city_name, radius, number_of_people, start_date, end_date):
        """
        Initialize the Survey.
        :param city_name: Name of the city where the survey is conducted.
        :param radius: Radius in meters of the survey zone.
        :param number_of_people: Number of people to track.
        :param start_date: Start date of the survey period (datetime object).
        :param end_date: End date of the survey period (datetime object).
        """
        self.city_name = city_name
        self.radius = radius
        self.number_of_people = number_of_people
        self.start_date = start_date
        self.end_date = end_date

        # Get the center point of the city
        self.center_point = self._get_city_center()

        # Initialize OSMManager
        self.osm_manager = OSMManager(self.center_point, radius, network_type="drive")

        # Generate people for the survey
        self.people = self._generate_people()

    def _get_city_center(self):
        """
        Fetch the center point of the city using geocoding.
        :return: Tuple (latitude, longitude) representing the city center.
        """
        try:
            geolocator = Nominatim(user_agent="geo_data_generator")
            location = geolocator.geocode(self.city_name)
            
            if location:
                print(f"Center point of {self.city_name}: ({location.latitude}, {location.longitude})")
                return (location.latitude, location.longitude)
            else:
                raise ValueError(f"City '{self.city_name}' not found.")
        except Exception as e:
            print(f"Error fetching center point for city '{self.city_name}': {e}")
            return (0.0, 0.0)  # Default to (0,0) if geocoding fails

    def _generate_people(self):
        """
        Generate a list of random people (children, adults, older individuals) based on realistic ratios.
        :return: List of `Person` instances (Child, Adult, Older).
        """
        people = []
        child_ratio = 0.3  # 30% children
        adult_ratio = 0.5  # 50% adults
        older_ratio = 0.2  # 20% older people

        # Calculate the number of each type
        num_children = int(self.number_of_people * child_ratio)
        num_adults = int(self.number_of_people * adult_ratio)
        num_older = self.number_of_people - num_children - num_adults 

        # Generate children
        for i in range(num_children):
            person = Child(
                unique_id=i,
                type="child",
                speed=random.uniform(4.2, 5.5),  # Bus speed: ~15-20 km/h
                osm_manager=self.osm_manager
            )
            people.append(person)

        # Generate adults
        for i in range(num_adults):
            person = Adult(
                unique_id=num_children + i,
                type="adult",
                speed=random.uniform(11.1, 16.7),  # Car speed: ~40-60 km/h
                osm_manager=self.osm_manager
            )
            people.append(person)

        # Generate older individuals
        for i in range(num_older):
            person = Older(
                unique_id=num_children + num_adults + i,
                type="older",
                speed=random.uniform(0.8, 1.4),  # Walking speed: ~3-5 km/h
                osm_manager=self.osm_manager
            )
            people.append(person)

        return people
    
    # def simulate(self, records_per_person=100):
    #     """
    #     Simulate random timestamps and record positions of all people.
    #     :param records_per_person: Number of random records per person.
    #     :return: List of dictionaries containing the survey data.
    #     """
    #     survey_data = []

    #     for person in self.people:
    #         for _ in range(records_per_person):
    #             # Generate a random timestamp within the survey period
    #             random_timestamp = self.start_date + timedelta(
    #                 seconds=random.randint(0, int((self.end_date - self.start_date).total_seconds()))
    #             )

    #             # Determine the person's position at the timestamp
    #             position = person.get_position_at_time(random_timestamp)

    #             # Record data
    #             survey_data.append({
    #                 "person_id": person.unique_id,
    #                 "timestamp": random_timestamp.isoformat(),
    #                 "latitude": position[0],
    #                 "longitude": position[1],
    #             })

    #     return survey_data

    def simulate(self, max_records_per_day=5):
        """
        Simulate random daily activity for each person in the survey.

        This method generates realistic movement data for each person over the survey period.
        - Each person is assigned a probability of being active on a given day.
        - If active, a random number of activity records are generated for that day, 
          based on the person's type (adult, child, older).
        - Each record includes a random timestamp within the day and the person's position 
          at that time.

        Parameters:
        - max_records_per_day: Maximum number of activity records a person can generate in a day.

        Returns:
        - survey_data: A list of dictionaries containing the following keys:
            - "person_id": Unique identifier for the person.
            - "timestamp": Randomly generated timestamp (YYYY-MM-DD HH:MM:SS format).
            - "latitude": Latitude of the person's position at the timestamp.
            - "longitude": Longitude of the person's position at the timestamp.
        """
        
        survey_data = []
        current_date = self.start_date

        while current_date <= self.end_date:
            for person in self.people:
                # Set realistic parameters based on person type
                if person.type == "adult":
                    activity_probability = 0.8  # Adults are active most days
                    max_records = random.randint(2, max_records_per_day)  # Higher daily variability
                elif person.type == "child":
                    activity_probability = 0.6  # Children may have fewer active days
                    max_records = random.randint(1, max_records_per_day)
                elif person.type == "older":
                    activity_probability = 0.5  # Older people may be less active
                    max_records = random.randint(1, max_records_per_day // 2)

                # Randomly decide if the person is active on this day
                if random.random() < activity_probability:
                    for _ in range(max_records):
                        # Generate a random time within the current day
                        random_time = current_date + timedelta(
                            seconds=random.randint(0, 86399)  # Random seconds in a day
                        )

                        # Determine the person's position at the timestamp
                        position = person.get_position_at_time(random_time)

                        # Record data
                        survey_data.append({
                            "person_id": person.unique_id,
                            "timestamp": random_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "latitude": position[0],
                            "longitude": position[1],
                        })

            # Move to the next day
            current_date += timedelta(days=1)

        return survey_data
    
    def save_to_csv(self, survey_data, file_path):
        """
        Save survey data to a CSV file.
        :param survey_data: List of dictionaries containing the survey data.
        :param file_path: Path to the CSV file.
        """
        with open(file_path, mode="w", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["person_id", "timestamp", "latitude", "longitude"])
            writer.writeheader()
            writer.writerows(survey_data)

        print(f"Survey data saved to {file_path}")

