# 1. Create a Workload Identity Pool
gcloud iam workload-identity-pools create "github-pool" \
    --location="global" \
    --display-name="GitHub Actions Pool"

# 2. Create a Workload Identity Provider for GitHub Actions
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
    --location="global" \
    --workload-identity-pool="github-pool" \
    --display-name="GitHub Actions Provider" \
    --issuer-uri="https://githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository"

# 3. Allow your specific GitHub repository to impersonate the service account
# REPLACE: myusername/myrepo with your GitHub username and repository name (e.g., 'analytics-team/dbt-project')
# REPLACE: dbt-prod-sa@PROJECT_NAME://gserviceaccount.com with your Service Account
export GCP_PROJECT_ID=$(gcloud config get-value project)
export GCP_PROJECT_NUM=$(gcloud projects describe $GCP_PROJECT_ID --format="value(projectNumber)")
export GITHUB_REPO="myusername/myrepo"  # REPLACE with your GitHub username and repository name
gcloud iam service-accounts add-iam-policy-binding "dbt-prod-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://://googleapis.com${GCP_PROJECT_NUM}/locations/global/workloadIdentityPools/github-pool/attribute.repository/${GITHUB_REPO}"
