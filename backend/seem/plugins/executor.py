import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, Callable
from enum import Enum


class PluginType(str, Enum):
    SKILL_EXECUTION = "skill_execution"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    EXTERNAL_SERVICE = "external_service"


@dataclass
class Plugin:
    id: str
    name: str
    plugin_type: PluginType
    description: str = ""
    execute_fn: Optional[Callable] = None
    enabled: bool = True

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled:
            raise RuntimeError(f"Plugin {self.id} is disabled")

        if not self.execute_fn:
            raise RuntimeError(f"Plugin {self.id} has no execute function")

        return await self.execute_fn(input_data)


class ExecutionEngine:
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.execution_history: list[Dict[str, Any]] = []

    def register_plugin(self, plugin: Plugin) -> None:
        self.plugins[plugin.id] = plugin

    def unregister_plugin(self, plugin_id: str) -> bool:
        if plugin_id in self.plugins:
            del self.plugins[plugin_id]
            return True
        return False

    def enable_plugin(self, plugin_id: str) -> bool:
        if plugin_id in self.plugins:
            self.plugins[plugin_id].enabled = True
            return True
        return False

    def disable_plugin(self, plugin_id: str) -> bool:
        if plugin_id in self.plugins:
            self.plugins[plugin_id].enabled = False
            return True
        return False

    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        return self.plugins.get(plugin_id)

    def list_plugins(self, plugin_type: Optional[PluginType] = None) -> list[Plugin]:
        plugins = list(self.plugins.values())
        if plugin_type:
            plugins = [p for p in plugins if p.plugin_type == plugin_type]
        return plugins

    async def execute_plugin(
        self,
        plugin_id: str,
        input_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            raise ValueError(f"Plugin {plugin_id} not found")

        if not plugin.enabled:
            raise RuntimeError(f"Plugin {plugin_id} is disabled")

        start_time = time.time()

        try:
            result = await plugin.execute(input_data)
            execution_time = (time.time() - start_time) * 1000

            execution_record = {
                "plugin_id": plugin_id,
                "plugin_name": plugin.name,
                "success": True,
                "result": result,
                "execution_time_ms": execution_time,
                "metadata": metadata or {},
                "timestamp": time.time(),
            }

            self.execution_history.append(execution_record)
            return result

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000

            execution_record = {
                "plugin_id": plugin_id,
                "plugin_name": plugin.name,
                "success": False,
                "error": str(e),
                "execution_time_ms": execution_time,
                "metadata": metadata or {},
                "timestamp": time.time(),
            }

            self.execution_history.append(execution_record)
            raise

    def get_execution_history(self, plugin_id: Optional[str] = None, limit: int = 50) -> list[Dict[str, Any]]:
        history = self.execution_history

        if plugin_id:
            history = [r for r in history if r["plugin_id"] == plugin_id]

        return history[-limit:]

    def get_plugin_statistics(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        history = [r for r in self.execution_history if r["plugin_id"] == plugin_id]

        if not history:
            return None

        total = len(history)
        successful = sum(1 for r in history if r["success"])
        failed = total - successful

        avg_time = sum(r.get("execution_time_ms", 0) for r in history) / total if total > 0 else 0

        return {
            "plugin_id": plugin_id,
            "total_executions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0.0,
            "average_execution_time_ms": avg_time,
        }
