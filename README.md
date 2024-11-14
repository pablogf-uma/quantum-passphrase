# Random Quantum Passphrase Generator

## Input:
- Number of qubits that will compose the quantum circuit.
- Number of words included in the generated passphrase.

## How does it work?
1 - Creates a quantum circuit in complete superposition by placing a Hadamard gate in each qubit.

2 - Measures (and therefore collapses) each qubit, generating a random bitstring as output.

3 - Locates the circuit's output bitstring in [Datamuse API](https://www.datamuse.com/api/) to specify which is the randomly selected word.

4 - Generates the output passphrase based on the randomly selected word and the "n - 1" following words per the API index.
