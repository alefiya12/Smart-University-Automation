*** Settings ***
Documentation    Attendance Automation Bot
...              Reads attendance data from an Excel file, records entries per
...              student per subject per date, and automatically sends low-attendance
...              warning emails (≤75%) and critical alerts (≤60%).
...              Idempotent: upserts on (student_id, subject, date).

Library    ${CURDIR}/AttendanceKeywords.py
Library    OperatingSystem

Resource   ../resources/common.resource

Suite Setup      Suite Setup Steps
Suite Teardown   Log Run Summary

*** Variables ***
${EXCEL_PATH}    ${CURDIR}${/}..${/}..${/}docs${/}sample_data${/}attendance_sample.xlsx

*** Test Cases ***

Process All Attendance Records
    [Documentation]    Load attendance Excel and record each entry.
    ${records}=    Load Attendance Excel    ${EXCEL_PATH}
    FOR    ${record}    IN    @{records}
        Process Single Attendance Record    ${record}
    END

Check And Send Low Attendance Warnings
    [Documentation]    After recording, evaluate thresholds and send warning emails.
    Check And Send Low Attendance Warnings

*** Keywords ***

Suite Setup Steps
    File Should Exist    ${EXCEL_PATH}
    ...    msg=Attendance Excel not found: ${EXCEL_PATH}
