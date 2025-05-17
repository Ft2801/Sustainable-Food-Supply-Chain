from dataclasses import dataclass, field
from model.operation_model import OperationModel
@dataclass
class Componente:
    prodotto_id: int
    trasformazioni: list[OperationModel] = field(default_factory=list)