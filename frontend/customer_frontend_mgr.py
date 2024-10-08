from typing import Union
import logging
from backend.customer_backend_mgr import *
from backend.exceptions import InvalidInputError
from backend.api.payment.paypal_external import PayPalCreditCard
from backend.api.payment.stripe_external import StripeCardInfo, StripeUserInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FrontEndManager:
    def __init__(self):
        self.customer = None

    def run(self):
        self.customer = CustomerAccount('1304', 'user', '1234')
        paypal_creditcard = PayPalCreditCard("user", "gaza", "23232", "20-02", "###")
        paypal_method = PayPalPayment(paypal_creditcard)
        stripe_user_info = StripeUserInfo('user', 'gaza')
        stripe_card_info = StripeCardInfo('32434', '30-03')
        stripe_method = StripePayment(stripe_card_info, stripe_user_info)

        self.customer.payment_methods_manager.add_payment_method(paypal_method)
        self.customer.payment_methods_manager.add_payment_method(stripe_method)
        print("Welcome to the Flight Reservation System!")

        self.base_ui()

    def base_ui(self):
        """Initial UI for login/signup"""
        while True:
            choice = self.get_user_choice(
                "System Access: \n1) Login\n2) Sign up\n3) Exit\nEnter your choice (from 1 to 3): ", 3)
            if choice == 1:
                self.login()
            elif choice == 2:
                # self.signup()  # Currently not implemented
                print("Not supported yet.")
            elif choice == 3:
                print("Exiting system.")
                exit()

    def login(self):
        """Login Interface"""
        username = input("Enter Username: ")
        password = input("Enter Password: ")
        pass_auth: PasswordAuthenticator = PasswordAuthenticator()
        customer_account_mgr: CustomerLoginManager = CustomerLoginManager(pass_auth)
        try:
            if not customer_account_mgr.authenticate_customer(username, password, self.customer):
                raise LoginError("Login failed")
            self.customer_processing_page()
        except LoginError as e:
            logger.error(f"Login failed for user {username}: {e}")

    def customer_processing_page(self):
        """Customer-specific operations once logged in"""
        while True:
            choice = self.get_user_choice(f"\nWelcome {self.customer.get_username().capitalize()} | Customer:\n"
                                          "1) View Profile \n2) Make itinerary\n3) List my itineraries\n4) Logout\nEnter your choice (from 1 to 4): ",
                                          4)
            if choice == 1:
                self.view_profile()
            elif choice == 2:
                self.create_itinerary()
            elif choice == 3:
                self.list_itineraries()
            elif choice == 4:
                print("Logging out...")
                self.customer = None
                break

    def view_profile(self):
        profile_display: Profile = Profile(self.customer)
        profile_display.view_profile()

    def create_itinerary(self):
        itinerary = Itinerary()
        payment_mgr = PaymentManager()
        refund_mgr = RefundManager()
        itinerary_mgr: SingleItineraryManager = SingleItineraryManager(itinerary, payment_mgr, refund_mgr)

        if self.make_reservations(itinerary_mgr):
            self.customer.itineraries_manager.add_itinerary(itinerary)
            print("Itinerary created")
        else:
            del itinerary

    def list_itineraries(self):
        self.customer.itineraries_manager.display_itineraries()

    def make_reservations(self, itinerary_mgr: SingleItineraryManager):
        num_reservations = 0
        while True:
            choice = self.get_user_choice(
                "\nCreate your itinerary:\n1) Add flight\n2) Add Hotel\n3) Reserve itinerary\n4) Cancel itinerary\nEnter your choice (from 1 to 4): ",
                4)
            if choice == 1:
                selected_api, selected_flight = self.select_flight()
                flight_reservation: ReservationInterface = FlightReservation(self.customer.get_customer_id(),
                                                                             selected_api, selected_flight, [])
                itinerary_mgr.add_reservation(flight_reservation)
                num_reservations += 1

            elif choice == 2:
                print("Not supported yet.")
                # num_reservations += 1

            elif choice == 3:
                if num_reservations > 0:
                    payment_method: RegularPaymentInterface = self.select_payment_method()
                    itinerary_mgr.payment_mgr.set_payment_method(payment_method)
                    itinerary_mgr.refund_mgr.set_refund_method(payment_method)
                    if itinerary_mgr.book_all_reservations():
                        return True
                else:
                    print("There is no reservations to book.")

            elif choice == 4:
                if itinerary_mgr.cancel_all():
                    return False

    def select_payment_method(self):
        """Select a payment method"""
        print("\nWhich Payment card:")
        num_payment_methods = self.customer.payment_methods_manager.display_payment_methods()
        choice: int = self.get_user_choice(f"Enter your choice (from 1 to {num_payment_methods}): ", num_payment_methods)
        return self.customer.payment_methods_manager.get_payment_method(choice)

    def select_flight(self):
        flight_data = self.get_customer_flight_info()
        turkish_flight_api: FlightAPIInterface = TurkishFlightAPI()
        flight_research_mgr = FlightSearchManager([turkish_flight_api])
        flight_map = flight_research_mgr.search_flights(
            flight_data["date_from"], flight_data["from_location"],
            flight_data["date_to"], flight_data["to_location"],
            flight_data["num_infants"], flight_data["num_children"],
            flight_data["num_adults"])

        print("Select a flight:")
        for idx, (api, flight) in flight_map.items():
            print(f"{idx}) {flight}")

        selected_index = self.get_user_choice(f"Enter a number (from 1 to {len(flight_map)}): ", len(flight_map))
        return flight_map[selected_index]

    def get_customer_flight_info(self):
        return {
            "from_location": self.get_input_string("Enter departure location: "),
            "date_from": self.get_input_date("Enter departure date (DD-MM-YYYY): "),
            "to_location": self.get_input_string("Enter destination: "),
            "date_to": self.get_input_date("Enter return date (DD-MM-YYYY): "),
            "num_infants": self.get_input_integer("Enter number of infants: "),
            "num_children": self.get_input_integer("Enter number of children: "),
            "num_adults": self.get_input_integer("Enter number of adults: ")
        }

    def get_user_choice(self, prompt: str, num_of_choices):
        while True:
            try:
                choice = self.get_input_integer(prompt)
                if not 1 <= choice <= num_of_choices:
                    raise InvalidInputError(f"Invalid input, please enter a number (from 1 to {num_of_choices}).")
                return choice
            except InvalidInputError as e:
                logger.error(e)

    def get_input_string(self, prompt):
        return input(prompt)

    def get_input_date(self, prompt):
        while True:
            try:
                return datetime.strptime(input(prompt), "%d-%m-%Y")
            except ValueError:
                logger.error("Invalid date format. Please enter in DD-MM-YYYY format.")

    def get_input_integer(self, prompt):
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                logger.error("Invalid input. Please enter a valid number.")




# from typing import Union
# from backend.customer_backend_mgr import *
# from backend.exceptions import InvalidInputError
# from backend.api.payment.paypal_external import PayPalCreditCard
# from backend.api.payment.stripe_external import StripeCardInfo, StripeUserInfo
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# class FrontEndManager:
#     def __init__(self):
#         self.customer = None
#
#     def run(self):
#         print("Welcome to the Flight ReservationInterface System!")
#         self.base_ui()
#
#     def base_ui(self):
#
#         #Initalize customer user and related payment methods with him
#
#         self.customer = CustomerAccount('1304', 'user', '1234')
#         paypal_creditcard = PayPalCreditCard("user", "gaza", "23232", "20-02", "###")
#         paypal_method = PayPalPayment(paypal_creditcard)
#         stripe_user_info = StripeUserInfo('user', 'gaza')
#         stripe_card_info = StripeCardInfo('32434', '30-03')
#         stripe_method = StripePayment(stripe_card_info, stripe_user_info)
#
#         self.customer.payment_methods_manager.add_payment_method(paypal_method)
#         self.customer.payment_methods_manager.add_payment_method(stripe_method)
#
#         #Login/Signup Interface
#         while True:
#             choice = self.get_user_choice("System Access: \n1) Login\n2) Sign up\nEnter your choice (from 1 to 2): ", 2)
#
#             if choice == 1:
#                 username = input("Enter Username: ")
#                 password = input("Enter Password: ")
#                 pass_auth: PasswordAuthenticator = PasswordAuthenticator()
#                 costumer_acc_mgr: CustomerLoginManager = CustomerLoginManager(pass_auth)
#
#                 try:
#                     if not costumer_acc_mgr.authenticate_customer(username, password, self.customer):
#                         raise LoginError("Login failed")
#
#                     self.customer_processing_page()
#
#                 except LoginError as e:
#                     logger.error(e)
#
#             elif choice == 2:
#                 print("Sign up is not yet supported, please wait.")
#
#             else:
#                 print("Invalid Input, please enter a number (from 1 to 2).")
#
#     def customer_processing_page(self):
#         while True:
#             #Display customer operations and enable customer selection
#             choice = self.get_user_choice(f"Welcome {self.customer.get_username().capitalize()} | Customer:\n1) View Profile \n2) Make itinerary\n3) List my itineraries\n4) Logout\nEnter your choice (from 1 to 4): ", 4)
#
#             if choice == 1:
#                 profile_display: Profile = Profile(self.customer)
#                 profile_display.view_profile()
#
#             elif choice == 2:
#                 #Make itinerary object and add reservations to it by make_reservations method and lastly add itinerary
#                 #to customer itineraries in customer itineraries manager
#                 itinerary: Itinerary = Itinerary()
#                 payment_mgr = PaymentManager()
#                 refund_mgr = RefundManager()
#                 itinerary_mgr: SingleItineraryManager = SingleItineraryManager(itinerary, payment_mgr, refund_mgr)
#                 if self.make_reservations(itinerary_mgr):
#                     self.customer.itineraries_manager.add_itinerary(itinerary)
#                 else:
#                     del itinerary
#
#             elif choice == 3:
#                 #Display customer itineraries
#                 self.customer.itineraries_manager.display_itineraries()
#
#             elif choice == 4:
#                 exit()
#
#             else:
#                 print("Invalid input, please enter a number (1, 2, 3 or 4).")
#
#     def make_reservations(self, itinerary_mgr: SingleItineraryManager):
#         while True:
#             choice = self.get_user_choice(f"Create your itinerary:\n1) Add flight\n2) Add Hotel\n3) Reserve itinerary\n4) Cancel itinerary\nEnter your choice (from 1 to 4): ", 4)
#
#             if choice == 1:
#                 selected_api, selected_flight = self.select_flight()
#                 flight_reservation: ReservationInterface = FlightReservation(self.customer.get_customer_id(), selected_api, selected_flight, [])
#                 itinerary_mgr.add_reservation(flight_reservation)
#
#             elif choice == 2:
#                 print("not supported yet.")
#
#             elif choice == 3:
#                 payment_method: RegularPaymentInterface = self.select_payment_method()
#                 itinerary_mgr.payment_mgr.set_payment_method(payment_method)
#                 itinerary_mgr.refund_mgr.set_refund_method(payment_method)
#                 itinerary_mgr.book_all_reservations()
#                 return True
#
#             elif choice == 4:
#                 itinerary_mgr.cancel_all()
#                 return False
#
#             else:
#                 print("Invalid input, please enter a number (1, 2, 3 or 4).")
#
#
#     def select_payment_method(self):
#         print("Which Payment card:")
#         self.customer.payment_methods_manager.display_payment_methods()
#         num_payment_methods = len(self.customer.payment_methods_manager.payment_methods)
#         choice = self.get_user_choice(f"Enter your choice (from 1 to {num_payment_methods}): ", num_payment_methods)
#         return self.customer.payment_methods_manager.get_payment_method[choice-1]
#
#
#
#     def select_flight(self):
#         flight_data: dict[str, Union[str, datetime, int]] = self.get_customer_flight_info()
#         turkish_flight_api: FlightAPIInterface = TurkishFlightAPI()
#         flight_research_mgr = FlightSearchManager([turkish_flight_api])
#         flight_map = flight_research_mgr.search_flights(flight_data["date_from"],
#                                                         flight_data["from_location"],
#                                                         flight_data["date_to"],
#                                                         flight_data["to_location"],
#                                                         flight_data["num_infants"],
#                                                         flight_data["num_children"],
#                                                         flight_data["num_adults"],)
#         print("Select a flight: ")
#
#         for idx, (api, flight) in flight_map.items():
#             print(f"{idx}) {flight}")
#
#         selected_index = self.get_user_choice(f"Enter a number (from 1 to {len(flight_map)}): ", len(flight_map))
#         selected_api, selected_flight = flight_map[selected_index]
#
#         return selected_api, selected_flight
#
#
#     def get_customer_flight_info(self):
#         from_location = self.get_input_string("Enter departure location: ")
#         date_from = self.get_input_date("Enter departure date (DD-MM-YYYY): ")
#         to_location = self.get_input_string("Enter destination: ")
#         date_to = self.get_input_date("Enter return date (DD-MM-YYYY): ")
#         num_infants = self.get_input_integer("Enter number of infants: ")
#         num_children = self.get_input_integer("Enter number of children: ")
#         num_adults = self.get_input_integer("Enter number of adults: ")
#
#         return {"from_location": from_location,
#                 "date_from": date_from,
#                 "to_location": to_location,
#                 "date_to": date_to,
#                 "num_infants": num_infants,
#                 "num_children": num_children,
#                 "num_adults": num_adults
#                 }
#
#
#
#     def get_user_choice(self, prompt: str, num_of_choices):
#         while True:
#             try:
#                 choice = self.get_input_integer(prompt)
#
#                 if not 1 <= choice <= num_of_choices:
#                     raise InvalidInputError(f"Invalid input, please enter a number (from 1 to {num_of_choices}).")
#
#                 return choice
#
#             except InvalidInputError as e:
#                 logger.error(e)
#
#
#     def get_input_string(self, prompt):
#         return input(prompt)
#
#
#     def get_input_date(self, prompt):
#         while True:
#             try:
#                 return datetime.strptime(input(prompt), "%d-%m-%Y")
#
#             except ValueError:
#                 print("Invalid date format. Please enter the date in DD-MM-YYYY format.")
#
#
#     def get_input_integer(self, prompt):
#         while True:
#             try:
#                 return int(input(prompt))
#
#             except ValueError:
#                 print("Invalid input. Please enter an integer.")

