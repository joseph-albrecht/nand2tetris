parser=$1
emulator=$2
test_contents=$3

## setup temp test directory
temp_dir=$(mktemp -d)
cp -r $test_contents $temp_dir
cd $temp_dir

## parse .vm file and create a .asm file
vm_dir=$(basename $test_contents)
$parser $vm_dir

## test generated .asm file
test_file=$(find $(pwd) | grep -v 'VME' | grep '.tst')
echo $test_file
asm_file=$(find $(pwd) | grep -v 'VME' | grep '.asm')

# echo "### ASM FILE ###"
# cat $asm_file
# echo "### ASM END ###\n"
echo "### TEST RESULTS for $test_contents"
echo $asm_file":0:"
$emulator $test_file
echo "### TEST END for $test_contents" "\n"
