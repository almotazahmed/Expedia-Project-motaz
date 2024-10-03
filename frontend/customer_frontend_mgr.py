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
                print("not supported yet")
                # customer.add_itinerary()
            elif choice == 3:
                itinerary_mgr: CustomerItineraryManager = CustomerItineraryManager()
                itinerary_mgr.display_customer_itineraries(customer.itineraries)
            elif choice == 4:
                exit()
            else:
                print("Invalid input, please enter a number (1, 2, 3 or 4).")
