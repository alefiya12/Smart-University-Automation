*** Settings ***
Documentation    Results Processing Bot
...              Reads examination marks from Excel, auto-calculates grades
...              (O/A+/A/B+/B/F) and SGPA/CGPA. F-grade results are flagged
...              for admin review before publishing. Publishes approved results,
...              generates PDF marksheets, and sends result notification emails.

Library    ${CURDIR}/ResultKeywords.py
Library    OperatingSystem

Resource   ../resources/common.resource

Suite Setup      Suite Setup Steps
Suite Teardown   Log Run Summary

*** Variables ***
${EXCEL_PATH}    ${CURDIR}${/}..${/}..${/}docs${/}sample_data${/}marks_sample.xlsx

*** Test Cases ***

Upload And Calculate Grades
    [Documentation]    Load marks, compute grades, upsert into DB.
    ${records}=    Load Marks Excel    ${EXCEL_PATH}
    FOR    ${record}    IN    @{records}
        Process Student Result    ${record}
    END

Flag Failing Students For Review
    [Documentation]    Log any F-grade results that need admin approval before publishing.
    Review Failing Students

Publish Approved Results
    [Documentation]    Publish non-F (or admin-approved F) results; send emails + generate PDFs.
    Publish Approved Results

*** Keywords ***

Suite Setup Steps
    File Should Exist    ${EXCEL_PATH}
    ...    msg=Marks Excel not found: ${EXCEL_PATH}
