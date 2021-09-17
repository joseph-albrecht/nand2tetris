import fs from "fs";
import path from "path";

if (process.argv.length < 3) {
    console.log("You need to specify a filepath.");
    process.exit(1);
}

var filePath = process.argv[2];
var filename = path.parse(filePath).name;
var vmScript = fs.readFileSync(filePath).toString();

function parseInput(fileContents){
    let lines = fileContents.split("\r\n");
    let nonCommentLines = lines.filter(line => ! line.startsWith("//"));
    let codeLines = nonCommentLines.filter(line => ! /^[ \t]*$/.test(line));
    return codeLines;
}

function parseVm(contents){
    return contents.join(" ");
}

function writeAsmFile(filename, fileContents){
    fs.writeFileSync(filename, fileContents)
}

function printVm(filename, contents){
    console.log("==== VM Script " + filename + " ====");
    contents.forEach((line) => {
	console.log(line);
    })
}

var vmCodeLines = parseInput(vmScript);
printVm(filename, vmCodeLines);

var asmCodeLines = parseVm(vmCodeLines);
writeAsmFile(filename+".asm", asmCodeLines);
