

from frontend.customer_frontend_mgr import *
if __name__ == "__main__":
    front_mgr = FrontEndManager()
    front_mgr.run()


# from abc import ABC, abstractmethod
# from datetime import datetime
# from APIs.turkish_external import TurkishOnlineAPI
# from APIs.aircanada_external import AirCanadaOnlineAPI
# from APIs.hilton_external import HiltonHotelAPI
# from APIs.marriott_external import MarriottHotelAPI
# from APIs.paypal_external import PayPalOnlinePaymentAPI, PayPalCreditCard
# from APIs.stripe_external import StripePaymentAPI, StripeCardInfo
#
#
# ###########################################################################################################
#
#
# class UserAccount:
#     def __init__(self, username: str, password: str):
#         self.__username = username
#         self.__password = password
#
#     def get_username(self):
#         return self.__username
#
#     def login(self, username: str, password: str) -> bool:
#         return username == self.__username and password == self.__password
#
#
# ###########################################################################################################
#
#
# class Customer(UserAccount):
#     def __init__(self, username: str, password: str):
#         super().__init__(username, password)
#         self.__itineraries = []
#         self.__paypal_card_info = None
#         self.__stripe_card_info = None
#         self.__cards_list = []
#
#     def set_paypal_card_info(self, card_info:PayPalCreditCard):
#         self.__paypal_card_info = card_info
#         self.__cards_list.append(card_info)
#
#     def get_paypal_card_info(self):
#         return self.__paypal_card_info
#
#     def set_stripe_card_info(self, card_info:StripeCardInfo):
#         self.__stripe_card_info = card_info
#         self.__cards_list.append(card_info)
#
#     def get_stripe_card_info(self):
#         return self.__stripe_card_info
#
#     def get_itineraries(self):
#         return self.__itineraries
#
#     def view_profile(self):
#         print(f"Hello {self.get_username().capitalize()}, this is your profile.")
#
#     def add_itinerary(self):
#         itinerary = Itinerary(self.__cards_list)
#         self.__itineraries.append(itinerary)
#         itinerary.add_reservations()
#
#     def list_itineraries(self):
#         if len(self.__itineraries) > 0:
#             for idx1, itinerary in enumerate(self.get_itineraries(), start=1):
#                 print(f"Itinerary total cost {itinerary.get_total_cost()}\n")
#                 for idx2, reservation in enumerate(itinerary.get_reservations(), start=1):
#                     print(f"    {idx1}: {idx2}: {reservation.get_reservation_object()}")
#         else:
#             print("There are no itineraries to present.")
#
#
# ###########################################################################################################
#
#
# class Itinerary:
#     def __init__(self, cards_list):
#         self.__cards_list = cards_list
#         self.__reservations = []
#         self.__total_cost = 0
#
#     def get_reservations(self):
#         return self.__reservations
#
#     def get_total_cost(self):
#             return self.__total_cost
#
#     def add_reservation(self, reservation):
#         self.__reservations.append(reservation)
#
#     def add_reservations(self):
#         while True:
#             choice = self.get_user_choice()
#             if choice == 1:
#                 reservation = FlightReservation()
#                 reservation.add_flight()
#                 self.add_reservation(reservation)
#             elif choice == 2:
#                 reservation = HotelReservation()
#                 reservation.add_hotel()
#                 self.add_reservation(reservation)
#             elif choice == 3:
#                 if self.reserve_itinerary():
#                     break
#             elif choice == 4:
#                 self.cancel_itinerary()
#                 break
#             else:
#                 print("Invalid input, please enter a number (1, 2, 3 or 4).")
#
#     def reserve_itinerary(self):
#         self.__total_cost = 0
#         if not self.__reservations:
#             print("No reservations in the itinerary to reserve.")
#             return False
#         if len(self.__cards_list) == 0:
#             print("There is no cards to reserve.")
#             return False
#         #choice the card type
#         choice = self.get_user_payment_card_choice()
#         successful_reservations = []
#
#         for reservation in self.__reservations:
#             payment_status = False
#             confirmation_id = None
#
#             if isinstance(choice, PayPalCreditCard):
#                 payment_api = PayPalOnlinePaymentAPI(choice)
#                 payment_status , confirmation_id = payment_api.pay_money(reservation.get_reservation_object().get_cost())
#             elif isinstance(choice, StripeCardInfo):
#                 payment_api = StripePaymentAPI()
#                 payment_status, confirmation_id = payment_api.withdraw_money("User info", choice,
#                                                                              reservation.get_reservation_object().get_cost())
#             else:
#                 print("No cards matched.")
#                 return False
#
#             if payment_status and confirmation_id:
#                 reserve = reservation.reserve(confirmation_id, "paypal")
#                 if reserve:
#                     self.__total_cost += reservation.get_reservation_object().get_cost()
#                     successful_reservations.append(reservation)
#                 else:
#                     print(f"ReservationInterface failed to complete: {reservation.get_reservation_object()}.")
#                     return False
#             else:
#                 print(f"Payment failed to complete pay for: {reservation.get_reservation_object()}.")
#                 return False
#
#         print(f"Successfully reserved {len(successful_reservations)} items in your itinerary.")
#         print(f"Total cost of itinerary: {self.__total_cost}")
#         return True
#
#     def cancel_itinerary(self):
#         if not self.__reservations:
#             print("No reservations to cancel.")
#             return
#
#         for reservation in self.__reservations:
#             reservation.cancel()
#
#         self.__reservations.clear()
#         self.__total_cost = 0
#         print("Itinerary canceled and all reservations removed.")
#
#     def get_user_choice(self):
#         while True:
#             try:
#                 return int(input("""Create your itinerary:
#                            1) Add flight
#                            2) Add Hotel
#                            3) Reserve itinerary
#                            4) Cancel itinerary
#                            Enter your choice (from 1 to 4): """))
#             except ValueError:
#                 print("Invalid input, please enter a number (1, 2, 3, or 4).")
#
#     def get_user_payment_card_choice(self):
#
#         print("Which payment card:")
#         for idx, card in enumerate(self.__cards_list[:2], start=1):  # Limit the choices to the first two cards
#             if isinstance(card, PayPalCreditCard):
#                 print(f"{idx}) PaypalCard- {card.name}, Number: {card.id}, Expiry date: {card.expire_date}")
#             elif isinstance(card, StripeCardInfo):
#                 print(f"{idx}) StripeCard- user1, Number: {card.id}, Expiry date: {card.expire_date}")
#             else:
#                 print(f"{idx}) Unknown card type")
#
#         while True:
#             try:
#                 choice = int(input(f"Enter your choice (1 or 2): "))
#                 if 1 <= choice <= 2:  # Ensures user can only choose 1 or 2
#                     return self.__cards_list[choice - 1]
#                 else:
#                     print(f"Invalid input, please enter 1 or 2.")
#             except ValueError:
#                 print(f"Invalid input, please enter a number (1 or 2).")
#
#
# ###########################################################################################################
#
#
# class ReservationInterface:
#     def __init__(self):
#         self.__reservation_type = None
#         self.__reservation_object = None
#         self.__confirmation_id = None
#         self.__confirmation_payment_id = None
#         self.__payment_card_type = None
#
#     def set_reservation_type(self, item_type):
#         self.__reservation_type = item_type
#
#     def get_reservation_type(self):
#         return self.__reservation_type
#
#     def set_reservation_object(self, item):
#         self.__reservation_object = item
#
#     def get_reservation_object(self):
#         return self.__reservation_object
#
#     def set_confirmation_id(self, confirmation_id):
#         self.__confirmation_id = confirmation_id
#
#     def get_confirmation_id(self):
#         return self.__confirmation_id
#
#     def set_payment_confirmation_id(self, confirmation_payment_id):
#         self.__confirmation_payment_id = confirmation_payment_id
#
#     def get_payment_confirmation_id(self):
#         return self.__confirmation_payment_id
#
#     def set_payment_card_type(self, payment_card_type):
#         self.__payment_card_type = payment_card_type
#
#     def get_payment_card_type(self):
#         return self.__payment_card_type
#
#     def reserve(self, confirmation_card_id, confirmation_card_type):
#         pass
#
#     def cancel(self):
#         pass
#
#
# ###########################################################################################################
#
#
# class FlightReservation(ReservationInterface):
#     def __init__(self):
#         super().__init__()
#         self.set_reservation_type("flight")
#
#     def add_flight(self):
#         from_loc = input("Enter departure location: ")
#         datetime_from = input_date("Enter departure date (DD-MM-YYYY): ")
#         to_loc = input("Enter destination: ")
#         datetime_to = input_date("Enter return date (DD-MM-YYYY): ")
#
#         num_infants = int(input("Enter number of infants: "))
#         num_children = int(input("Enter number of children: "))
#         num_adults = int(input("Enter number of adults: "))
#
#         available_flights_objects = self.get_available_flights(
#             from_loc, datetime_from, to_loc, datetime_to,num_infants, num_children, num_adults)
#
#         if available_flights_objects:
#             self.set_reservation_object(select_item(available_flights_objects, self.get_reservation_type()))
#         else:
#             print("No flights available for the selected dates and locations.")
#
#
#     @staticmethod
#     def get_available_flights(from_loc, datetime_from, to_loc, datetime_to, infants, children, adults):
#         available_flights_objects = []
#
#         turkish_api = TurkishOnlineAPI()
#         turkish_flights_data = turkish_api.get_available_flights()
#         for flight_object in turkish_flights_data:
#             flight = Flight(
#                 flight_object = flight_object,
#                 flight_company ="Turkish Airlines",
#                 from_loc=from_loc,
#                 datetime_from=flight_object.datetime_from,
#                 to_loc=to_loc,
#                 datetime_to=flight_object.datetime_to,
#                 num_infants=infants,
#                 num_children=children,
#                 num_adults=adults,
#                 cost = flight_object.cost
#             )
#             available_flights_objects.append(flight)
#
#         aircanada_api = AirCanadaOnlineAPI()
#         aircanada_flights_data = aircanada_api.get_flights(from_loc, datetime_from, to_loc, datetime_to, adults, children)
#         for flight_object in aircanada_flights_data:
#             flight = Flight(
#                 flight_object=flight_object,
#                 flight_company="AirCanada",
#                 from_loc=from_loc,
#                 datetime_from=flight_object.date_time_from,
#                 to_loc=to_loc,
#                 datetime_to=flight_object.date_time_to,
#                 num_infants=infants,
#                 num_children=children,
#                 num_adults=adults,
#                 cost = flight_object.price
#             )
#             available_flights_objects.append(flight)
#
#         return available_flights_objects
#
#     def reserve(self, confirmation_card_id, confirmation_card_type):
#         if self.get_reservation_object() is not None:
#             if self.get_reservation_object().get_flight_company() == "Turkish Airlines":
#                 turkish_api = TurkishOnlineAPI()
#                 self.set_confirmation_id(turkish_api.reserve_flight([], self.get_reservation_object().get_flight_object()))
#                 self.set_payment_card_type(confirmation_card_type)
#                 self.set_payment_confirmation_id(confirmation_card_id)
#                 return True
#             elif self.get_reservation_object().get_flight_company() == "AirCanada":
#                 aircanada_api = AirCanadaOnlineAPI()
#                 self.set_confirmation_id(aircanada_api.reserve_flight(self.get_reservation_object().get_flight_object(), []))
#                 self.set_payment_card_type(confirmation_card_type)
#                 self.set_payment_confirmation_id(confirmation_card_id)
#                 return True
#             else:
#                 print("Unknown airline.")
#                 return False
#         else:
#             print("No flights available for the selected dates and locations.")
#             return False
#
#     def cancel(self):
#         if self.get_confirmation_id() is not None:
#             if self.get_reservation_object().get_flight_company() == "Turkish Airlines":
#                 turkish_api = TurkishOnlineAPI()
#                 self.set_payment_card_type(None)
#                 self.set_payment_confirmation_id(None)
#                 return turkish_api.cancel_flight(self.get_confirmation_id())
#             elif self.get_reservation_object().get_flight_company() == "AirCanada":
#                 aircanada_api = AirCanadaOnlineAPI()
#                 self.set_payment_card_type(None)
#                 self.set_payment_confirmation_id(None)
#                 return aircanada_api.cancel_flight(self.get_confirmation_id())
#             else:
#                 print("Unknown airline.")
#                 return False
#         else:
#             print("No reservation found to cancel.")
#             return False
#
#
#
# class Flight:
#     def __init__(self, flight_object=None, flight_company=None, from_loc=None, datetime_from=None,
#                  to_loc=None, datetime_to=None, num_infants=0, num_children=0, num_adults=0, cost=0):
#         self.__flight_object = flight_object
#         self.__flight_company = flight_company
#         self.__from_loc = from_loc
#         self.__datetime_from = datetime_from
#         self.__to_loc = to_loc
#         self.__datetime_to = datetime_to
#         self.__num_infants = num_infants
#         self.__num_children = num_children
#         self.__num_adults = num_adults
#         self.__cost = cost
#
#     def set_flight_company(self, flight_company):
#         self.__flight_company = flight_company
#
#     def get_flight_company(self):
#         return self.__flight_company
#
#     def set_cost(self, cost):
#         self.__cost = cost
#
#     def get_cost(self):
#         return self.__cost
#
#     def set_flight_object (self, flight_object):
#         self.__flight_object = flight_object
#
#     def get_flight_object(self):
#         return self.__flight_object
#
#     def __str__(self):
#         return (f"{self.__flight_company}: Cost {self.__cost} - From: {self.__from_loc} on {self.__datetime_from} "
#                 f"To: {self.__to_loc} on {self.__datetime_to} - "
#                 f"#Infants: {self.__num_infants} - #Children: {self.__num_children} - #Adults: {self.__num_adults}")
#
#
# ###########################################################################################################
#
#
# class HotelReservation(ReservationInterface):
#     def __init__(self):
#         super().__init__()
#         self.set_reservation_type("hotel")
#
#     def add_hotel(self):
#         room_type = input("Enter room type: ")
#         datetime_from = input_date("Enter from date (DD-MM-YYYY): ")
#         datetime_to = input_date("Enter to date (DD-MM-YYYY): ")
#         location = input("Enter location: ")
#
#         num_rooms_needed = int(input("Enter number of rooms: "))
#         num_children = int(input("Enter number of children: "))
#         num_adults = int(input("Enter number of adults: "))
#
#         available_rooms_objects = self.get_available_rooms(
#             room_type, datetime_from, datetime_to, location, num_rooms_needed, num_children, num_adults)
#
#         if available_rooms_objects:
#             self.set_reservation_object(select_item(available_rooms_objects, self.get_reservation_type()))
#         else:
#             print("No Rooms available for the selected dates and locations.")
#
#
#     @staticmethod
#     def get_available_rooms(room_type, datetime_from, datetime_to, location, num_rooms_needed, children, adults):
#         available_rooms_objects = []
#
#         hilton_hotel_api = HiltonHotelAPI()
#         hilton_rooms_data = hilton_hotel_api.search_rooms(location, datetime_from, datetime_to, adults, children,
#                                                           num_rooms_needed)
#         for room_object in hilton_rooms_data:
#             room = Room(
#                 room_object = room_object,
#                 hotel_name ="Hilton",
#                 room_type = room_object.room_type,
#                 rooms_available = room_object.available,
#                 num_rooms_needed = num_rooms_needed,
#                 price_per_night = room_object.price_per_night,
#                 date_from=datetime_from,
#                 date_to=datetime_to,
#                 location=location,
#                 num_children = children,
#                 num_adults = adults,
#             )
#             available_rooms_objects.append(room)
#
#         marriott_hotel_api = MarriottHotelAPI()
#         marriott_rooms_data = marriott_hotel_api.search_available_rooms(location, datetime_from, datetime_to, adults,
#                                                                         children, num_rooms_needed)
#         for room_object in marriott_rooms_data:
#             room = Room(
#                 room_object=room_object,
#                 hotel_name="Marriott",
#                 room_type=room_object.room_type,
#                 rooms_available=room_object.available,
#                 num_rooms_needed=num_rooms_needed,
#                 price_per_night=room_object.price_per_night,
#                 date_from=datetime_from,
#                 date_to=datetime_to,
#                 location=location,
#                 num_children=children,
#                 num_adults=adults,
#             )
#             available_rooms_objects.append(room)
#
#         return available_rooms_objects
#
#     def reserve(self, confirmation_card_id, confirmation_card_type):
#         if self.get_reservation_object() is not None:
#             if self.get_reservation_object().get_hotel_name() == "Hilton":
#                 hilton_hotel_api = HiltonHotelAPI()
#                 self.set_confirmation_id(hilton_hotel_api.reserve_room(
#                     self.get_reservation_object().get_room_object(), []))
#                 self.set_payment_card_type(confirmation_card_type)
#                 self.set_payment_confirmation_id(confirmation_card_id)
#                 return True
#             elif self.get_reservation_object().get_hotel_name() == "Marriott":
#                 marriott_hotel_api = MarriottHotelAPI()
#                 self.set_confirmation_id(marriott_hotel_api.do_room_reservation(
#                     self.get_reservation_object().get_room_object(), []))
#                 self.set_payment_card_type(confirmation_card_type)
#                 self.set_payment_confirmation_id(confirmation_card_id)
#                 return True
#             else:
#                 print("Unknown Hotel.")
#                 return False
#         else:
#             print("No Rooms available for the selected dates and locations.")
#             return False
#
#     def cancel(self):
#         if self.get_confirmation_id() is not None:
#             if self.get_reservation_object().get_hotel_name() == "Hilton":
#                 hilton_hotel_api = HiltonHotelAPI()
#                 self.set_payment_card_type(None)
#                 self.set_payment_confirmation_id(None)
#                 return hilton_hotel_api.cancel_room(self.get_confirmation_id())
#             elif self.get_reservation_object().get_hotel_name() == "Marriott":
#                 marriott_hotel_api = MarriottHotelAPI()
#                 self.set_payment_card_type(None)
#                 self.set_payment_confirmation_id(None)
#                 return marriott_hotel_api.cancel_room(self.get_confirmation_id())
#             else:
#                 print("Unknown Hotel.")
#                 return False
#         else:
#             print("No reservation found to cancel.")
#             return False
#
# class Room:
#     def __init__(self, room_object=None, hotel_name=None, room_type=None, rooms_available=0, num_rooms_needed=0,
#                  price_per_night=0, date_from=None, date_to=None, location=None, num_children=0, num_adults=0):
#         self.__room_object = room_object
#         self.__hotel_name = hotel_name
#         self.__room_type = room_type
#         self.__rooms_available = rooms_available
#         self.__num_rooms_needed = num_rooms_needed
#         self.__price_per_night = price_per_night
#         self.__date_from = date_from
#         self.__date_to = date_to
#         self.__location = location
#         self.__num_children = num_children
#         self.__num_adults = num_adults
#
#         if date_from and date_to and isinstance(date_from, datetime) and isinstance(date_to, datetime):
#             self.__num_nights = (date_to - date_from).days
#         else:
#             self.__num_nights = 0
#
#         self.__cost = self.__num_nights * self.__price_per_night * self.__num_rooms_needed
#
#     def set_cost(self, cost):
#         self.__cost = cost
#
#     def get_cost(self):
#         return self.__cost
#
#     def set_hotel_name(self, hotel_name):
#         self.__hotel_name = hotel_name
#
#     def get_hotel_name(self):
#         return self.__hotel_name
#
#     def set_room_object(self, room_object):
#         self.__room_object = room_object
#
#     def get_room_object(self):
#         return self.__room_object
#
#
#     def __str__(self):
#         return (f"{self.__hotel_name}: Per night: {self.__price_per_night} - Total Cost: {self.__cost} - From {self.__num_rooms_needed} "
#                 f"on: {self.__date_from} - #num_nights {self.__num_nights} - "
#                 f"#num rooms: {self.__rooms_available} - #Children: {self.__num_children} - #Adults: {self.__num_adults}")
#
#
# ###########################################################################################################
#
#
# def select_item(available_items, item_type):
#         while True:
#             print(f"\nSelect a {item_type}:")
#             for idx, item in enumerate(available_items, start=1):
#                 print(f"{idx}) {item}")
#             try:
#                 choice = int(input(f"Enter your choice (from 1 to {len(available_items)}): "))
#                 if 1 <= choice <= len(available_items):
#                     selected_item = available_items[choice - 1]
#                     print(f"{item_type.capitalize()} ['{selected_item}'] added to your itinerary.")
#                     return selected_item
#                 else:
#                     print(f"Invalid choice, please enter a number between 1 and {len(available_items)}.")
#
#             except ValueError:
#                 print(f"Invalid input, please enter a valid number (1 to {len(available_items)}).")
#
#
# ###########################################################################################################
#
#
# def input_date(prompt):
#     while True:
#         try:
#             return datetime.strptime(input(prompt), "%d-%m-%Y")
#         except ValueError:
#             print("Invalid date format. Please enter the date in DD-MM-YYYY format.")
#
#
# ###########################################################################################################
#
#
# def base_ui():
#     customer = Customer('user', '1234')
#     customer.set_paypal_card_info(PayPalCreditCard("user", "gaza", id(123456), "20-02-2025", "AAAA"))
#     customer.set_stripe_card_info(StripeCardInfo(id(123456), "20-02-2025"))
#     while True:
#         try:
#             enter_choice = int(input("""System Access:
#                 1) Login
#                 2) Sign up
#                 Enter your choice (from 1 to 2): """))
#         except ValueError:
#             print("Invalid input, please enter a number (from 1 to 2).")
#             continue
#
#         if enter_choice == 1:
#             username = input("Enter Username: ")
#             password = input("Enter Password: ")
#             if customer.login(username, password):
#                 customer_page(customer)
#                 break
#             else:
#                 print("Invalid Username or Password. Please try again.")
#         elif enter_choice == 2:
#             print("Sign up is not yet supported, please wait.")
#         else:
#             print("Invalid Input, please enter a number (from 1 to 2).")
#
#
# ###########################################################################################################
#
#
# def customer_page(customer):
#     while True:
#         try:
#             choice = int(input(f"""Welcome {customer.get_username().capitalize()} | Customer:
#                     1) View Profile
#                     2) Make itinerary
#                     3) List my itineraries
#                     4) Logout
#                     Enter your choice (from 1 to 4): """))
#         except ValueError:
#             print("Invalid input, please enter a number (1, 2, 3 or 4).")
#             continue
#
#         if choice == 1:
#             customer.view_profile()
#         elif choice == 2:
#             customer.add_itinerary()
#         elif choice == 3:
#             customer.list_itineraries()
#         elif choice == 4:
#             exit()
#         else:
#             print("Invalid input, please enter a number (1, 2, 3 or 4).")
#
