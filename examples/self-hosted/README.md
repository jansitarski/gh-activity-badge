# Self-Hosted / Local Usage Example

This example shows how to run the badge generator locally or on self-hosted runners without GitHub Actions.

## Local Usage

### Prerequisites

- Python 3.8 or higher
- GitHub Personal Access Token

### Setup

1. **Clone the repository**:

```bash
git clone https://github.com/jansitarski/github-stats-badge.git
cd github-stats-badge
```

2. **Create a Personal Access Token**:
   - Go to [GitHub Settings → Personal access tokens](https://github.com/settings/tokens)
   - Generate a token with `repo` and `read:user` scopes
   - Save the token securely

3. **Set environment variables**:

```bash
export GITHUB_USERNAME="your-username"
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"  # Your PAT
export OUTPUT_PATH="gh_stats.svg"
export README_UPDATE="true"
export README_PATH="README.md"
```

4. **Run the script**:

```bash
python3 src/generate_badge.py
```

### Output

The script will:
- Fetch your GitHub statistics
- Generate `gh_stats.svg` in the current directory
- Update your `README.md` if markers are present

## Self-Hosted Runner

You can use this action with GitHub Actions self-hosted runners:

```yaml
name: Update GitHub Stats Badge

on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  update-stats:
    runs-on: self-hosted  # Use your self-hosted runner
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Generate stats badge
        uses: jansitarski/github-stats-badge@v1
        with:
          github_token: ${{ secrets.STATS_TOKEN }}
      
      - name: Commit updated stats
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: 'chore: update GitHub stats badge'
          file_pattern: 'gh_stats.svg README.md'
```

## Scripted Automation

You can create a shell script for regular updates:

**`update-badge.sh`:**

```bash
#!/bin/bash

# Configuration
export GITHUB_USERNAME="your-username"
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
export OUTPUT_PATH="gh_stats.svg"
export README_UPDATE="true"

# Navigate to your profile repository
cd ~/projects/your-profile-repo

# Pull latest changes
git pull

# Generate badge
python3 ~/github-stats-badge/src/generate_badge.py

# Commit and push
if git diff --quiet; then
    echo "No changes to commit"
else
    git add gh_stats.svg README.md
    git commit -m "chore: update GitHub stats badge"
    git push
    echo "Badge updated and pushed"
fi
```

Make it executable:

```bash
chmod +x update-badge.sh
```

### Cron Job

Run automatically with cron (Linux/macOS):

```bash
# Edit crontab
crontab -e

# Add this line to run daily at midnight
0 0 * * * /path/to/update-badge.sh >> /tmp/badge-update.log 2>&1
```

### Windows Task Scheduler

Create a PowerShell script **`update-badge.ps1`**:

```powershell
$env:GITHUB_USERNAME = "your-username"
$env:GITHUB_TOKEN = "ghp_xxxxxxxxxxxx"
$env:OUTPUT_PATH = "gh_stats.svg"

Set-Location "C:\projects\your-profile-repo"
git pull
python src/generate_badge.py

if (git diff --quiet) {
    Write-Host "No changes to commit"
} else {
    git add gh_stats.svg README.md
    git commit -m "chore: update GitHub stats badge"
    git push
    Write-Host "Badge updated and pushed"
}
```

Then schedule it in Task Scheduler to run daily.

## Docker Container

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy script
COPY src/generate_badge.py /app/

# Set environment variables (override at runtime)
ENV GITHUB_USERNAME=""
ENV GITHUB_TOKEN=""
ENV OUTPUT_PATH="gh_stats.svg"

CMD ["python3", "generate_badge.py"]
```

Build and run:

```bash
docker build -t github-stats-badge .

docker run -it --rm \
  -e GITHUB_USERNAME="your-username" \
  -e GITHUB_TOKEN="ghp_xxxxxxxxxxxx" \
  -v $(pwd):/app \
  github-stats-badge
```

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GITHUB_USERNAME` | GitHub username | ✅ Yes | - |
| `GITHUB_TOKEN` | Personal Access Token | ✅ Yes | - |
| `OUTPUT_PATH` | Badge output path | No | `gh_stats.svg` |
| `README_UPDATE` | Update README | No | `true` |
| `README_PATH` | README file path | No | `README.md` |
| `STATS_START_MARKER` | Start marker | No | `<!-- stats:start -->` |
| `STATS_END_MARKER` | End marker | No | `<!-- stats:end -->` |

## Security Notes

- **Never commit your token** to version control
- Use environment variables or secrets managers
- Set appropriate token scopes (minimal required)
- Rotate tokens periodically
- Consider using `.env` file for local development (add to `.gitignore`)

## Troubleshooting

### Permission Denied

```bash
chmod +x src/generate_badge.py
```

### Module Not Found

Ensure you're using Python 3.8+ - the script uses only standard library:

```bash
python3 --version
```

### API Rate Limiting

GitHub has rate limits:
- 5,000 requests/hour for authenticated requests
- Don't run more frequently than every 15 minutes

Check your rate limit status:

```bash
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/rate_limit
```

## Notes

- No external dependencies required (pure Python stdlib)
- Works on Linux, macOS, Windows
- Can be integrated into CI/CD pipelines
- Suitable for air-gapped or restricted environments
