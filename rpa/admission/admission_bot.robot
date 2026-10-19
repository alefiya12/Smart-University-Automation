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
    [Documentation]    Validate input file exists before starting, with fallback search paths.
    ${exists}=    Run Keyword And Return Status    File Should Exist    ${EXCEL_PATH}
    IF    not ${exists}
        ${p1}=    Run Keyword And Return Status    File Should Exist    ${CURDIR}${/}..${/}..${/}backend${/}sample_data${/}01_Fresh_Admissions_Bulk_Upload.xlsx
        IF    ${p1}
            Set Suite Variable    ${EXCEL_PATH}    ${CURDIR}${/}..${/}..${/}backend${/}sample_data${/}01_Fresh_Admissions_Bulk_Upload.xlsx
        ELSE
            ${p2}=    Run Keyword And Return Status    File Should Exist    ${CURDIR}${/}..${/}..${/}sample_data${/}Sample_Admission.xlsx
            IF    ${p2}
                Set Suite Variable    ${EXCEL_PATH}    ${CURDIR}${/}..${/}..${/}sample_data${/}Sample_Admission.xlsx
            END
        END
    END
    File Should Exist    ${EXCEL_PATH}    msg=Admission Excel not found: ${EXCEL_PATH}

