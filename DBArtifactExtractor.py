import re
import sqlparse
from pathlib import Path

class DatabaseArtifactExtractor:
    def extract_from_file(self, file_path: str, content: str):
        artifacts = []
        
        # SQL files
        if file_path.endswith(('.sql', '.migration')):
            artifacts.extend(self._extract_sql_artifacts(content, file_path))
        
        # ORM files (Python, Java, etc.)
        artifacts.extend(self._extract_orm_artifacts(content, file_path))
        
        return artifacts
    
    def _extract_sql_artifacts(self, content: str, file_path: str):
        artifacts = []
        
        # Parse SQL statements
        parsed = sqlparse.parse(content)
        
        for statement in parsed:
            if statement.get_type() == 'CREATE':
                # Extract table names
                table_match = re.search(r'CREATE\s+TABLE\s+(\w+)', str(statement), re.IGNORECASE)
                if table_match:
                    artifacts.append({
                        'type': 'table',
                        'name': table_match.group(1),
                        'file': file_path,
                        'line': content[:statement.pos].count('\n') + 1
                    })
            
            # Extract column definitions
            column_matches = re.findall(r'(\w+)\s+(\w+)', str(statement))
            for col_name, col_type in column_matches:
                artifacts.append({
                    'type': 'column',
                    'name': col_name,
                    'data_type': col_type,
                    'file': file_path
                })
        
        return artifacts