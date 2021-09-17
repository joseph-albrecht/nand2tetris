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

function writeAsmFile(filename, fileContents){
    fs.writeFileSync(filename, fileContents)
}

function printVm(contents){
    console.log("VM SCRIPT");
    contents.forEach((line) => {
	console.log(line);
    })
}

function parseVm(contents){
    return contents.join(" ");
}

var vmCodeLines = parseInput(vmScript);
printVm(vmCodeLines);

var asmCodeLines = parseVm(vmCodeLines);
writeAsmFile(filename+".asm", asmCodeLines);
