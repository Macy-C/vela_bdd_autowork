# SRS ID: TBD
# SSRS ID: CT-NMP.SSRS.Console.2869
# SSRS Description:
# The Console shall display the first Accession number, Procedure Description as a first line and set it as a primary procedure.
# Author: TBD
# Business Reviewer: TBD
# Test Reviewer: TBD
# Development Reviewer: TBD
# Feature Status: Draft
# Created Date: 2026-08-17
# Updated Date: 2026-08-17
# Version: V1

Feature: Establish the primary procedure and split-study descriptions
  As a CT technologist
  I want the first accession and procedure to identify the primary procedure
  So that unassigned results and study descriptions remain associated with the intended study

  Rule: The Console shall display the first accession number and Procedure Description on the first line and set that procedure as the primary procedure.

    @TestCase_34531
    Scenario: The first entered procedure receives results that retain their default assignment
      Given a patient has two procedures with associated accession numbers
      And Procedure 1 and its accession number are entered on the first line of the patient registration page
      When two protocols are selected for the patient
      Then the first line displays the accession number and Procedure Description for Procedure 1
      And Procedure 1 is identified as the primary procedure
      When a single surview and two reconstruction results for each clinical sequence are configured
      And the two results of the first clinical sequence are assigned respectively to Procedure 1 and Procedure 2
      And the procedure assignments of the second clinical sequence retain their default values
      And all scans, reconstructions, and the examination are completed
      Then the results of the second clinical sequence are stored in the study for Procedure 1

    @TestCase_34531
    Scenario: The procedure selected first from Worklist becomes the primary procedure
      Given a HIS/RIS patient has two accession numbers with two Procedure Descriptions
      And a CT technologist is signed in to the Console
      When one procedure is selected first for the patient from Worklist
      And the patient is loaded on the patient registration page
      Then the first line displays the accession number and Procedure Description selected first from Worklist
      And that procedure is identified as the primary procedure
      When two protocols with a single surview and two reconstruction results per clinical sequence are loaded
      And the two results of the first clinical sequence are assigned respectively to the two procedures
      And the procedure assignments of the second clinical sequence retain their default values
      And all scans, reconstructions, and the examination are completed
      Then the results of the second clinical sequence are stored in the study for the primary procedure

    @TestCase_70536
    Scenario: A non-split RIS study uses its requested procedure description
      Given a RIS patient has a nonempty requested procedure description
      And the patient has a nonempty procedure description supplied through one of the six supported procedure-description tags
      When the patient is loaded and an exam card is selected on the New Patient page
      Then "Study Description" displays the requested procedure description from RIS
      And the displayed procedure description matches the value defined in RIS
      When the non-split scan and examination are completed
      Then the Completed page displays the requested procedure description as the study description

    @TestCase_70536
    Scenario: A non-split manually registered study falls back to its procedure description
      Given a patient is created on the New Patient page with an empty "Study Description"
      And the patient has a nonempty procedure description
      And two exam cards are selected
      When the non-split scan and examination are completed
      Then the Completed page displays the procedure description as the study description

    @TestCase_70536
    Scenario: A non-split RIS study falls back to its selected exam card name
      Given a RIS patient has an empty requested procedure description
      And the patient has an empty procedure description
      And one or more exam cards are selected after the patient is loaded
      When the non-split scan and examination are completed
      Then the Completed page displays the selected exam card name as the study description

    @TestCase_70538
    Scenario: Empty study descriptions for three manually registered split studies fall back to procedure descriptions
      Given a patient is created on the New Patient page with three distinct accession numbers and Procedure Descriptions
      And "Study Description" is empty
      And one or more exam cards are selected
      When the split-study scans and examination are completed
      Then the Completed page displays three split studies
      And each split study displays its corresponding Procedure Description as its study description
      And no split study uses the selected exam card name as its study description

    @TestCase_70538
    Scenario: An entered study description is retained for two manually registered split studies
      Given a patient is created on the New Patient page with two distinct accession numbers and Procedure Descriptions
      And a nonempty value is entered in "Study Description"
      And one or more exam cards are selected
      When the split-study scans and examination are completed
      Then both split studies on the Completed page display the entered study description
      And neither split study uses the selected exam card name as its study description

    @TestCase_70538
    Scenario: Three C T and L procedure results reconstruct as separate studies
      Given a patient is created on the New Patient page with three distinct accession numbers
      And the three Procedure Descriptions are "C", "T", and "L"
      And the Thoracic Volume exam card has three reconstruction results
      And the three results are assigned respectively to procedures "C", "T", and "L"
      When all scans and reconstructions are completed
      Then the three split studies are reconstructed without errors

    @TestCase_70539
    Scenario: Empty Scheduled Local study descriptions fall back to procedure descriptions
      Given a patient is created on the New Patient page with two distinct accession numbers and Procedure Descriptions
      And "Study Description" is empty
      When the patient is added to Scheduled Local
      Then Scheduled Local displays two entries for the patient
      And both entries retain their corresponding accession numbers and Procedure Descriptions
      And "Study Description" is empty for both entries
      When both entries are loaded together on the New Patient page
      And an exam card is selected
      Then both Scheduled Local entries are present on the New Patient page
      When the split-study scans and examination are completed
      Then each split study on the Completed page displays its corresponding Procedure Description as its study description
      And neither split study uses the selected exam card name as its study description

    @TestCase_70539
    Scenario: A Scheduled Local description is cleared when its entries are loaded as a split study
      Given a patient is created on the New Patient page with two distinct accession numbers and Procedure Descriptions
      And a nonempty value is entered in "Study Description"
      When the patient is added to Scheduled Local
      Then Scheduled Local displays two entries with their corresponding accession numbers and Procedure Descriptions
      And exactly one Scheduled Local entry displays the entered study description
      When both entries are loaded together on the New Patient page
      Then both Scheduled Local entries are present
      And the Console clears "Study Description" for the split study
      When an exam card is selected and the scans and examination are completed
      Then each split study on the Completed page displays its corresponding Procedure Description as its study description
      And neither split study uses the selected exam card name as its study description

    @TestCase_70539
    Scenario: A study description entered after Scheduled Local loading is applied to both split studies
      Given a patient is created on the New Patient page with two distinct accession numbers and Procedure Descriptions
      And a nonempty value is entered in "Study Description"
      When the patient is added to Scheduled Local
      Then Scheduled Local displays two entries with their corresponding accession numbers and Procedure Descriptions
      And exactly one Scheduled Local entry displays the entered study description
      When both entries are loaded together on the New Patient page
      And an exam card is selected
      Then both Scheduled Local entries are present
      And the Console clears "Study Description" for the split study
      When a new value is entered in "Study Description"
      And the split-study scans and examination are completed
      Then both split studies on the Completed page display the newly entered study description
      And neither split study uses the selected exam card name as its study description

    @TestCase_70537
    Scenario: Split RIS entries without requested procedure descriptions use their procedure descriptions
      Given a RIS patient has two entries with distinct accession numbers and Procedure Descriptions
      And the requested procedure description is empty for both entries
      And an exam card is selected after both entries are loaded
      When the split-study scans and examination are completed
      Then each split study on the Completed page displays its corresponding RIS Procedure Description as its study description
      And neither split study uses the selected exam card name as its study description

    @TestCase_70537
    Scenario: Requested procedure descriptions are cleared when RIS entries form a split study
      Given a RIS patient has two entries with distinct accession numbers and Procedure Descriptions
      And both entries have nonempty requested procedure descriptions
      When both entries are loaded together on the New Patient page
      Then the Console clears "Study Description" for the split study
      When an exam card is selected and the scans and examination are completed
      Then each split study on the Completed page displays its corresponding RIS Procedure Description as its study description
      And neither split study uses its requested procedure description or selected exam card name as its study description

    @TestCase_70537
    Scenario: A study description entered after RIS loading is applied to both split studies
      Given a RIS patient has two entries with distinct accession numbers and Procedure Descriptions
      And both entries have nonempty requested procedure descriptions
      And the Console clears "Study Description" when both entries are loaded together on the New Patient page
      When a new value is entered in "Study Description"
      And an exam card is selected
      And the split-study scans and examination are completed
      Then both split studies on the Completed page display the newly entered study description
      And neither split study uses the selected exam card name as its study description