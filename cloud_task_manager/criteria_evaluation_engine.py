
class InvalidSelCrit(Exception):
    def __init__(self, expression:str, e:Exception):
        super().__init__(f"Expression '{expression}' is invalid: {e}")

def eval_select_crit_expression(expression:str, info:dict) -> bool:
    """
    Verifies if a client matches the criteria for the task

    NOTE: unsafe function

    :param expression: boolean expression
    :type expression: str

    :param info: client info
    :type info: dict
    
    :returns: Ture if the client matches the criteria
    :rtype: bool

    :raises InvalidSelCrit: expression sysntax is not a valid python statement
    """
    if expression == "":
        return True
    try:
        return eval(expression, {"__builtins__": None}, info)
    except Exception as e:
        raise InvalidSelCrit(expression,e)
