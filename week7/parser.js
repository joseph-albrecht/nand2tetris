import fs from "fs";
import path from "path";

if (process.argv.length < 3) {
    console.log("You need to specify a filepath.");
    process.exit(1);
}

var filePath = process.argv[2];

class Parser{
    constructor(filePath){
	this.filePath = filePath;
	this.filename = path.parse(filePath).name;
	this.lines = null;
	this.parseInput();
	this.index = null;
	this.commandType = null;
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

    advance(){
	if (this.index === null){
	    this.index = 0;
	} else {
	    this.index = this.index + 1;
	}
	var currentLine = this.lines[this.index];
	var lineTokens = currentLine.split(" ");
	this.commandType = lineTokens[0];
	this.arg1        = lineTokens[1];
	this.arg2        = lineTokens[2];
    }

    hasMoreCommands(){
	return (this.index || 0) + 1 <= this.lines.length - 1;
    }

    print(){
	console.log("==== VM Script " + this.filename + " ====");
	while (this.hasMoreCommands()){
	    this.advance();
	    var output = this.commandType;
	    if (this.arg1 != null) output = output + " " + this.arg1;
	    if (this.arg2 != null) output = output + " " + this.arg2;
	    console.log(output);
	}
	console.log("==== END VM Script " + this.filename + " ====");
	console.log("");
    }
}

function writeAsmFile(filename, fileContents){
    fs.writeFileSync(filename, fileContents)
}

var parser = new Parser(filePath);
parser.print();

//writeAsmFile(filename+".asm", parser.parseVm());
