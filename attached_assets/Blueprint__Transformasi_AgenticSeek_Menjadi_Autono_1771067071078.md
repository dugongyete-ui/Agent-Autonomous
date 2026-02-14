# Blueprint: Transformasi AgenticSeek Menjadi Autonomous Full-Stack Engine

Untuk mencapai level Manus.im, Anda perlu menambahkan komponen-komponen berikut ke dalam struktur folder `sources/` Anda.

## 1. File Baru: `sources/orchestrator.py` (The Brain)
Saat ini, agen Anda bekerja secara linear. Manus bekerja secara **iteratif**. Anda butuh Orchestrator yang menjalankan loop: **Plan -> Execute -> Observe -> Reflect**.

```python
# Logic yang harus ada di orchestrator.py:
class AutonomousOrchestrator:
    def __init__(self, task):
        self.plan = self.planner.create_initial_plan(task)
        self.memory = []

    async def run_loop(self):
        while not self.is_task_complete():
            step = self.plan.get_next_step()
            result = await self.execute_step(step)
            self.memory.append(result)
            
            # REFLECTION: Ini kunci Manus. Agen melihat hasilnya, jika error, dia revisi plan.
            if "error" in result:
                self.plan = self.planner.revise_plan(self.plan, result)
            else:
                self.plan.mark_step_done(step)
```

## 2. File Baru: `sources/tools/terminal.py` (The Hands)
`CoderAgent` Anda saat ini hanya menulis file. Manus bisa menjalankan server, menginstal library, dan mengecek log. Anda butuh tool Terminal yang persisten (bukan sekadar `subprocess.run` yang mati setelah selesai).

**Yang harus ditambahkan:**
*   **Persistent Shell Session:** Gunakan library seperti `pexpect` atau `teletype` agar agen bisa menjalankan `npm start` dan tetap memantau outputnya sambil mengerjakan hal lain.
*   **Port Management:** Tool ini harus bisa mendeteksi jika agen menjalankan web server di port 3000 dan otomatis memberikan URL Replit-nya ke user.

## 3. File Baru: `sources/browser_engine.py` (The Eyes)
`BrowserAgent` Anda saat ini mungkin hanya melakukan pencarian. Manus menggunakan browser untuk **mengecek hasil kodingannya sendiri**.

**Alur Otonom:**
1.  `CoderAgent` membuat website React.
2.  `TerminalTool` menjalankan `npm start`.
3.  `BrowserEngine` membuka URL website tersebut secara headless.
4.  `BrowserEngine` mengambil screenshot dan log konsol browser.
5.  `Orchestrator` memberikan screenshot itu kembali ke `CoderAgent` untuk verifikasi visual.

## 4. Peningkatan Frontend: `PreviewPanel.tsx`
Anda harus membuat komponen di frontend yang bisa menampilkan:
*   **Terminal Live:** Stream output dari terminal backend menggunakan Socket.io.
*   **Browser Preview:** Iframe yang menampilkan hasil website yang sedang dibuat agen.

## 5. Prompt "Master System" (The Soul)
Ganti system prompt utama Anda dengan ini untuk memaksa agen bertindak otonom:

```text
"Anda adalah AI Agent Autonomous yang beroperasi di lingkungan Linux. 
Anda memiliki akses penuh ke Terminal, Browser, dan File System.
PRINSIP UTAMA:
1. JANGAN PERNAH bertanya 'bolehkah saya menginstal ini?' - LAKUKAN SAJA.
2. JANGAN PERNAH berhenti karena error - BACA ERRORNYA, PERBAIKI, COBA LAGI.
3. VERIFIKASI HASIL: Setelah membuat website, jalankan servernya, buka browser, dan pastikan tampilannya benar.
4. MANDIRI: Selesaikan seluruh proyek dari inisialisasi hingga siap pakai tanpa bantuan manusia."
```

## Tabel Struktur Folder Baru yang Direkomendasikan

| Path | Fungsi |
| :--- | :--- |
| `sources/orchestrator.py` | Mengatur alur kerja Plan-Reflect. |
| `sources/tools/terminal.py` | Eksekusi perintah shell persisten. |
| `sources/tools/web_viewer.py` | Mengambil screenshot hasil kodingan agen. |
| `workspace/` | Folder khusus tempat agen membangun proyek (agar tidak mengganggu kode utama). |

---
**Rekomendasi Replit:**
Karena Anda di Replit, gunakan **Replit Object Storage** untuk menyimpan "Long-term Memory" agen Anda agar dia tetap ingat proyek sebelumnya meskipun container di-restart.
