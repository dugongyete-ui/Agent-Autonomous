import asyncio
import time
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from sources.logger import Logger
from sources.utility import pretty_print, animate_thinking


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


@dataclass
class ExecutionPlan:
    goal: str
    steps: List[TaskStep] = field(default_factory=list)
    current_step: int = 0
    completed: bool = False
    reflection_log: List[str] = field(default_factory=list)

    def get_next_step(self) -> Optional[TaskStep]:
        for step in self.steps:
            if step.status == "pending":
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
            icon = {"pending": "⏳", "completed": "✅", "failed": "❌", "running": "🔄"}.get(step.status, "⏳")
            lines.append(f"{icon} Langkah {step.id}: [{step.agent_type.upper()}] {step.description} ({step.status})")
        return "\n".join(lines)


class AutonomousOrchestrator:
    def __init__(self, agents: dict, provider):
        self.agents = agents
        self.provider = provider
        self.logger = Logger("orchestrator.log")
        self.plan: Optional[ExecutionPlan] = None
        self.memory: List[Dict] = []
        self.status_message = "Idle"
        self.last_answer = ""

    def create_plan_from_tasks(self, goal: str, agent_tasks: list) -> ExecutionPlan:
        plan = ExecutionPlan(goal=goal)
        for i, (task_name, task_info) in enumerate(agent_tasks):
            step = TaskStep(
                id=i + 1,
                description=task_info.get('task', task_name),
                agent_type=task_info.get('agent', 'coder'),
            )
            plan.steps.append(step)
        self.plan = plan
        self.logger.info(f"Plan created with {len(plan.steps)} steps for: {goal}")
        return plan

    async def execute_step(self, step: TaskStep, required_infos: dict = None) -> Tuple[str, bool]:
        step.status = "running"
        agent_key = step.agent_type.lower()
        if agent_key not in self.agents:
            agent_key = "coder"

        agent = self.agents[agent_key]
        prompt = step.description
        if required_infos:
            context = "\n".join([f"- Info dari langkah {k}: {v}" for k, v in required_infos.items()])
            prompt = f"Konteks dari langkah sebelumnya:\n{context}\n\nTugas kamu:\n{step.description}"

        self.logger.info(f"Executing step {step.id}: {step.description} with agent {agent_key}")
        self.status_message = f"Langkah {step.id}: {step.description}"

        try:
            answer, reasoning = await agent.process(prompt, None)
            success = agent.get_success
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
        retry_step = TaskStep(
            id=len(self.plan.steps) + 1,
            description=f"[RECOVERY] Coba lagi: {failed_step.description} (dengan pendekatan berbeda)",
            agent_type=failed_step.agent_type,
            max_attempts=2
        )
        self.plan.steps.append(retry_step)
        self.logger.info(f"Plan revised: added recovery step for failed step {failed_step.id}")

    async def run_loop(self, goal: str, agent_tasks: list, speech_module=None) -> str:
        plan = self.create_plan_from_tasks(goal, agent_tasks)
        work_results = {}
        final_answer = ""

        pretty_print(f"\n🚀 AUTONOMOUS MODE: {len(plan.steps)} langkah", color="status")
        pretty_print(plan.get_progress_text(), color="info")

        max_iterations = len(plan.steps) * 3
        iteration = 0

        while not plan.is_complete() and iteration < max_iterations:
            step = plan.get_next_step()
            if step is None:
                break

            iteration += 1
            pretty_print(f"\n🔄 Langkah {step.id}/{len(plan.steps)}: {step.description}", color="status")
            self.last_answer = plan.get_progress_text()

            required_infos = {}
            for prev_step in plan.steps:
                if prev_step.id < step.id and prev_step.status == "completed":
                    required_infos[str(prev_step.id)] = prev_step.result[:500]

            result, success = await self.execute_step(step, required_infos if required_infos else None)

            reflection = self.reflect(step, result, success)
            pretty_print(f"📝 {reflection}", color="info" if success else "warning")

            if not success and step.status == "failed":
                self.revise_plan(step)

            work_results[str(step.id)] = result
            if success:
                final_answer = result

            self.last_answer = plan.get_progress_text()

        completed = sum(1 for s in plan.steps if s.status == "completed")
        total = len(plan.steps)
        pretty_print(f"\n✅ Selesai: {completed}/{total} langkah berhasil", color="success" if completed == total else "warning")

        summary_lines = [plan.get_progress_text(), "\n---\n"]
        if final_answer:
            summary_lines.append(f"**Hasil akhir:**\n{final_answer}")
        self.last_answer = "\n".join(summary_lines)

        return self.last_answer
