const fs = require('fs');
const { Transform } = require('node:stream');

// This function doubles unescaped quotes in a csv file
// It can't solve every problem, for example text fields with embedded '","' or '|@|' but those should be rare.
function clean_unescaped_quotes_row(line) {
  return line.replace(/^"|"$/g, '|%|') // temporarily move first and last quotes
    .replace(/","/g, '|@|') // temporarily move all quote-comma-quotes
    .replace(/"/g, '""')  // double all quotes
    .replace(/\|@\|/g, '","') // restore all quote-comma-quotes
    .replace(/\|%\|/g, '"'); // restore first and last quotes
}

const clean_unescaped_quotes = new Transform({
  transform(chunk, encoding, callback) {
    this.remaining = (this.remaining || '') + chunk.toString();
    const lines = this.remaining.split(/\r?\n/);
    this.remaining = lines.pop(); // Save the last incomplete line to be processed with the next chunk
    for (const line of lines) {
      this.push(clean_unescaped_quotes_row(line)+ '\n');
    }
    callback();
  },
  flush(callback) {
    if (this.remaining) {
      this.push(clean_unescaped_quotes_row(line)+ '\n');
    }
    callback();
  }
});

module.exports = clean_unescaped_quotes;

//
// TEST/USAGE
/*
const inputstream = fs.createReadStream("PD-Payroll-Export-.csv");
const outputstream = fs.createWriteStream("PD-Payroll-Export-FIXED.csv");
inputstream.pipe(clean_unescaped_quotes).pipe(outputstream);
*/
