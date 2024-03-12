from src.eval.envs.env import Env


class MathEnv(Env):
    async def init(self, init_params: dict) -> str:
        pass

    @staticmethod
    def _multiply(first_int: int, second_int: int) -> int:
        """Multiply two integers together."""
        return first_int * second_int

    @staticmethod
    def _add(first_int: int, second_int: int) -> int:
        "Add two integers."
        return first_int + second_int

    @staticmethod
    def _exponentiate(base: int, exponent: int) -> int:
        "Exponentiate the base to the exponent power."
        return base ** exponent

    async def run_command(self, command_name: str, command_params: dict) -> int:
        if command_name == 'multiply':
            first_int = command_params['first_int']
            second_int = command_params['second_int']
            return self._multiply(first_int, second_int)
        elif command_name == 'add':
            first_int = command_params['first_int']
            second_int = command_params['second_int']
            return self.add(first_int, second_int)
        elif command_name == 'exponentiate':
            base = command_params['base']
            exponent = command_params['exponent']
            return self._exponentiate(base, exponent)
        else:
            print("Unknown command")

    async def get_tools(self) -> list[dict]:
        return [{
            "type": "function",
            "function": {
                "name": "multiply",
                "description": "Multiply two integers together.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "first_int": {
                            "type": "integer",
                            "description": "First integer",
                        },
                        "second_int": {
                            "type": "integer",
                            "description": "Second integer",
                        },
                    },
                    "required": ["first_int", "second_int"],
                },
            }
        }, {
            "type": "function",
            "function": {
                "name": "add",
                "description": "Add two integers together.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "first_int": {
                            "type": "integer",
                            "description": "First integer",
                        },
                        "second_int": {
                            "type": "integer",
                            "description": "Second integer",
                        },
                    },
                    "required": ["first_int", "second_int"],
                },
            }
        }, {
            "type": "function",
            "function": {
                "name": "exponentiate",
                "description": "Exponentiate the base to the exponent power.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "base": {
                            "type": "integer",
                            "description": "Base integer",
                        },
                        "exponent": {
                            "type": "integer",
                            "description": "Exponent integer",
                        },
                    },
                    "required": ["base", "exponent"],
                },
            }
        }]

    async def get_state(self) -> str:
        pass
