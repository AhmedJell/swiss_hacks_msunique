import json

from langchain_text_splitters import MarkdownHeaderTextSplitter


class ReportParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_json(self):
        with open(self.file_path) as file:
            return json.load(file)
        
    
    def parse_markdown(self, json_data ):
        json_data['analyzeResult']['content']
        markdown = ""
        for key, value in json_data.items():
            markdown += f"### {key}\n"
            if isinstance(value, dict):
                for k, v in value.items():
                    markdown += f"- **{k}**: {v}\n"
            else:
                markdown += f"- {value}\n"
        return markdown