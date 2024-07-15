import os
import zipfile
import git
import tempfile
# from sentence_transformers import SentenceTransformer, util
import shutil
import mimetypes

class GitHubUtils:
    def __init__(self):
        self.exclude_dirs = {'.git', '.github', '__pycache__'}
        self.exclude_files = {'.gitignore', '.gitattributes', 'LICENSE', 'requirements.txt'}
        pass
    def clone_repo(self, github_url):
        temp_dir = tempfile.mkdtemp()
        git.Repo.clone_from(github_url, temp_dir)
        return temp_dir
    def read_zip_file(self, zip_path):
        """
        Read and process the contents of a ZIP file.
        """
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        text_data = self.read_all_files(temp_dir)
        shutil.rmtree(temp_dir)
        return text_data
    
    def read_all_files(self, repo_path):
        text_data = []
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            print(dirs)
            for file in files:
                if file in self.exclude_files or file.startswith('.'):
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text_data.append(f.read())
                except Exception as e:
                    print(f"Could not read file {file_path}: {e}")
        return text_data
    def cleanup(self, path):
        if path and os.path.exists(path):
            shutil.rmtree(path, onerror=self._handle_remove_readonly)

    def _handle_remove_readonly(self, func, path, exc_info):
        os.chmod(path, 0o700)
        func(path)