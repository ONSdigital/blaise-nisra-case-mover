Feature:
  As a TO Manager
  I want NISRA data transferred from NISRA to the ONS regularly
  So that the NISRA data can integrated with the ONS data

  Scenario: Do NOT transfer already processed files
    Given there is no new OPN NISRA data on the NISRA SFTP
    When the nisra-mover service is run with an OPN configuration
    Then no data is copied to the GCP storage bucket
    And a call is not made to the RESTful API to process the new data


