//! Order-status agent built on Goose, served over HTTP.
//!
//! Goose is a CLI agent, so each request runs `goose run` headless with the
//! developer extension, which lets it call `./order-status.sh` as its tool.
//!
//! POST /run {"prompt": "What's the status of order 42?"} -> {"answer": "..."}
//! Needs the Goose CLI and a configured provider (`goose configure`, or
//! GOOSE_PROVIDER, GOOSE_MODEL and the provider's key). Run: cargo run

use axum::{http::StatusCode, routing::post, Json, Router};
use serde::Deserialize;
use serde_json::{json, Value};
use tokio::process::Command;

const INSTRUCTIONS: &str = "You are a customer support agent. To look up an order, run \
`./order-status.sh <order_id>` in the current directory and answer from its output.";

#[derive(Deserialize)]
struct RunRequest {
    prompt: String,
}

async fn run(Json(req): Json<RunRequest>) -> Result<Json<Value>, (StatusCode, String)> {
    let goose = std::env::var("GOOSE_BIN").unwrap_or_else(|_| "goose".to_string());
    let output = Command::new(goose)
        .args(["run", "--no-session", "--quiet", "--with-builtin", "developer", "--text"])
        .arg(format!("{INSTRUCTIONS}\n\n{}", req.prompt))
        .output()
        .await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("can't run goose: {e}")))?;
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr).into_owned();
        return Err((StatusCode::INTERNAL_SERVER_ERROR, stderr));
    }
    let answer = String::from_utf8_lossy(&output.stdout).trim().to_string();
    Ok(Json(json!({ "answer": answer })))
}

#[tokio::main]
async fn main() {
    let port = std::env::var("PORT").unwrap_or_else(|_| "8000".to_string());
    let listener = tokio::net::TcpListener::bind(format!("0.0.0.0:{port}"))
        .await
        .expect("bind");
    println!("listening on :{port}");
    axum::serve(listener, Router::new().route("/run", post(run)))
        .await
        .expect("serve");
}
