from src.llm_agents.base import AgentTemplate

from .prompts import KPI_FORMULA_FINDER_SYSTEM_PROMPT, KPI_FORMULA_FINDER_TRIGGER_PROMPT


class KPIFormulaFinderAgent(AgentTemplate):
    @property
    def system(self):
        """System Prompt contains the description of the task the the agent need
        to achieve"""
        return KPI_FORMULA_FINDER_SYSTEM_PROMPT

    @property
    def trigger(self):
        """Trigger Prompt needs to contain {query} and {context} placeholders."""
        return KPI_FORMULA_FINDER_TRIGGER_PROMPT

    def _get_prompt(self, query):
        return [
            {"role": "system", "content": self.system},
            {
                "role": "user",
                "content": self.trigger.format(query=query),
            },
        ]
