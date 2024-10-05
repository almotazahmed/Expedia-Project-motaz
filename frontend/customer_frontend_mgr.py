from typing import Union

from backend.customer_backend_mgr import *
# from backend.api.payment import *
from backend.exceptions import InvalidInputError

class FrontEndManager:
    def run(self):
        print("Welcome to the Flight Reservation System!")
        self.base_ui()

    def base_ui(self):

        customer1: CustomerAccount = CustomerAccount('1304', 'user', '1234')


        while True:
            choice = self.get_user_choice("System Access: \n1) Login\n2) Sign up\nEnter your choice (from 1 to 2): ", 2)

            if choice == 1:
                username = input("Enter Username: ")
                password = input("Enter Password: ")
                pass_auth: PasswordAuthenticator = PasswordAuthenticator()
                costumer_acc_mgr: CustomerAccountManager = CustomerAccountManager(pass_auth)

                if costumer_acc_mgr.authenticate_customer(username, password, customer1):
                    self.customer_processing_page(customer1)

                else:
                    print("Invalid Username or Password. Please try again.")

            elif choice == 2:
                print("Sign up is not yet supported, please wait.")

            else:
                print("Invalid Input, please enter a number (from 1 to 2).")

    def customer_processing_page(self, customer: CustomerAccount):
        while True:
            choice = self.get_user_choice(f"Welcome {customer.get_username().capitalize()} | Customer:\n1) View Profile \n2) Make itinerary\n3) List my itineraries\n4) Logout\nEnter your choice (from 1 to 4): ", 4)

            if choice == 1:
                profile_display: Profile = Profile(customer)
                profile_display.view_profile()

            elif choice == 2:
                itinerary: Itinerary = Itinerary()
                customer_itinerary_mgr: CustomerItineraryManager = CustomerItineraryManager()
                itinerary_mgr: ItineraryManager = ItineraryManager(itinerary)
                self.make_reservations(itinerary_mgr, customer.get_customer_id())
                customer_itinerary_mgr.add_itinerary(customer, itinerary)

            elif choice == 3:
                itinerary_mgr: CustomerItineraryManager = CustomerItineraryManager()
                itinerary_mgr.display_customer_itineraries(customer.itineraries)

            elif choice == 4:
                exit()

            else:
                print("Invalid input, please enter a number (1, 2, 3 or 4).")

    def make_reservations(self, itinerary_mgr: ItineraryManager, customer_id: str):
        while True:
            choice = self.get_user_choice(f"Create your itinerary:\n1) Add flight\n2) Add Hotel\n3) Reserve itinerary\n4) Cancel itinerary\nEnter your choice (from 1 to 4): ", 4)

            if choice == 1:
                selected_api, selected_flight = self.select_flight()
                flight_reservation: Reservation = FlightReservation(customer_id, selected_api, selected_flight, [])
                itinerary_mgr.add_reservation(flight_reservation)

            elif choice == 2:
                print("not supported yet.")

            elif choice == 3:
                print("not supported yet.")
                break

            elif choice == 4:
                print("not supported yet.")
                break

            else:
                print("Invalid input, please enter a number (1, 2, 3 or 4).")




    def select_flight(self):
        flight_data: dict[str, Union[str, datetime, int]] = self.get_customer_flight_info()
        turkish_flight_api = TurkishOnlineFlightAPI()
        flight_research_mgr = FlightSearchManager([turkish_flight_api])
        flight_map = flight_research_mgr.search_flights(flight_data["date_from"],
                                                        flight_data["from_location"],
                                                        flight_data["date_to"],
                                                        flight_data["to_location"],
                                                        flight_data["num_infants"],
                                                        flight_data["num_children"],
                                                        flight_data["num_adults"],)
        print("Select a flight: ")

        for idx, (api, flight) in flight_map.items():
            print(f"{idx}) {flight}")

        selected_index = self.get_user_choice(f"Enter a number (from 1 to {len(flight_map)}): ", len(flight_map))
        selected_api, selected_flight = flight_map[selected_index]

        return selected_api, selected_flight


    def get_customer_flight_info(self):
        from_location = self.get_input_string("Enter departure location: ")
        date_from = self.get_input_date("Enter departure date (DD-MM-YYYY): ")
        to_location = self.get_input_string("Enter destination: ")
        date_to = self.get_input_date("Enter return date (DD-MM-YYYY): ")
        num_infants = self.get_input_integer("Enter number of infants: ")
        num_children = self.get_input_integer("Enter number of children: ")
        num_adults = self.get_input_integer("Enter number of adults: ")

        return {"from_location": from_location,
                "date_from": date_from,
                "to_location": to_location,
                "date_to": date_to,
                "num_infants": num_infants,
                "num_children": num_children,
                "num_adults": num_adults
                }



    def get_user_choice(self, prompt: str, num_of_choices):
        while True:
            try:
                choice = self.get_input_integer(prompt)

                if not 1 <= choice <= num_of_choices:
                    raise InvalidInputError(f"Invalid input, please enter a number (from 1 to {num_of_choices}).")

                return choice

            except InvalidInputError as e:
                print(e)


    def get_input_string(self, prompt):
        return input(prompt)


    def get_input_date(self, prompt):
        while True:
            try:
                return datetime.strptime(input(prompt), "%d-%m-%Y")

            except ValueError:
                print("Invalid date format. Please enter the date in DD-MM-YYYY format.")


    def get_input_integer(self, prompt):
        while True:
            try:
                return int(input(prompt))

            except ValueError:
                print("Invalid input. Please enter an integer.")