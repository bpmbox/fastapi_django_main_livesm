import gradio as gr
from mysite.libs.utilities import chat_with_interpreter, completion, process_file,no_process_file
from interpreter import interpreter
import mysite.interpreter.interpreter_config  # インポートするだけで設定が適用されます
import duckdb
#from logger import logger

def format_response(chunk, full_response):
    # Message
    if chunk["type"] == "message":
        full_response += chunk.get("content", "")
        if chunk.get("end", False):
            full_response += "\n"

    # Code
    if chunk["type"] == "code":
        if chunk.get("start", False):
            full_response += "```python\n"
        #full_response += chunk.get("content", "").replace("`", "")
        if chunk.get("end", False):
            full_response += "\n```\n"

    # Output
    if chunk["type"] == "confirmation":
        if chunk.get("start", False):
            full_response += "```python\n"
        #full_response += chunk.get("content", {}).get("code", "")
        if chunk.get("end", False):
            full_response += "```\n"

    # Console
    if chunk["type"] == "console":
        console_content = chunk.get("content", "")
        
        # デバッグログ: console_content の内容と型を出力
        print(f"Processing console content: {console_content}, type={type(console_content)}")
        
        if not isinstance(console_content, str):
            console_content = str(console_content)
            print(f"Converted console_content to string: {console_content}")
        
        # 不要な内容のフィルタリング
        if console_content.isdigit() or console_content.strip().lower() == "none":
            print(f"Skipping unwanted console content: {console_content}")
            return full_response
        
        # バッククオートを削除
        console_content = console_content.replace("`", "")
        
        # 言語タグなしでコードブロックを開始
        if chunk.get("start", False):
            full_response += "```python\n"
        
        if chunk.get("format", "") == "active_line":
            if not console_content.strip():
                full_response += "No output available on console.\n"
            else:
                full_response += console_content.rstrip("\n") + "\n"
        elif chunk.get("format", "") == "output":
            full_response += console_content.rstrip("\n") + "\n"
        
        if chunk.get("end", False):
            full_response += "```\n"
    # Image
    if chunk["type"] == "image":
        if chunk.get("start", False) or chunk.get("end", False):
            full_response += "\n"
        else:
            image_format = chunk.get("format", "")
            if image_format == "base64.png":
                image_content = chunk.get("content", "")
                if image_content:
                    image = Image.open(BytesIO(base64.b64decode(image_content)))
                    new_image = Image.new("RGB", image.size, "white")
                    new_image.paste(image, mask=image.split()[3])
                    buffered = BytesIO()
                    new_image.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    full_response += f"![Image](data:image/png;base64,{img_str})\n"

    return full_response

import sqlite3
from datetime import datetime

# SQLiteの設定
db_name = "chat_history.db"

def initialize_db():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT,
        type TEXT,
        content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def add_message_to_db(role, message_type, content):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO history (role, type, content) VALUES (?, ?, ?)", (role, message_type, content))
    conn.commit()
    conn.close()

def get_recent_messages(limit=4):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT role, type, content FROM history ORDER BY timestamp DESC LIMIT ?", (limit,))
    messages = cursor.fetchall()
    conn.close()
    return messages[::-1]  # 最新の20件を取得して逆順にする

def format_responses(chunk, full_response):
    # This function will format the response from the interpreter
    return full_response + chunk.get("content", "")

def chat_with_interpreter(message, history=None, a=None, b=None, c=None, d=None):
    if message == "reset":
        interpreter.reset()
        return "Interpreter reset", history

    full_response = ""
    recent_messages = get_recent_messages(limit=4)

    for role, message_type, content in recent_messages:
        entry = {"role": role, "type": message_type, "content": content}
        interpreter.messages.append(entry)

    user_entry = {"role": "user", "type": "message", "content": message}
    interpreter.messages.append(user_entry)
    add_message_to_db("user", "message", message)

    for chunk in interpreter.chat(message, display=False, stream=True):
        if isinstance(chunk, dict):
            full_response = format_response(chunk, full_response)
        else:
            raise TypeError("Expected chunk to be a dictionary")
        print(full_response)  
        yield full_response

    assistant_entry = {"role": "assistant", "type": "message", "content": full_response}
    interpreter.messages.append(assistant_entry)
    add_message_to_db("assistant", "message", full_response)

    yield full_response
    return full_response, history


def chat_with_interpreter_no_stream(message, history=None, a=None, b=None, c=None, d=None):
    if message == "reset":
        interpreter.reset()
        return "Interpreter reset", history

    full_response = ""
    recent_messages = get_recent_messages()

    for role, message_type, content in recent_messages:
        entry = {"role": role, "type": message_type, "content": content}
        interpreter.messages.append(entry)

    user_entry = {"role": "user", "type": "message", "content": message}
    interpreter.messages.append(user_entry)
    add_message_to_db("user", "message", message)

    chunks = interpreter.chat(message, display=False, stream=False)
    for chunk in chunks:
        if isinstance(chunk, dict):
            full_response = format_response(chunk, full_response)
        else:
            raise TypeError("Expected chunk to be a dictionary")
        #yield full_response
    assistant_entry = {"role": "assistant", "type": "message", "content": str(full_response)}
    interpreter.messages.append(assistant_entry)
    add_message_to_db("assistant", "message", str(full_response))

    #yield full_response
    return str(full_response), history


# 初期化
initialize_db()


PLACEHOLDER = """
<div style="padding: 30px; text-align: center; display: flex; flex-direction: column; align-items: center;">
   <img src="https://ysharma-dummy-chat-app.hf.space/file=/tmp/gradio/8e75e61cc9bab22b7ce3dec85ab0e6db1da5d107/Meta_lockup_positive%20primary_RGB.jpg" style="width: 80%; max-width: 550px; height: auto; opacity: 0.55;  ">
   <h1 style="font-size: 28px; margin-bottom: 2px; opacity: 0.55;">Meta llama3</h1>
   <p style="font-size: 18px; margin-bottom: 2px; opacity: 0.65;">Ask me anything...</p>
</div>
"""

chatbot = gr.Chatbot(height=450, placeholder=PLACEHOLDER, label="Gradio ChatInterface")



gradio_interface = gr.ChatInterface(
    fn=chat_with_interpreter,
    chatbot=chatbot,
    fill_height=True,
    additional_inputs_accordion=gr.Accordion(
        label="⚙️ Parameters", open=False, render=False
    ),
    additional_inputs=[
        gr.Slider(
            minimum=0,
            maximum=1,
            step=0.1,
            value=0.95,
            label="Temperature",
            render=False,
        ),
        gr.Slider(
            minimum=128,
            maximum=4096,
            step=1,
            value=512,
            label="Max new tokens",
            render=False,
        ),
        
    ],
    # democs,
    examples=[
        ["HTMLのサンプルを作成して"],
        [
            "CUDA_VISIBLE_DEVICES=0 llamafactory-cli train examples/lora_single_gpu/llama3_lora_sft.yaml"
        ],
    ],
    cache_examples=False,
)

if __name__ == '__main__':
    message = f"""
    postgres connection is this postgresql://miyataken999:yz1wPf4KrWTm@ep-odd-mode-93794521.us-east-2.aws.neon.tech/neondb?sslmode=require
    create this tabale 
    CREATE TABLE items (
  id INT PRIMARY KEY,
  brand_name VARCHAR(255),
  model_name VARCHAR(255),
  product_number VARCHAR(255),
  purchase_store VARCHAR(255),
  purchase_date DATE,
  purchase_price INT,
  accessories TEXT,
  condition INT,
  metal_type VARCHAR(255),
  metal_weight DECIMAL(10, 2),
  diamond_certification BLOB,
  initial BOOLEAN
);
    
    """
    chat_with_interpreter(message)
