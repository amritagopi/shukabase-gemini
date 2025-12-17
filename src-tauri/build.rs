fn main() {
  if let Ok(path) = dotenvy::dotenv() {
      println!("cargo:rerun-if-changed={}", path.display());
      if let Ok(key) = std::env::var("APTABASE_KEY") {
          println!("cargo:rustc-env=APTABASE_KEY={}", key);
      }
  }
  tauri_build::build()
}
