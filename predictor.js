const { spawn } = require('child_process');
const path = require('path');

class Predictor {
    constructor() {
        this.queue = [];
        this.process = null;
        this.startProcess();
    }

    startProcess() {
        // Use the python executable from the virtual environment
        const pythonPath = path.join(__dirname, 'myenv', 'Scripts', 'python.exe');
        const scriptPath = path.join(__dirname, 'predict_worker.py');

        console.log(`Starting prediction background worker process...`);
        this.process = spawn(pythonPath, [scriptPath]);

        let buffer = '';

        this.process.stdout.on('data', (data) => {
            buffer += data.toString();
            let boundary = buffer.indexOf('\n');
            while (boundary !== -1) {
                const line = buffer.substring(0, boundary).trim();
                buffer = buffer.substring(boundary + 1);
                
                if (line) {
                    const callback = this.queue.shift();
                    if (callback) {
                        try {
                            const parsed = JSON.parse(line);
                            if (parsed.error) {
                                callback(new Error(parsed.error));
                            } else {
                                callback(null, parsed);
                            }
                        } catch (e) {
                            callback(new Error(`Failed to parse prediction response: ${e.message}`));
                        }
                    }
                }
                boundary = buffer.indexOf('\n');
            }
        });

        this.process.stderr.on('data', (data) => {
            console.error(`Predictor background worker error stream: ${data}`);
        });

        this.process.on('close', (code) => {
            console.warn(`Predictor process exited with code ${code}`);
            // Reject any pending promises in the queue
            const oldQueue = this.queue;
            this.queue = [];
            for (const cb of oldQueue) {
                cb(new Error('Predictor process exited unexpectedly.'));
            }
            // Auto-restart after 1 second
            setTimeout(() => this.startProcess(), 1000);
        });
    }

    predict(inputData) {
        return new Promise((resolve, reject) => {
            if (!this.process || this.process.killed) {
                return reject(new Error('Prediction background process is not running.'));
            }

            this.queue.push((err, result) => {
                if (err) reject(err);
                else resolve(result);
            });

            this.process.stdin.write(JSON.stringify(inputData) + '\n');
        });
    }
}

// Export a singleton instance
module.exports = new Predictor();
