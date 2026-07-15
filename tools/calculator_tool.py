import logging
import math
import re

logger = logging.getLogger(__name__)


class CalculatorTool:

    def calculate(self, expression: str) -> str:
        logger.info(f"[Calculator] Expression: {expression}")

        try:
            # Clean the expression
            cleaned = expression.strip()
            cleaned = re.sub(r'[^0-9+\-*/().%^ ]', '', cleaned)
            cleaned = cleaned.replace("^", "**")

            if not cleaned:
                return "No valid mathematical expression found."

            # Safe eval with only math functions allowed
            allowed = {
                "abs": abs, "round": round,
                "sqrt": math.sqrt, "pow": math.pow,
                "log": math.log, "log10": math.log10,
                "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "pi": math.pi, "e": math.e,
            }

            result = eval(cleaned, {"__builtins__": {}}, allowed)
            return f"Result: {expression} = {result}"

        except ZeroDivisionError:
            return "Error: Division by zero."
        except Exception as e:
            logger.error(f"[Calculator] Failed: {e}")
            return f"Could not calculate '{expression}': {str(e)}"


# Singleton
_calculator_instance = None


def get_calculator_tool() -> CalculatorTool:
    global _calculator_instance
    if _calculator_instance is None:
        _calculator_instance = CalculatorTool()
    return _calculator_instance