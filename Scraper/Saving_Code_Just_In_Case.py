# def scrape_cars(self):
#     """Simulate car scraping in a loop while the event is set."""
#     car_to_scrape = self.car_scrape_entry.get()
#
#     if not car_to_scrape.strip():
#         print("Error: No car entered.")
#         return
#
#     while self.scraping_event.is_set():
#         try:
#             lowest_score = self.slider_value_label.cget("text")
#             mileage_importance = int(self.mileage_importance_entry.get() or 1)
#             price_importance = int(self.price_importance_entry.get() or 1)
#             year_importance = int(self.year_importance_entry.get() or 1)
#             print(f"Starting to scrape for car: {car_to_scrape}")
#             print(f"Will email items with score higher than {lowest_score}")
#
#             # Simulate the actual car scraping process
#             scrape_offerUp.initialization(car_to_scrape)
#             print('scrape finished, Email starting')
#
#             Email.fetch_recent_highscore(lowest_score, car_to_scrape, price_importance, mileage_importance,
#                                          year_importance)
#             print('emailing ended')
#
#             time.sleep(10)  # Simulate scraping delay
#
#             # Wait for a random time between 20 and 40 minutes (1200 to 2400 seconds)
#             random_delay = random.randint(1200, 2400)
#             print(f"Scraping completed. Waiting for {random_delay // 60} minutes before the next scrape.")
#
#             time.sleep(random_delay)
#
#         except Exception as e:
#             print(f"Error during scraping: {e}")
#             raise
#             # break

# def on_tab_change(self, event):
#     """Handle tab change, stop scraping, and notify the user."""
#     if self.scraping_event.is_set():  # Check if scraping is active
#         # Stop the scraping process
#         self.stop_scrape()
#         self.scraping_event.clear()
#
#         # Notify the user that the scraping process has been stopped
#         CustomMessageBox(
#             self,
#             "Scraping Stopped",
#             "The scraping process was stopped because you switched tabs.",
#             buttons=[("OK", lambda: None)]
#         )

# def on_tab_change(self, event):
#     """Handle tab change, stop scraping, and notify the user."""
#     if self.scraping_event.is_set():  # Check if scraping is active
#         # Stop the scraping process
#         self.stop_car_scrape()
#         self.scraping_event.clear()
#
#         # Notify the user that the scraping process has been stopped
#         CustomMessageBox(
#             self,
#             "Scraping Stopped",
#             "The scraping process was stopped because you switched tabs.",
#             buttons=[("OK", lambda: None)]
#         )