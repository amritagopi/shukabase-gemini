# ⚡️ Быстрый старт: Подпись кода

Всего 3 шага за 2 минуты:

1. **Сгенерируйте ключи:**
   ```bash
   npm run tauri signer generate -- -w ваш_пароль
   ```

2. **Добавьте в GitHub Secrets:**
   - `TAURI_PRIVATE_KEY` -> Содежимое файла `src-tauri/keys/private_key.pem`
   - `TAURI_KEY_PASSWORD` -> ваш_пароль

3. **Запушьте код:**
   ```bash
   git push origin main
   ```

✅ **Готово!** GitHub Actions автоматически подпишет сборку.
