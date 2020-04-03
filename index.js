const spawn = require("child_process").spawn;

const pythonProcess = spawn('python',["./app.py", "resume.pdf", "12345"]);
console.log('done');