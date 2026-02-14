let angka1 = '';
let angka2 = '';
let operator = '';

function tombolKlik(tombol) {
    const nilaiTombol = tombol.innerHTML;
    if (nilaiTombol === '+' || nilaiTombol === '-' || nilaiTombol === '*' || nilaiTombol === '/') {
        angka1 = document.getElementById('layar').value;
        operator = nilaiTombol;
        document.getElementById('layar').value = '';
    } else if (nilaiTombol === '=') {
        angka2 = document.getElementById('layar').value;
        const hasil = eval(angka1 + operator + angka2);
        document.getElementById('layar').value = hasil;
    } else {
        document.getElementById('layar').value += nilaiTombol;
    }
}

function hapus() {
    document.getElementById('layar').value = '';
    angka1 = '';
    angka2 = '';
    operator = '';
}
