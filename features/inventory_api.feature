Feature: Inventory reservations API
  The inventory service is also tested directly through its API.

  Scenario: Reserving stock lowers it and running low publishes an event
    When I reserve 2 of "P-300" for order "manual-1"
    Then the reservation is created
    And the inventory stock of "P-300" is 2
    And a low stock event was published for "P-300"

  Scenario: Releasing a reservation gives the stock back
    Given I reserve 3 of "P-200" for order "manual-2"
    When I release that reservation
    Then the inventory stock of "P-200" is 30

  Scenario: Reserving more than is in stock is refused
    When I reserve 9 of "P-300" for order "manual-3"
    Then the reservation is refused with "insufficient_stock"
