## parser location
parser=$(pwd)/parser.js

## setup temp test directory
test_contents=$1
work_dir=$(mktemp -d)
cp -r $1 $work_dir
cd $work_dir

## parse .vm file and create a .asm file
vm_file=$(find $(pwd) | grep 'vm$')
node $parser $vm_file

## test generated .asm file
test_file=$(find $(pwd) | grep -v 'VME' | grep '.tst')
~/home/dev/nand2tetris-materials/tools/CPUEmulator.sh $test_file
