from __future__ import annotations

import logging
import re
from typing import Any

from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from pydantic import ConfigDict

from talos.models.services import PRReviewResponse
from talos.prompts.prompt_manager import PromptManager
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.skills.base import Skill
from talos.tools.github.tools import GithubTools


class PRReviewSkill(Skill):
    """
    A skill for reviewing GitHub pull requests with automated commenting and approval.
    
    This skill analyzes PR diffs, provides security assessments, code quality feedback,
    and can automatically comment on or approve PRs based on the analysis.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    llm: BaseLanguageModel
    prompt_manager: PromptManager = FilePromptManager("src/talos/prompts")
    github_tools: GithubTools

    @property
    def name(self) -> str:
        return "pr_review_skill"

    def run(self, **kwargs: Any) -> PRReviewResponse:
        """
        Review a pull request and optionally comment/approve.
        
        Args:
            user: GitHub username/org
            repo: Repository name
            pr_number: Pull request number
            auto_comment: Whether to automatically comment (default: True)
            auto_approve: Whether to automatically approve if criteria met (default: True)
        """
        user = kwargs.get("user")
        repo = kwargs.get("repo") 
        pr_number = kwargs.get("pr_number")
        auto_comment = kwargs.get("auto_comment", True)
        auto_approve = kwargs.get("auto_approve", True)
        
        if not all([user, repo, pr_number]):
            raise ValueError("Missing required arguments: user, repo, pr_number")
            
        if not isinstance(user, str):
            raise ValueError("user must be a string")
        if not isinstance(repo, str):
            raise ValueError("repo must be a string")
        if not isinstance(pr_number, int):
            raise ValueError("pr_number must be an integer")
            
        logger = logging.getLogger(__name__)
        logger.info(f"Reviewing PR {user}/{repo}#{pr_number}")
        
        diff = self.github_tools.get_pr_diff(user, repo, pr_number)
        comments = self.github_tools.get_pr_comments(user, repo, pr_number)
        files = self.github_tools.get_pr_files(user, repo, pr_number)
        
        if self._has_existing_review(comments) and not self._has_new_changes(comments, diff):
            logger.info("Already reviewed and no new changes detected")
            return PRReviewResponse(
                answers=["Already reviewed this PR with no new changes"],
                recommendation="SKIP"
            )
        
        review_response = self._analyze_pr(diff, comments, files)
        
        if auto_comment and review_response.recommendation != "SKIP":
            comment_text = self._format_review_comment(review_response)
            self.github_tools.comment_on_pr(user, repo, pr_number, comment_text)
            logger.info("Posted review comment")
        
        if (auto_approve and 
            review_response.recommendation == "APPROVE" and
            review_response.security_score and review_response.security_score > 80 and
            review_response.quality_score and review_response.quality_score > 70):
            self.github_tools.approve_pr(user, repo, pr_number)
            logger.info("Approved PR")
            
        return review_response

    def _analyze_pr(self, diff: str, comments: list, files: list) -> PRReviewResponse:
        """Analyze PR using LLM and extract structured response."""
        prompt = self.prompt_manager.get_prompt("github_pr_review")
        if not prompt:
            raise ValueError("Prompt 'github_pr_review' not found")
            
        prompt_template = PromptTemplate(
            template=prompt.template,
            input_variables=prompt.input_variables,
        )
        chain = prompt_template | self.llm
        
        comments_str = "\n".join([f"- {c.get('user', 'unknown')}: {c.get('comment', '')}" for c in comments])
        files_str = ", ".join(files)
        
        response = chain.invoke({
            "diff": diff,
            "comments": comments_str,
            "files": files_str
        })
        
        content = response.content
        security_score = self._extract_score(content, "security")
        quality_score = self._extract_score(content, "quality")
        recommendation = self._extract_recommendation(content)
        reasoning = self._extract_reasoning(content)
        
        return PRReviewResponse(
            answers=[content],
            security_score=security_score,
            quality_score=quality_score,
            recommendation=recommendation,
            reasoning=reasoning
        )

    def _extract_score(self, content: str, score_type: str) -> float | None:
        """Extract security or quality score from LLM response."""
        pattern = rf"{score_type}.*?score.*?(\d+)"
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return None

    def _extract_recommendation(self, content: str) -> str | None:
        """Extract recommendation from LLM response."""
        for rec in ["APPROVE", "REQUEST_CHANGES", "COMMENT"]:
            if rec in content.upper():
                return rec
        return "COMMENT"

    def _extract_reasoning(self, content: str) -> str | None:
        """Extract reasoning from LLM response."""
        match = re.search(r"reasoning:?\s*(.*?)(?:\n\n|\Z)", content, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _has_existing_review(self, comments: list) -> bool:
        """Check if we've already reviewed this PR."""
        bot_comments = [c for c in comments if "talos" in c.get("user", "").lower()]
        return len(bot_comments) > 0

    def _has_new_changes(self, comments: list, diff: str) -> bool:
        """Check if there are new changes since last review."""
        return True

    def _format_review_comment(self, review: PRReviewResponse) -> str:
        """Format the review response into a GitHub comment."""
        comment = "## 🤖 Talos PR Review\n\n"
        
        if review.answers:
            comment += review.answers[0] + "\n\n"
        
        if review.security_score is not None:
            comment += f"**Security Score:** {review.security_score}/100\n"
        
        if review.quality_score is not None:
            comment += f"**Quality Score:** {review.quality_score}/100\n"
        
        if review.recommendation:
            comment += f"**Recommendation:** {review.recommendation}\n"
        
        if review.reasoning:
            comment += f"\n**Reasoning:** {review.reasoning}\n"
        
        comment += "\n---\n*This review was generated automatically by Talos AI*"
        
        return comment
