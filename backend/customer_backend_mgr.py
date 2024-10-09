import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Tuple
import bcrypt
from backend.api.flights.turkish_external import TurkishOnlineAPI
from backend.api.payment.paypal_external import *
from backend.api.payment.stripe_external import StripeCardInfo, StripePaymentAPI, StripeUserInfo
from backend.exceptions import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#########################################    --Customer Account Container--    #########################################

class CustomerAccount:
    def __init__(self, customer_id: str, username: str, password: str):
        self._customer_id = customer_id
        self._username = username
        self.__password_hash = self._hash_password(password)
        self.itineraries_manager = ItineraryCollectionManager()
        self.payment_methods_manager = PaymentMethodsManager()

    def get_customer_id(self):
        return self._customer_id

    def get_username(self):
        return self._username

    def _hash_password(self, password: str):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt)

    def verify_password(self, password: str):
        return bcrypt.checkpw(password.encode(), self.__password_hash)

########################################################################################################################


#########################################    --Customer Account Services--    ##########################################

class Profile:
    def __init__(self, customer_account: CustomerAccount):
        self.__customer_account = customer_account

    def view_profile(self):
        print(f"Hello {self.__customer_account.get_username()}")


class AuthinticatorInterface(ABC):
    @abstractmethod
    def login(self, username: str, password: str, customer_account: CustomerAccount) -> bool:
        pass


class PasswordAuthenticator(AuthinticatorInterface):
    def login(self, username: str, password: str, customer_account: CustomerAccount) -> bool:
        return customer_account.get_username() == username and customer_account.verify_password(password)


class CustomerLoginManager:
    def __init__(self, authinticator: AuthinticatorInterface):
        self.__authinticator = authinticator

    def authenticate_customer(self, username: str, password: str, customer_account: CustomerAccount) -> bool:
        return self.__authinticator.login(username, password, customer_account)

########################################################################################################################


######################################    --Customer Account Payment Service--    ######################################

class PaymentMethodInterface(ABC):
    @abstractmethod
    def pay(self, amount):
        pass


class RefundablePaymentMethodInterface(PaymentMethodInterface):
    @abstractmethod
    def refund(self, transaction_id):
        pass


class PayPalPayment(RefundablePaymentMethodInterface):
    def __init__(self, card: PayPalCreditCard):
        self.__card = card
        self.paypal_api = PayPalOnlinePaymentAPI(card)

    def pay(self, amount):
        return self.paypal_api.pay_money(amount)

    def refund(self, transaction_id):
        return self.paypal_api.cancel_money(transaction_id)

    def __str__(self):
        return (f"PayPalCreditcard:- Name: {self.__card.name}, Number: {self.__card.id}, "
                f"Expiry Date: {self.__card.expire_date}")


class StripePayment(RefundablePaymentMethodInterface):
    def __init__(self, card: StripeCardInfo, user_info: StripeUserInfo):
        self.__stripe_card = card
        self.user_info = user_info
        self.stripe_api = StripePaymentAPI()

    def pay(self, amount):
        return self.stripe_api.withdraw_money(self.user_info, self.__stripe_card, amount)

    def refund(self, transaction_id):
        return self.stripe_api.cancel_money(transaction_id)

    def __str__(self):
        return (f"StripeCard:- Name: {self.user_info.name}, Number: {self.__stripe_card.id}, "
                f"Expiry Date: {self.__stripe_card.expire_date}")


class PaymentManager:
    def __init__(self):
        self.payment_method = None

    def set_payment_method(self, payment_method: RefundablePaymentMethodInterface):
        self.payment_method = payment_method

    def process_payment(self, amount):
        if amount > 0:
            return self.payment_method.pay(amount)

    def process_refund(self, transaction_id):
        if transaction_id is not None:
            return self.payment_method.refund(transaction_id)


########################################################################################################################


#################################    --Abstract ReservationInterface Container--    ####################################

class ReservationInterface(ABC):
    def __init__(self, customer_id: str, customer_info: list, cost: float):
        self._customer_id = customer_id
        self._customer_info = customer_info
        self._cost = cost
        self._booking_confirmation_id = None
        self._payment_transaction_id = None

    def get_customer_id(self):
        return self._customer_id

    def get_customer_info(self):
        return self._customer_info

    def set_cost(self, cost: float):
        self._cost = cost

    def get_cost(self):
        return self._cost

    def set_confirmation_id(self, confirmation_id):
        self._booking_confirmation_id = confirmation_id

    def get_confirmation_id(self):
        return self._booking_confirmation_id

    def set_payment_transaction_id(self, payment_confirmation_id):
        self._payment_transaction_id = payment_confirmation_id

    def get_payment_transaction_id(self):
        return self._payment_transaction_id


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
        self._reservations: List[ReservationInterface] = []
        self._total_cost = 0.0


    def get_reservations(self) -> List[ReservationInterface]:
        return self._reservations

    def get_total_cost(self) -> float:
        return self._total_cost

    def add_reservation(self, reservation: ReservationInterface):
        self._reservations.append(reservation)
        self._total_cost += reservation.get_cost()

    def remove_reservation(self, reservation: ReservationInterface):
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
            print(f"Listing {len(self._itineraries)} itineraries")
            for itinerary in self._itineraries:
                print(f"Itinerary total cost {itinerary.get_total_cost()}")
                for reservation in itinerary.get_reservations():
                    reservation.display()
        else:
            print("There are no itineraries to present.")

########################################################################################################################


##########################################    --Customer's Cards Manager--    ##########################################

class PaymentMethodsManager:
    def __init__(self):
        self._payment_methods: Dict[int, RefundablePaymentMethodInterface] = {}
        self._num_payment_methods = 0

    def add_payment_method(self, payment_method):
        self._num_payment_methods += 1
        self._payment_methods[self._num_payment_methods] = payment_method

    def display_payment_methods(self):
        for idx, payment_method in self._payment_methods.items():
            print(f"{idx}) {payment_method}")
        return self._num_payment_methods

    def get_payment_method(self, choice: int):
        return self._payment_methods[choice]

########################################################################################################################


#############################################    --Itinerary Manager--    ##############################################

class SingleItineraryManager:
    def __init__(self, itinerary: Itinerary, payment_mgr: PaymentManager):
        self._itinerary = itinerary
        self.payment_mgr = payment_mgr

    def add_reservation(self, reservation: ReservationInterface):
        self._itinerary.add_reservation(reservation)

    def book_all_reservations(self):
        booked_reservations = []

        try:
            for reservation in self._itinerary.get_reservations():
                if not self._process_reservation(reservation):
                    raise BookingError(f"Failed to book reservation [{reservation.display()}]")

                booked_reservations.append(reservation)

            logger.info("All reservations successfully booked.")
            return True

        except (PaymentProcessingError, BookingError) as e:
            self._handle_booking_failure(booked_reservations, e)
            return False

    def _process_reservation(self, reservation: ReservationInterface):
        status, payment_confirmation_id = self.payment_mgr.process_payment(reservation.get_cost())

        if not status:
            raise PaymentProcessingError(f"Payment failed for reservation [{reservation.display()}].")


        if not reservation.book():
            self._process_refund(reservation)
            return False

        reservation.set_payment_transaction_id(payment_confirmation_id)
        return True


    def _process_refund(self, reservation):
        try:
            if not self.payment_mgr.process_refund(reservation.get_payment_transaction_id()):
                raise NetworkError(f"Refund failed for reservation [{reservation.display()}].")
        except NetworkError as e:
            logger.error(f"Failed to process refund: {e}")


    def _handle_booking_failure(self, booked_reservations: List[ReservationInterface], error):
        logger.error(f"Error occurred during booking: {error}")
        self._rollback_booked_reservations(booked_reservations)


    def _rollback_booked_reservations(self, booked_reservations: List[ReservationInterface]):
        for reservation in booked_reservations:
            try:
                if not self.payment_mgr.process_refund(reservation.get_payment_transaction_id()) or not reservation.cancel():
                    raise NetworkError(f"Rollback failed for reservation [{reservation.display()}].")
            except NetworkError as e:
                logger.error(f"Failed to rollback reservation: {e}")


    def cancel_all(self):
        if len(self._itinerary.get_reservations()) == 0:
            logger.info("There is no reservation to cancel.")

        else:
            self._itinerary.get_reservations().clear()
            logger.info("All reservations have been cancelled and removed.")

        return True




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



class FlightAPIInterface(ABC):
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


class FlightReservation(ReservationInterface):
    def __init__(self, customer_id: str, flight_api: FlightAPIInterface, flight: Flight, customer_info: list):
        super().__init__(customer_id, customer_info, flight.cost)
        self.flight = flight
        self.flight_api = flight_api

    def book(self):
        try:
            confirmation_id = self.flight_api.book_flight(self.flight.flight_fetched_object, self.get_customer_info())
            if not confirmation_id:
                raise BookingError("Failed to get a valid confirmation ID from the flight API.")

            self.set_confirmation_id(confirmation_id)
            return True

        except Exception as e:
            print(f"Booking error: {e}")
            return False

    def cancel(self):
        try:
            confirmation_id = self.get_confirmation_id()
            if not confirmation_id:
                raise BookingError("No confirmation ID found for this reservation.")

            if not self.flight_api.cancel_flight(confirmation_id):
                raise CancellationError(f"Failed to cancel flight with confirmation ID {confirmation_id}.")

            self._booking_confirmation_id = None
            self._payment_transaction_id = None
            return True

        except Exception as e:
            print(f"Cancellation error: {e}")
            return False

    def display(self):
        print(f"\t{self.flight}")


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


class TurkishFlightAPI(FlightAPIInterface):
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
    def __init__(self, flight_apis: List[FlightAPIInterface]):
        self.flight_apis = flight_apis

    def search_flights(self, date_from: datetime, from_location: str, date_to: datetime, to_location: str,
                       num_infants: int, num_children: int, num_adults: int) -> Dict[int, Tuple[FlightAPIInterface, Flight]]:
        flight_map: Dict[int, Tuple[FlightAPIInterface, Flight]] = {}
        index = 1

        for api in self.flight_apis:
            flights = api.fetch_flights(date_from, from_location, date_to, to_location, num_infants, num_children, num_adults)

            for flight in flights:
                flight_map[index] = (api, flight)
                index += 1

        return flight_map





#################################################################################################################################



