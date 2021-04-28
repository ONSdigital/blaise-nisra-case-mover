Feature: NISRA Case Mover
  As a TO Manager
  I want NISRA data transferred from NISRA to the ONS regularly
  So that the NISRA data can integrated with the ONS data

  Scenario: Transfer new OPN NISRA data from the NISRA SFTP to an ONS GCP storage bucket
    Given there is new OPN NISRA data on the NISRA SFTP that hasn't previously been transferred
    When the nisra-mover service is run with an OPN configuration
    Then the new data is copied to the GCP storage bucket including all necessary support files
    And a call is made to the RESTful API to process the new data

  Scenario: Transfer new OPN NISRA data from the NISRA SFTP to an ONS GCP storage bucket
    Given there is new OPN NISRA data on the NISRA SFTP that hasn't previously been transferred
    When the nisra-mover service is run with the survey_source_path of ./ONS/TEST
    Then the new data is copied to the GCP storage bucket including all necessary support files
    And a call is made to the RESTful API to process the new data

  Scenario: Do NOT transfer already processed files
    Given there is no new OPN NISRA data on the NISRA SFTP
    When the nisra-mover service is run with an OPN configuration
    Then no data is copied to the GCP storage bucket
    And a call is not made to the RESTful API
