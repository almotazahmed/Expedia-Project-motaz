from backend.customer_backend_mgr import *


class FrontEndManager:
    def run(self):
        print("Welcome to the Flight Reservation System!")
        self.base_ui()

    def base_ui(self):

        customer1: CustomerAccount = CustomerAccount('1304', 'user', '1234')

        while True:
            try:
                enter_choice = int(input("""System Access: 
                    1) Login
                    2) Sign up
                    Enter your choice (from 1 to 2): """))
            except ValueError:
                print("Invalid input, please enter a number (from 1 to 2).")
                continue

            if enter_choice == 1:
                username = input("Enter Username: ")
                password = input("Enter Password: ")
                pass_auth: PasswordAuthenticator = PasswordAuthenticator()
                costumer_acc_mgr: CustomerAccountManager = CustomerAccountManager(pass_auth)
                if costumer_acc_mgr.authenticate_customer(username, password, customer1):
                    self.customer_processing_page(customer1)
                    break
                else:
                    print("Invalid Username or Password. Please try again.")
            elif enter_choice == 2:
                print("Sign up is not yet supported, please wait.")
            else:
                print("Invalid Input, please enter a number (from 1 to 2).")

    def customer_processing_page(self, customer: CustomerAccount):
        while True:
            try:
                choice = int(input(f"""Welcome {customer.get_username().capitalize()} | Customer:
                        1) View Profile 
                        2) Make itinerary
                        3) List my itineraries
                        4) Logout
                        Enter your choice (from 1 to 4): """))
            except ValueError:
                print("Invalid input, please enter a number (1, 2, 3 or 4).")
                continue

            if choice == 1:
                profile_display: Profile = Profile(customer)
                profile_display.view_profile()
            elif choice == 2:
                itinerary: Itinerary = Itinerary()
                customer_itinerary_mgr: CustomerItineraryManager = CustomerItineraryManager()
                itinerary_mgr: ItineraryManager = ItineraryManager(itinerary)
                self.add_reservations(itinerary_mgr, customer)
                customer_itinerary_mgr.add_itinerary(customer, itinerary)
            elif choice == 3:
                itinerary_mgr: CustomerItineraryManager = CustomerItineraryManager()
                itinerary_mgr.display_customer_itineraries(customer.itineraries)
            elif choice == 4:
                exit()
            else:
                print("Invalid input, please enter a number (1, 2, 3 or 4).")

    def add_reservations(self, itinerary_mgr: ItineraryManager, customer: CustomerAccount):
        while True:
            choice = self.get_user_choice()
            if choice == 1:
                selected_api, selected_flight = self.add_flight()
                flight_reservation: Reservation = FlightReservation(customer, selected_api, selected_flight, [])
                itinerary_mgr.add_reservation(flight_reservation)
            elif choice == 2:
                print("not supported yet.")
            elif choice == 3:
                print("not supported yet.")
            elif choice == 4:
                print("not supported yet.")
            else:
                print("Invalid input, please enter a number (1, 2, 3 or 4).")

    def get_user_choice(self):
        while True:
            try:
                return int(input("""Create your itinerary:
                           1) Add flight
                           2) Add Hotel
                           3) Reserve itinerary
                           4) Cancel itinerary
                           Enter your choice (from 1 to 4): """))
            except ValueError:
                print("Invalid input, please enter a number (1, 2, 3, or 4).")

    def add_flight(self):
        turkish_flight_api = TurkishOnlineFlightAPI()
        flight_research_mgr = FlightSearchManager([turkish_flight_api])
        flight_map = flight_research_mgr.search_flights(datetime.strptime("20-06-2024", "%d-%m-%Y"), "gaza",
                                                     datetime.strptime("20-07-2024", "%d-%m-%Y"), "cairo",
                                                     2, 2, 2)
        print("Select a flight: ")
        for idx, (api, flight) in flight_map.items():
            print(f"{idx}) {flight}")

        while True:
            try:
                selected_index = int(input(f"Enter a number (from 1 to {len(flight_map)}): "))
                selected_api, selected_flight = flight_map[selected_index]
                return selected_api, selected_flight
            except ValueError:
                print(f"Invalid input, please enter a number (from 1 to {len(flight_map)}).")

