from flask import Flask, jsonify
from braket.circuits import Circuit
from braket.devices import LocalSimulator
import requests

app = Flask(__name__)

# Storage for the bitstring to use between endpoints
cached_bitstring = None

# Generate random bits from a quantum circuit
def generate_random_bits(n_qubits = 20):
    qc = Circuit().h(range(n_qubits))
    device = LocalSimulator()
    result = device.run(qc, shots=1).result()
    bitstring = result.measurements[0].tolist()
    return bitstring

# Convert bits to a numerical index
def bits_to_index(bitstring):
    bitstring_int = int(''.join(map(str, bitstring)), 2)
    return bitstring_int

# Use this index to search a word in Datamuse API
DATAMUSE_API = "https://api.datamuse.com/words"
def get_100_words():
    parameters = {'rel_jja': 'common', 'max': 100}
    response = requests.get(DATAMUSE_API, params=parameters)
    if response.status_code == 200:
        words = [word['word'] for word in response.json()]
        return words
    else:
        raise Exception("Error retrieving data from Datamuse API")

@app.route('/generate-random-bits', methods=['GET'])
def generate_random_bits_endpoint():
    global cached_bitstring
    try:
        # Generate random bits from a quantum circuit
        cached_bitstring = generate_random_bits()
        
        # Return the result
        return jsonify({
            "random_bits": ''.join(map(str, cached_bitstring)),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/generate-passphrase', methods=['GET'])
def generate_passphrase():
    global cached_bitstring
    try:
            # Convertbitstring to index
            index = bits_to_index(cached_bitstring)
            
            # Get the word list and select a word based on the index
            words = get_100_words()
            selected_word = words[index % len(words)]  # Ensure the index is within bounds
            
            # Create a passprhase from that selected word and the next 9
            passphrase = [selected_word]

            for i in range(1,10):
                passphrase.append(words[(index + i) % len(words)])

            # Return the result as a JSON response
            return jsonify({
                'passphrase': '-'.join(map(str, passphrase))
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)