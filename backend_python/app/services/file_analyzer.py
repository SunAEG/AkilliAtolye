import io
import asyncio
from docx import Document

async def process_ai_prompt(text: str) -> str:
    """
    Mock AI Motoru. 
    Metinde belirli komutlar varsa ('üret', 'yaz', 'oluştur') akıllıca bir cevap döner.
    """
    await asyncio.sleep(1)  # Simüle edilmiş gecikme (asenkron işlemi test etmek için)
    text_lower = text.lower()
    
    if any(keyword in text_lower for keyword in ["üret", "yaz", "oluştur", "generate"]):
        return f"✨ [Mock AI] İsteğiniz ('{text[:30]}...') başarıyla analiz edildi ve işlendi. Gerekli HTML/Bileşen şablonları hazırlanıyor..."
    else:
        return f"🤖 [Mock AI] Metniniz incelendi ancak net bir komut bulunamadı. Lütfen daha belirgin ('üret', 'yaz') komutlar girin. Metin Özeti: {text[:50]}..."


async def convert_docx_to_html(file_bytes: bytes) -> str:
    """
    .docx dosyasını okuyup GrapesJS uyumlu (veya temel) HTML çıktısına dönüştürür.
    """
    # python-docx dosya benzeri (file-like) obje bekler
    doc_io = io.BytesIO(file_bytes)
    
    try:
        # Senkron bir kütüphane olan python-docx işlemini event loop'u bloklamadan çalıştırmak daha iyidir, 
        # ancak demo için doğrudan event_loop içinde thread'e atıyoruz.
        document = await asyncio.to_thread(Document, doc_io)
        html_blocks = []
        
        for para in document.paragraphs:
            text = para.text.strip()
            if text:
                # GrapesJS'de block/satır yapısı için div eklenebilir. Temel bir HTML iskeleti kuralım.
                html_blocks.append(f'<div class="gjs-row" style="margin-bottom: 10px;"><div class="gjs-cell"><p>{text}</p></div></div>')
                
        # Eğer hiç metin yoksa
        if not html_blocks:
            return "<div class='gjs-row'><div class='gjs-cell'><p>Boş doküman.</p></div></div>"
            
        # Temel HTML çıktısı
        final_html = "\n".join(html_blocks)
        return final_html
    except Exception as e:
        raise ValueError(f"Word dosyası işlenirken hata oluştu: {str(e)}")
