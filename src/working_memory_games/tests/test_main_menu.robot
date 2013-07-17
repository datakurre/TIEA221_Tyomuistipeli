*** Settings ***

Resource  selenium.robot

TestSetup  Open test browser
TestTeardown  Close all browsers

*** Test Cases ***

New player button is rendered
    Go to  ${HOME}
    Page should contain  Liity
    Capture page screenshot

Guest button is rendered
    Go to  ${HOME}
    Page should contain  Kokeile
    Capture page screenshot
