
class InvalidSelCrit(Exception):
    def __init__(self, expression:str, e:Exception):
        super().__init__(f"Expression '{expression}' is invalid: {e}")

# UNSAFE
def eval_select_crit_expression(expression:str, info:dict) -> bool:
    """
    Verifies if a client matches the criteria for the task

    :param expression: boolean expression
    :type expression: str

    :param info: client info
    :type info: dict

    :raises: InvalidSelCrit
    
    :returns: Ture if the client matches the criteria
    :rtype: bool
    """
    if expression == "":
        return True
    try:
        return eval(expression, {"__builtins__": None}, info)
    except Exception as e:
        raise InvalidSelCrit(expression,e)
