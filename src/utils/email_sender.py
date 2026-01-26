# -*- coding: utf-8 -*-
"""
Sistema de envío de emails por SMTP.
Soporta Gmail y otros proveedores SMTP.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import (
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    DEFAULT_RECIPIENT
)

logger = logging.getLogger(__name__)


def is_email_configured() -> bool:
    """
    Verifica si la configuración de email está completa.
    
    Returns:
        bool: True si hay credenciales configuradas.
    """
    return bool(SMTP_USER and SMTP_PASSWORD)


import markdown

# ... existing code ...

def send_email(
    recipient: str,
    subject: str,
    body: str,
    attachment_path: Optional[str] = None,
    is_html: bool = True  # Nuevo flag, por defecto True para la "Visual AI"
) -> Tuple[bool, str]:
    """
    Envía un email con opción de adjunto y soporte HTML/Markdown.
    """
    if not is_email_configured():
        return False, "Error: Credenciales de email no configuradas. Revisa el archivo .env"
    
    if not recipient:
        recipient = DEFAULT_RECIPIENT
    
    try:
        # Crear mensaje
        msg = MIMEMultipart("alternative") if is_html else MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = recipient
        msg["Subject"] = subject
        
        # Procesar Cuerpo
        if is_html:
            # 1. Convertir Markdown a HTML
            html_content = markdown.markdown(body, extensions=['tables', 'fenced_code'])
            
            # 2. Estilizar HTML (AI THEME)
            styled_html = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: 'Segoe UI', sans-serif; color: #1e293b; line-height: 1.6; }}
                        h1, h2, h3 {{ color: #000080; }} /* Navy */
                        strong {{ color: #000080; }}
                        code {{ background: #f1f5f9; padding: 2px 4px; border-radius: 4px; font-family: monospace; color: #ef4444; }}
                        blockquote {{ border-left: 4px solid #00f2ff; margin: 0; padding-left: 15px; color: #475569; }}
                        .footer {{ margin-top: 30px; border-top: 1px solid #e2e8f0; padding-top: 10px; font-size: 0.8rem; color: #94a3b8; }}
                    </style>
                </head>
                <body>
                    {html_content}
                    <div class="footer">
                        <p>Generado por <strong>COHEMO Intelligence System</strong></p>
                    </div>
                </body>
            </html>
            """
            
            # Parte HTML
            msg.attach(MIMEText(styled_html, "html", "utf-8"))
            # Parte Texto Plano (Fallback)
            msg.attach(MIMEText(body, "plain", "utf-8"))
        else:
            msg.attach(MIMEText(body, "plain", "utf-8"))
        
        # Añadir adjunto si existe
        if attachment_path:
            # (Logica de adjunto igual que antes, pero adjuntandolo al root message)
            attachment = Path(attachment_path)
            
            if not attachment.exists():
                return False, f"Error: El archivo adjunto no existe: {attachment_path}"
            
            try:
                with open(attachment, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={attachment.name}"
                    )
                    msg.attach(part)
                    
            except Exception as e:
                logger.error(f"Error leyendo adjunto: {e}")
                return False, f"Error leyendo archivo adjunto: {str(e)}"
        
        # Conectar y enviar
        logger.info(f"Conectando a {SMTP_SERVER}:{SMTP_PORT}")
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.starttls()
            
            try:
                server.login(SMTP_USER, SMTP_PASSWORD)
            except smtplib.SMTPAuthenticationError:
                return False, "Error: Credenciales de email incorrectas. Verifica usuario y contraseña en .env"
            
            server.send_message(msg)
        
        logger.info(f"Email enviado correctamente a: {recipient}")
        return True, f"Email enviado correctamente a {recipient}"
        
    except Exception as e:
        logger.error(f"Error enviando email: {e}")
        return False, f"Error enviando email: {str(e)}"


def send_daily_report(
    recipient: str,
    body: str,
    excel_path: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Envía el informe diario de contratos.
    
    Args:
        recipient: Destinatario del email.
        body: Texto adicional del usuario.
        excel_path: Ruta al Excel para adjuntar (opcional).
    
    Returns:
        Tuple[bool, str]: (éxito, mensaje de resultado)
    """
    today = datetime.now().strftime("%d/%m/%Y")
    subject = f"Informe Diario de Contratos - {today}"
    
    # Construir cuerpo del email
    full_body = f"""Informe Diario de Contratos - Sistema de Control de Defensa
Fecha: {today}

{body}

---
Este email ha sido generado automáticamente por el Sistema de Control de Contratos.
"""
    
    return send_email(
        recipient=recipient,
        subject=subject,
        body=full_body,
        attachment_path=excel_path
    )
