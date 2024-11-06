import os
import google.generativeai as genai
import gradio as gr
from PIL import Image
import json

# Your API key - for Hugging Face, set this as a secret in the Space settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # This will get the API key from environment variables

# Configure Gemini API
def configure_genai():
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-8b')
    return model

def process_form(image):
    try:
        model = configure_genai()
        
        if not isinstance(image, Image.Image):
            image = Image.open(image)
            
        prompt = """
        لطفاً این تصویر فرم را تحلیل کنید و اطلاعات زیر را در قالب JSON استخراج کنید:
        1. تمام فیلدهای متنی و مقادیر آنها
        2. چک باکس‌ها یا دکمه‌های رادیویی و وضعیت آنها
        3. امضاها یا مهرها در صورت وجود
        
        لطفاً پاسخ را به صورت یک شیء JSON با نام فیلدها و مقادیر مناسب فرمت کنید.
        """
        
        response = model.generate_content([prompt, image])
        response_text = response.text
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start != -1 and json_end != -1:
            json_str = response_text[json_start:json_end]
            parsed_json = json.loads(json_str)
            return json.dumps(parsed_json, indent=2, ensure_ascii=False)
        else:
            return response.text
            
    except Exception as e:
        return f"خطا در پردازش فرم: {str(e)}"

def create_interface():
    css = """
    body {
        background-color: #000000;
    }
    
    .gradio-container {
        color: white !important;
        direction: rtl !important;
        text-align: right !important;
    }
    
    .title-text {
        color: white !important;
        text-align: right !important;
    }
    
    .subtitle-text {
        color: white !important;
        text-align: right !important;
    }
    
    .description-text {
        color: white !important;
        text-align: right !important;
    }
    
    .label-wrap span {
        color: white !important;
        text-align: right !important;
    }
    
    .md h1, .md h2, .md h3, .md p, .md ol, .md li {
        color: white !important;
        text-align: right !important;
        direction: rtl !important;
    }
    
    button {
        direction: rtl !important;
        background-color: #ff4b1f !important;
        color: white !important;
    }
    
    .output-markdown {
        direction: rtl !important;
        text-align: right !important;
    }
    
    textarea {
        direction: rtl !important;
        text-align: right !important;
        background-color: #2d2d2d !important;
        color: white !important;
    }
    """
    
    with gr.Blocks(title="سیستم استخراج متن از فرم - نسخه نمایشی هایمارت", css=css, theme="darker") as interface:
        gr.Markdown('<h1 class="title-text">سیستم هوشمند استخراج متن از فرم</h1>')
        gr.Markdown('<h3 class="subtitle-text">نسخه نمایشی برای هایمارت</h3>')
        gr.Markdown('<p class="description-text">لطفاً تصویر فرم خود را بارگذاری کنید تا اطلاعات آن به صورت خودکار استخراج شود</p>')
        
        with gr.Row():
            with gr.Column():
                image_input = gr.Image(
                    label="تصویر فرم را اینجا بارگذاری کنید",
                    type="pil"
                )
                submit_btn = gr.Button("پردازش فرم")
            
            with gr.Column():
                output_text = gr.Textbox(
                    label="اطلاعات استخراج شده",
                    lines=10,
                    rtl=True
                )
        
        submit_btn.click(
            fn=process_form,
            inputs=[image_input],
            outputs=output_text
        )
        
        gr.Markdown("""
        <div class="guide-section">
        <h3>راهنما:</h3>
        <ol>
            <li>یک تصویر از فرم خود را بارگذاری کنید</li>
            <li>روی دکمه 'پردازش فرم' کلیک کنید</li>
            <li>نتیجه به صورت خودکار نمایش داده خواهد شد</li>
        </ol>
        
        <p><strong>نکته:</strong> برای نتیجه بهتر، لطفاً از تصاویر واضح و با نور کافی استفاده کنید.</p>
        
        <p><em>این نسخه نمایشی صرفاً جهت ارزیابی قابلیت‌های سیستم می‌باشد.</em></p>
        </div>
        """)
    
    return interface

interface = create_interface()
interface.launch()