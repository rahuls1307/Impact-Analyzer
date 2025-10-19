import os
import re
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure API key globally
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

class SemanticArtifactExtractor:
    def __init__(self, model_name="gemini-2.5-flash", cache_file="artifact_cache.json"):
        self.model_name = model_name
        self.cache_file = cache_file
        self.artifact_cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file) as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        with open(self.cache_file, "w") as f:
            json.dump(self.artifact_cache, f, indent=2)

    # ---------------- Common artifacts (language-agnostic) ----------------
    def extract_common_artifacts(self, code: str, file_path: str):
        detected = []

        # API endpoints
        if re.search(r'@GetMapping|@PostMapping|router\.(get|post|put|delete)', code):
            routes = re.findall(r'["\'](/[\w/\-]+)["\']', code)
            for r in routes:
                detected.append({"type": "api_endpoint", "entity": r})

        # Config keys
        if file_path.endswith((".env", ".yml", ".yaml", ".properties")):
            keys = re.findall(r"([A-Z_][A-Z0-9_]+)\s*[:=]", code)
            for k in keys:
                detected.append({"type": "config_key", "entity": k})

        # Imports
        imports = re.findall(r"import\s+([\w\.]+);?", code)
        for imp in imports:
            detected.append({"type": "code_import", "entity": imp})

        # Classes / Functions
        for match in re.finditer(r"\bclass\s+(\w+)", code):
            detected.append({"type": "code_class", "entity": match.group(1)})

        return detected

    # ---------------- LLM-based DB extraction ----------------
    def extract_db_artifacts_llm(self, db_files: dict):
        """
        db_files: dict[file_path] = code
        Sends multiple files in one LLM call for efficiency.
        Asks LLM to detect database artifacts (tables, columns, procedures)
        in a language-agnostic way.
        """
        if not db_files:
            return []

        combined_prompt = (
            "You are an expert software architect. "
            "Analyze the following code files and extract all database artifacts "
            "(tables, columns, procedures). Respond only in JSON array format:\n\n"
        )

        for path, code in db_files.items():
            # Detect language from file extension
            ext = os.path.splitext(path)[1].lower()
            language_map = {
                ".java": "Java",
                ".py": "Python",
                ".js": "JavaScript",
                ".ts": "TypeScript",
                ".go": "Go",
                ".rb": "Ruby",
                ".cs": "C#",
                ".sql": "SQL",
                ".ddl": "SQL",
                ".dml": "SQL",
                ".psql": "SQL",
                ".pgsql": "SQL",
            }
            language = language_map.get(ext, "Unknown")

            snippet = code[:3000]  # truncate to first 3KB for efficiency
            combined_prompt += f"File: {path}\nLanguage: {language}\nCode:\n{snippet}\n\n"

        combined_prompt += (
            "Output format example:\n"
            "[\n"
            "  {\"type\": \"table\", \"name\": \"bonds\", \"file\": \"...\"},\n"
            "  {\"type\": \"column\", \"table\": \"bonds\", \"name\": \"id\", \"file\": \"...\"},\n"
            "  {\"type\": \"procedure\", \"name\": \"calculate_interest\", \"file\": \"...\"}\n"
            "]\n"
            "Return valid JSON only."
        )

        # Call the LLM
        model = genai.GenerativeModel(self.model_name)
        response = model.generate_content(combined_prompt)

        try:
            db_artifacts = json.loads(response.text)
        except Exception:
            db_artifacts = []

        # Attach file info if missing
        for artifact in db_artifacts:
            if "file" not in artifact:
                artifact["file"] = "unknown"

        return db_artifacts


    # ---------------- Full repo extraction ----------------
    def extract_from_repo(self, repo_path: str, repo_name: str):
        all_artifacts = []
        db_files_to_send = {}

        for root, _, files in os.walk(repo_path):
            for file in files:
                path = os.path.join(root, file)
                with open(path, "r", errors="ignore") as f:
                    code = f.read()

                # 1️⃣ Extract common artifacts (API, config, code)
                common = self.extract_common_artifacts(code, path)
                for c in common:
                    c["repo"] = repo_name
                    c["file"] = path
                all_artifacts.extend(common)

                # 2️⃣ Collect DB-related files for LLM
                if file.endswith((
                    ".sql", ".ddl", ".dml", ".psql", ".pgsql",
                    ".py", ".java", ".js", ".ts", ".go", ".rb", ".cs",
                    ".xml", ".yml", ".yaml"
                )):
                    db_files_to_send[path] = code

        # 3️⃣ Send DB files to LLM in batch
        if db_files_to_send:
            db_artifacts = self.extract_db_artifacts_llm(db_files_to_send)
            for a in db_artifacts:
                a["repo"] = repo_name
            all_artifacts.extend(db_artifacts)

        return all_artifacts
