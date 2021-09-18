## parser location
parser=$(pwd)/VMTranslator.js

## setup temp test directory
test_contents=$1
temp_dir=$(mktemp -d)
cp -r $test_contents $temp_dir
cd $temp_dir

## parse .vm file and create a .asm file
vm_file=$(find $(pwd) | grep 'vm$')
node $parser $vm_file

## test generated .asm file
test_file=$(find $(pwd) | grep -v 'VME' | grep '.tst')
~/home/dev/nand2tetris-materials/tools/CPUEmulator.sh $test_file
