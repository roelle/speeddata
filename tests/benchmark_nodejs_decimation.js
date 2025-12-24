/**
 * Benchmark Node.js decimation pipeline for stripchart server
 */

// Decimation algorithms
function downsample(samples, factor) {
    const result = [];
    for (let i = 0; i < samples.length; i += factor) {
        result.push(samples[i]);
    }
    return result;
}

function average(samples, factor) {
    const result = [];
    for (let i = 0; i < samples.length; i += factor) {
        const window = samples.slice(i, i + factor);
        const sum = window.reduce((a, b) => a + b, 0);
        result.push(sum / window.length);
    }
    return result;
}

function minMax(samples, factor) {
    const result = [];
    for (let i = 0; i < samples.length; i += factor) {
        const window = samples.slice(i, i + factor);
        result.push(Math.min(...window));
        result.push(Math.max(...window));
    }
    return result;
}

function rms(samples, factor) {
    const result = [];
    for (let i = 0; i < samples.length; i += factor) {
        const window = samples.slice(i, i + factor);
        const sumSquares = window.reduce((a, b) => a + b * b, 0);
        result.push(Math.sqrt(sumSquares / window.length));
    }
    return result;
}

function benchmarkAlgorithm(name, func, samples, factor, iterations = 100) {
    const times = [];

    for (let i = 0; i < iterations; i++) {
        const start = process.hrtime.bigint();
        const result = func(samples, factor);
        const end = process.hrtime.bigint();
        times.push(Number(end - start) / 1e6); // Convert to ms
    }

    const avgTime = times.reduce((a, b) => a + b, 0) / times.length;
    const stdDev = Math.sqrt(
        times.map(t => Math.pow(t - avgTime, 2))
             .reduce((a, b) => a + b, 0) / times.length
    );
    const throughput = samples.length / (avgTime / 1000);

    return {
        name,
        avgMs: avgTime,
        stdMs: stdDev,
        throughput
    };
}

// Simulate Node.js event loop with concurrent WebSocket clients
function simulateEventLoop(numChannels, samplesPerSec, decimationFactor, numClients) {
    const samples = Array.from({ length: samplesPerSec }, () => Math.random());

    console.log('\n' + '='.repeat(60));
    console.log('Node.js Event Loop Simulation');
    console.log('='.repeat(60));
    console.log(`Channels: ${numChannels}`);
    console.log(`Input rate per channel: ${samplesPerSec} Hz`);
    console.log(`Decimation factor: ${decimationFactor}x`);
    console.log(`WebSocket clients: ${numClients}`);
    console.log(`Total input rate: ${numChannels * samplesPerSec} samples/sec`);
    console.log();

    // Simulate 1 second of operation
    const start = process.hrtime.bigint();

    for (let channel = 0; channel < numChannels; channel++) {
        // Receive from multicast (simulated)
        // Decimate
        const decimated = average(samples, decimationFactor);

        // Broadcast to all WebSocket clients (simulated)
        for (let client = 0; client < numClients; client++) {
            const payload = JSON.stringify({
                channel,
                data: decimated
            });
            // Simulate send (measure serialization overhead)
        }
    }

    const end = process.hrtime.bigint();
    const totalTimeMs = Number(end - start) / 1e6;
    const overheadPct = (totalTimeMs / 1000) * 100;

    console.log(`Total processing time: ${totalTimeMs.toFixed(2)}ms`);
    console.log(`CPU overhead: ${overheadPct.toFixed(1)}%`);

    if (overheadPct < 10) {
        console.log('✓ Event loop can handle load without blocking');
    } else if (overheadPct < 50) {
        console.log('⚠ Event loop under moderate load, monitor performance');
    } else {
        console.log('✗ Event loop BLOCKED, will drop packets/connections');
    }
}

// Main benchmark
console.log('='.repeat(60));
console.log('Stripchart Server Decimation Benchmark (Node.js)');
console.log('='.repeat(60));

const samplesPerSec = 5000;
const decimationFactor = 50;
const samples = Array.from({ length: samplesPerSec }, () => Math.random());

console.log(`\nInput rate: ${samplesPerSec} Hz`);
console.log(`Decimation factor: ${decimationFactor}x`);
console.log(`Target output: ${samplesPerSec / decimationFactor} Hz\n`);

const algorithms = [
    ['Downsample', downsample],
    ['Average', average],
    ['Min-Max', minMax],
    ['RMS', rms]
];

console.log('Single Channel Performance:');
console.log('-'.repeat(60));

for (const [name, func] of algorithms) {
    const result = benchmarkAlgorithm(name, func, samples, decimationFactor);
    console.log(`${result.name.padEnd(12)} ${result.avgMs.toFixed(3)}ms ± ${result.stdMs.toFixed(3)}ms (${result.throughput.toLocaleString()} samples/sec)`);
}

// Realistic scenarios
console.log('\n' + '='.repeat(60));
console.log('Realistic Load Scenarios');
console.log('='.repeat(60));

console.log('\nScenario 1: Light load (5 channels, 3 clients)');
simulateEventLoop(5, samplesPerSec, decimationFactor, 3);

console.log('\nScenario 2: Medium load (20 channels, 10 clients)');
simulateEventLoop(20, samplesPerSec, decimationFactor, 10);

console.log('\nScenario 3: Heavy load (100 channels, 20 clients)');
simulateEventLoop(100, samplesPerSec, decimationFactor, 20);

console.log('\n' + '='.repeat(60));
console.log('Conclusion:');
console.log('If CPU overhead < 50%, Node.js can handle decimation pipeline');
console.log('If CPU overhead > 80%, event loop blocking is HIGH RISK');
console.log('='.repeat(60));
