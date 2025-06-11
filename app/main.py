from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
import requests
import io

from openpyxl import Workbook


app = FastAPI()

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BACKEND_URL = "https://mini-erp-y8nj.onrender.com/produtos"

class ProdutoRelatorio(BaseModel):
    nome: str
    quantidade: int

@app.get("/relatorio/estoque", response_model=list[ProdutoRelatorio])
def relatorio_estoque():
    response = requests.get(BACKEND_URL)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao buscar produtos")

    produtos = response.json()
    relatorio = []

    for produto in produtos:
        relatorio.append({
            "nome": produto.get("nome", "Sem nome"),
            "quantidade": produto.get("estoque", {}).get("quantidade", 0)
        })

    return relatorio


# Responsável por pegar o json e salvar em arquivo  excel 
@app.get("/relatorio/estoque/excel")
def relatorio_estoque_excel():
    response = requests.get(BACKEND_URL)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao buscar produtos")
    
    produtos = response.json()

    wb = Workbook()
    ws = wb.active
    ws.title = "Estoque"

    # Cabeçalho
    ws.append(["Nome do produto", "Quantidade"])

    # Preencher dados
    for produto in produtos:
        nome = produto.get("nome", "Sem nome")
        quantidade = produto.get("estoque", {}).get("quantidade", 0)
        ws.append([nome, quantidade])

    # Buffer para streaming
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=relatorio_estoque.xlsx"},)

# Responsável por pegar o json e salvar em arquivo pdf


@app.get("/relatorio/estoque/pdf")
def relatorio_estoque_pdf():
    response = requests.get(BACKEND_URL)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao buscar produtos.")

    produtos = response.json()

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    # Título
    pdf.setFont("Helvetica-Bold", 18)
    pdf.setFillColor(colors.darkblue)
    pdf.drawCentredString(largura / 2, altura - 2 * cm, "Relatório de Estoque")

    # Cabeçalho da tabela
    pdf.setFont("Helvetica-Bold", 12)
    pdf.setFillColor(colors.black)
    y = altura - 4 * cm
    pdf.drawString(2 * cm, y, "Produto")
    pdf.drawString(13 * cm, y, "Quantidade")
    pdf.line(2 * cm, y - 0.2 * cm, largura - 2 * cm, y - 0.2 * cm)

    # Listagem dos dados
    y -= 1 * cm
    pdf.setFont("Helvetica", 11)
    for produto in produtos:
        nome = produto.get("nome", "Sem nome")
        quantidade = produto.get("estoque", {}).get("quantidade", 0)

        pdf.drawString(2 * cm, y, nome)
        pdf.drawString(13 * cm, y, str(quantidade))
        y -= 0.8 * cm

        # Nova página se faltar espaço
        if y < 2.5 * cm:
            pdf.showPage()
            y = altura - 3 * cm
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(2 * cm, y, "Produto")
            pdf.drawString(13 * cm, y, "Quantidade")
            pdf.line(2 * cm, y - 0.2 * cm, largura - 2 * cm, y - 0.2 * cm)
            y -= 1 * cm
            pdf.setFont("Helvetica", 11)

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=relatorio_estoque.pdf"}
    )

    