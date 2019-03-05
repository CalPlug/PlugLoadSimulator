#!/bin/bash
function pause() {
    read -p "$*"
}

python CalculationEngine.py

pause 'Press [Enter] to close'