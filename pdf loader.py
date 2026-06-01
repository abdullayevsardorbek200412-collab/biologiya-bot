import os
import glob

try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# Kitoblar asosiy papkada ham, pdfs/ papkasida ham bo'lishi mumkin
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class PDFLoader:
    def __init__(self):
        self.pdf_texts = {}
        self._load_pdfs()

    def _load_pdfs(self):
        if not PDF_SUPPORT:
            print("PyPDF2 o'rnatilmagan")
            return

        # Har ikki joydan qidirish
        patterns = [
            os.path.join(BASE_DIR, "*.pdf"),
            os.path.join(BASE_DIR, "pdfs", "*.pdf"),
        ]

        pdf_files = []
        for pattern in patterns:
            pdf_files.extend(glob.glob(pattern))

        print(f"📚 {len(pdf_files)} ta PDF topildi")

        for pdf_path in pdf_files:
            filename = os.path.basename(pdf_path)
            try:
                text = self._extract_pdf_text(pdf_path)
                self.pdf_texts[filename] = text
                print(f"✅ O'qildi: {filename}")
            except Exception as e:
                print(f"❌ Xato {filename}: {e}")

    def _extract_pdf_text(self, pdf_path: str) -> str:
        text = ""
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                try:
                    text += page.extract_text() + "\n"
                except:
                    pass
        return text

    def search_in_pdfs(self, query: str, max_chars: int = 3000) -> str:
        if not self.pdf_texts:
            return ""

        query_lower = query.lower()
        query_words = [w for w in query_lower.split() if len(w) > 2]

        results = []
        for filename, text in self.pdf_texts.items():
            grade_info = ""
            for g in ["5", "6", "7", "8", "9", "10", "11"]:
                if g in filename:
                    grade_info = f"{g}-sinf"
                    break

            paragraphs = text.split("\n")
            for para in paragraphs:
                if len(para.strip()) < 20:
                    continue
                para_lower = para.lower()
                score = sum(1 for word in query_words if word in para_lower)
                if score > 0:
                    results.append((score, grade_info, para.strip()))

        if not results:
            return ""

        results.sort(reverse=True)
        top_results = results[:5]

        context = "📚 Darslik ma'lumotlari:\n\n"
        for score, grade, para in top_results:
            prefix = f"[{grade}] " if grade else ""
            context += f"{prefix}{para}\n\n"

        if len(context) > max_chars:
            context = context[:max_chars] + "..."

        return context

    def reload_pdfs(self):
        self.pdf_texts = {}
        self._load_pdfs()
