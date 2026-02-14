from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/kalkulator', methods=['POST'])
def kalkulator():
    data = request.get_json()
    bil1 = float(data['bil1'])
    bil2 = float(data['bil2'])
    operator = data['operator']

    if operator == '+':
        hasil = bil1 + bil2
    elif operator == '-':
        hasil = bil1 - bil2
    elif operator == '*':
        hasil = bil1 * bil2
    elif operator == '/':
        if bil2 != 0:
            hasil = bil1 / bil2
        else:
            return jsonify({'error': 'Tidak bisa membagi dengan nol'}), 400

    return jsonify({'hasil': hasil})
