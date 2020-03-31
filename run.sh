#!/bin/sh
if [ ! -d "./input_vm" ]; then
    mkdir -p ./input_vm
fi
if [ ! -d "./output" ]; then
    mkdir -p ./output
fi
if [ ! -f "./input_vm/input_vm_1.csv" ]; then
    echo "./input_vm has no file!Please copy files to it!"
    exit
fi
cd Program
python3 main.py
echo "Finished! The answer file is in ./output/"