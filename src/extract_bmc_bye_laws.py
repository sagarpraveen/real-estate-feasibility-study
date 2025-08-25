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


DEFAULT_MODEL_ID = os.getenv("LANGEXTRACT_MODEL_ID", "gemini-2.5-flash")


def build_prompt() -> str:
	return (
		"Extract structured entities from BMC (MCGM) building bye-laws. "
		"Return sections, clauses, definitions, FSI-related rules, and penalties as structured items."
	)


def build_examples() -> List["lx.data.ExampleData"]:
	# Construct typed examples for few-shot guidance
	example_text = (
		"Section 5: Water Supply. Clause 5.1: The corporation shall ensure adequate supply. "
		"Penalty: A fine of Rs. 5000 shall be imposed for non-compliance."
	)
	extractions = [
		lx.data.Extraction(
			extraction_class="section",
			extraction_text="Section 5: Water Supply",
		),
		lx.data.Extraction(
			extraction_class="clause",
			extraction_text="Clause 5.1: The corporation shall ensure adequate supply.",
		),
		lx.data.Extraction(
			extraction_class="penalty",
			extraction_text="A fine of Rs. 5000 shall be imposed for non-compliance.",
		),
	]
	return [lx.data.ExampleData(text=example_text, extractions=extractions)]


def extract(text: str, model_id: str = DEFAULT_MODEL_ID) -> Any:
	prompt = build_prompt()
	examples = build_examples()
	result = lx.extract(
		text_or_documents=text,
		prompt_description=prompt,
		examples=examples,
		model_id=model_id,
	)
	return result


def save_results(result: Any, output_dir: Path) -> Path:
	output_dir.mkdir(parents=True, exist_ok=True)
	jsonl_path = output_dir / "results.jsonl"
	lx.io.save_annotated_documents([result], output_name=str(jsonl_path))
	return jsonl_path


def visualize(jsonl_path: Path, output_html: Path) -> None:
	html_content = lx.visualize(str(jsonl_path))
	output_html.write_text(html_content, encoding="utf-8")


def main() -> None:
	load_dotenv()
	input_path = Path(os.getenv("BMC_BYELAWS_PATH", "tests/sample_bmc_bye_laws.txt"))
	output_dir = Path(os.getenv("OUTPUT_DIR", "outputs"))
	output_html = output_dir / "visualization.html"

	if not input_path.exists():
		raise SystemExit(f"Input text file not found: {input_path}")

	text = input_path.read_text(encoding="utf-8")
	result = extract(text)
	jsonl_path = save_results(result, output_dir)
	visualize(jsonl_path, output_html)

	print(f"Saved JSONL: {jsonl_path}")
	print(f"Saved HTML visualization: {output_html}")


if __name__ == "__main__":
	main()
