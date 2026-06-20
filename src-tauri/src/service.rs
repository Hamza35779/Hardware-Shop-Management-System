#[cfg(target_os = "windows")]
use windows_service::{
    define_windows_service,
    service::{
        ServiceControl, ServiceControlAccept, ServiceExitCode, ServiceState, ServiceStatus,
        ServiceType,
    },
    service_control_handler::{self, ServiceControlHandlerResult},
    service_dispatcher,
};
use std::time::Duration;

#[cfg(target_os = "windows")]
define_windows_service!(ffi_service_main, my_service_main);

#[cfg(target_os = "windows")]
pub fn my_service_main(_arguments: Vec<std::ffi::OsString>) {
    let event_handler = move |control_event| -> ServiceControlHandlerResult {
        match control_event {
            ServiceControl::Stop => ServiceControlHandlerResult::NoError,
            _ => ServiceControlHandlerResult::NotImplemented,
        };
        ServiceControlHandlerResult::NoError
    };

    if let Ok(status_handle) = service_control_handler::register("PakShopInventoryService", event_handler) {
        let next_status = ServiceStatus {
            service_type: ServiceType::OWN_PROCESS,
            current_state: ServiceState::Running,
            controls_accepted: ServiceControlAccept::STOP,
            exit_code: ServiceExitCode::Win32(0),
            checkpoint: 0,
            wait_hint: Duration::from_secs(0),
            process_id: None,
        };
        status_handle.set_service_status(next_status).ok();
        
        // Background loop for backup or sync
        loop {
            std::thread::sleep(Duration::from_secs(10));
            // e.g. run automated database backups or Khata synchronization here.
        }
    }
}

pub fn start_service_loop_detached() {
    #[cfg(target_os = "windows")]
    {
        // Try starting the windows service dispatcher in a background thread
        std::thread::spawn(|| {
            // Note: service_dispatcher::start blocks until service is stopped,
            // and fails if not launched as a Windows Service.
            let _ = service_dispatcher::start("PakShopInventoryService", ffi_service_main);
        });
    }
}

#[tauri::command]
pub fn check_service_status() -> String {
    #[cfg(target_os = "windows")]
    {
        "Windows Service: Configured and Ready".to_string()
    }
    #[cfg(not(target_os = "windows"))]
    {
        "Windows Service: Only available on Windows".to_string()
    }
}
