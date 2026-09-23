"""Genera un vídeo narrado con capturas reales de la app local.

Dependencias opcionales: playwright, pyttsx3, imageio-ffmpeg.
Requiere Bacci Operaciones en http://127.0.0.1:8765/.
"""

from __future__ import annotations

import subprocess
import wave
from pathlib import Path

import imageio_ffmpeg
import pyttsx3
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT.parent / "video-work"
OUT = ROOT.parent / "bacci-operaciones-demo.mp4"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
SLIDES = Path(__file__).with_name("slides.html").as_uri()
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

SCRIPT = {
    "problem": "Hola, equipo de Bacci. He entendido el problema como una necesidad de convertir datos dispersos en decisiones operativas. Los pedidos están en Navision, las comprobaciones se hacen en Excel y las solicitudes llegan por Outlook. La pregunta diaria no es solo cuántas unidades faltan: es qué caso requiere atención ahora y qué puede hacer la persona responsable.",
    "method": "Mi método parte del contrato de datos. Una línea se identifica por pedido y línea; los correos se incorporan por identificador estable. Los duplicados idénticos se consolidan, los contradictorios se muestran para revisión y las referencias ambiguas quedan sin resolver. Las rectificaciones sustituyen solicitudes anteriores cuando lo indican expresamente. Un correo nunca cambia el ERP por sí solo; stock, logística y autorización de contactos exigen verificación humana.",
    "demo": "Esta es la cola real sobre los archivos de muestra. Cada fila muestra la prioridad, lo pendiente, el motivo y la acción propuesta. Busco P veintiséis mil dos: la petición vigente es el trece de septiembre, mientras el ERP conserva el once. Abro el correo que justifica la rectificación. En la vista sin resolver aparecen mensajes que no podemos asignar con seguridad. Finalmente, en ejecuciones repito el lote: no se añade ningún mensaje y el resultado se mantiene.",
    "scope": "Ahora abro el conjunto completo en la misma aplicación. Aquí hay diecisiete mil cuatrocientos veintitrés casos que requieren atención. La vista Todos los registros permite consultar además las líneas ya servidas. La búsqueda alcanza referencias, productos, fechas, cantidades, datos de cliente y texto de los correos.",
    "validation": "La validación compara resultados esperados y obtenidos en cuarenta comprobaciones. La muestra y el conjunto completo pasan todas. Procesamos veinte mil filas de pedidos y cuatro mil de correo. El lote aporta tres mensajes nuevos; repetirlo aporta cero y mantiene el mismo hash. Cada pasada completa tardó alrededor de nueve segundos en este equipo. Es un prototipo local: la conexión real con Navision y Outlook y la migración de ERP quedan diseñadas, no fingidas.",
    "close": "Gracias por revisar esta propuesta. La solución deja una cola útil, auditable y fácil de ejecutar, y separa con claridad lo que sabemos de lo que una persona todavía debe comprobar. El código, las instrucciones y la evidencia de validación están disponibles en el fork de GitHub mostrado en pantalla.",
}


def duration(path: Path) -> float:
    with wave.open(str(path), "rb") as audio:
        return audio.getnframes() / audio.getframerate()


def command(*args: str) -> None:
    subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def synthesize() -> dict[str, Path]:
    engine = pyttsx3.init()
    voice = next(v.id for v in engine.getProperty("voices") if "Helena" in v.name)
    engine.setProperty("voice", voice)
    engine.setProperty("rate", 165)
    paths = {}
    for key, text in SCRIPT.items():
        target = WORK / f"{key}.wav"
        engine.save_to_file(text, str(target))
        paths[key] = target
    engine.runAndWait()
    return paths


def capture_slides() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=str(EDGE), headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
        for key in ("problem", "method", "validation", "close"):
            page.goto(f"{SLIDES}?slide={key}", wait_until="load")
            page.screenshot(path=str(WORK / f"{key}.png"))
        browser.close()


def capture_scope() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=str(EDGE), headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
        page.goto("http://127.0.0.1:8765/?dataset=full", wait_until="networkidle")
        page.locator("#range").filter(has_text="17.423 casos").wait_for(timeout=90000)
        page.locator("#search").blur()
        page.screenshot(path=str(WORK / "scope.png"))
        browser.close()


def record_demo(seconds: float) -> Path:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=str(EDGE), headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720}, record_video_dir=str(WORK),
                                      record_video_size={"width": 1280, "height": 720}, device_scale_factor=1)
        page = context.new_page()
        page.goto("http://127.0.0.1:8765/", wait_until="networkidle")
        page.locator("#case-rows tr").first.wait_for()
        pause = max(1000, int((seconds - 7) * 1000 / 9))
        page.wait_for_timeout(pause)
        page.locator("#search").fill("P-26002")
        page.locator("#detail-title").filter(has_text="P-26002").wait_for()
        page.wait_for_timeout(pause)
        page.locator("#detail").scroll_into_view_if_needed()
        page.wait_for_timeout(pause)
        first_mail = page.locator("#detail-evidence details").first
        first_mail.locator("summary").click()
        page.wait_for_timeout(pause)
        page.locator("#search").fill("")
        page.locator('[data-section="unresolved"]').click()
        page.locator("#case-rows tr").first.wait_for()
        page.wait_for_timeout(pause)
        page.locator("#case-rows tr").first.click()
        page.locator("#detail").scroll_into_view_if_needed()
        page.wait_for_timeout(pause)
        page.locator('[data-section="runs"]').click()
        page.locator("#run-rows tr").first.wait_for()
        page.wait_for_timeout(pause)
        page.locator("#update-button").click()
        page.locator("#notice").wait_for(state="visible")
        page.wait_for_timeout(pause * 2)
        video = page.video
        context.close()
        path = video.path()
        browser.close()
        return Path(path)


def render_segment(key: str, audio: Path, video_source: Path | None = None) -> Path:
    target = WORK / f"segment-{key}.mp4"
    seconds = duration(audio) + 1.0
    if video_source:
        command("-i", str(video_source), "-i", str(audio), "-t", f"{seconds:.2f}", "-vf",
                "scale=1280:720,fps=30,tpad=stop_mode=clone:stop_duration=12,format=yuv420p",
                "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-ar", "48000",
                "-b:a", "160k", "-af", "apad", "-movflags", "+faststart", str(target))
    else:
        command("-loop", "1", "-framerate", "30", "-i", str(WORK / f"{key}.png"), "-i", str(audio),
                "-t", f"{seconds:.2f}", "-vf", "format=yuv420p", "-c:v", "libx264", "-preset", "medium",
                "-crf", "21", "-c:a", "aac", "-ar", "48000", "-b:a", "160k", "-af", "apad",
                "-movflags", "+faststart", str(target))
    return target


def main() -> None:
    WORK.mkdir(exist_ok=True)
    voices = synthesize()
    print("Narraciones:", {key: round(duration(path), 1) for key, path in voices.items()}, flush=True)
    capture_slides()
    capture_scope()
    demo = record_demo(duration(voices["demo"]) + 1.0)
    order = ("problem", "method", "demo", "scope", "validation", "close")
    segments = [render_segment(key, voices[key], demo if key == "demo" else None) for key in order]
    concat = WORK / "segments.txt"
    concat.write_text("\n".join(f"file '{path.as_posix()}'" for path in segments), encoding="utf-8")
    command("-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", "-movflags", "+faststart", str(OUT))
    print(OUT, OUT.stat().st_size, flush=True)


if __name__ == "__main__":
    main()
