use std::process::{Command, Child};
use std::sync::Mutex;
use tauri::Manager;

struct AppState {
    python_process: Mutex<Option<Child>>,
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  let state = AppState {
      python_process: Mutex::new(None),
  };

  tauri::Builder::default()
    .manage(state)
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }

      // Запускаем Python RAG сервер
      let app_handle = app.handle().clone();
      std::thread::spawn(move || {
          if let Some(state) = app_handle.try_state::<AppState>() {
              let python_script = if cfg!(debug_assertions) {
                  // В режиме разработки - поднимаемся из src-tauri в корень проекта
                  std::env::current_dir()
                      .unwrap()
                      .parent()
                      .unwrap()
                      .join("rag")
                      .join("rag_api_server.py")
              } else {
                  // В продакшене - из ресурсов
                  let resource_path = app_handle.path().resource_dir()
                      .unwrap_or_else(|_| std::env::current_dir().unwrap());
                  resource_path.join("rag").join("rag_api_server.py")
              };

              println!("Запуск Python сервера: {:?}", python_script);

              // Запускаем Python процесс из корня проекта
              let project_root = python_script.parent().unwrap().parent().unwrap();
              
              println!("Project root: {:?}", project_root);

              match Command::new("python")
                  .arg(&python_script)
                  .current_dir(project_root)
                  .spawn()
              {
                  Ok(child) => {
                      println!("✅ Python RAG сервер запущен (PID: {})", child.id());
                      *state.python_process.lock().unwrap() = Some(child);
                  }
                  Err(e) => {
                      eprintln!("❌ Ошибка запуска Python сервера: {}", e);
                      eprintln!("💡 Попробуйте запустить вручную: python rag/rag_api_server.py");
                  }
              }
          }
      });

      Ok(())
    })
    .on_window_event(|window, event| {
        if let tauri::WindowEvent::Destroyed = event {
            // Останавливаем Python процесс при закрытии окна
            if let Some(state) = window.try_state::<AppState>() {
                if let Some(mut child) = state.python_process.lock().unwrap().take() {
                    let _ = child.kill();
                    println!("🛑 Python RAG сервер остановлен");
                }
            }
        }
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
