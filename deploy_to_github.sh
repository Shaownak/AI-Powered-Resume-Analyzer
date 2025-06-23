#!/bin/bash
# Quick deployment script for GitHub Actions

echo "🚀 Starting GitHub deployment process..."

# Step 1: Push to GitHub
echo "📤 Pushing code to GitHub..."
git add .
git commit -m "Add CI/CD pipeline and deployment configuration"
git push origin main

# Step 2: Create develop branch if it doesn't exist
if ! git show-ref --verify --quiet refs/heads/develop; then
    echo "🌿 Creating develop branch..."
    git checkout -b develop
    git push -u origin develop
    git checkout main
fi

echo "✅ Code pushed to GitHub!"
echo ""
echo "🔧 Next steps:"
echo "1. Go to your GitHub repository settings"
echo "2. Add the required secrets (see DEPLOYMENT_SECRETS.md)"
echo "3. Set up your production server (see CICD_DEPLOYMENT_GUIDE.md)"
echo "4. Make a test commit to trigger the CI/CD pipeline"
echo ""
echo "📋 Required GitHub Secrets:"
echo "   - PRODUCTION_HOST"
echo "   - PRODUCTION_USER" 
echo "   - PRODUCTION_SSH_KEY"
echo "   - PRODUCTION_DOMAIN"
echo ""
echo "📚 Documentation:"
echo "   - CICD_DEPLOYMENT_GUIDE.md - Complete setup guide"
echo "   - DEPLOYMENT_SECRETS.md - Secrets configuration"
echo "   - .github/workflows/main.yml - CI/CD pipeline"
echo ""
echo "🎯 Test the pipeline:"
echo "   git commit -m 'Test CI/CD pipeline' --allow-empty"
echo "   git push origin main"
