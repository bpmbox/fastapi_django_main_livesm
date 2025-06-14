import gradio as gr
from mysite.libs.utilities import completion
import os
import json

def get_feature_details():
    """各機能の詳細情報"""
    return {
        "スタート": {
            "初心者ガイド": {
                "説明": "システムの基本的な使い方を学べるガイド",
                "使い方": "1. ガイドを開く → 2. ステップに従う → 3. 実践してみる",
                "場所": "🚀 はじめる タブ",
                "実行方法": "「🚀 はじめる」タブから「初心者ガイド」を選択"
            }
        },
        "AI作成": {
            "プログラム生成": {
                "説明": "自然言語の仕様書からプログラムコードを自動生成",
                "使い方": "1. 要件を入力 → 2. 言語選択 → 3. 生成実行",
                "場所": "🤖 AI作成 タブ",
                "実行方法": "「仕様書を入力してください」欄に要件を記述"
            },
            "GitHub Issue作成": {
                "説明": "プロジェクトのIssueを自動生成・投稿",
                "使い方": "1. Issue内容入力 → 2. ラベル選択 → 3. 作成実行",
                "場所": "🤖 AI作成 タブ",
                "実行方法": "Issue内容を記述して「作成」ボタンを押す"
            },
            "RPA自動化": {
                "説明": "Webページの操作を自動化するシステム",
                "使い方": "1. 対象サイト指定 → 2. 操作手順設定 → 3. 自動実行",
                "場所": "🤖 AI作成 タブ",
                "実行方法": "「RPA自動化システム」から操作を設定"
            }
        },
        "チャット": {
            "AIチャット": {
                "説明": "汎用的なAI対話システム",
                "使い方": "メッセージを入力して送信するだけ",
                "場所": "💬 チャット タブ",
                "実行方法": "メッセージボックスに質問を入力"
            },
            "OpenInterpreter": {
                "説明": "コード実行機能付きの高度なAIチャット",
                "使い方": "1. パスワード入力 → 2. コード生成依頼 → 3. 実行確認",
                "場所": "💬 チャット タブ",
                "実行方法": "パスワード認証後、プログラミング関連の質問"
            }
        },
        "文書作成": {
            "ドキュメント生成": {
                "説明": "技術文書やマニュアルを自動生成",
                "使い方": "1. 文書タイプ選択 → 2. 内容指定 → 3. 生成実行",
                "場所": "📝 文書作成 タブ",
                "実行方法": "文書の種類と内容を指定して生成"
            },
            "プロンプト管理": {
                "説明": "AIプロンプトの保存・管理システム",
                "使い方": "1. プロンプト登録 → 2. カテゴリ分類 → 3. 検索・利用",
                "場所": "📝 文書作成 タブ",
                "実行方法": "プロンプトライブラリから選択・編集"
            }
        },
        "管理": {
            "統合ダッシュボード": {
                "説明": "システム全体の状況を一元管理",
                "使い方": "各種メトリクスやログを確認",
                "場所": "📊 管理 タブ",
                "実行方法": "ダッシュボードで各項目をクリック"
            }
        },
        "その他": {
            "ファイル管理": {
                "説明": "ファイルのアップロード・ダウンロード・管理",
                "使い方": "1. ファイル選択 → 2. アップロード → 3. 処理実行",
                "場所": "🔧 その他 タブ",
                "実行方法": "ファイルをドラッグ&ドロップまたは選択"
            },
            "データベース": {
                "説明": "データの登録・検索・編集機能",
                "使い方": "1. テーブル選択 → 2. データ操作 → 3. 保存",
                "場所": "🔧 その他 タブ",
                "実行方法": "データベース管理画面から操作"
            }
        }
    }

def search_feature_help(query):
    """機能のヘルプを検索"""
    details = get_feature_details()
    results = []
    
    query_lower = query.lower()
    
    for category, features in details.items():
        for feature_name, feature_info in features.items():
            # 機能名、説明、使い方で検索
            searchable_text = f"{feature_name} {feature_info['説明']} {feature_info['使い方']}".lower()
            
            if query_lower in searchable_text:
                result = f"## 🎯 {feature_name}\n\n"
                result += f"**📍 場所**: {feature_info['場所']}\n\n"
                result += f"**📝 説明**: {feature_info['説明']}\n\n"
                result += f"**🚀 使い方**: {feature_info['使い方']}\n\n"
                result += f"**▶️ 実行方法**: {feature_info['実行方法']}\n\n"
                result += "---\n\n"
                results.append(result)
    
    if results:
        return "".join(results)
    else:
        return f"「{query}」に関する機能が見つかりませんでした。\n\n以下のキーワードで検索してみてください：\n- プログラム、コード、生成\n- チャット、AI、対話\n- ファイル、データベース、管理\n- ドキュメント、文書、作成"

def enhanced_help_chat(message, history):
    """ヘルプ特化型チャット"""
    if any(keyword in message.lower() for keyword in ['機能', '使い方', 'ヘルプ', 'help', '方法', 'やり方']):
        return search_feature_help(message)
    
    # システム情報を含めてAIに質問
    system_prompt = "あなたは AI-Human協働開発システムのヘルプアシスタントです。ユーザーの質問に対して、システムの機能の使い方を具体的で分かりやすく説明してください。"
    enhanced_message = f"{system_prompt}\n\nユーザーの質問: {message}"
    
    return completion(enhanced_message, history)

# CSS for better styling
help_css = """
.help-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 15px;
    padding: 20px;
    color: white;
    margin: 10px 0;
}
.feature-card {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}
.quick-help {
    background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
    border-radius: 10px;
    padding: 15px;
    color: white;
    margin: 10px 0;
}
"""

with gr.Blocks(css=help_css, title="🆘 システムヘルプ") as gradio_interface:
    gr.Markdown("# 🆘 システムヘルプ・機能ガイド")
    gr.Markdown("### 💡 機能の使い方を詳しく説明します")
    
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(
                height=500,
                placeholder="🆘 機能の使い方について何でも聞いてください！\n\n例：\n- 「プログラム生成の使い方」\n- 「GitHub Issueの作り方」\n- 「ファイル管理機能について」",
                label="ヘルプチャット"
            )
            
            msg = gr.Textbox(
                placeholder="使い方を知りたい機能名や操作を入力...",
                label="質問",
                lines=2
            )
            
            with gr.Row():
                submit_btn = gr.Button("質問する", variant="primary")
                clear_btn = gr.Button("クリア")
        
        with gr.Column(scale=1):
            with gr.Group():
                gr.Markdown("### 🔍 クイック検索")
                
                search_query = gr.Textbox(
                    placeholder="機能名で検索...",
                    label="機能検索"
                )
                search_btn = gr.Button("検索", variant="secondary")
                search_result = gr.Markdown("")
            
            with gr.Group():
                gr.Markdown("### 📚 人気の質問")
                gr.Markdown("""
                • **プログラム生成の使い方**
                • **チャット機能の種類**  
                • **ファイルのアップロード方法**
                • **GitHub Issue作成手順**
                • **データベースの操作方法**
                """)
    
    # チャット機能
    def respond(message, chat_history):
        bot_message = enhanced_help_chat(message, chat_history)
        chat_history.append((message, bot_message))
        return "", chat_history
    
    def search_and_display(query):
        if query.strip():
            return search_feature_help(query)
        return "検索キーワードを入力してください。"
    
    # イベントハンドラー
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    submit_btn.click(respond, [msg, chatbot], [msg, chatbot])
    clear_btn.click(lambda: ([], ""), outputs=[chatbot, msg])
    
    search_btn.click(search_and_display, inputs=search_query, outputs=search_result)
    search_query.submit(search_and_display, inputs=search_query, outputs=search_result)
    
    # よくある質問の例
    gr.Examples(
        examples=[
            ["プログラム生成機能の詳しい使い方を教えて"],
            ["GitHub Issueを作成する手順は？"],
            ["ファイルをアップロードするには？"],
            ["チャット機能の違いを説明して"],
            ["データベース操作の方法は？"],
            ["RPA自動化システムの使い方"]
        ],
        inputs=msg,
        label="💡 よくある質問"
    )

# 自動検出システム用のメタデータ  
interface_title = "🆘 システムヘルプ"
interface_description = "機能の使い方を詳しく案内するヘルプシステム"
