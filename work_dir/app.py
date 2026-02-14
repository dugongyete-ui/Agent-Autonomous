from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/kalkulator', methods=['POST'])
def kalkulator():
    data = request.json
    angka1 = data['angka1']
    angka2 = data['angka2']
    operator = data['operator']

    if operator == '+':
        result = angka1 + angka2
    elif operator == '-':
        result = angka1 - angka2
    elif operator == '*':
        result = angka1 * angka2
    elif operator == '/':
        if angka2 != 0:
            result = angka1 / angka2
        else:
            result = 'Error: Pembagian dengan nol!'
    else:
        result = 'Error: Operator tidak valid!'

    return jsonify({'hasil': result})
