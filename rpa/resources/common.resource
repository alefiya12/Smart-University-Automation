*** Settings ***
Documentation    Common resources shared across all robot suites.
Library          SeleniumLibrary
Library          Collections
Library          OperatingSystem
Library          String
Library          DateTime

*** Variables ***
${BASE_URL}              http://localhost:5173
${API_URL}               http://localhost:8000
${BROWSER}               chrome
${IMPLICIT_WAIT}         10
${SCREENSHOT_DIR}        ${CURDIR}/../../../reports/screenshots

*** Keywords ***
Open Smart University Browser
    [Documentation]    Opens the browser and navigates to the app.
    Open Browser    ${BASE_URL}    ${BROWSER}
    Maximize Browser Window
    Set Selenium Implicit Wait    ${IMPLICIT_WAIT}

Close Smart University Browser
    [Documentation]    Captures final screenshot and closes the browser.
    Capture Page Screenshot    ${SCREENSHOT_DIR}/final_${BROWSER}.png
    Close Browser

Wait And Click
    [Arguments]    ${locator}
    Wait Until Element Is Visible    ${locator}    timeout=15s
    Click Element    ${locator}

Wait And Input
    [Arguments]    ${locator}    ${text}
    Wait Until Element Is Visible    ${locator}    timeout=15s
    Clear Element Text    ${locator}
    Input Text    ${locator}    ${text}
