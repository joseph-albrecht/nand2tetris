import fs from "fs";
import path from "path";

if (process.argv.length < 3) {
    console.log("You need to specify a filepath.");
    process.exit(1);
}

var filePath = process.argv[2];
var filename = path.parse(filePath).name;

class Parser{
    constructor(filePath){
	this.filePath = filePath;
	this.parseInput()
    }

    parseInput(){
	let raw = fs.readFileSync(this.filePath).toString();
	let lines = raw.split("\r\n");
	let nonCommentLines = lines.filter(line => ! line.startsWith("//"));
	let codeLines = nonCommentLines.filter(line => ! /^[ \t]*$/.test(line));
	this.lines = codeLines;
    }

    parseVm(){
	return this.lines.join(" ");
    }

    printVm(){
	console.log("==== VM Script " + this.filename + " ====");
	this.lines.forEach((line) => {
	    console.log(line);
	})
	console.log("==== END VM Script " + this.filename + " ====");
	console.log("");
    }

}

function writeAsmFile(filename, fileContents){
    fs.writeFileSync(filename, fileContents)
}

var parser = new Parser(filePath);
parser.printVm();

writeAsmFile(filename+".asm", parser.parseVm());
