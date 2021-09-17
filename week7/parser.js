import fs from "fs";

if (process.argv.length < 3) {
    console.log("You need to specify a filepath.");
    process.exit(1);
}

var filePath = process.argv[2];
var vmScript = fs.readFileSync(filePath).toString();

function parseInput(fileContents){
    let lines = fileContents.split("\r\n");
    let nonCommentLines = lines.filter(line => ! line.startsWith("//"));
    let codeLines = nonCommentLines.filter(line => ! /^[ \t]*$/.test(line));
    return codeLines;
}

console.log(JSON.stringify(parseInput(vmScript)));
