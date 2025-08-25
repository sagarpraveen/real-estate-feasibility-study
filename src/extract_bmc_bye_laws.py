import os
import json
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv

try:
	import langextract as lx
except ImportError as exc:
	raise SystemExit(
		"LangExtract is not installed. Please run: pip install -r requirements.txt"
	) from exc

# PDF support
try:
	from pypdf import PdfReader
except Exception:
	PdfReader = None  # Optional; we handle at runtime


# Prefer user-provided model id; default to a local Ollama model
DEFAULT_MODEL_ID = os.getenv("LANGEXTRACT_MODEL_ID", "llama3.2:1b")


def build_prompt() -> str:
	return (
		"Extract structured entities from BMC (MCGM) building bye-laws.\n"
		"Respond with a strict JSON object having the key 'extractions', where 'extractions' is an array of objects.\n"
		"Allowed 'extraction_class' values: section, clause, definition, fsi_rule, setback_rule, height_rule, penalty.\n"
		"Each object must have: 'extraction_class', 'extraction_text' (exact span), and optional 'attributes' (JSON).\n"
		"Recommended attributes by class:\n"
		"- fsi_rule: { max_fsi: number|string, zone?: string, notes?: string }\n"
		"- setback_rule: { front?: string, side?: string, rear?: string, units?: string, notes?: string }\n"
		"- height_rule: { max_height: string, units?: string, condition?: string, notes?: string }\n"
		"- penalty: { penalty_type?: string, amount?: string }\n"
		"Example output:\n"
		"{\n"
		"  \"extractions\": [\n"
		"    {\"extraction_class\": \"section\", \"extraction_text\": \"Section 5: Water Supply\"},\n"
		"    {\"extraction_class\": \"fsi_rule\", \"extraction_text\": \"FSI up to 2.0 permitted in Zone R\", \"attributes\": {\"max_fsi\": \"2.0\", \"zone\": \"R\"}},\n"
		"    {\"extraction_class\": \"setback_rule\", \"extraction_text\": \"Front setback 6 m for roads > 18 m\", \"attributes\": {\"front\": \"6 m\", \"units\": \"m\"}},\n"
		"    {\"extraction_class\": \"height_rule\", \"extraction_text\": \"Max building height 70 m subject to fire NOC\", \"attributes\": {\"max_height\": \"70\", \"units\": \"m\", \"condition\": \"fire NOC\"}}\n"
		"  ]\n"
		"}\n"
	)


def build_examples() -> List["lx.data.ExampleData"]:
	# Construct typed examples for few-shot guidance including Mumbai specifics
	example_text = (
		"Section 10: FSI. In Residential Zone (R), FSI up to 2.0 is permitted. "
		"Setbacks: Front setback 6 m for roads > 18 m; side and rear 3 m. "
		"Max building height 70 m subject to fire NOC. Penalty: Fine Rs. 5000."
	)
	extractions = [
		lx.data.Extraction(
			extraction_class="section",
			extraction_text="Section 10: FSI",
		),
		lx.data.Extraction(
			extraction_class="fsi_rule",
			extraction_text="FSI up to 2.0 is permitted",
			attributes={"max_fsi": "2.0", "zone": "R"},
		),
		lx.data.Extraction(
			extraction_class="setback_rule",
			extraction_text="Front setback 6 m for roads > 18 m; side and rear 3 m",
			attributes={"front": "6 m", "side": "3 m", "rear": "3 m", "units": "m"},
		),
		lx.data.Extraction(
			extraction_class="height_rule",
			extraction_text="Max building height 70 m subject to fire NOC",
			attributes={"max_height": "70", "units": "m", "condition": "fire NOC"},
		),
		lx.data.Extraction(
			extraction_class="penalty",
			extraction_text="Fine Rs. 5000",
			attributes={"penalty_type": "Fine", "amount": "Rs. 5000"},
		),
	]
	return [lx.data.ExampleData(text=example_text, extractions=extractions)]


def _read_text(input_path: Path) -> str:
	if input_path.suffix.lower() == ".pdf":
		if PdfReader is None:
			raise SystemExit("pypdf not installed. Run: uv pip install -r requirements.txt")
		reader = PdfReader(str(input_path))
		pages = []
		for page in reader.pages:
			try:
				pages.append(page.extract_text() or "")
			except Exception:
				pages.append("")
		return "\n\n".join(pages)
	return input_path.read_text(encoding="utf-8", errors="ignore")


def extract(text: str, model_id: str = DEFAULT_MODEL_ID) -> Any:
	prompt = build_prompt()
	examples = build_examples()
	result = lx.extract(
		text_or_documents=text,
		prompt_description=prompt,
		examples=examples,
		model_id=model_id,
		fence_output=False,
	)
	return result


def save_results(result: Any, output_dir: Path) -> Path:
	output_dir = output_dir.resolve()
	output_dir.mkdir(parents=True, exist_ok=True)
	jsonl_path = (output_dir / "results.jsonl").resolve()
	lx.io.save_annotated_documents([result], output_name=str(jsonl_path))
	if not jsonl_path.exists():
		raise FileNotFoundError(f"Expected results not found at {jsonl_path}")
	return jsonl_path


def visualize(jsonl_path: Path, output_html: Path) -> None:
	html_content = lx.visualize(str(jsonl_path.resolve()))
	output_html.parent.mkdir(parents=True, exist_ok=True)
	output_html.write_text(html_content, encoding="utf-8")


def main() -> None:
	load_dotenv()
	input_path = Path(os.getenv("BMC_BYELAWS_PATH", "tests/sample_bmc_bye_laws.txt")).resolve()
	output_dir = Path(os.getenv("OUTPUT_DIR", "outputs")).resolve()
	output_html = (output_dir / "visualization.html").resolve()

	if not input_path.exists():
		raise SystemExit(f"Input text file not found: {input_path}")

	text = _read_text(input_path)
	result = extract(text)
	jsonl_path = save_results(result, output_dir)
	visualize(jsonl_path, output_html)

	print(f"Saved JSONL: {jsonl_path}")
	print(f"Saved HTML visualization: {output_html}")


if __name__ == "__main__":
	main()
