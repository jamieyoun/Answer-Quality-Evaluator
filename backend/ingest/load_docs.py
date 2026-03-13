import os
import re
import yaml
from typing import List
from schemas.document import Document, DocumentSection

FRONT_MATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

def load_markdown_file(path: str) -> Document:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    text = text.lstrip("\ufeff").replace("\r\n", "\n").lstrip()

    match = FRONT_MATTER_PATTERN.match(text)

    if match:
        metadata = yaml.safe_load(match.group(1))
        body = text[match.end():].strip()
    else:
        # ✅ Fallback: allow docs without YAML (realistic)
        metadata = synthesize_metadata(path, text)
        body = text.strip()

    sections = parse_sections(body)

    return Document(
        doc_id=metadata["doc_id"],
        title=metadata["title"],
        owner_team=metadata["owner_team"],
        last_updated=str(metadata["last_updated"]),
        effective_date=str(metadata["effective_date"]),
        policy_type=metadata["policy_type"],
        region_scope=metadata["region_scope"],
        source_of_truth=metadata["source_of_truth"],
        supersedes=metadata.get("supersedes"),
        sections=sections,
        raw_text=body,
        file_path=path,
    )


def parse_sections(markdown_body: str) -> List[DocumentSection]:
    sections = []
    current_header = "Introduction"
    current_content = []

    for line in markdown_body.splitlines():
        if line.startswith("## "):
            if current_content:
                sections.append(
                    DocumentSection(
                        header=current_header,
                        content="\n".join(current_content).strip(),
                    )
                )
            current_header = line.replace("## ", "").strip()
            current_content = []
        else:
            current_content.append(line)

    if current_content:
        sections.append(
            DocumentSection(
                header=current_header,
                content="\n".join(current_content).strip(),
            )
        )

    return sections


def load_all_documents(docs_dir: str) -> List[Document]:
    documents = []
    for file in os.listdir(docs_dir):
        if file.endswith(".md"):
            path = os.path.join(docs_dir, file)
            documents.append(load_markdown_file(path))
    return documents

def synthesize_metadata(path: str, text: str) -> dict:
    filename = os.path.basename(path)
    slug = os.path.splitext(filename)[0]

    title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else slug.replace("_", " ").title()

    return {
        "doc_id": f"KB-FALLBACK-{slug[:24]}",
        "title": title,
        "owner_team": "Unknown",
        "last_updated": "1970-01-01",
        "effective_date": "1970-01-01",
        "policy_type": "guidance",
        "region_scope": ["US", "EMEA", "APAC"],
        "source_of_truth": False,
        "supersedes": None,
    }