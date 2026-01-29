<#
PowerShell helper to create a feature branch and commit the refactor changes.

Usage (from repository root):
  .\scripts\create_branch_and_commit.ps1 -BranchName "refactor/separation-of-concerns"

This script only stages & commits; it will not push. Review the staged files
before pushing.
#>

param(
    [string]$BranchName = "refactor/separation-of-concerns",
    [string]$Author = "Your Name <you@example.com>"
)

Write-Host "Creating branch $BranchName and committing changes..."

git checkout -b $BranchName

git add .

git commit -m "refactor: separate concerns — add controller, services, view helpers, and background worker"

Write-Host "Committed to branch $BranchName. Review with 'git status' and push when ready:"
Write-Host "  git push -u origin $BranchName"
