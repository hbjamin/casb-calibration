# casb-calibration

Code to analyze and plot results of casb calibration tests

# Board descriptions

- `CASB 1`: Shipped to Berkeley October 2024. Unity gain path of ~ 0.7
- `CASB 2`: Currently being tested at Penn . Unity gain path of ~ 0.9
- `CASB 3`: Currenlty being debugged at Penn

- `MTC/A 1`: Was used at Berkeley to trigger EOS until October 2024.

# Robinson Baseline Restoration Schematic

                +3.3V
                |
                2
                |
   DAC---1-------------DIODES(>)------GND
                |
                3
                |
     IN---||------------OUT
              |    |
              5    4
              |    | 
             ADC   |
                   -2.5V
