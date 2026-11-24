Feature: Customers loyalty API
  The customers service is also tested directly through its API.

  Scenario: Points are awarded once per order
    When I award points for order "O-TEST1" worth 250.00 to customer "C-1"
    Then the customer "C-1" has 370 points and tier "silver"
    And awarding points for order "O-TEST1" again is refused with "already_awarded"

  Scenario: Gold tier starts at 500 points
    When I award points for order "O-TEST2" worth 20.00 to customer "C-2"
    Then the customer "C-2" has 500 points and tier "gold"
