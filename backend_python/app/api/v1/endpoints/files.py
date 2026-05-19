from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.file_analyzer import process_ai_prompt, convert_docx_to_html

router = APIRouter(prefix="/files", tags=["files"])

ALLOWED_EXTENSIONS = {"txt", "png", "jpg", "jpeg", "pdf", "doc", "docx", "xls", "xlsx"}

@router.post("/upload", summary="Dosya yükle ve AI/Docx analizi yap")
async def upload_file(file: UploadFile = File(...)):
    """
    Dosya yükleme noktası. 
    - Sadece izin verilen uzantıları kabul eder.
    - .txt dosyalarında mock AI analizi yapar.
    - .docx dosyalarını HTML (GrapesJS) formatına çevirir.
    """
    filename = file.filename or "unknown"
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Geçersiz dosya formatı. İzin verilenler: {', '.join(ALLOWED_EXTENSIONS)}"
        )
        
    # Dosya okuma (belleğe)
    try:
        content_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dosya okunamadı: {e}")

    result = {
        "filename": filename,
        "extension": ext,
        "size_bytes": len(content_bytes),
        "status": "success",
        "analysis_result": None
    }

    # Dosya tipine göre özel işlemler
    if ext == "txt":
        try:
            text_content = content_bytes.decode('utf-8')
            ai_result = await process_ai_prompt(text_content)
            result["analysis_result"] = ai_result
        except UnicodeDecodeError:
            result["analysis_result"] = "Hata: TXT dosyası geçerli bir UTF-8 formatında değil."
            
    elif ext == "docx":
        try:
            html_result = await convert_docx_to_html(content_bytes)
            result["analysis_result"] = html_result
            result["is_html"] = True
        except ValueError as ve:
             result["analysis_result"] = str(ve)
             
    return result
