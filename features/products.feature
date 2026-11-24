Feature: Browsing products
  Shoppers see the catalogue with prices and stock, which come from the inventory service.

  Scenario: The product list shows every product with its price
    When I open the products page
    Then I see 4 products
    And the product "P-100" costs "24.90"

  Scenario: A product page shows how much stock is left
    When I open the product page of "P-300"
    Then the stock badge says "Only 4 left"

  Scenario: An out of stock product cannot be added to the cart
    When I open the product page of "P-400"
    Then the stock badge says "Out of stock"
    And there is no add to cart button
