import platform, os
import asyncio

from sources.utility import pretty_print, animate_thinking
from sources.agents.agent import Agent, executorResult
from sources.tools.C_Interpreter import CInterpreter
from sources.tools.GoInterpreter import GoInterpreter
from sources.tools.PyInterpreter import PyInterpreter
from sources.tools.BashInterpreter import BashInterpreter
from sources.tools.JavaInterpreter import JavaInterpreter
from sources.tools.fileFinder import FileFinder
from sources.logger import Logger
from sources.memory import Memory
from sources.sandbox import Sandbox

class CoderAgent(Agent):
    """
    The code agent is an agent that can write and execute code.
    """
    def __init__(self, name, prompt_path, provider, verbose=False, use_sandbox=True):
        super().__init__(name, prompt_path, provider, verbose, None)
        self.tools = {
            "bash": BashInterpreter(),
            "python": PyInterpreter(),
            "c": CInterpreter(),
            "go": GoInterpreter(),
            "java": JavaInterpreter(),
            "file_finder": FileFinder()
        }
        self.work_dir = self.tools["file_finder"].get_work_dir()
        self.use_sandbox = use_sandbox
        if self.use_sandbox:
            self.sandbox = Sandbox(work_dir=self.work_dir)
        else:
            self.sandbox = None
        self.role = "code"
        self.type = "code_agent"
        self.logger = Logger("code_agent.log")
        self.memory = Memory(self.load_prompt(prompt_path),
                        recover_last_session=False, # session recovery in handled by the interaction class
                        memory_compression=False,
                        model_provider=provider.get_model_name())
    
    def add_sys_info_prompt(self, prompt):
        """Add system information to the prompt."""
        info = (
            f"System Info:\n"
            f"OS: {platform.system()} {platform.release()}\n"
            f"Python Version: {platform.python_version()}\n"
            f"Environment: Server headless (tanpa display/GUI)\n"
            f"Direktori kerja: {self.work_dir}\n"
            f"Library tersedia: flask, requests, beautifulsoup4, numpy, sqlite3, json, csv, dan library standar Python\n"
            f"\nATURAN WAJIB:\n"
            f"- Simpan semua file di direktori kerja dengan format ```bahasa:namafile\n"
            f"- JANGAN jalankan pip install atau npm install via bash\n"
            f"- JANGAN gunakan Tkinter atau library GUI desktop\n"
            f"- JANGAN jalankan server (python app.py, flask run) via bash\n"
            f"- JANGAN tulis app.run() atau if __name__ == '__main__' di kode Python\n"
            f"- Port 5000 SUDAH DIGUNAKAN oleh sistem. JANGAN pernah bind ke port 5000\n"
            f"- Untuk website: buat sebagai HTML statis lengkap (HTML+CSS+JS dalam satu file)\n"
            f"- Untuk backend: simpan file saja tanpa app.run(), jangan jalankan server\n"
            f"- Untuk kalkulator/tools: buat sebagai HTML+CSS+JS statis yang bisa dibuka langsung di browser\n"
            f"- SELALU buat kode yang LENGKAP, FUNGSIONAL, dan SIAP PAKAI"
        )
        return f"{prompt}\n\n{info}"

    def sandbox_execute(self, code: str, language: str) -> tuple:
        if self.sandbox is None:
            return None, None
        if language not in ('python', 'bash'):
            return None, None
        result = self.sandbox.run(code, language)
        feedback = self.sandbox.format_result(result)
        return result.success, feedback

    def execute_modules_with_sandbox(self, answer: str):
        feedback = ""
        success = True
        if answer.startswith("```"):
            answer = "I will execute:\n" + answer

        self.success = True
        for name, tool in self.tools.items():
            feedback = ""
            blocks, save_path = tool.load_exec_block(answer)

            if blocks is not None:
                pretty_print(f"Executing {len(blocks)} {name} blocks (sandbox)...", color="status")
                for block in blocks:
                    self.show_block(block)
                    if name in ('python', 'bash'):
                        sb_success, sb_feedback = self.sandbox_execute(block, name)
                        if sb_success is not None:
                            success = sb_success
                            feedback = sb_feedback
                            self.blocks_result.append(executorResult(block, feedback, success, name))
                            if not success:
                                self.success = False
                                self.memory.push('user', feedback)
                                return False, feedback
                            continue
                    output = tool.execute([block])
                    feedback = tool.interpreter_feedback(output)
                    success = not tool.execution_failure_check(output)
                    self.blocks_result.append(executorResult(block, feedback, success, name))
                    if not success:
                        self.success = False
                        self.memory.push('user', feedback)
                        return False, feedback
                self.memory.push('user', feedback)
                if save_path is not None:
                    tool.save_block(blocks, save_path)
        return True, feedback

    def _build_debug_prompt(self, feedback, attempt, max_attempts):
        return (
            f"KODE SEBELUMNYA GAGAL (percobaan {attempt}/{max_attempts}).\n"
            f"Error yang terjadi:\n{feedback}\n\n"
            f"INSTRUKSI DEBUGGING:\n"
            f"1. Analisis error message di atas dengan teliti\n"
            f"2. Identifikasi akar penyebab error\n"
            f"3. Tulis ulang kode yang SUDAH DIPERBAIKI secara LENGKAP\n"
            f"4. Jangan hanya memberikan potongan - tulis SELURUH kode yang diperbaiki\n"
            f"5. Pastikan semua import, dependensi, dan syntax sudah benar\n"
            f"6. Jika error berulang, coba pendekatan/library yang berbeda"
        )

    async def process(self, prompt, speech_module) -> str:
        answer = ""
        attempt = 0
        max_attempts = 7
        prompt = self.add_sys_info_prompt(prompt)
        self.memory.push('user', prompt)
        clarify_trigger = "REQUEST_CLARIFICATION"
        original_prompt = prompt
        no_code_retries = 0

        while attempt < max_attempts and not self.stop:
            self.logger.info(f"Attempt {attempt + 1}/{max_attempts}")
            animate_thinking("Thinking...", color="status")
            self.status_message = f"Berpikir... (percobaan {attempt + 1}/{max_attempts})"
            await self.wait_message(speech_module)
            answer, reasoning = await self.llm_request()
            self.last_reasoning = reasoning
            if clarify_trigger in answer:
                self.last_answer = answer
                await asyncio.sleep(0)
                return answer, reasoning
            if "```" not in answer:
                if no_code_retries < 2 and any(kw in original_prompt.lower() for kw in [
                    'buatkan', 'buat ', 'create', 'make', 'write', 'build', 'coding',
                    'website', 'aplikasi', 'program', 'script', 'game', 'kalkulator',
                    'deploy', 'full stack', 'fullstack', 'api', 'server', 'debug',
                    'perbaiki', 'fix', 'error'
                ]):
                    self.memory.push('user',
                        'Kamu belum menulis kode. WAJIB tulis kode LENGKAP sekarang dalam blok ```bahasa:namafile.ext```.\n'
                        'Contoh: ```python:app.py atau ```html:index.html\n'
                        'Tulis SEMUA kode yang dibutuhkan, lengkap dan siap jalan. JANGAN jelaskan, langsung tulis kode.'
                    )
                    no_code_retries += 1
                    attempt += 1
                    continue
                self.last_answer = answer
                await asyncio.sleep(0)
                break
            no_code_retries = 0
            self.show_answer()
            animate_thinking("Executing code...", color="status")
            self.status_message = f"Menjalankan kode... (percobaan {attempt + 1}/{max_attempts})"
            self.logger.info(f"Attempt {attempt + 1}:\n{answer}")
            exec_success, feedback = self.execute_modules_with_sandbox(answer) if self.use_sandbox else self.execute_modules(answer)
            self.logger.info(f"Execution result: {exec_success}")
            answer = self.remove_blocks(answer)
            self.last_answer = answer
            await asyncio.sleep(0)
            if exec_success:
                self.status_message = "Selesai"
                break
            pretty_print(f"Execution failure:\n{feedback}", color="failure")
            pretty_print("Auto-debugging...", color="status")
            self.status_message = f"Auto-debugging... (percobaan {attempt + 1}/{max_attempts})"
            debug_prompt = self._build_debug_prompt(feedback, attempt + 1, max_attempts)
            self.memory.push('user', debug_prompt)
            self.logger.info(f"Debug prompt sent for attempt {attempt + 1}")
            attempt += 1
        self.status_message = "Siap"
        if attempt == max_attempts:
            return "Maaf, saya sudah mencoba beberapa kali tapi belum berhasil. Silakan berikan detail lebih lanjut agar saya bisa membantu.", reasoning
        self.last_answer = answer
        return answer, reasoning

if __name__ == "__main__":
    pass