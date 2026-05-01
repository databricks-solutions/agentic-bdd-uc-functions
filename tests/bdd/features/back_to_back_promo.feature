Feature: Back-to-Back Promotion Compliance
  As a compliance officer
  I need products to have a 4-week cooling period between promotions
  So that we comply with ACCC pricing guidelines

  Rule: Products must have a minimum 4-week gap between promotions

    # Canonical examples — written by the compliance officer, never auto-generated.
    Scenario: Two promotions in consecutive weeks violates the rule
      Given a product was promoted in weeks 1, 2
      When I check for back-to-back promotions
      Then the result should be "FAILED"

    Scenario: A 5-week gap is compliant
      Given a product was promoted in weeks 1, 6
      When I check for back-to-back promotions
      Then the result should be "PASSED"

    # Coverage scaffolding around the 4/5-week rule boundary.
    Scenario Outline: Promotion gap validation
      Given a product was promoted in weeks <weeks>
      When I check for back-to-back promotions
      Then the result should be "<expected>"

      Examples: Various gaps
        | weeks    | expected |
        | 1, 2     | FAILED   |
        | 1, 3     | FAILED   |
        | 1, 4     | FAILED   |
        | 1, 5     | FAILED   |
        | 1, 6     | PASSED   |
        | 1, 6, 11 | PASSED   |
        | 1, 3, 5  | FAILED   |
