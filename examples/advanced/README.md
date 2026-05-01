# Advanced Usage Example

This example shows advanced configuration options for customizing the badge location, markers, and schedule.

## Scenario

You want to:
- Save the badge to `assets/` folder
- Use custom markers in your README
- Update daily instead of weekly
- Use a Personal Access Token for private repo stats

## Setup

### 1. Create Assets Folder

```bash
mkdir -p assets
```

### 2. Add Custom Markers to README

Edit your `README.md` with custom markers:

```markdown
# Your Profile

## GitHub Activity

<!-- BEGIN STATS -->
<!-- END STATS -->
```

### 3. Create Personal Access Token

1. Go to [GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes: `repo` and `read:user`
4. Generate and copy the token
5. Add to repository secrets as `STATS_TOKEN`

### 4. Create Advanced Workflow

Create `.github/workflows/update-stats.yml`:

```yaml
name: Update GitHub Stats Badge

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight UTC
  workflow_dispatch:

permissions:
  contents: write

jobs:
  update-stats:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Generate stats badge
        uses: jansitarski/github-stats-badge@v1
        with:
          github_token: ${{ secrets.STATS_TOKEN }}
          output_path: assets/github-stats.svg
          stats_start_marker: '<!-- BEGIN STATS -->'
          stats_end_marker: '<!-- END STATS -->'
      
      - name: Commit updated stats
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: 'chore: update GitHub stats badge [skip ci]'
          file_pattern: 'assets/github-stats.svg README.md'
```

### 5. Update .gitignore (Optional)

If you want to exclude the badge from version control:

```gitignore
# Ignore generated badge
assets/github-stats.svg
```

Then remove the badge from `file_pattern` in the workflow.

## Multiple Schedules

You can run the workflow on multiple schedules:

```yaml
on:
  schedule:
    # Every day at midnight
    - cron: '0 0 * * *'
    # Every Monday at 9 AM
    - cron: '0 9 * * 1'
    # First day of the month
    - cron: '0 0 1 * *'
  workflow_dispatch:
```

## Different Configurations for Different Users

You can generate badges for different users:

```yaml
jobs:
  update-my-stats:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate my stats
        uses: jansitarski/github-stats-badge@v1
        with:
          github_token: ${{ secrets.MY_TOKEN }}
          username: my-username
          output_path: my-stats.svg
          readme_update: 'false'
      
      - name: Generate team stats
        uses: jansitarski/github-stats-badge@v1
        with:
          github_token: ${{ secrets.TEAM_TOKEN }}
          username: team-member
          output_path: team-stats.svg
          readme_update: 'false'
      
      - name: Commit
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: 'chore: update stats badges'
          file_pattern: '*-stats.svg'
```

## Result

Your badge will be saved to `assets/github-stats.svg` and automatically embedded in your README between the custom markers.

## Notes

- Personal Access Token allows access to private repo statistics
- Daily updates keep stats fresh
- Custom output path keeps repository organized
- `[skip ci]` in commit message prevents infinite workflow loops
