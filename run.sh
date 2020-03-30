#!/bin/sh
cp -r ./input_vm/* ./Program/input_vm/
cd Program
python3 main.py
cp -r ./output/* ../output