import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Tuple
import bcrypt
from backend.api.flights.turkish_external import *
from backend.api.flights.aircanada_external import *
from backend.api.hotels.hilton_external import *
from backend.api.hotels.marriott_external import *
from backend.api.payment.paypal_external import *
from backend.api.payment.stripe_external import *
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
        print(f"\nHello {self.__customer_account.get_username()}")


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
        else:
            logger.info("\nThe should be grater than zero.")


    def process_refund(self, transaction_id):
        if transaction_id is not None:
            return self.payment_method.refund(transaction_id)
        else:
            logger.info("\nThere is no transaction id.")
            return False, None

########################################################################################################################


#################################    --Abstract ReservationInterface Container--    ####################################

class ReservationInterface(ABC):
    def __init__(self, customer_id: str, customer_info: list, cost: float):
        self.reservation_id = None
        self._customer_id = customer_id
        self._customer_info = customer_info
        self._cost = cost
        self._booking_confirmation_id = None
        self._payment_transaction_id = None
        self._reservation_date = datetime.now()

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
    def __str__(self):
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

    # def remove_reservation(self, reservation: ReservationInterface):
    #     if reservation in self._reservations:
    #         self._reservations.remove(reservation)
    #         self._total_cost -= reservation.get_cost()

########################################################################################################################


#######################################    --Customer's Itineraries Manager--    #######################################

class ItineraryCollectionManager:
    def __init__(self):
        self._itineraries: List[Itinerary] = []

    def add_itinerary(self, itinerary: Itinerary):
        self._itineraries.append(itinerary)

    def get_itineraries(self):
        return self._itineraries.copy()


########################################################################################################################


##########################################    --Customer's Cards Manager--    ##########################################

class PaymentMethodsManager:
    def __init__(self):
        self._payment_methods: Dict[int, RefundablePaymentMethodInterface] = {}
        self._num_payment_methods = 0

    def add_payment_method(self, payment_method):
        self._num_payment_methods += 1
        self._payment_methods[self._num_payment_methods] = payment_method

    def get_payment_methods(self):
        return self._payment_methods.copy()

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

                self._process_reservation(reservation)

                booked_reservations.append(reservation)

            return True

        except (PaymentProcessingError, BookingError) as e:
            logger.error(f"\nError occurred during booking: {e}")
            self._handle_booking_failure(booked_reservations)
            return False

    def _process_reservation(self, reservation: ReservationInterface):
        self._process_payment(reservation)
        self._process_book(reservation)



    def _handle_booking_failure(self, booked_reservations: List[ReservationInterface]):
        try:
            self._rollback_booked_reservations(booked_reservations)

        except (BookingError, CancellationError, PaymentProcessingError) as e:
            logger.error(f"\nError occurred during cancellation: {e}")



    def _rollback_booked_reservations(self, booked_reservations: List[ReservationInterface]):
        for reservation in booked_reservations:
            self._process_refund(reservation)
            self._process_cancel(reservation)


    def _process_book(self, reservation: ReservationInterface):
        status =  reservation.book()

        if not status:
            self._process_refund(reservation)
            raise BookingError(f"\nFailed to book reservation [{reservation}]")


    #Rollback for cancellation not supported yet.
    def _process_cancel(self, reservation: ReservationInterface):
        status = reservation.cancel()

        if not status:
            raise CancellationError(f"\nFailed to cancel reservation [{reservation}].")


    def _process_payment(self, reservation: ReservationInterface):
        status, payment_confirmation_id = self.payment_mgr.process_payment(reservation.get_cost())

        if not status:
            raise PaymentProcessingError(f"\nFailed to pay for reservation [{reservation}].")

        reservation.set_payment_transaction_id(payment_confirmation_id)


    #Rollback for refund money not supported yet.
    def _process_refund(self, reservation: ReservationInterface):
        status = self.payment_mgr.process_refund(reservation.get_payment_transaction_id())

        if not status:
            raise PaymentProcessingError(f"\nFailed to refund payment for reservation [{reservation}].")


    def cancel_all(self):
        if len(self._itinerary.get_reservations()) == 0:
            logger.info("\nThere is no reservation to cancel.")

        else:
            self._itinerary.get_reservations().clear()
            logger.info("\nAll reservations have been cancelled and removed.")

        return True

########################################################################################################################


####################################    --Flight Reservation Service Classes --    #####################################

class Flight:
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

    def __str__(self):
        return (f"{self._airline_name}: Cost {self._cost} - From: {self._from_loc} on {self._date_from} "
                f"To: {self._to_location} on {self._date_to} - "
                f"#Infants: {self._num_infants} - #Children: {self._num_children} - #Adults: {self._num_adults}")


class FlightOnlineAPIInterface(ABC):
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

    @abstractmethod
    def get_company_name(self) -> str:
        pass


class FlightReservation(ReservationInterface):
    def __init__(self, customer_id: str, flight_api: FlightOnlineAPIInterface, flight: Flight, customer_info: list):
        super().__init__(customer_id, customer_info, flight.cost)
        self.flight = flight
        self.flight_api = flight_api

    def book(self):
        confirmation_id = self.flight_api.book_flight(self.flight.flight_fetched_object, self.get_customer_info())

        if confirmation_id is None:
            return False

        self.set_confirmation_id(confirmation_id)
        return True

    def cancel(self):
        confirmation_id = self.get_confirmation_id()
        if confirmation_id is None:
            logger.error("There is no confirmation ID to cancel the flight.")
            return False

        if not self.flight_api.cancel_flight(confirmation_id):
            return False

        self._booking_confirmation_id = None
        self._payment_transaction_id = None
        return True

    def __str__(self):
        return f"\t{self.flight}"


class TurkishFlightOnlineOnlineAPI(FlightOnlineAPIInterface):
    def __init__(self):
        self.turkish_api = TurkishOnlineAPI()

    def fetch_flights(self, date_from :datetime, from_location :str, date_to :datetime, to_location: str,
                      num_infants: int, num_children: int, num_adults: int) -> List[Flight]:
        available_flights = []

        flight_objects = self.turkish_api.get_available_flights()
        for flight in flight_objects:
            available_flights.append(Flight(flight_fetched_object=flight,
                                       airline_name= self.get_company_name(),
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

    def get_company_name(self) -> str:
        return "Turkish Airlines"


class AirCanadaFlightOnlineOnlineAPI(FlightOnlineAPIInterface):
    def __init__(self):
        self.aircanada_api = AirCanadaOnlineAPI()

    def fetch_flights(self, date_from :datetime, from_location :str, date_to :datetime, to_location: str,
                      num_infants: int, num_children: int, num_adults: int) -> List[Flight]:
        available_flights = []

        flight_objects = self.aircanada_api.get_flights(from_location, date_from, to_location, date_to, num_adults, num_children)
        for flight in flight_objects:
            available_flights.append(Flight(flight_fetched_object=flight,
                                       airline_name= self.get_company_name(),
                                       from_loc=from_location,
                                       date_from=flight.date_time_from,
                                       to_location=to_location,
                                       date_to=flight.date_time_to,
                                       num_infants=num_infants,
                                       num_children=num_children,
                                       num_adults=num_adults,
                                       cost=flight.price))

        return available_flights

    def book_flight(self, flight :AirCanadaFlight, customer_info :list) -> str:
        return self.aircanada_api.reserve_flight(flight, customer_info)

    def cancel_flight(self, confirmation_id :str) -> bool:
        return self.aircanada_api.cancel_flight(confirmation_id)

    def get_company_name(self) -> str:
        return "AirCanada"

# --- Flight Search Manager --- #
class FlightSearchManager:
    def __init__(self, flight_apis: List[FlightOnlineAPIInterface]):
        self.flight_apis = flight_apis

    def search_flights(self, date_from: datetime, from_location: str, date_to: datetime, to_location: str,
                       num_infants: int, num_children: int, num_adults: int) -> Dict[int, Tuple[FlightOnlineAPIInterface, Flight]]:
        flight_map: Dict[int, Tuple[FlightOnlineAPIInterface, Flight]] = {}
        index = 1

        for api in self.flight_apis:
            flights = api.fetch_flights(date_from, from_location, date_to, to_location, num_infants, num_children, num_adults)

            for flight in flights:
                flight_map[index] = (api, flight)
                index += 1

        return flight_map

########################################################################################################################


####################################    --Hotel Reservation Service Classes --    #####################################

class Room:
    def __init__(self, room_fetched_object, hotel_name: str, room_type: str=None, rooms_available: int=0, num_rooms_needed: int=0,
                  price_per_night: float=0.0, date_from: datetime=None, date_to: datetime=None, location: str=None, num_children: int=0, num_adults: int=0):

        self._room_fetched_object = room_fetched_object
        self._hotel_name = hotel_name
        self._room_type = room_type
        self._rooms_available = rooms_available
        self._num_rooms_needed = num_rooms_needed
        self._price_per_night = price_per_night
        self._date_from = date_from
        self._date_to = date_to
        self._num_children = num_children
        self._num_adults = num_adults
        self._num_nights = (date_to - date_from).days
        self._cost = self._num_nights * self._price_per_night * self._num_rooms_needed

    @property
    def room_fetched_object(self):
        return self._room_fetched_object

    @property
    def cost(self):
        return self._cost

    def __str__(self):
        return (f"{self._hotel_name}: Per night: {self._price_per_night} - Total Cost: {self._cost} - From {self._num_rooms_needed} "
                f"on: {self._date_from} - #num_nights {self._num_nights} - "
                f"#num rooms: {self._rooms_available} - #Children: {self._num_children} - #Adults: {self._num_adults}")


class HotelOnlineAPIInterface(ABC):
    @abstractmethod
    def fetch_rooms(self, location: str, from_date: datetime, to_date: datetime, adults: int, children: int, needed_rooms: int) -> list[Room]:
        pass

    @abstractmethod
    def book_room(self, room: Room, customer_info: list) -> str:
        pass

    @abstractmethod
    def cancel_room(self, confirmation_id: str) -> bool:
        pass

    @abstractmethod
    def get_hotel_name(self) -> str:
        pass


class HotelReservation(ReservationInterface):
    def __init__(self, customer_id: str, hotel_api: HotelOnlineAPIInterface, room: Room, customer_info: list):
        super().__init__(customer_id, customer_info, room.cost)
        self.room = room
        self.hotel_api = hotel_api

    def book(self):
        confirmation_id = self.hotel_api.book_room(self.room.room_fetched_object, self.get_customer_info())

        if confirmation_id is None:
            return False

        self.set_confirmation_id(confirmation_id)
        return True

    def cancel(self):
        confirmation_id = self.get_confirmation_id()
        if confirmation_id is None:
            logger.error("There is no confirmation ID to cancel the hotel.")
            return False

        if not self.hotel_api.cancel_room(confirmation_id):
            return False

        self._booking_confirmation_id = None
        self._payment_transaction_id = None
        return True

    def __str__(self):
        return f"\t{self.room}"


class HiltonHotelOnlineOnlineAPI(HotelOnlineAPIInterface):
    def __init__(self):
        self.hilton_api = HiltonHotelAPI()

    def fetch_rooms(self, location: str, from_date: datetime, to_date: datetime, adults: int, children: int,
                    needed_rooms: int) -> List[Room]:
        available_rooms = []

        room_objects = self.hilton_api.search_rooms(location, from_date, to_date, adults, children, needed_rooms)
        for room in room_objects:
            available_rooms.append(Room(
                                        room_fetched_object=room,
                                        hotel_name = self.get_hotel_name(),
                                        room_type = room.room_type,
                                        rooms_available = room.available,
                                        num_rooms_needed = needed_rooms,
                                        price_per_night = room.price_per_night,
                                        date_from = from_date,
                                        date_to = to_date,
                                        num_children = children,
                                        num_adults = adults

            ))

        return available_rooms

    def book_room(self, room: HiltonRoom, customer_info :list) -> str:
        return self.hilton_api.reserve_room(room, customer_info)

    def cancel_room(self, confirmation_id :str) -> bool:
        return self.hilton_api.cancel_room(confirmation_id)

    def get_hotel_name(self) -> str:
        return "Hilton"


class MarriottHotelOnlineOnlineAPI(HotelOnlineAPIInterface):
    def __init__(self):
        self.marriott_api = MarriottHotelAPI()

    def fetch_rooms(self, location: str, from_date: datetime, to_date: datetime, adults: int, children: int,
                    needed_rooms: int) -> List[Room]:
        available_rooms = []

        room_objects = self.marriott_api.search_available_rooms(location, from_date, to_date, adults, children, needed_rooms)
        for room in room_objects:
            available_rooms.append(Room(
                                        room_fetched_object=room,
                                        hotel_name = self.get_hotel_name(),
                                        room_type = room.room_type,
                                        rooms_available = room.available,
                                        num_rooms_needed = needed_rooms,
                                        price_per_night = room.price_per_night,
                                        date_from = from_date,
                                        date_to = to_date,
                                        num_children = children,
                                        num_adults = adults

            ))

        return available_rooms

    def book_room(self, room: MarriottRoom, customer_info :list) -> str:
        return self.marriott_api.do_room_reservation(room, customer_info)

    def cancel_room(self, confirmation_id :str) -> bool:
        return self.marriott_api.cancel_room(confirmation_id)

    def get_hotel_name(self) -> str:
        return "Marriott"


class RoomSearchManager:
    def __init__(self, hotel_apis: List[HotelOnlineAPIInterface]):
        self.hotel_apis = hotel_apis

    def search_rooms(self, location: str, from_date: datetime, to_date: datetime, adults: int, children: int,
                     needed_rooms: int) -> Dict[int, Tuple[HotelOnlineAPIInterface, Room]]:
        room_map: Dict[int, Tuple[HotelOnlineAPIInterface, Room]] = {}
        index = 1

        for api in self.hotel_apis:
            rooms = api.fetch_rooms(location, from_date, to_date, adults, children, needed_rooms)

            for room in rooms:
                room_map[index] = (api, room)
                index += 1

        return room_map

########################################################################################################################

