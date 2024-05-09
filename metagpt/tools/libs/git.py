#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from github.Issue import Issue
from github.PullRequest import PullRequest

from metagpt.tools.tool_registry import register_tool
from metagpt.utils.git_repository import GitBranch, GitRepository


# @register_tool(tags=["git"])
async def git_clone(url: str, output_dir: str | Path = None) -> Path:
    """
    Clones a Git repository from the given URL.

    Args:
        url (Union[str, Path]): The URL or local path of the Git repository to clone.
        output_dir (Union[str, Path], optional): The directory where the repository should be cloned.
            If None, the repository will be cloned into the current working directory. Defaults to None.

    Returns:
        Path: The path to the cloned repository.

    Example:
        >>> url = "https://github.com/iorisa/snake-game.git"
        >>> local_path = await git_clone(url=url)
        >>> print(local_path)
        /local/path/to/snake-game
    """
    repo = await GitRepository.clone_from(url=url, output_dir=output_dir)
    return repo.workdir


@register_tool(
    tags=["software development", "git", "Checks out the specific commit/branch/tag of the local Git repository."]
)
async def git_checkout(repo_dir: str | Path, commit_id: str):
    """
    Checks out a specific commit in a Git repository.

    Args:
        repo_dir (str or Path): The directory containing the Git repository.
        commit_id (str): The ID of the commit or the name of branch/tag to check out.

    Raises:
        ValueError: If the specified Git root is invalid.

    Example:
        >>> repo_dir = '/TO/GIT/REPO'
        >>> commit_id = 'main'
        >>> await git_checkout(repo_dir=repo_dir, commit_id=commit_id)
        git checkout main
    """
    repo = GitRepository(local_path=repo_dir, auto_init=False)
    if not repo.is_valid:
        ValueError(f"Invalid git root: {repo_dir}")
    await repo.checkout(commit_id)


@register_tool(tags=["software development", "git", "Commit the changes and push to remote git repository."])
async def git_push(
    local_path: Union[str, Path],
    access_token: str,
    comments: str = "Commit",
    new_branch: str = "",
) -> GitBranch:
    """
    Pushes changes from a local Git repository to its remote counterpart.

    Args:
        local_path (Union[str, Path]): The path to the local Git repository.
        access_token (str): The access token for authentication. Use `get_env` to get access token.
        comments (str, optional): The commit message to use. Defaults to "Commit".
        new_branch (str, optional): The name of the new branch to create and push changes to.
            If not provided, changes will be pushed to the current branch. Defaults to "".

    Returns:
        GitBranch: The branch to which the changes were pushed.
    Raises:
        ValueError: If the provided local_path does not point to a valid Git repository.

    Example:
        >>> url = "https://github.com/iorisa/snake-game.git"
        >>> local_path = await git_clone(url=url)
        >>> from metagpt.tools.libs import get_env
        >>> access_token = await get_env(key="access_token", app_name="github")  # Read access token from enviroment variables.
        >>> comments = "Archive"
        >>> new_branch = "feature/new"
        >>> branch = await git_push(local_path=local_path, access_token=access_token, comments=comments, new_branch=new_branch)
        >>> base = branch.base
        >>> head = branch.head
        >>> repo_name = branch.repo_name
        >>> print(f"base branch:'{base}', head branch:'{head}', repo_name:'{repo_name}'")
        base branch:'master', head branch:'feature/new', repo_name:'iorisa/snake-game'

    """
    if not GitRepository.is_git_dir(local_path):
        raise ValueError("Invalid local git repository")

    repo = GitRepository(local_path=local_path, auto_init=False)
    branch = await repo.push(new_branch=new_branch, comments=comments, access_token=access_token)
    return branch


@register_tool(tags=["software development", "git", "create a git pull/merge request"])
async def git_create_pull(
    base: str,
    head: str,
    base_repo_name: str,
    access_token: str,
    head_repo_name: Optional[str] = None,
    title: Optional[str] = None,
    body: Optional[str] = None,
    issue: Optional[Issue] = None,
) -> PullRequest:
    """
    Creates a pull request on a Git repository.

    Args:
        base (str): The base branch of the pull request.
        head (str): The head branch of the pull request.
        base_repo_name (str): The full repository name (user/repo) where the pull request will be created.
        access_token (str): The access token for authentication. Use `get_env` to get access token.
        head_repo_name (Optional[str], optional): The full repository name (user/repo) where the pull request will merge from. Defaults to None.
        title (Optional[str], optional): The title of the pull request. Defaults to None.
        body (Optional[str], optional): The body of the pull request. Defaults to None.
        issue (Optional[Issue], optional): The related issue of the pull request. Defaults to None.

    Example:
        >>> # push and create pull
        >>> url = "https://github.com/iorisa/snake-game.git"
        >>> local_path = await git_clone(url=url)
        >>> from metagpt.tools.libs import get_env
        >>> access_token = await get_env(key="access_token", app_name="github")
        >>> comments = "Archive"
        >>> new_branch = "feature/new"
        >>> branch = await git_push(local_path=local_path, access_token=access_token, comments=comments, new_branch=new_branch)
        >>> base = branch.base
        >>> head = branch.head
        >>> repo_name = branch.repo_name
        >>> print(f"base branch:'{base}', head branch:'{head}', repo_name:'{repo_name}'")
        base branch:'master', head branch:'feature/new', repo_name:'iorisa/snake-game'
        >>> title = "feat: modify http lib",
        >>> body = "Change HTTP library used to send requests"
        >>> pr = await git_create_pull(
        >>>   base_repo_name=repo_name,
        >>>   base=base,
        >>>   head=head,
        >>>   title=title,
        >>>   body=body,
        >>>   access_token=access_token,
        >>> )
        >>> print(pr)
        PullRequest("feat: modify http lib")

        >>> # create pull request
        >>> base_repo_name = "geekan/MetaGPT"
        >>> head_repo_name = "ioris/MetaGPT"
        >>> base = "master"
        >>> head = "feature/http"
        >>> title = "feat: modify http lib",
        >>> body = "Change HTTP library used to send requests"
        >>> from metagpt.tools.libs import get_env
        >>> access_token = await get_env(key="access_token", app_name="github")
        >>> pr = await git_create_pull(
        >>>   base_repo_name=base_repo_name,
        >>>   head_repo_name=head_repo_name,
        >>>   base=base,
        >>>   head=head,
        >>>   title=title,
        >>>   body=body,
        >>>   access_token=access_token,
        >>> )
        >>> print(pr)
        PullRequest("feat: modify http lib")


    Returns:
        PullRequest: The created pull request.
    """
    return await GitRepository.create_pull(
        base=base,
        head=head,
        base_repo_name=base_repo_name,
        head_repo_name=head_repo_name,
        title=title,
        body=body,
        issue=issue,
        access_token=access_token,
    )


@register_tool(tags=["software development", "create a git issue"])
async def git_create_issue(
    repo_name: str,
    title: str,
    access_token: str,
    body: Optional[str] = None,
) -> Issue:
    """
    Creates an issue on a Git repository.

    Args:
        repo_name (str): The name of the repository.
        title (str): The title of the issue.
        access_token (str): The access token for authentication. Use `get_env` to get access token.
        body (Optional[str], optional): The body of the issue. Defaults to None.

    Example:
        >>> repo_name = "geekan/MetaGPT"
        >>> title = "This is a new issue"
        >>> from metagpt.tools.libs import get_env
        >>> access_token = await get_env(key="access_token", app_name="github")
        >>> body = "This is the issue body."
        >>> issue = await git_create_issue(
        >>>   repo_name=repo_name,
        >>>   title=title,
        >>>   access_token=access_token,
        >>>   body=body,
        >>> )
        >>> print(issue)
        Issue("This is a new issue")

    Returns:
        Issue: The created issue.
    """
    return await GitRepository.create_issue(repo_name=repo_name, title=title, body=body, access_token=access_token)