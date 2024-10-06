import hashlib
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Tuple
import bcrypt
from backend.api.flights.turkish_external import TurkishOnlineAPI
from backend.api.payment.paypal_external import *
from backend.exceptions import *


#########################################    --Customer Account Container--    #########################################

class CustomerAccount:
    def __init__(self, customer_id: str, username: str, password: str):
        self._customer_id = customer_id
        self._username = username
        self.__password_hash = self._hash_password(password)
        self.itineraries_manager = ItineraryCollectionManager()
        self.cards_manager = CardCollectionManager()

    def get_customer_id(self):
        return self._customer_id

    def get_username(self):
        return self._username

    def _hash_password(self, password: str):
        salt = os.urandom(16)  # Generate a random salt
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)

    def verify_password(self, password: str):
        return bcrypt.checkpw(password.encode(), self.__password_hash)

########################################################################################################################


######################################    --Customer Account Display Service--    ######################################

class Profile:
    def __init__(self, customer_account: CustomerAccount):
        self.__customer_account = customer_account

    def view_profile(self):
        print(f"Hello {self.__customer_account.get_username()}")


class Authinticator(ABC):
    @abstractmethod
    def login(self, username: str, password: str, customer_account: CustomerAccount) -> bool:
        pass


class PasswordAuthenticator(Authinticator):
    def login(self, username: str, password: str, customer_account: CustomerAccount) -> bool:
        return customer_account.get_username() == username and customer_account.verify_password(password)


class CustomerLoginManager:
    def __init__(self, authinticator: Authinticator):
        self.__authinticator = authinticator

    def authenticate_customer(self, username: str, password: str, customer_account: CustomerAccount) -> bool:
        return self.__authinticator.login(username, password, customer_account)

########################################################################################################################


######################################    --Customer Account Payment Service--    ######################################

class PaymentProcessorInterface(ABC):
    @abstractmethod
    def pay(self, amount):
        pass


class RefundProcessorInterface(ABC):
    @abstractmethod
    def refund(self, amount):
        pass


class PayPalPayment(PaymentProcessorInterface, RefundProcessorInterface):
    def __init__(self, card: PayPalCreditCard):
        self.paypal_api = PayPalOnlinePaymentAPI(card)

    def pay(self, amount):
        return self.paypal_api.pay_money(amount)

    def refund(self, transaction_id):
        return self.paypal_api.cancel_money(transaction_id)



class StripePayment(PaymentProcessorInterface, RefundProcessorInterface):

    def pay(self, amount):
        print(f"Processing Stripe payment of {amount}")

    def refund(self, amount):
        print(f"Processing PayPal refund of {amount}")


class PaymentManager:
    def __init__(self, payment_method: PaymentProcessorInterface):
        self.payment_method = payment_method

    def process_payment(self, amount):
        return self.payment_method.pay(amount)


class RefundManager:
    def __init__(self, refund_method: RefundProcessorInterface):
        self.refund_method = refund_method

    def process_refund(self, amount):
        self.refund_method.refund(amount)

########################################################################################################################


######################################    --Abstract Reservation Container--    ########################################

class Reservation(ABC):
    def __init__(self, customer_id: str, customer_info: list, cost: float):
        self._customer_id = customer_id
        self._customer_info = customer_info
        self._cost = cost
        self._confirmation_id = None
        self._payment_confirmation_id = None

    def get_customer_id(self):
        return self._customer_id

    def get_customer_info(self):
        return self._customer_info

    def set_cost(self, cost: float):
        self._cost = cost

    def get_cost(self):
        return self._cost

    def set_confirmation_id(self, confirmation_id):
        self._confirmation_id = confirmation_id

    def get_confirmation_id(self):
        return self._confirmation_id

    def set_payment_confirmation_id(self, payment_confirmation_id):
        self._payment_confirmation_id = payment_confirmation_id

    def get_payment_confirmation_id(self):
        return self._payment_confirmation_id


    @abstractmethod
    def book(self):
        pass

    @abstractmethod
    def cancel(self):
        pass

    @abstractmethod
    def display(self):
        pass

########################################################################################################################


############################################    --Itinerary Container--    #############################################

class Itinerary:
    def __init__(self):
        self._reservations: List[Reservation] = []
        self._total_cost = 0

    @property
    def reservations(self) -> List[Reservation]:
        return self._reservations

    @property
    def total_cost(self) -> float:
        return self._total_cost

    def add_reservation(self, reservation: Reservation):
        self._reservations.append(reservation)
        self._total_cost += reservation.get_cost()

    def remove_reservation(self, reservation: Reservation):
        if reservation in self._reservations:
            self._reservations.remove(reservation)
            self._total_cost -= reservation.get_cost()

########################################################################################################################


#######################################    --Customer's Itineraries Manager--    #######################################

class ItineraryCollectionManager:
    def __init__(self):
        self._itineraries: List[Itinerary] = []

    def add_itinerary(self, itinerary: Itinerary):
        self._itineraries.append(itinerary)

    def display_itineraries(self):
        if len(self._itineraries) > 0:
            for itinerary in self._itineraries:
                for reservation in itinerary.reservations:
                    reservation.display()
        else:
            print("There are no itineraries to present.")

########################################################################################################################


##########################################    --Customer's Cards Manager--    ##########################################

class CardCollectionManager:
    def __init__(self):
        self._cards = []

    def add_card(self, card):
        self._cards.append(card)

########################################################################################################################


#############################################    --Itinerary Manager--    ##############################################

class SingleItineraryManager:
    def __init__(self, itinerary: Itinerary):
        self._itinerary = itinerary

    def add_reservation(self, reservation: Reservation):
        self._itinerary.add_reservation(reservation)

    def book_all_reservations(self, payment_method: PaymentProcessorInterface):
        payment_mgr: PaymentManager = PaymentManager(payment_method)
        booked_reservations = []

        try:
            for reservation in self._itinerary.reservations:

                status, payment_confirmation_id = payment_mgr.process_payment(reservation.get_cost())

                if not status:
                    raise PaymentProcessingError("Payment failed for reservation.")

                reservation.book()

                if not reservation.get_confirmation_id() or not isinstance(reservation.get_confirmation_id(), str):
                    raise BookingError(f"Failed to book reservation [{reservation.display()}]")

                reservation.set_payment_confirmation_id(payment_confirmation_id)
                booked_reservations.append(reservation)

            return True

        except (PaymentProcessingError, BookingError) as e:
            print(f"Error occurred: {e}")
            self._rollback_booked_reservations(booked_reservations, payment_method)
            self._remove_failed_reservations()
            return False

    def _rollback_booked_reservations(self, booked_reservations: List[Reservation], payment_method):
        refund_mgr: RefundManager = RefundManager(payment_method)
        for reservation in booked_reservations:
            try:
                refund_mgr.process_refund(reservation.get_payment_confirmation_id())
                reservation.cancel()
            except Exception as e:
                print(f"Failed to rollback reservation {reservation.get_confirmation_id()}: {e}")

    def _remove_failed_reservations(self):
        failed_reservations = [r for r in self._itinerary.reservations if not r.get_confirmation_id()]
        for reservation in failed_reservations:
            self._itinerary.remove_reservation(reservation)



class Flight(ABC):
    def __init__(self, flight_fetched_object, airline_name: str, from_loc: str, date_from: datetime,
                 to_location: str, date_to: datetime, num_infants: int, num_children: int, num_adults: int, cost: float):
        self._flight_fetched_object = flight_fetched_object
        self._airline_name = airline_name
        self._from_loc = from_loc
        self._date_from = date_from
        self._to_location = to_location
        self._date_to = date_to
        self._num_infants = num_infants
        self._num_children = num_children
        self._num_adults = num_adults
        self._cost = cost

    @property
    def flight_fetched_object(self):
        return self._flight_fetched_object

    @property
    def cost(self):
        return self._cost

    @abstractmethod
    def __str__(self):
        pass



class OnlineFlightAPI(ABC):
    @abstractmethod
    def fetch_flights(self, date_from: datetime, from_location: str, date_to: datetime, to_location: str,
                      num_infants: int, num_children: int, num_adults: int) -> list[Flight]:
        pass

    @abstractmethod
    def book_flight(self, flight: Flight, customer_info: list) -> str:
        pass

    @abstractmethod
    def cancel_flight(self, confirmation_id: str) -> bool:
        pass



class FlightReservation(Reservation):
    def __init__(self, customer_id: str, flight_api: OnlineFlightAPI, flight: Flight, customer_info: list):
        super().__init__(customer_id, customer_info, flight.cost)
        self.flight = flight
        self.flight_api = flight_api

    def book(self):
        try:
            confirmation_id = self.flight_api.book_flight(self.flight.flight_fetched_object, self.get_customer_info())

            if not confirmation_id or not isinstance(confirmation_id, str):
                raise BookingError(f"Failed to book flight [{self.flight}]")

            self.set_confirmation_id(confirmation_id)
        except BookingError as e:
            print(f"Booking error: {e}")
            raise

    def cancel(self):
        if self.get_confirmation_id():
            self.set_confirmation_id(None)
            self.set_payment_confirmation_id(None)
            return self.flight_api.cancel_flight(self.get_confirmation_id())

    def display(self):
        print(self.flight)


#Type 1 from flights companies
class TurkishFlight(Flight):
    def __init__(self, flight_fetched_object: object, airline_name: str, from_loc: str, date_from: datetime,
                 to_location: str, date_to: datetime, num_infants: int, num_children: int, num_adults: int, cost: float):
        super().__init__(flight_fetched_object,airline_name, from_loc, date_from,
                 to_location, date_to, num_infants, num_children, num_adults, cost)

    def __str__(self):
        return (f"{self._airline_name}: Cost {self._cost} - From: {self._from_loc} on {self._date_from} "
                f"To: {self._to_location} on {self._date_to} - "
                f"#Infants: {self._num_infants} - #Children: {self._num_children} - #Adults: {self._num_adults}")


class TurkishOnlineFlightAPI(OnlineFlightAPI):
    def __init__(self):
        self.turkish_api = TurkishOnlineAPI()

    def fetch_flights(self, date_from :datetime, from_location :str, date_to :datetime, to_location: str,
                      num_infants: int, num_children: int, num_adults: int) -> List[Flight]:
        available_flights = []

        flight_objects = self.turkish_api.get_available_flights()
        for flight in flight_objects:
            available_flights.append(TurkishFlight(flight_fetched_object=flight,
                                       airline_name="Turkish Airlines",
                                       from_loc=from_location,
                                       date_from=flight.datetime_from,
                                       to_location=to_location,
                                       date_to=flight.datetime_to,
                                       num_infants=num_infants,
                                       num_children=num_children,
                                       num_adults=num_adults,
                                       cost=flight.cost))

        return available_flights

    def book_flight(self, flight :TurkishFlight, customer_info :list) -> str:
        return self.turkish_api.reserve_flight(customer_info, flight)

    def cancel_flight(self, confirmation_id :str) -> bool:
        return self.turkish_api.cancel_flight(confirmation_id)



# --- Search Manager ---
class FlightSearchManager:
    def __init__(self, flight_apis: List[OnlineFlightAPI]):
        self.flight_apis = flight_apis

    def search_flights(self, date_from: datetime, from_location: str, date_to: datetime, to_location: str,
                       num_infants: int, num_children: int, num_adults: int) -> Dict[int, Tuple[OnlineFlightAPI, Flight]]:
        flight_map: Dict[int, Tuple[OnlineFlightAPI, Flight]] = {}
        index = 1

        for api in self.flight_apis:
            flights = api.fetch_flights(date_from, from_location, date_to, to_location, num_infants, num_children, num_adults)

            for flight in flights:
                flight_map[index] = (api, flight)
                index += 1

        return flight_map





#################################################################################################################################





#
# class FlightCancellation:
#     def __init__(self, flight_api: OnlineFlightAPI, confirmation_id: str):
#         self.flight_api = flight_api
#
#     def cancel_flight(self, confirmation_id: str) -> bool:
#         return self.flight_api.cancel(confirmation_id)
#
#
#
# class CancellationManager:
#     def __init__(self):
#         pass
#





# class CancelationManager:
#     def __init__(self, flight_cancelation_mgr: FlightCancellationManager):
#         self.flight_cancelation_mgr = flight_cancelation_mgr






