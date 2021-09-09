## setup temp test directory
test_contents=$1
work_dir=`mktemp -d`
cp -r $1 $work_dir

## find full path to .vm file
vm_file=$(find $(cd $test_contents; pwd;) | grep 'vm$')

## parser location
parser=$(pwd)/parser.js

## parse .vm file and create a .asm file
cd $work_dir
node $parser $vm_file

## test .asm file
test_file=$(find $(pwd) | grep -v 'VME' | grep '.tst')
~/home/dev/nand2tetris-materials/tools/CPUEmulator.sh $test_file
