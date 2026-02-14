import asyncio
import time
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from sources.logger import Logger
from sources.utility import pretty_print, animate_thinking
from sources.persistent_memory import PersistentMemory


@dataclass
class TaskStep:
    id: int
    description: str
    agent_type: str
    status: str = "pending"
    result: str = ""
    error: str = ""
    attempts: int = 0
    max_attempts: int = 3
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ExecutionPlan:
    goal: str
    steps: List[TaskStep] = field(default_factory=list)
    current_step: int = 0
    completed: bool = False
    reflection_log: List[str] = field(default_factory=list)
    start_time: float = 0.0

    def get_next_step(self) -> Optional[TaskStep]:
        for step in self.steps:
            if step.status == "pending":
                deps_met = True
                for dep_id in step.dependencies:
                    dep_step = next((s for s in self.steps if str(s.id) == str(dep_id)), None)
                    if dep_step and dep_step.status != "completed":
                        deps_met = False
                        break
                if deps_met:
                    return step
        return None

    def mark_step_done(self, step_id: int, result: str):
        for step in self.steps:
            if step.id == step_id:
                step.status = "completed"
                step.result = result
                return

    def mark_step_failed(self, step_id: int, error: str):
        for step in self.steps:
            if step.id == step_id:
                step.attempts += 1
                if step.attempts >= step.max_attempts:
                    step.status = "failed"
                else:
                    step.status = "pending"
                step.error = error
                return

    def is_complete(self) -> bool:
        return all(s.status in ("completed", "failed") for s in self.steps)

    def get_progress_text(self) -> str:
        lines = [f"**Rencana: {self.goal}**\n"]
        for step in self.steps:
            icon = {"pending": "...", "completed": "[OK]", "failed": "[X]", "running": "[~]"}.get(step.status, "...")
            lines.append(f"{icon} Langkah {step.id}: [{step.agent_type.upper()}] {step.description} ({step.status})")
        elapsed = time.time() - self.start_time if self.start_time else 0
        if elapsed > 0:
            lines.append(f"\nWaktu: {elapsed:.1f}s")
        return "\n".join(lines)

    def get_progress_data(self) -> List[Dict]:
        return [
            {
                "id": step.id,
                "description": step.description,
                "agent_type": step.agent_type,
                "status": step.status,
                "attempts": step.attempts,
            }
            for step in self.steps
        ]

    def get_success_rate(self) -> float:
        if not self.steps:
            return 0.0
        completed = sum(1 for s in self.steps if s.status == "completed")
        return completed / len(self.steps)


class AutonomousOrchestrator:
    def __init__(self, agents: dict, provider, ws_manager=None):
        self.agents = agents
        self.provider = provider
        self.logger = Logger("orchestrator.log")
        self.plan: Optional[ExecutionPlan] = None
        self.execution_memory: List[Dict] = []
        self.status_message = "Idle"
        self.last_answer = ""
        self.ws_manager = ws_manager
        self.persistent_memory = PersistentMemory()

    async def _notify_status(self, agent_name: str, status: str, progress: float = 0.0, details: str = ""):
        if self.ws_manager:
            try:
                await self.ws_manager.send_status(agent_name, status, progress, details)
            except Exception:
                pass

    async def _notify_plan(self, current_step: int = 0):
        if self.ws_manager and self.plan:
            try:
                await self.ws_manager.send_plan_update(self.plan.get_progress_data(), current_step)
            except Exception:
                pass

    def create_plan_from_tasks(self, goal: str, agent_tasks: list) -> ExecutionPlan:
        plan = ExecutionPlan(goal=goal, start_time=time.time())
        for i, (task_name, task_info) in enumerate(agent_tasks):
            deps = task_info.get('need', [])
            if isinstance(deps, str):
                deps = [deps] if deps else []
            step = TaskStep(
                id=i + 1,
                description=task_info.get('task', task_name),
                agent_type=task_info.get('agent', 'coder'),
                dependencies=deps,
            )
            plan.steps.append(step)
        self.plan = plan
        self.logger.info(f"Plan created with {len(plan.steps)} steps for: {goal}")
        return plan

    async def execute_step(self, step: TaskStep, required_infos: dict = None) -> Tuple[str, bool]:
        step.status = "running"
        agent_key = step.agent_type.lower()
        if agent_key not in self.agents:
            for key in self.agents:
                if key.startswith(agent_key[:3]):
                    agent_key = key
                    break
            else:
                agent_key = "coder"

        agent = self.agents[agent_key]
        prompt = step.description

        if required_infos:
            context_parts = []
            for k, v in required_infos.items():
                context_parts.append(f"- Hasil langkah {k}: {v}")
            prompt = (
                f"Konteks dari langkah sebelumnya:\n"
                f"{''.join(context_parts)}\n\n"
                f"Tugas kamu sekarang:\n{step.description}\n\n"
                f"INSTRUKSI: Langsung kerjakan tanpa bertanya. Gunakan informasi dari langkah sebelumnya."
            )

        if step.error and step.attempts > 0:
            prompt += (
                f"\n\nPERINGATAN: Percobaan sebelumnya GAGAL dengan error:\n{step.error[:500]}\n"
                f"Gunakan PENDEKATAN BERBEDA kali ini. Jangan ulangi cara yang sama."
            )

        memory_context = self.persistent_memory.get_context_for_prompt(step.description)
        if memory_context:
            prompt += f"\n{memory_context}"

        self.logger.info(f"Executing step {step.id}: {step.description} with agent {agent_key}")
        self.status_message = f"Langkah {step.id}: {step.description}"

        total_steps = len(self.plan.steps) if self.plan else 1
        await self._notify_status("orchestrator", f"Langkah {step.id}/{total_steps}",
                                   step.id / total_steps, step.description[:100])

        try:
            answer, reasoning = await agent.process(prompt, None)
            success = agent.get_success

            self.execution_memory.append({
                "step_id": step.id,
                "agent": agent_key,
                "success": success,
                "answer_preview": (answer or "")[:200],
                "timestamp": time.time(),
            })

            if success:
                self.persistent_memory.store_fact(
                    "execution_success",
                    f"Langkah '{step.description[:100]}' berhasil dengan agent {agent_key}",
                    "orchestrator"
                )

            return answer, success
        except Exception as e:
            self.logger.error(f"Step {step.id} error: {str(e)}")
            return f"Error: {str(e)}", False

    def reflect(self, step: TaskStep, result: str, success: bool) -> str:
        reflection = ""
        if success:
            reflection = f"Langkah {step.id} berhasil: {step.description}"
            step.status = "completed"
            step.result = result
        else:
            step.attempts += 1
            if step.attempts >= step.max_attempts:
                reflection = f"Langkah {step.id} gagal setelah {step.max_attempts} percobaan: {step.description}"
                step.status = "failed"
                step.error = result
            else:
                reflection = f"Langkah {step.id} gagal (percobaan {step.attempts}/{step.max_attempts}), akan dicoba lagi"
                step.status = "pending"
                step.error = result

        if self.plan:
            self.plan.reflection_log.append(reflection)
        self.logger.info(f"Reflection: {reflection}")
        return reflection

    def revise_plan(self, failed_step: TaskStep) -> None:
        if not self.plan:
            return

        alternative_agents = {
            "coder": "file",
            "file": "coder",
            "web": "casual",
            "casual": "coder",
        }
        alt_agent = alternative_agents.get(failed_step.agent_type.lower(), failed_step.agent_type)

        retry_step = TaskStep(
            id=len(self.plan.steps) + 1,
            description=f"[RECOVERY] Coba lagi: {failed_step.description} (pendekatan berbeda, tanpa ulangi error sebelumnya)",
            agent_type=alt_agent,
            max_attempts=2,
            dependencies=failed_step.dependencies,
        )
        self.plan.steps.append(retry_step)
        self.logger.info(f"Plan revised: recovery step {retry_step.id} (agent: {alt_agent}) for failed step {failed_step.id}")

    async def run_loop(self, goal: str, agent_tasks: list, speech_module=None) -> str:
        plan = self.create_plan_from_tasks(goal, agent_tasks)
        work_results = {}
        final_answer = ""

        pretty_print(f"\n>> AUTONOMOUS MODE: {len(plan.steps)} langkah", color="status")
        pretty_print(plan.get_progress_text(), color="info")

        await self._notify_status("orchestrator", "Memulai eksekusi otonom", 0.0, f"{len(plan.steps)} langkah")
        await self._notify_plan(0)

        max_iterations = len(plan.steps) * 4
        iteration = 0
        consecutive_failures = 0

        while not plan.is_complete() and iteration < max_iterations:
            step = plan.get_next_step()
            if step is None:
                has_pending = any(s.status == "pending" for s in plan.steps)
                if has_pending:
                    self.logger.warning("Dependency deadlock detected - marking blocked steps as failed")
                    for s in plan.steps:
                        if s.status == "pending":
                            s.status = "failed"
                            s.error = "Dependency deadlock: langkah yang dibutuhkan gagal"
                break

            iteration += 1
            pretty_print(f"\n>> Langkah {step.id}/{len(plan.steps)}: {step.description}", color="status")
            self.last_answer = plan.get_progress_text()
            await self._notify_plan(step.id)

            required_infos = {}
            for prev_step in plan.steps:
                if str(prev_step.id) in step.dependencies and prev_step.status == "completed":
                    required_infos[str(prev_step.id)] = prev_step.result[:500] if prev_step.result else ""

            if not required_infos:
                for prev_step in plan.steps:
                    if prev_step.id < step.id and prev_step.status == "completed":
                        required_infos[str(prev_step.id)] = prev_step.result[:300] if prev_step.result else ""

            result, success = await self.execute_step(step, required_infos if required_infos else None)

            reflection = self.reflect(step, result, success)
            pretty_print(f">> {reflection}", color="info" if success else "warning")

            if success:
                consecutive_failures = 0
            else:
                consecutive_failures += 1

            if not success and step.status == "failed":
                if consecutive_failures < 3:
                    self.revise_plan(step)
                else:
                    self.logger.warning(f"Too many consecutive failures ({consecutive_failures}), skipping recovery")

            work_results[str(step.id)] = result
            if success:
                final_answer = result

            self.last_answer = plan.get_progress_text()
            await self._notify_plan(step.id)

        completed = sum(1 for s in plan.steps if s.status == "completed")
        total = len(plan.steps)
        elapsed = time.time() - plan.start_time

        pretty_print(f"\n>> Selesai: {completed}/{total} langkah berhasil ({elapsed:.1f}s)", color="success" if completed == total else "warning")

        await self._notify_status("orchestrator", f"Selesai: {completed}/{total}", 1.0,
                                   f"Waktu: {elapsed:.1f}s")

        self.persistent_memory.store_project(
            name=goal[:100],
            project_type="autonomous",
            path="",
            description=f"{completed}/{total} langkah berhasil",
            status="completed" if completed == total else "partial"
        )

        summary_lines = [plan.get_progress_text(), "\n---\n"]
        summary_lines.append(f"**Hasil:** {completed}/{total} langkah selesai dalam {elapsed:.1f} detik")

        if plan.reflection_log:
            summary_lines.append("\n**Log refleksi:**")
            for log_entry in plan.reflection_log[-5:]:
                summary_lines.append(f"  - {log_entry}")

        if final_answer:
            summary_lines.append(f"\n\n**Hasil akhir:**\n{final_answer}")

        self.last_answer = "\n".join(summary_lines)
        return self.last_answer
