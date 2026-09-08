"""Artifacts: flashcards Anki TSV, cheat-sheet PDF, diagrama mermaid, outlines de video, diagramas HTML interactivos, quiz PDFs y resúmenes de lecciones."""
from fpdf import FPDF
from datetime import datetime, timedelta


def gen_flashcards(course, out):
    rows = []
    for m in course.modules:
        for les in m.lessons:
            for b in les.bullets:
                rows.append(f"{les.title['es']}\t{b['es']}\t{b['en']}\t{b['pt']}")
    (out / f"{course.slug}_anki.tsv").write_text("\n".join(rows), encoding="utf-8")


def gen_cheatsheet(course, out):
    """Cheat sheet PDF mejorado con portada de marca, metadatos y formato trilingüe."""
    pdf = FPDF()
    pdf.add_page()

    # PORTADA DE MARCA
    pdf.set_fill_color(7, 13, 24)  # bg brand color
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 28)
    pdf.cell(0, 20, "SECURE T", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 16)
    pdf.cell(0, 12, course.title["es"], fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    # META DATOS EN LA PORTADA
    pdf.set_text_color(100, 100, 100)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Módulos: {len(course.modules)}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Lecciones: {sum(len(m.lessons) for m in course.modules)}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Idiomas: Español, English, Português", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Generado: {datetime.now().strftime('%d/%m/%Y')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # CONTENIDO RESUMEN TRILINGÜE
    pdf.set_text_color(20, 20, 20)
    for m in course.modules:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, m.title["es"], new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        for les in m.lessons:
            pdf.set_font("Helvetica", "I", 8)
            pdf.cell(0, 5, f"  {les.title['es']} ({les.type})", new_x="LMARGIN", new_y="NEXT")
            for b in les.bullets[:2]:
                pdf.set_font("Helvetica", "", 8)
                pdf.cell(0, 4, f"    - {b['es']}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    pdf.output(str(out / f"{course.slug}_cheatsheet.pdf"))


def gen_diagram(course, out):
    lines = ["graph TD"]
    for m in course.modules:
        for les in m.lessons:
            lines.append(f'  {m.id}["{m.title["es"]}"] --> {les.id}["{les.title["es"]}"]')
    (out / f"{course.slug}.mmd").write_text("\n".join(lines), encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════
# NUEVOS ACTIVOS: outlines de video, diagramas HTML, quiz PDFs
# ════════════════════════════════════════════════════════════════════


def gen_video_outline(course, out):
    """Outline de video resumido por lección — los estudiantes pueden leerlo o pedir TTS."""
    lines = [f"SECURE T - {course.title['es']} - Módulo {course.modules[0].id}"]
    lines.append("=" * 60)
    for m in course.modules:
        lines.append(f"MÓDULO: {m.title['es']}")
        lines.append("-" * 40)
        for les in m.lessons:
            lines.append(f"LECCIÓN: {les.title['es']} ({les.type})")
            # Los 3 bullets principales
            for b in les.bullets[:3]:
                lines.append(f"  • {b['es']}")
            # Línea en blanco entre lecciones
            lines.append("")
    (out / f"{course.slug}_video-outline.txt").write_text("\n".join(lines), encoding="utf-8")


def gen_diagram_html(course, out):
    """Diagrama Mermaid convertido a HTML interactivo con selector de temas."""
    # Generar el diagrama Mermaid
    lines = ["graph TD"]
    for m in course.modules:
        for les in m.lessons:
            lines.append(f'  {m.id}["{m.title["es"]}"] --> {les.id}["{les.title["es"]}"]')
    diagram = "\n".join(lines)

    # Template HTML con Mermaid CDN
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{course.title['es']} - Diagrama de Curso</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0f;
            color: #e0e0e0;
            margin: 0;
            padding: 20px;
        }}
        .mermaid { 
            background: #2a2a3e; 
            padding: 20px; 
            border-radius: 8px; 
            margin: 20px 0;
        }}
        .controls {{
            background: #1a1a2e;
            padding: 10px 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        .controls span {{
            color: #7a7a8e;
            font-size: 12px;
        }}
        .controls select, .controls button {{
            background: #3a3a4e;
            color: #e0e0e0;
            border: 1px solid #3a3a4e;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 13px;
        }}
        .controls button {{ cursor: pointer; }}
    </style>
</head>
<body>
    <div class="controls">
        <span>Tema: </span>
        <select id="theme">
            <option value="forest">Forest (verde)</option>
            <option value="default">Default</option>
            <option value="neptune">Neptune (azul)</option>
        </select>
        <button onclick="mermaid.run()">Renderizar</button>
        <button onclick="window.print()">Imprimir</button>
    </div>
    <div class="mermaid" id="mermaid-diagram">{diagram}</div>
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'forest' }});
        // Cambiar tema al cambiar el selector
        document.getElementById('theme').addEventListener('change', (e) => {{
            mermaid.initialize({{ theme: e.target.value }});
            mermaid.render('mermaid-diagram');
        }});
    </script>
</body>
</html>"""
    (out / f"{course.slug}-diagram.html").write_text(html, encoding="utf-8")


def gen_quiz_pdf(course, out):
    """PDF de quizzes imprimible por módulo. Cada módulo con preguntas de opción múltiple A-D."""
    import json
    from fpdf import FPDF

    pdf = FPDF()
    quiz_count = 0

    for m in course.modules:
        if not m.quiz:
            continue
        quiz_count += 1
        pdf.add_page()
        # Título del módulo
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_fill_color(7, 13, 24)
        pdf.cell(0, 10, f"MÓDULO {m.id}: {m.title['es']}", fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        if not m.quiz:
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 6, "No hay preguntas de quiz definidas para este módulo.", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
            continue

        pdf.set_font("Helvetica", "", 11)
        for i, q in enumerate(m.quiz):
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 7, f"Pregunta {i+1}:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5, f"  {q['question']}")
            pdf.ln(1)

            # Opciones A-D
            options = q.get('options', [])
            opts_len = len(options)
            # Mostrar hasta 4 opciones
            for j in range(4):
                if j < opts_len:
                    pdf.set_font("Helvetica", "", 10)
                    pdf.cell(0, 6, f"  {chr(65+j)}) {options[j]}", new_x="LMARGIN", new_y="NEXT")
                else:
                    pdf.cell(0, 6, "  —", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)

    if quiz_count == 0:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Ningún módulo tiene quizzes definidas", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, "Añade preguntas de tipo QUIZ a los módulos del curso para generar este archivo.")

    pdf.output(str(out / f"{course.slug}-quizzes.pdf"))
