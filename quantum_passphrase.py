from flask import Flask, jsonify, render_template, request, session
from braket.circuits import Circuit
from braket.devices import LocalSimulator
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key allows for session between both endpoints


# Generate random bits from a quantum circuit
def generate_random_bits(n_qubits=20):
    qc = Circuit().h(range(n_qubits))
    device = LocalSimulator()
    result = device.run(qc, shots=1).result()
    bitstring = result.measurements[0].tolist()
    return bitstring

# Convert bits to a numerical index
def bits_to_index(bitstring):
    bitstring_int = int(''.join(map(str, bitstring)), 2)
    return bitstring_int

# Use index to search a word in Datamuse API
DATAMUSE_API = "https://api.datamuse.com/words"
def get_100_words():
    parameters = {'rel_jja': 'common', 'max': 100}
    response = requests.get(DATAMUSE_API, params=parameters)
    if response.status_code == 200:
        words = [word['word'] for word in response.json()]
        return words
    else:
        raise Exception("Error retrieving data from Datamuse API")


@app.route('/')
def index():
    # Retrieve the html form
    return render_template('index.html')

@app.route('/generate-random-bits', methods=['POST'])
def generate_random_bits_endpoint():
    try:
        # Retrieve the number of qubits specified by the user
        n_qubits = int(request.form['n_qubits'])

        # Generate random bits from a quantum circuit
        bitstring = generate_random_bits(n_qubits)
        session['cached_bitstring'] = bitstring  # Store the bitstring in the session

        # Get the word list and store it in the session
        words = get_100_words()
        session['words'] = words
        
        return jsonify({
            "random_bits": ''.join(map(str, bitstring))
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate-passphrase', methods=['POST'])
def generate_passphrase():
    try:
        # Retrieve number of words specified by the user
        n_words = int(request.form['n_words'])

        # Retrieve the cached bitstring from the session
        bitstring = session.get('cached_bitstring')
        if bitstring is None:
            return jsonify({"error": "No bitstring found. Please generate random bits first."}), 400

        # Convert bitstring to index
        index = bits_to_index(bitstring)
        
        # Get the word list and select a word based on the index
        words = session.get('words')
        selected_word = words[index % len(words)]  # Ensure the index is within bounds
        
        # Create a passphrase from that selected word and the next `n_words`
        passphrase = [selected_word]
        for i in range(1, n_words):
            passphrase.append(words[(index + i) % len(words)])

        return jsonify({
            'passphrase': '-'.join(passphrase)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
