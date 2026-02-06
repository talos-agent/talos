import hmac
import hashlib
import json
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from app.configs.config import config

app = FastAPI(title="Webhook Handler")

async def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature"""
    digest = hmac.new(
        secret.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={digest}", signature)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/webhooks/github")
async def handle_github_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Handle GitHub webhooks"""

    # Get signature
    signature = request.headers.get("x-hub-signature-256")
    if not signature:
        raise HTTPException(400, "Missing signature")

    # Get payload
    payload = await request.body()

    # Verify signature
    if not await verify_signature(payload, signature, config.GITHUB_WEBHOOK_SECRET):
        raise HTTPException(403, "Invalid signature")

    # Parse event
    event_type = request.headers.get("x-github-event")
    payload_json = json.loads(payload)

    # Process based on event type
    if event_type == "push":
        background_tasks.add_task(handle_push_event, payload_json)
    elif event_type == "pull_request":
        background_tasks.add_task(handle_pr_event, payload_json)

    return JSONResponse({"status": "processing"})

async def handle_push_event(payload: dict):
    """Handle push events for auto-deploy"""
    branch = payload.get("ref", "").split("/")[-1]
    commits = payload.get("commits", [])

    if branch == "main":
        print(f"🚀 Main branch updated with {len(commits)} commits")
        # Trigger deploy pipeline
        await trigger_deployment()

async def handle_pr_event(payload: dict):
    """Handle PR events for auto-review"""
    action = payload.get("action")
    pr = payload.get("pull_request", {})

    if action in ["opened", "synchronize"]:
        print(f"📝 PR #{pr.get('number')}: {pr.get('title')}")
        # Trigger CI checks
        await trigger_ci_checks(pr)

async def trigger_deployment():
    """Trigger deployment pipeline"""
    # Implementation for deployment trigger
    pass

async def trigger_ci_checks(pr: dict):
    """Trigger CI checks for PR"""
    # Implementation for CI trigger
    pass
