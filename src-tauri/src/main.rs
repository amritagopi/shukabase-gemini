// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

#[tokio::main]
async fn main() {
  let _guard = sentry::init(("https://e1d334a9f0c3f9dfc3bf6762742e4ce1@04509290473324544.ingest.de.sentry.io/4510551299129424", sentry::ClientOptions {
      release: sentry::release_name!(),
      send_default_pii: true,
      ..Default::default()
  }));

  app_lib::run();
}
