#!/bin/sh
mkdir output
mkdir ./Program/input_vm
mkdir ./Program/output
cp -r ./input_vm/* ./Program/input_vm/
cd Program
python3 main.py
cp -r ./output/* ../output