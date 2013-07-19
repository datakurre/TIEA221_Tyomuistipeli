*** Settings ***

Resource  saucelabs.robot

Test Setup  Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers

*** Test Cases ***

New player button is rendered
    Go to  ${HOME}
    Page should contain  Liity
    Capture page screenshot

Guest button is rendered
    Go to  ${HOME}
    Page should contain  Kokeile
    Capture page screenshot
