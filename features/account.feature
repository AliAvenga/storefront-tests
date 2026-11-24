Feature: Customer account and loyalty
  Customers, loyalty points and wishlists come from the customers service.

  Scenario: Signing in shows the customer's points and tier
    When I sign in as "ana@example.com"
    Then the account shows "Ana Silva"
    And the account shows 120 points and tier "bronze"

  Scenario: An unknown email address cannot sign in
    When I sign in as "nobody@example.com"
    Then the account page says "No customer has this email address."

  Scenario: Checking out while signed in earns loyalty points
    Given I sign in as "ana@example.com"
    And I add 2 of "P-100" to the cart
    When I check out
    Then the order is confirmed
    And the order says I earned 49 points
    And the account shows 169 points and tier "bronze"

  Scenario: The wishlist shows whether each product is available
    Given I sign in as "ana@example.com"
    When I add "P-400" to my wishlist
    Then my wishlist shows "P-300" as "Running low"
    And my wishlist shows "P-400" as "Out of stock"
