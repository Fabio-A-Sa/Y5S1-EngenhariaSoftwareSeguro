from typing import Any
from pydantic import BaseModel, ValidationError

class User(BaseModel):
    
    username: str
    password: str
    
    def say_hello(self):
        return f"Hello, {self.username}!"
    
def model_cast[T: BaseModel](model: type[T], kwargs: Any):
    try:
        if not isinstance(kwargs, dict):
            raise ValueError(f"kwargs must be a dictionary, found {type(kwargs)}")
        
        instance = model(**kwargs)
        return instance
    
    except ValidationError:
        return None 
    except ValueError as e:
        raise e
        return None
