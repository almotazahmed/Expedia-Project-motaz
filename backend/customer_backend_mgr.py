from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict

from backend.api.flights.turkish_external import TurkishOnlineAPI


class CustomerAccount:
    def __init__(self, customer_id: str, username: str, password: str):
        self.__customer_id = customer_id
        self.__username = username
        self.__password = password
        self.itineraries: List[Itinerary] = []

    def get_customer_id(self):
        return self.__customer_id

    def get_username(self):
        return self.__username

    def get_password(self):
        return self.__password


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
        return customer_account.get_username() == username and customer_account.get_password() == password


class CustomerAccountManager:
    def __init__(self, authinticator: Authinticator):
        self.__authinticator = authinticator

    def authenticate_customer(self, username: str, password: str, customer_account: CustomerAccount) -> bool:
        return self.__authinticator.login(username, password, customer_account)


class Itinerary:
    def __init__(self):
        self.reservations: List[Reservation] = []
        self.total_cost = 0


class Reservation(ABC):
    def __init__(self, customer: CustomerAccount, customer_info: list):
        self.customer_id = customer.get_customer_id()
        self.customer_info = customer_info
        self.confirmation_id = None

    @abstractmethod
    def book(self):
        pass

    @abstractmethod
    def cancel(self):
        pass

    @abstractmethod
    def display(self):
        pass


class CustomerItineraryManager:

    def add_itinerary(self, customer_account: CustomerAccount, itinerary: Itinerary):
        customer_account.itineraries.append(itinerary)

    def display_customer_itineraries(self, itineraries_list: List[Itinerary]):
        if len(itineraries_list) > 0:
            for itinerary in itineraries_list:
                for reservation in itinerary.reservations:
                    reservation.display()
        else:
            print("There are no itineraries to present.")



class ItineraryManager:

    def add_reservation(self,itinerary: Itinerary, reservation: Reservation):
        itinerary.reservations.append(reservation)

    def book_all(self, itinerary: Itinerary):
        for reservation in itinerary.reservations:
            reservation.book()




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

    @abstractmethod
    def get_airline_name(self) -> str:
        pass



class FlightReservation(Reservation):
    def __init__(self, customer: CustomerAccount, flight_api: OnlineFlightAPI, flight: Flight, customer_info: list):
        super().__init__(customer, customer_info)
        self.flight = flight
        self.flight_api = flight_api

    def book(self):
        self.confirmation_id = self.flight_api.book_flight(self.flight.flight_fetched_object, self.customer_info)

    def cancel(self):
        if self.confirmation_id:
            self.flight_api.cancel_flight(self.confirmation_id)

    def display(self):
        print(self.flight)



# --- Search Manager ---
class FlightSearchManager:
    def __init__(self, flight_apis: List[OnlineFlightAPI]):
        self.flight_apis = flight_apis

    def search_flights(self, date_from: datetime, from_location: str, date_to: datetime, to_location: str,
                       num_infants: int, num_children: int, num_adults: int) -> List[Dict[OnlineFlightAPI, List[Flight]]]:
        api_flight_list: List[Dict[OnlineFlightAPI, List[Flight]]] = []
        flight_reservations: List[FlightReservation] = []
        for api in self.flight_apis:
            flights = api.fetch_flights(date_from, from_location, date_to, to_location, num_infants, num_children,
                                        num_adults)

            api_flights = {api: flights}

            api_flight_list.append(api_flights)

        return api_flight_list



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
                                       airline_name=self.get_airline_name(),
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

    def get_airline_name(self) -> str:
        return "Turkish Airlines"





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




class PaymentManager:
    def __init__(self):
        pass


