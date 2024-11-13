from flask import Flask, jsonify
from braket.circuits import Circuit
from braket.devices import LocalSimulator
import requests

app = Flask(__name__)

def generate_random_bits(n_qubits = 20):

    qc = Circuit().h(range(n_qubits))
    device = LocalSimulator()
    result = device.run(qc, shots=1).result()
    
    bitstring = result.measurements[0]
    return bitstring

def bits_to_index(bitstring):
    bitstring_int = int(''.join(map(str, bitstring)), 2)
    return bitstring_int

def get_word_from_index(index):
    response = requests.get(f"https://api.datamuse.com/words?sp=p*&max=1000")
    if response.status_code == 200:
        words = response.json()
        if words:
            # Use modulo to ensure index is within the range of words list
            selected_word = words[index % len(words)]['word']
            return selected_word
    return None

@app.route('/generate-random-bits', methods=['GET'])
def generate_random_bits_endpoint():
    try:
        # Generate random bits
        bitstring = generate_random_bits()
        # Convert bits to a numerical index
        index = bits_to_index(bitstring)
        # Fetch a word based on the index
        word = get_word_from_index(index)
        
        # Return the result
        if word:
            return jsonify({
                "random_bits": bitstring,
                "index": index,
                "selected_word": word
            })
        else:
            return jsonify({"error": "Failed to fetch word"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)