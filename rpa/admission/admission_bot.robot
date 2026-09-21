*** Settings ***
Documentation    Admission Automation Bot
...              Reads student records from an Excel file, creates user accounts,
...              generates enrollment numbers (SU{year}-{seq}), sends PDF admission
...              letters and confirmation emails, and writes a BotRunLog entry.
...              Idempotent: skips students whose email already exists.

Library    ${CURDIR}/AdmissionKeywords.py
Library    OperatingSystem
Library    Collections

Resource   ../resources/common.resource

Suite Setup      Suite Setup Steps
Suite Teardown   Log Run Summary

*** Variables ***
${EXCEL_PATH}    ${CURDIR}${/}..${/}..${/}docs${/}sample_data${/}admission_sample.xlsx

*** Test Cases ***

Process All Admissions From Excel
    [Documentation]    Load Excel and process each admission record.
    ${records}=    Load Admission Excel    ${EXCEL_PATH}
    FOR    ${record}    IN    @{records}
        Process Single Admission    ${record}
    END

*** Keywords ***

Suite Setup Steps
    [Documentation]    Validate input file exists before starting.
    File Should Exist    ${EXCEL_PATH}
    ...    msg=Admission Excel not found: ${EXCEL_PATH}
