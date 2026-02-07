from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, date, time
from typing import List, Optional
from uuid import uuid4

app = FastAPI(title="Nail Studio API")

# -----------------------
# esses são os modelos, broxas? Sim, mas são
# -----------------------

class Servico(BaseModel):
    id: str
    nome: str
    duracao_minutos: int
    preco: float


class AgendamentoCreate(BaseModel):
    cliente_nome: str
    servico_id: str
    data: date
    horario: time


class Agendamento(BaseModel):
    id: str
    cliente_nome: str
    servico: Servico
    data: date
    horario: time
    status: str
    criado_em: datetime


# -----------------------
# banco de dados de mentirinha, de mentira msm, pq nao funciona (eu acho)
# -----------------------

servicos_db: List[Servico] = [
    Servico(id="1", nome="Manicure Tradicional", duracao_minutos=60, preco=150.0),
    Servico(id="2", nome="Pedicure", duracao_minutos=60, preco=130.0),
]

agendamentos_db: List[Agendamento] = []

# -----------------------
# aq vc ve oq agendou, isso se agendou
# -----------------------

@app.get("/servicos", response_model=List[Servico])
def listar_servicos():
    return servicos_db


# -----------------------
# essa daq é do cliente, a rota dos pobres
# -----------------------

@app.post("/agendamentos", response_model=Agendamento)
def criar_agendamento(dados: AgendamentoCreate):
    servico = next((s for s in servicos_db if s.id == dados.servico_id), None)

    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    novo_agendamento = Agendamento(
        id=str(uuid4()),
        cliente_nome=dados.cliente_nome,
        servico=servico,
        data=dados.data,
        horario=dados.horario,
        status="pendente",
        criado_em=datetime.now()
    )

    agendamentos_db.append(novo_agendamento)
    return novo_agendamento


@app.get("/agendamentos/{agendamento_id}", response_model=Agendamento)
def buscar_agendamento(agendamento_id: str):
    agendamento = next((a for a in agendamentos_db if a.id == agendamento_id), None)

    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")

    return agendamento


@app.delete("/agendamentos/{agendamento_id}")
def cancelar_agendamento(agendamento_id: str):
    for agendamento in agendamentos_db:
        if agendamento.id == agendamento_id:
            agendamento.status = "cancelado"
            return {"mensagem": "Agendamento cancelado"}

    raise HTTPException(status_code=404, detail="Agendamento não encontrado")


# -----------------------
# eu acho q embaixo aq é a rota admin, eu só acho, não confie noq eu codei
# -----------------------

@app.get("/dashboard/agendamentos")
def listar_agendamentos(
    status: Optional[str] = None,
    data_filtro: Optional[date] = None
):
    resultado = agendamentos_db

    if status:
        resultado = [a for a in resultado if a.status == status]

    if data_filtro:
        resultado = [a for a in resultado if a.data == data_filtro]

    return resultado


@app.patch("/dashboard/agendamentos/{agendamento_id}/confirmar")
def confirmar_agendamento(agendamento_id: str):
    for agendamento in agendamentos_db:
        if agendamento.id == agendamento_id:
            if agendamento.status != "pendente":
                raise HTTPException(
                    status_code=400,
                    detail="Apenas agendamentos pendentes podem ser confirmados"
                )

            agendamento.status = "confirmado"
            return {"mensagem": "Agendamento confirmado"}

    raise HTTPException(status_code=404, detail="Agendamento não encontrado")


@app.patch("/dashboard/agendamentos/{agendamento_id}/finalizar")
def finalizar_agendamento(agendamento_id: str):
    for agendamento in agendamentos_db:
        if agendamento.id == agendamento_id:
            if agendamento.status != "confirmado":
                raise HTTPException(
                    status_code=400,
                    detail="Apenas agendamentos confirmados podem ser finalizados"
                )

            agendamento.status = "finalizado"
            return {"mensagem": "Agendamento finalizado"}

    raise HTTPException(status_code=404, detail="Agendamento não encontrado")


# nao teve nada broxa nesse codigo, acho eu