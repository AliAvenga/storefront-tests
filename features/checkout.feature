Feature: Cart and checkout
  Checking out reserves the stock of every cart line in the inventory service.

  Scenario: Adding a product to the cart
    When I add 2 of "P-100" to the cart
    Then the cart holds 2 of "P-100"

  Scenario: Checking out confirms the order and reserves the stock
    Given I add 2 of "P-100" to the cart
    When I check out
    Then the order is confirmed
    And the inventory stock of "P-100" is 10

  Scenario: Checking out more than is in stock is refused and reserves nothing
    Given I add 1 of "P-100" to the cart
    And I add 5 of "P-300" to the cart
    When I check out
    Then the cart says "Only 4 of Hand grinder left."
    And the inventory stock of "P-100" is 12
