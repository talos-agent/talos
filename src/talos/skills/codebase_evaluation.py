from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from pydantic import ConfigDict, Field

from talos.models.proposals import QueryResponse
from talos.prompts.prompt_manager import PromptManager
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.skills.base import Skill
from talos.tools.github.tools import GithubTools


class CodebaseEvaluationSkill(Skill):
    """
    A skill for evaluating codebase quality and suggesting improvements.
    
    This skill analyzes repository structure, code patterns, documentation,
    and other quality metrics to provide actionable improvement recommendations.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    llm: BaseLanguageModel
    prompt_manager: PromptManager = Field(default_factory=lambda: FilePromptManager("src/talos/prompts"))
    github_tools: GithubTools | None = None

    @property
    def name(self) -> str:
        return "codebase_evaluation_skill"

    def run(self, **kwargs: Any) -> QueryResponse:
        """
        Evaluates a codebase and returns improvement recommendations.
        
        Args:
            repo_path: Local path to repository (optional)
            github_user: GitHub username (optional, requires github_project)
            github_project: GitHub project name (optional, requires github_user)
            
        Returns:
            QueryResponse with evaluation results and recommendations
        """
        repo_path = kwargs.get("repo_path")
        github_user = kwargs.get("github_user")
        github_project = kwargs.get("github_project")
        
        if not repo_path and not (github_user and github_project):
            raise ValueError("Must provide either repo_path or both github_user and github_project")
        
        if github_user and github_project:
            return self._evaluate_github_repo(github_user, github_project)
        elif repo_path:
            return self._evaluate_local_repo(repo_path)
        else:
            raise ValueError("Must provide either repo_path or both github_user and github_project")

    def _evaluate_github_repo(self, user: str, project: str) -> QueryResponse:
        """Evaluate a GitHub repository."""
        if not self.github_tools:
            try:
                from talos.settings import GitHubSettings
                github_settings = GitHubSettings()
                if github_settings.GITHUB_API_TOKEN:
                    self.github_tools = GithubTools(token=github_settings.GITHUB_API_TOKEN)
                else:
                    raise ValueError("GitHub API token not available")
            except Exception:
                raise ValueError("GitHub tools not configured and cannot be initialized")
        
        structure = self._analyze_github_structure(user, project)
        key_files = self._get_key_files_content(user, project)
        evaluation = self._generate_evaluation(structure, key_files, f"{user}/{project}")
        
        return QueryResponse(answers=[evaluation])

    def _evaluate_local_repo(self, repo_path: str) -> QueryResponse:
        """Evaluate a local repository."""
        if not os.path.exists(repo_path):
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        structure = self._analyze_local_structure(repo_path)
        key_files = self._get_local_files_content(repo_path)
        evaluation = self._generate_evaluation(structure, key_files, repo_path)
        
        return QueryResponse(answers=[evaluation])

    def _analyze_github_structure(self, user: str, project: str) -> dict[str, Any]:
        """Analyze GitHub repository structure."""
        if not self.github_tools:
            return {"error": "GitHub tools not available"}
        
        try:
            root_contents = self.github_tools.get_project_structure(user, project)
            
            structure = {
                "total_files": len(root_contents),
                "directories": [f for f in root_contents if "." not in f.split("/")[-1]],
                "files": [f for f in root_contents if "." in f.split("/")[-1]],
                "has_readme": any("readme" in f.lower() for f in root_contents),
                "has_tests": any("test" in f.lower() for f in root_contents),
                "has_docs": any("doc" in f.lower() for f in root_contents),
                "config_files": [f for f in root_contents if f.split("/")[-1] in [
                    "package.json", "requirements.txt", "Cargo.toml", "go.mod", 
                    "pom.xml", "build.gradle", "Makefile", "pyproject.toml"
                ]]
            }
            
            return structure
        except Exception as e:
            return {"error": f"Failed to analyze structure: {str(e)}"}

    def _analyze_local_structure(self, repo_path: str) -> dict[str, Any]:
        """Analyze local repository structure."""
        repo = Path(repo_path)
        all_files = list(repo.rglob("*"))
        
        structure = {
            "total_files": len([f for f in all_files if f.is_file()]),
            "directories": [str(f.relative_to(repo)) for f in all_files if f.is_dir()],
            "files": [str(f.relative_to(repo)) for f in all_files if f.is_file()],
            "has_readme": any("readme" in f.name.lower() for f in all_files),
            "has_tests": any("test" in str(f).lower() for f in all_files),
            "has_docs": any("doc" in str(f).lower() for f in all_files),
            "config_files": [str(f.relative_to(repo)) for f in all_files 
                           if f.name in ["package.json", "requirements.txt", "Cargo.toml", 
                                       "go.mod", "pom.xml", "build.gradle", "Makefile", "pyproject.toml"]]
        }
        
        return structure

    def _get_key_files_content(self, user: str, project: str) -> dict[str, str]:
        """Get content of key files from GitHub repository."""
        key_files: dict[str, str] = {}
        
        if not self.github_tools:
            return key_files
        
        for readme_name in ["README.md", "README.rst", "README.txt", "readme.md"]:
            try:
                content = self.github_tools.get_file_content(user, project, readme_name)
                key_files["readme"] = content[:2000]
                break
            except Exception:
                continue
        
        try:
            structure = self.github_tools.get_project_structure(user, project)
            source_files = [f for f in structure if f.endswith(('.py', '.js', '.ts', '.java', '.go', '.rs'))][:5]
            
            for file_path in source_files:
                try:
                    content = self.github_tools.get_file_content(user, project, file_path)
                    key_files[file_path] = content[:1000]
                except Exception:
                    continue
        except Exception:
            pass
        
        return key_files

    def _get_local_files_content(self, repo_path: str) -> dict[str, str]:
        """Get content of key files from local repository."""
        key_files: dict[str, str] = {}
        repo = Path(repo_path)
        
        for readme_file in repo.glob("README*"):
            try:
                content = readme_file.read_text(encoding='utf-8')
                key_files["readme"] = content[:2000]
                break
            except Exception:
                continue
        
        source_patterns = ["**/*.py", "**/*.js", "**/*.ts", "**/*.java", "**/*.go", "**/*.rs"]
        source_files = []
        
        for pattern in source_patterns:
            source_files.extend(list(repo.glob(pattern))[:2])
            if len(source_files) >= 5:
                break
        
        for file_path in source_files[:5]:
            try:
                content = file_path.read_text(encoding='utf-8')
                key_files[str(file_path.relative_to(repo))] = content[:1000]
            except Exception:
                continue
        
        return key_files

    def _generate_evaluation(self, structure: dict, key_files: dict, repo_identifier: str) -> str:
        """Generate codebase evaluation using LLM."""
        prompt = self.prompt_manager.get_prompt("codebase_evaluation_prompt")
        if not prompt:
            raise ValueError("Could not find prompt 'codebase_evaluation_prompt'")
        
        analysis_data = {
            "repo_identifier": repo_identifier,
            "structure": structure,
            "key_files": key_files,
            "file_count": structure.get("total_files", 0),
            "has_readme": structure.get("has_readme", False),
            "has_tests": structure.get("has_tests", False),
            "has_docs": structure.get("has_docs", False),
            "config_files": structure.get("config_files", [])
        }
        
        prompt_template = PromptTemplate(
            template=prompt.template,
            input_variables=prompt.input_variables,
        )
        
        chain = prompt_template | self.llm
        response = chain.invoke(analysis_data)
        
        return response.content
