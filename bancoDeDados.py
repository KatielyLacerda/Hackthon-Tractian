import openai
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import pymysql
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Inicializar o app FastAPI
app = FastAPI()

# Configurar a chave da API do ChatGPT
openai.api_key = 'sk-svcacct-sfPksbla4y63WqxeORLZ3bpKbx8TT-g11JLyH9muw5RCxOT1xHYlN51id_5BQeHT3BlbkFJXLYO0zRcxRSa6JjyXX_t37CDN1sp7Q8Bd5H8j11B7fLVocOUCduBGupXZi5XzyQA'  # Substitua pela sua chave

# Configurações CORS (se necessário)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Função para criar a conexão do banco de dados
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='Tractian@123',
        database='tractian',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# Primeiramente, defina as ferramentas que você deseja adicionar à tabela
tools_data = [
    ("MAT001", "Serra Circular", "Ferramentas de Corte"),
    ("MAT002", "Disco de Corte", "Ferramentas de Corte"),
    ("MAT003", "Serra de Fita", "Ferramentas de Corte"),
    ("MAT004", "Disco de Desbaste", "Ferramentas de Corte"),
    ("MAT005", "Broca de Aço Rápido 10mm", "Ferramentas de Corte"),
    ("MAT006", "Conjunto de Fresas para Usinagem", "Ferramentas de Corte"),
    ("MAT007", "Lâmina de Serra Sabre", "Ferramentas de Corte"),
    ("EQP001", "Lixadeira Angular", "Ferramentas de Corte"),
    ("MAT101", "Paquímetro Digital", "Ferramentas de Medição"),
    ("MAT102", "Micrômetro", "Ferramentas de Medição"),
    ("MAT103", "Relógio Comparador", "Ferramentas de Medição"),
    ("MAT104", "Trena de Aço 5m", "Ferramentas de Medição"),
    ("MAT105", "Nível de Bolha", "Ferramentas de Medição"),
    ("MAT106", "Goniômetro Digital", "Ferramentas de Medição"),
    ("MAT107", "Manômetro para Pressão", "Ferramentas de Medição"),
    ("MAT108", "Calibrador de Roscas", "Ferramentas de Medição"),
    ("EQP201", "Máquina de Solda MIG", "Equipamentos de Solda"),
    ("MAT201", "Eletrodo de Solda Inox", "Equipamentos de Solda"),
    ("MAT202", "Máscara de Solda Automática", "Equipamentos de Solda"),
    ("EQP202", "Maçarico de Corte Oxiacetilênico", "Equipamentos de Solda"),
    ("MAT203", "Tocha de Solda TIG", "Equipamentos de Solda"),
    ("MAT204", "Fio de Solda MIG ER70S-6", "Equipamentos de Solda"),
    ("MAT205", "Regulador de Pressão para Gás", "Equipamentos de Solda"),
    ("MAT206", "Tubo de Gás Acetileno", "Equipamentos de Solda"),
    ("MAT301", "Graxa Industrial", "Lubrificação e Manutenção"),
    ("MAT302", "Óleo Lubrificante 10W30", "Lubrificação e Manutenção"),
    ("EQP301", "Bomba de Graxa Pneumática", "Lubrificação e Manutenção"),
    ("MAT303", "Limpa Contatos Elétricos", "Lubrificação e Manutenção"),
    ("MAT304", "Spray Desengripante", "Lubrificação e Manutenção"),
    ("MAT305", "Veda Rosca em Fita", "Lubrificação e Manutenção"),
    ("MAT401", "Capacete de Segurança com Aba", "Equipamentos de Segurança"),
    ("MAT402", "Luvas Térmicas de Alta Resistência", "Equipamentos de Segurança"),
    ("MAT403", "Óculos de Proteção Antirrespingos", "Equipamentos de Segurança"),
    ("MAT404", "Protetor Auricular Tipo Plug", "Equipamentos de Segurança"),
    ("MAT405", "Máscara Respiratória com Filtro P3", "Equipamentos de Segurança"),
    ("MAT406", "Cinto de Segurança para Trabalho em Altura", "Equipamentos de Segurança"),
    ("MAT407", "Sapato de Segurança com Biqueira de Aço", "Equipamentos de Segurança"),
    ("MAT408", "Protetor Facial de Policarbonato", "Equipamentos de Segurança"),
    ("EQP501", "Talha Elétrica de Corrente", "Equipamentos de Elevação"),
    ("MAT501", "Corrente de Elevação de 10m", "Equipamentos de Elevação"),
    ("MAT502", "Gancho Giratório com Trava de Segurança", "Equipamentos de Elevação"),
    ("MAT503", "Cinta de Elevação com Olhal", "Equipamentos de Elevação"),
    ("EQP502", "Carrinho de Transporte de Bobinas", "Equipamentos de Elevação"),
    ("EQP503", "Macaco Hidráulico 10 Toneladas", "Equipamentos de Elevação"),
    ("MAT601", "Rolamento Esférico de Precisão", "Componentes Mecânicos"),
    ("MAT602", "Parafuso de Alta Resistência M12", "Componentes Mecânicos"),
    ("MAT603", "Correia de Transmissão Industrial", "Componentes Mecânicos"),
    ("MAT604", "Junta de Vedação em Borracha", "Componentes Mecânicos"),
    ("MAT605", "Engrenagem Cilíndrica de Aço", "Componentes Mecânicos"),
    ("MAT606", "Bucha de Bronze Autolubrificante", "Componentes Mecânicos"),
    ("MAT607", "Eixo de Transmissão", "Componentes Mecânicos"),
    ("MAT608", "Polia de Alumínio", "Componentes Mecânicos"),
    ("EQP601", "Válvula Solenoide Hidráulica", "Equipamentos Hidráulicos"),
    ("EQP602", "Bomba Hidráulica de Pistão", "Equipamentos Hidráulicos"),
    ("MAT701", "Mangueira Hidráulica de Alta Pressão", "Equipamentos Hidráulicos"),
    ("MAT702", "Conector Hidráulico Rápido", "Equipamentos Hidráulicos"),
    ("EQP701", "Motor Elétrico Trifásico 5HP", "Equipamentos Elétricos"),
    ("MAT801", "Cabo Elétrico 10mm²", "Equipamentos Elétricos"),
    ("MAT802", "Disjuntor de 100A", "Equipamentos Elétricos"),
    ("EQP702", "Quadro de Comando Elétrico com Inversor de Frequência", "Equipamentos Elétricos"),
    ("MAT803", "Chave Seccionadora", "Equipamentos Elétricos"),
    ("MAT804", "Fusível NH 100A", "Equipamentos Elétricos"),
    ("MAT805", "Tomada Industrial 380V", "Equipamentos Elétricos"),
    ("MAT901", "Chave de Fenda Phillips 6mm", "Ferramentas Manuais"),
    ("MAT902", "Alicate de Corte", "Ferramentas Manuais"),
    ("MAT903", "Martelo de Borracha", "Ferramentas Manuais"),
    ("MAT904", "Torquímetro 40-200Nm", "Ferramentas Manuais"),
    ("MAT905", "Conjunto de Chaves Allen", "Ferramentas Manuais"),
    ("MAT906", "Chave Estrela 12mm", "Ferramentas Manuais"),
    ("MAT907", "Serra Manual", "Ferramentas Manuais"),
]

# Modelos de Dados
class Message(BaseModel):
    sender: str
    text: str

class Archive(BaseModel):
    name: str
    type: str
    content: bytes

class Tool(BaseModel):
    tool_sap: str
    category: str
    name: str

class Reservation(BaseModel):
    tool_sap: str
    reservation_date: str  # YYYY-MM-DD

class SafetyNorm(BaseModel):
    paragraph: str

class Employee(BaseModel):
    employee_id: int
    name: str
    position: str
    workload_completed: int
    day_off: int

class Holiday(BaseModel):
    name: str
    date: str  # YYYY-MM-DD

# Criar tabelas
def create_tables(connection):
    with connection.cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS archives (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100),
                type VARCHAR(100),
                content BLOB
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tools_catalog (
                tool_sap VARCHAR(100) PRIMARY KEY,
                category VARCHAR(100),
                name VARCHAR(100)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                reservation_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                tool_sap VARCHAR(100),
                reservation_date DATE,
                FOREIGN KEY (tool_sap) REFERENCES tools_catalog(tool_sap)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS safety_norms (
                paragraph VARCHAR(100) PRIMARY KEY
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employee_data (
                employee_id INTEGER PRIMARY KEY,
                name VARCHAR(100),
                position VARCHAR(100),
                workload_completed INT,
                day_off INT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS holidays (
                name VARCHAR(100),
                date DATE
            )
        ''')

    connection.commit()

# Função para adicionar ferramentas ao banco de dados
def add_tools(connection, tools):
    with connection.cursor() as cursor:
        cursor.executemany('INSERT INTO tools_catalog (tool_sap, name, category) VALUES (%s, %s, %s)', tools)
    connection.commit()

# Adicionar ao arquivo
def add_to_archive(connection, file_path: str, file_name: str, file_type: str):
    try:
        with open(file_path, 'rb') as file:
            content = file.read()
            with connection.cursor() as cursor:
                cursor.execute('INSERT INTO archives (name, type, content) VALUES (%s, %s, %s)', (file_name, file_type, content))
            connection.commit()
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Definir ferramentas
tools_data = [
    ("MAT001", "Serra Circular", "Ferramentas de Corte"),
    # ... outras ferramentas
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    connection = get_db_connection()
    create_tables(connection)
    add_tools(connection, tools_data)
    add_to_archive(connection, '/home/shwonck/Documents/Tractian/audio.ogg', 'audio', 'audio')
    yield
    connection.close()

app.router.lifespan_context = lifespan

class ChatMessage(BaseModel):
    sender: str
    text: str

@app.post("/chat")
async def chat_with_openai(message: ChatMessage):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # Choose the appropriate engine
            prompt=message.text,
            max_tokens=150
        )
        return {"text": response.choices[0].text.strip()}
    except Exception as e:
        return {"error": str(e)}

@app.post("/messages")
async def create_message(message: Message):
    # Aqui você pode processar a mensagem, salvar no banco, etc.
    return {"sender": message.sender, "text": message.text}

# Endpoints para Archives
@app.post("/archives/")
async def create_archive(archive: Archive, file: UploadFile = File(...)):
    content = await file.read()
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO archives (name, type, content) VALUES (%s, %s, %s)', (archive.name, archive.type, content))
        connection.commit()
    finally:
        connection.close()
    return {"message": "Arquivo adicionado com sucesso."}

@app.get("/archives/")
async def read_archives():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM archives')
            rows = cursor.fetchall()
    finally:
        connection.close()
    return rows

@app.delete("/archives/{archive_id}")
async def delete_archive(archive_id: int):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM archives WHERE id = %s', (archive_id,))
        connection.commit()
    finally:
        connection.close()
    return {"message": "Arquivo deletado com sucesso."}

# Endpoints para Tools Catalog
@app.post("/tools/")
async def create_tool(tool: Tool):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO tools_catalog (tool_sap, category, name) VALUES (%s, %s, %s)', (tool.tool_sap, tool.category, tool.name))
        connection.commit()
    finally:
        connection.close()
    return {"message": "Ferramenta adicionada com sucesso."}

@app.get("/tools/")
async def read_tools():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM tools_catalog')
            rows = cursor.fetchall()
    finally:
        connection.close()
    return rows

@app.put("/tools/{tool_sap}")
async def update_tool(tool_sap: str, tool: Tool):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE tools_catalog SET category = %s, name = %s WHERE tool_sap = %s', (tool.category, tool.name, tool_sap))
        connection.commit()
    finally:
        connection.close()
    return {"message": "Ferramenta atualizada com sucesso."}

@app.delete("/tools/{tool_sap}")
async def delete_tool(tool_sap: str):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM tools_catalog WHERE tool_sap = %s', (tool_sap,))
        connection.commit()
    finally:
        connection.close()
    return {"message": "Ferramenta deletada com sucesso."}

# Endpoints para Reservations
@app.post("/reservations/")
async def create_reservation(reservation: Reservation):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO reservations (tool_sap, reservation_date) VALUES (%s, %s)', (reservation.tool_sap, reservation.reservation_date))
        connection.commit()
    finally:
        connection.close()
    return {"message": "Reserva criada com sucesso."}

@app.get("/reservations/")
async def read_reservations():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM reservations')
            rows = cursor.fetchall()
    finally:
        connection.close()
    return rows

@app.delete("/reservations/{reservation_id}")
async def delete_reservation(reservation_id: int):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM reservations WHERE reservation_id = %s', (reservation_id,))
        connection.commit()
    finally:
        connection.close()
    return {"message": "Reserva deletada com sucesso."}

# Endpoints para Safety Norms
@app.post("/safety-norms/")
async def create_safety_norm(safety_norm: SafetyNorm):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO safety_norms (paragraph) VALUES (%s)', (safety_norm.paragraph,))
        connection.commit()
    finally:
        connection.close()
    return {"message": "Norma de segurança adicionada com sucesso."}

@app.get("/safety-norms/")
async def read_safety_norms():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM safety_norms')
            rows = cursor.fetchall()
    finally:
        connection.close()
    return rows

# Endpoints para Employee Data
@app.post("/employees/")
async def create_employee(employee: Employee):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO employee_data (employee_id, name, position, workload_completed, day_off) VALUES (%s, %s, %s, %s, %s)',
                           (employee.employee_id, employee.name, employee.position, employee.workload_completed, employee.day_off))
        connection.commit()
    finally:
        connection.close()
    return {"message": "Funcionário adicionado com sucesso."}

@app.get("/employees/")
async def read_employees():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM employee_data')
            rows = cursor.fetchall()
    finally:
        connection.close()
    return rows

# Endpoints para Holidays
@app.post("/holidays/")
async def create_holiday(holiday: Holiday):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO holidays (name, date) VALUES (%s, %s)', (holiday.name, holiday.date))
        connection.commit()
    finally:
        connection.close()
    return {"message": "Feriado adicionado com sucesso."}

@app.get("/holidays/")
async def read_holidays():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM holidays')
            rows = cursor.fetchall()
    finally:
        connection.close()
    return rows








