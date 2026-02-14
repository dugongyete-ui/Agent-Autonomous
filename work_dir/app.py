from flask import Flask, jsonify, request
import json

app = Flask(__name__)

# Data kalkulator
data_kalkulator = {
    "hasil": None,
    "error": None
}

# Route untuk menghitung
@app.route('/kalkulator', methods=['POST'])
def kalkulator():
    global data_kalkulator
    try:
        data = json.loads(request.data)
        angka1 = float(data['angka1'])
        angka2 = float(data['angka2'])
        operator = data['operator']

        if operator == '+':
            hasil = angka1 + angka2
        elif operator == '-':
            hasil = angka1 - angka2
        elif operator == '*':
            hasil = angka1 * angka2
        elif operator == '/':
            if angka2 != 0:
                hasil = angka1 / angka2
            else:
                data_kalkulator['error'] = 'Pembagian dengan nol!'
                return jsonify(data_kalkulator)
        else:
            data_kalkulator['error'] = 'Operator tidak valid!'
            return jsonify(data_kalkulator)

        data_kalkulator['hasil'] = hasil
        return jsonify(data_kalkulator)
    except Exception as e:
        data_kalkulator['error'] = str(e)
        return jsonify(data_kalkulator)

if __name__ == '__main__':
    app.run(port=5001)
