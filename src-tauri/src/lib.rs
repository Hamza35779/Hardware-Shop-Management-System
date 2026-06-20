use std::sync::Mutex;
use std::path::PathBuf;
use tauri::{Manager, State};

mod db;
mod sys;
mod service;
mod ai;

use db::{DbManager, Product, Contact, Transaction, PriceHistoryEntry};
use sys::SystemMetrics;

pub struct AppState {
    db: Mutex<DbManager>,
    app_data_dir: PathBuf,
}

#[tauri::command]
fn get_products(state: State<AppState>) -> Result<Vec<Product>, String> {
    let db = state.db.lock().map_err(|e| e.to_string())?;
    db.get_products().map_err(|e| e.to_string())
}

#[tauri::command]
fn add_product(state: State<AppState>, product: Product) -> Result<i64, String> {
    let db = state.db.lock().map_err(|e| e.to_string())?;
    db.insert_product(product).map_err(|e| e.to_string())
}

#[tauri::command]
fn update_product(state: State<AppState>, product: Product) -> Result<(), String> {
    let db = state.db.lock().map_err(|e| e.to_string())?;
    db.update_product(product).map_err(|e| e.to_string())
}

#[tauri::command]
fn delete_product(state: State<AppState>, id: i64) -> Result<(), String> {
    let db = state.db.lock().map_err(|e| e.to_string())?;
    db.delete_product(id).map_err(|e| e.to_string())
}

#[tauri::command]
fn adjust_stock(state: State<AppState>, id: i64, change: f64) -> Result<(), String> {
    let db = state.db.lock().map_err(|e| e.to_string())?;
    db.adjust_stock(id, change).map_err(|e| e.to_string())
}

#[tauri::command]
fn get_contacts(state: State<AppState>) -> Result<Vec<Contact>, String> {
    let db = state.db.lock().map_err(|e| e.to_string())?;
    db.get_contacts().map_err(|e| e.to_string())
}

#[tauri::command]
fn add_contact(state: State<AppState>, contact: Contact) -> Result<i64, String> {
    let db = state.db.lock().map_err(|e| e.to_string())?;
    db.insert_contact(contact).map_err(|e| e.to_string())
}

#[tauri::command]
fn get_transactions(state: State<AppState>, contact_id: Option<i64>) -> Result<Vec<Transaction>, String> {
    let db = state.db.lock().map_err(|e| e.to_string())?;
    db.get_transactions(contact_id).map_err(|e| e.to_string())
}

#[tauri::command]
fn add_transaction(state: State<AppState>, transaction: Transaction) -> Result<i64, String> {
    let db = state.db.lock().map_err(|e| e.to_string())?;
    db.insert_transaction(transaction).map_err(|e| e.to_string())
}

#[tauri::command]
fn get_sys_metrics() -> Result<SystemMetrics, String> {
    Ok(sys::get_system_metrics())
}

#[tauri::command]
fn query_ai_chat(state: State<AppState>, prompt: String) -> Result<String, String> {
    let db = state.db.lock().map_err(|e| e.to_string())?;
    
    // Fetch current state for AI context mapping
    let products = db.get_products().unwrap_or_default();
    let contacts = db.get_contacts().unwrap_or_default();
    let transactions = db.get_transactions(None).unwrap_or_default();

    let products_json = serde_json::to_string(&products).unwrap_or_default();
    let contacts_json = serde_json::to_string(&contacts).unwrap_or_default();
    let transactions_json = serde_json::to_string(&transactions).unwrap_or_default();

    Ok(ai::execute_ai_query(
        &prompt,
        &products_json,
        &contacts_json,
        &transactions_json,
        state.app_data_dir.clone(),
    ))
}

#[tauri::command]
fn save_product_image(state: State<AppState>, sku: String, base64_data: String) -> Result<String, String> {
    let images_dir = state.app_data_dir.join("images");
    std::fs::create_dir_all(&images_dir).map_err(|e| e.to_string())?;
    
    let file_path = images_dir.join(format!("{}.png", sku));
    let cleaned_base64 = if base64_data.contains(",") {
        base64_data.split(",").nth(1).unwrap_or(&base64_data)
    } else {
        &base64_data
    };

    use base64::{Engine as _, engine::general_purpose};
    let data = general_purpose::STANDARD.decode(cleaned_base64).map_err(|e| e.to_string())?;
    std::fs::write(&file_path, data).map_err(|e| e.to_string())?;
    
    Ok(file_path.to_string_lossy().to_string())
}

#[tauri::command]
fn load_product_image_base64(path: String) -> Result<String, String> {
    let data = std::fs::read(&path).map_err(|e| e.to_string())?;
    use base64::{Engine as _, engine::general_purpose};
    let encoded = general_purpose::STANDARD.encode(data);
    Ok(format!("data:image/png;base64,{}", encoded))
}

#[tauri::command]
fn get_price_history(state: State<AppState>, id: i64) -> Result<Vec<PriceHistoryEntry>, String> {
    let db = state.db.lock().map_err(|e| e.to_string())?;
    db.get_price_history(id).map_err(|e| e.to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    service::start_service_loop_detached();

    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .setup(|app| {
            let app_data_dir = app.path().app_data_dir().unwrap_or_else(|_| PathBuf::from("./"));
            let db_mgr = DbManager::new(app_data_dir.clone());
            
            app.manage(AppState {
                db: Mutex::new(db_mgr),
                app_data_dir,
            });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            get_products,
            add_product,
            update_product,
            delete_product,
            adjust_stock,
            get_contacts,
            add_contact,
            get_transactions,
            add_transaction,
            get_sys_metrics,
            query_ai_chat,
            save_product_image,
            load_product_image_base64,
            get_price_history,
            service::check_service_status
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
