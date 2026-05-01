# Basic Usage Example

This example shows the simplest setup for the GitHub Stats Badge Generator.

## Setup

### 1. Add Markers to README

Edit your `README.md` and add these markers where you want the badge:

```markdown
# Your Profile

Some introduction text...

<!-- stats:start -->
<!-- stats:end -->

More content...
```

### 2. Create Workflow

Create `.github/workflows/update-stats.yml`:

```yaml
name: Update GitHub Stats Badge

on:
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday at midnight UTC
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
          github_token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Commit updated stats
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: 'chore: update GitHub stats badge'
          file_pattern: 'gh_stats.svg README.md'
```

### 3. Run Workflow

Go to your repository's **Actions** tab, select **Update GitHub Stats Badge**, and click **Run workflow**.

## Result

After the workflow runs, your README will be updated with the badge between the markers:

```markdown
<!-- stats:start -->
<p align="center">
  <img src="./gh_stats.svg" alt="username's GitHub Stats" />
</p>
<!-- stats:end -->
```

## Notes

- Uses default `GITHUB_TOKEN` (works for public repos only)
- For **private repo stats**, see the main README for PAT setup
- Badge saves to root directory as `gh_stats.svg`
- Automatically updates weekly
